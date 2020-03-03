# -*- coding: utf-8 -*-
import sys
import logging
import time
import json

import requests
import pandas as pd

from thomas.core import BayesianNetwork

class Client(object):
    """A client for Thomas' RESTful API and webinterface"""

    def __init__(self, host: str='http://localhost', port: int=5000, path: str=''):
        """Create a new Client instance.

        Args:
            host (str): hostname
            port (int): port
            path (str): path
        """
        self.host = host
        self.port = port
        self.path = path

        self._access_token = None
        self._refresh_token = None
        self._refresh_url = ''

        self.log = logging.getLogger(__name__)

    @property
    def base_path(self):
        """Return the servers' base path."""
        if self.port:
            return f"{self.host}:{self.port}{self.path}"

        return f"{self.host}{self.path}"

    @property
    def headers(self):
        if self._access_token:
            return {'Authorization': 'Bearer ' + self._access_token}
        else:
            return {}

    def generate_url_to(self, endpoint: str):
        """Generate URL from host port and endpoint"""
        if endpoint.startswith('/'):
            path = self.base_path + endpoint
        else:
            path = self.base_path + '/' + endpoint

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
        url = self.generate_url_to(endpoint)
        response = rest_method(
            url,
            json=json,
            headers=self.headers,
            params=params
        )

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

        return response.json()

    def authenticate(self, username, password, endpoint="token"):
        """Authenticate using username/password."""
        credentials = {'username': username,'password': password}
        url = self.generate_url_to(endpoint)

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
        url = self.generate_url_to(self._refresh_url)
        response = requests.post(
            url,
            headers={'Authorization': f'Bearer {self._refresh_token}'}
        )

        # server says no!
        if response.status_code != 200:
            self.log.critical("Could not refresh token")
            raise Exception("Authentication Error!")

        self._access_token = response.json()["_access_token"]

    def get_network(self, id_=None):
        """Return a list of networks form the server."""
        if id_:
            result = self.request(f'network/{id_}')
            return BayesianNetwork.from_dict(result['json'])

        return pd.DataFrame(self.request('network'))
