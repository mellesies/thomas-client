# The Dockerfile tells Docker how to construct the image.
FROM mellesies/thomas-core:latest

LABEL maintainer="Melle Sieswerda <m.sieswerda@iknl.nl>"


# Copy package
COPY . /usr/local/python/thomas-client/

# Copy Jupyter settings
COPY lab-settings /root/.jupyter/lab/

WORKDIR /usr/local/python/

RUN pip install thomas-jupyter-widget
RUN jupyter labextension install --minimize=False thomas-jupyter-widget
RUN pip install -e ./thomas-client
RUN cp thomas-client/notebooks/6.\ Using\ the\ server.ipynb thomas-core/notebooks

# JupyterLab runs on port 8888
EXPOSE 8888

# CMD /bin/bash
WORKDIR /usr/local/python/thomas-core/notebooks
CMD jupyter lab --ip 0.0.0.0 --allow-root --LabApp.token=''
