FROM debian:buster-slim

USER root

RUN apt-get clean -y && apt-get update -y && \
    apt-get install --no-install-recommends -y python3-pip python3-setuptools python3-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install argparse prometheus_client requests mock

COPY jupyterhub_users_exporter.py /usr/bin/jupyterhub_users_exporter.py
COPY test.py /usr/bin/test.py
RUN chmod +x /usr/bin/jupyterhub_users_exporter.py /usr/bin/test.py
CMD python3 -u /usr/bin/jupyterhub_users_exporter.py

# Create a non-root user
RUN useradd -m -u 1000 -s /bin/bash user
USER 1000

EXPOSE 8000
