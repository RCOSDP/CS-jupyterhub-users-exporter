## How to use

### Set environment variables
- `JUPYTER_HUB_HOST`: Host and port (default: `127.0.0.1:8000`)
- `JUPYTER_HUB_API_TOKEN`: API token of JupyterHub (can be created on the JupyterHub Admin UI)
- `JUE_INTERVAL`: Time interval to retrieve information (unit: seconds, default: 10)

### To execute directly 

```python jupyterhub_users_exporter.py -p 8070```

### By docker 

```
docker build --tag jupyterhub-users-exporter .
docker run -it --rm jupyterhub-users-exporter
```

## DockerHub

https://hub.docker.com/r/lmeval/jupyterhub_users_exporter
