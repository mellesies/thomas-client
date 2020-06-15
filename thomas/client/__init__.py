# -*- coding: utf-8 -*-
import sys
import logging
import time
import json

# from urllib import parse
import requests

import pandas as pd

from thomas.core import BayesianNetwork

class ServerError(Exception):
    """Raised on server error."""

    def __init__(self, message, status_code):
        """Create a new instance."""
        super().__init__(message, status_code)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f'HTTP {self.status_code}: {self.message}'


class Client(object):
    """A client for Thomas' RESTful API and webinterface"""

    def __init__(self, url: str='http://localhost:5000'):
        """Create a new Client instance.

        Args:
            url (str): URL to the server, may include protocol & port number.
            port (int): port
            path (str): path
        """
        self.url = url

        self._access_token = None
        self._refresh_token = None
        self._refresh_url = ''
        self._metadata = {}

        self.log = logging.getLogger(__name__)

    @property
    def headers(self):
        if self._access_token:
            return {'Authorization': 'Bearer ' + self._access_token}
        else:
            return {}

    def url_to(self, endpoint: str):
        """Generate URL from host port and endpoint"""
        if endpoint.startswith('/'):
            path = self.url + endpoint
        else:
            path = self.url + '/' + endpoint

        return path

    def request(self, endpoint: str, json: dict=None, method: str='GET',
                params=None, first_try=True):
        """Perform HTTP request"""

        # get appropiate method
        rest_method = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'PATCH': requests.patch,
            'DELETE': requests.delete
        }.get(method.upper(), 'GET')

        # send request to server
        url = self.url_to(endpoint)
        response = rest_method(
            url,
            json=json,
            headers=self.headers,
            params=params
        )

        json_data = response.json()

        # server says no!
        if response.status_code > 200:
            self.log.error(f'Server responded with error code: {response.status_code}')
            self.log.debug(response)

            if response.status_code == 401 and first_try:
                self.log.info(f'Trying to refresh token ...')
                self.refresh_token()
                return self.request(endpoint, json, method, params, False)
            else:
                self.log.warn(f'Not refreshing token ...')
                raise ServerError(json_data['message'], response.status_code)

        return json_data

    def authenticate(self, username, password, endpoint="token"):
        """Authenticate using username/password."""
        credentials = {'username': username,'password': password}
        url = self.url_to(endpoint)

        response = requests.post(url, json=credentials)
        data = {}

        try:
            data = response.json()
        except:
            pass

        # handle negative responses
        if response.status_code > 200:
            self.log.critical(f"Failed to authenticate {data.get('msg')}")
            raise Exception("Failed to authenticate")

        # store tokens
        self.log.info("Successfully authenticated!")
        self._access_token = data.get("access_token")
        self._refresh_token = data.get("refresh_token")
        self._refresh_url = data.get("refresh_url")

    def refresh_token(self):
        """Refresh the access token."""
        self.log.info("Refreshing token")

        # send request to server
        url = self.url_to(self._refresh_url)
        response = requests.post(
            url,
            headers={'Authorization': f'Bearer {self._refresh_token}'}
        )

        # server says no!
        if response.status_code != 200:
            self.log.critical("Could not refresh token")
            raise Exception("Authentication Error!")

        self._access_token = response.json()["_access_token"]

    def list_networks(self):
        """Return the networks available on the server as a pandas.DataFrame."""
        df = pd.DataFrame(self.request('network'))

        try:
            df = df[['id', 'name', 'owner']]
        except:
            pass

        return df

    def load(self, id_):
        """Load a Bayesian Network from the server.

        Args:
            id_ (str): id of a Bayesian Network on the server.

        Return:
            BayesianNetwork
        """
        response = self.request(f'network/{id_}')
        json_data = response.pop('json')
        bn = BayesianNetwork.from_dict(json_data)
        self._metadata[bn] = response

        return bn

    def save_as(self, bn, as_):
        """Save a network as ...

        Args:
            bn (BayesianNetwork): Bayesian Network.
            as_ (str): identifier to use when saving
        """
        # If 'as_' is specified, we'll use that value to create a new
        # network on the server.
        bn = bn.copy()

        resource = {
            "id": as_,
            "name": bn.name,
            "json": bn.as_dict(),
        }

        response = self.request('/network', resource, 'POST')
        response.pop('json')

        self._metadata[bn] = response
        return bn


    def save(self, bn):
        """Save a Bayesian Network on the server.

        Args:
            bn (BayesianNetwork): Bayesian Network. After calling this function
                bn.id will be set if it wasn't already.
        """
        # If bn.id is set, we can assume the bn has been loaded from the
        # server.
        try:
            metadata = self._metadata[bn]
        except KeyError:
            id_ = None
        else:
            id_ = metadata['id']

        endpoint = f'/network/{id_}' if id_ else '/network'

        resource = {
            "name": bn.name,
            "json": bn.as_dict(),
        }

        response = self.request(endpoint, resource, 'POST')
        response.pop('json')
        self._metadata[bn] = response


