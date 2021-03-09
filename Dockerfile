FROM debian:buster-slim

USER root

RUN apt-get clean -y && apt-get update -y && \
    apt-get install --no-install-recommends -y python3-pip python3-setuptools python3-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install argparse prometheus_client requests

COPY jupyterhub_users_exporter.py /usr/bin/jupyterhub_users_exporter.py
RUN chmod +x /usr/bin/jupyterhub_users_exporter.py
CMD python3 -u /usr/bin/jupyterhub_users_exporter.py

EXPOSE 8000
