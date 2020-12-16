#!/usr/bin/env python3
import subprocess, socket, argparse, os, asyncio, sys
import urllib
import requests
import time
from prometheus_client import Counter, start_http_server, Gauge

metric_labels = ['user', 'org']

api_host = 'http://127.0.0.1:8000'
api_url = api_host + '/hub/api'
token = '7db0e93d8a314e3caf12c2461aa739da'


# Run tcpdump and stream the packets out
def stream_packets():
    while True:
        try:
            r = requests.get(api_url + '/users',
                             headers={'Authorization': 'token %s' % token, }
            )
            r.raise_for_status()
            users = r.json()

            for user in users:
                labels = {
                    'user': user['name'],
                    'org': 'fuga',
                }
                try: 
                    kernel_num = 0
                    for k, server in user['servers'].items():
                        r = requests.get(api_host + server['url'] + 'api/kernels',
                                         headers={'Authorization': 'token %s' % token,}
                        )
                        r.raise_for_status()
                        kernel_num += len(r.json())
                    server_num_gauge.labels(**labels).set(len(user['servers']))
                    kernel_num_gauge.labels(**labels).set(kernel_num)
                except Exception as e:
                    print(f'Failed to retrieve user information: {e}')
        except Exception as e:
            print(f'Failed to retrieve hub information: {e}')
        time.sleep(60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', default=int(os.getenv('NOE_PORT', 8000)),
        help='The Prometheus metrics port.')
    parser.add_argument('--metric_prefix', '-s', default=os.getenv('NOE_METRIC_PREFIX', 'jue'),
        help='Metric prefix (group) for Prometheus')
    opts = parser.parse_args()

    server_num_gauge = Gauge(f'{opts.metric_prefix}_server_num', 'Number of servers for each user', metric_labels)
    kernel_num_gauge = Gauge(f'{opts.metric_prefix}_kernel_num', 'Number of kernels for each user', metric_labels)
    
    start_http_server(int(opts.port))
    asyncio.run(stream_packets())
