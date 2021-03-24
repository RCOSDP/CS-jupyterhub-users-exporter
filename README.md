## How to use

### Set environment variables
- `EXPOSED_PORT`: Port where the metrics will be exposed (default: `9000`)
- `METRICS_PREFIX`: Prefix to be added into the metrics names (default: `jue`)
- `JUPYTER_HUB_HOST`: Host (default: `127.0.0.1`)
- `JUPYTER_HUB_PORT`:  Port (default: `8000`)
- `JUPYTER_HUB_API_TOKEN`: API token of JupyterHub which can be created on the JupyterHub Admin UI (default: None)
- `JUE_INTERVAL`: Time interval to retrieve information (default: 10, unit: seconds)

### Execute by docker 

```
docker build --tag jupyterhub-users-exporter .
docker run -it --rm jupyterhub-users-exporter python3 /usr/bin/test.py # for testing
docker run -it --rm jupyterhub-users-exporter
```

## DockerHub

https://hub.docker.com/r/lmeval/jupyterhub_users_exporter
