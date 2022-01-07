#!/usr/bin/env python3
import subprocess, argparse, os
import urllib
import requests
import time
from prometheus_client import Counter, start_http_server, Gauge

metric_labels = ['user', 'org']

def monitor_metrics(api_host, token, only_servers):
    try:
        api_url = api_host + '/hub/api'
        request_headers = {'Authorization': 'token %s' % token, }
        r = requests.get(api_url + '/users',
                         headers=request_headers)
        r.raise_for_status()
        users = r.json()
        
        for user in users:
            if '@' in user['name']:
                (name, org) = user['name'].rsplit('@')
                labels = {
                    'user': name,
                    'org': org,
                }
            else:
                labels = {
                    'user': user['name'],
                    'org': 'none',
                }
            try: 
                kernel_num = 0
                terminal_num = 0
                for k, server in user['servers'].items():
                    server_num_gauge.labels(**labels).set(len(user['servers']))
                    if not only_servers:
                        try:
                            r = requests.get(api_host + server['url'] + 'api/kernels',
                                             headers=request_headers
                            )
                            r.raise_for_status()
                            kernel_num += len(r.json())
                            r = requests.get(api_host + server['url'] + 'api/terminals',
                                             headers=request_headers
                            )
                            r.raise_for_status()
                            terminal_num += len(r.json())
                        except requests.exceptions.HTTPError as e:
                            print(f'Failed to retrieve server information: {e}')
                        kernel_num_gauge.labels(**labels).set(kernel_num)
                        terminal_num_gauge.labels(**labels).set(terminal_num)
            except Exception as e:
                print(f'Failed to retrieve user information: {e}')
    except Exception as e:
        print(f'Failed to retrieve hub information: {e}')

def get_gauges(prefix):
    return (Gauge(f'{prefix}_server_num', 'Number of servers for each user', metric_labels),
            Gauge(f'{prefix}_kernel_num', 'Number of kernels for each user', metric_labels),
            Gauge(f'{prefix}_terminal_num', 'Number of terminals for each user', metric_labels)
    )
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', default=int(os.getenv('EXPOSED_PORT', 9000)),
        help='The Prometheus metrics port.')
    parser.add_argument('--interval', '-i', default=int(os.environ.get('JUE_INTERVAL', 10)))
    parser.add_argument('--metrics_prefix', '-m', default=os.getenv('METRICS_PREFIX', 'jue'),
        help='Metrics prefix (group) for Prometheus')
    parser.add_argument('--jupyterhub_host', default=os.environ.get('JUPYTER_HUB_HOST', '127.0.0.1'))
    parser.add_argument('--jupyterhub_port', default=os.environ.get('JUPYTER_HUB_PORT', '8000'))
    parser.add_argument('--jupyterhub_token', default=os.environ.get('JUPYTER_HUB_API_TOKEN', ''))
    parser.add_argument('--servers_only', action='store_true')
    opts = parser.parse_args()

    server_num_gauge, kernel_num_gauge, terminal_num_gauge = get_gauges(opts.metrics_prefix)
    start_http_server(int(opts.port))
    print(f'Started to monitor JupyterHub users...')
    while True:
        monitor_metrics(f'http://{opts.jupyterhub_host}:{opts.jupyterhub_port}', opts.jupyterhub_token, os.environ.get('JUE_ONLY_SERVERS', '').lower() == 'true')
        time.sleep(opts.interval)
