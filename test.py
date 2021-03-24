import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import jupyterhub_users_exporter as jue

import io
import requests
import unittest
import mock


(jue.server_num_gauge,
 jue.kernel_num_gauge,
 jue.terminal_num_gauge) = jue.get_gauges('jue')

class TestMonitorMetrics(unittest.TestCase):
    
    def test_no_exception_when_no_user_exists(self):
        requests.get = mock.MagicMock(side_effect=lambda *args, **kwargs:mock.Mock(raise_for_status=lambda: None, json=lambda: []))
        jue.monitor_metrics('http://localhost', 'dummy-token')
        requests.get.assert_called_with('http://localhost/hub/api/users', headers={'Authorization': 'token dummy-token'})

    def test_for_one_user(self):
        def side_effect(*args, **kwargs):
            if args[0] == 'http://localhost/hub/api/users':          
                return mock.Mock(raise_for_status=lambda: None,
                                 json=lambda: [{'name': 'test@example.com', 'servers': {'server1': {'url': '/user/test/'}}}])
            if args[0] == 'http://localhost/user/test/api/kernels':
                return mock.Mock(raise_for_status=lambda: None, json=lambda: ['dummy1', 'dummy2'])
            if args[0] == 'http://localhost/user/test/api/terminals':
                return mock.Mock(raise_for_status=lambda: None, json=lambda: ['dummy1', 'dummy2', 'dummy3'])

        requests.get = mock.MagicMock(side_effect=side_effect)
        jue.monitor_metrics('http://localhost', 'dummy-token')
        requests.get.assert_has_calls(
            [
                mock.call('http://localhost/hub/api/users', headers={'Authorization': 'token dummy-token'}),
                mock.call('http://localhost/user/test/api/kernels', headers={'Authorization': 'token dummy-token'}),
                mock.call('http://localhost/user/test/api/terminals', headers={'Authorization': 'token dummy-token'})
            ]
        )
        self.assertEqual(jue.server_num_gauge.labels(user='test', org='example.com')._value._value, 1.0)
        self.assertEqual(jue.kernel_num_gauge.labels(user='test', org='example.com')._value._value, 2.0)
        self.assertEqual(jue.terminal_num_gauge.labels(user='test', org='example.com')._value._value, 3.0)


    def test_for_two_users(self):
        def side_effect(*args, **kwargs):
            if args[0] == 'http://localhost/hub/api/users':          
                return mock.Mock(raise_for_status=lambda: None,
                                 json=lambda: [
                                     {'name': 'test@example.com', 'servers': {'server1': {'url': '/user/test/'}}},
                                     {'name': 'test2@example2.com', 'servers': {'server2': {'url': '/user/test2/'},
                                                                                'server3': {'url': '/user/test2/server3/'}}}
                                 ])
            if args[0] == 'http://localhost/user/test/api/kernels':
                return mock.Mock(raise_for_status=lambda: None, json=lambda: ['dummy1', 'dummy2'])
            if args[0] == 'http://localhost/user/test/api/terminals':
                return mock.Mock(raise_for_status=lambda: None, json=lambda: ['dummy1', 'dummy2', 'dummy3'])
            if args[0] == 'http://localhost/user/test2/api/kernels':
                return mock.Mock(raise_for_status=lambda: None, json=lambda: ['dummy4'])
            if args[0] == 'http://localhost/user/test2/api/terminals':
                return mock.Mock(raise_for_status=lambda: None, json=lambda: ['dummy5'])
            if args[0] == 'http://localhost/user/test2/server3/api/kernels':
                return mock.Mock(raise_for_status=lambda: None, json=lambda: ['dummy6', 'dummy7', 'dummy8'])
            if args[0] == 'http://localhost/user/test2/server3/api/terminals':
                return mock.Mock(raise_for_status=lambda: None, json=lambda: [])


        requests.get = mock.MagicMock(side_effect=side_effect)
        jue.monitor_metrics('http://localhost', 'dummy-token')
        requests.get.assert_has_calls(
            [
                mock.call('http://localhost/hub/api/users', headers={'Authorization': 'token dummy-token'}),
                mock.call('http://localhost/user/test/api/kernels', headers={'Authorization': 'token dummy-token'}),
                mock.call('http://localhost/user/test/api/terminals', headers={'Authorization': 'token dummy-token'}),
                mock.call('http://localhost/user/test2/api/kernels', headers={'Authorization': 'token dummy-token'}),
                mock.call('http://localhost/user/test2/api/terminals', headers={'Authorization': 'token dummy-token'}),
                mock.call('http://localhost/user/test2/server3/api/kernels', headers={'Authorization': 'token dummy-token'}),
                mock.call('http://localhost/user/test2/server3/api/terminals', headers={'Authorization': 'token dummy-token'}),
            ]
        )
        self.assertEqual(jue.server_num_gauge.labels(user='test', org='example.com')._value._value, 1.0)
        self.assertEqual(jue.kernel_num_gauge.labels(user='test', org='example.com')._value._value, 2.0)
        self.assertEqual(jue.terminal_num_gauge.labels(user='test', org='example.com')._value._value, 3.0)
        self.assertEqual(jue.server_num_gauge.labels(user='test2', org='example2.com')._value._value, 2.0)
        self.assertEqual(jue.kernel_num_gauge.labels(user='test2', org='example2.com')._value._value, 4.0)
        self.assertEqual(jue.terminal_num_gauge.labels(user='test2', org='example2.com')._value._value, 1.0)
        
    def test_exporter_still_alive_even_if_request_failed(self):
        sys.stdout = io.StringIO() # suppress stdout
        def dummy_raise():
            raise Exception('Because this is anomaly test')
        requests.get = mock.MagicMock(side_effect=lambda *args, **kwargs:mock.Mock(raise_for_status=dummy_raise, json=lambda: []))
        jue.monitor_metrics('http://localhost', 'dummy-token')
        requests.get.assert_called_with('http://localhost/hub/api/users', headers={'Authorization': 'token dummy-token'})
        sys.stdout = sys.__stdout__

        
if __name__ == '__main__':
    unittest.main()
