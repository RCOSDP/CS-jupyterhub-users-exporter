## How to use

### Set environment variables
- `EXPOSED_PORT`: Port where the metrics will be exposed (default: `9000`)
- `METRICS_PREFIX`: Prefix to be added into the metrics names (default: `jue`)
- `JUPYTER_HUB_HOST`: Host (default: `127.0.0.1`)
- `JUPYTER_HUB_PORT`:  Port (default: `8000`)
- `JUPYTER_HUB_API_TOKEN`: API token of JupyterHub (can be created on the JupyterHub Admin UI)
- `JUE_INTERVAL`: Time interval to retrieve information (unit: seconds, default: 10)

### To execute directly 

```python jupyterhub_users_exporter.py```

### By docker 

```
docker build --tag jupyterhub-users-exporter .
docker run -it --rm jupyterhub-users-exporter
```

## DockerHub

https://hub.docker.com/r/lmeval/jupyterhub_users_exporter
