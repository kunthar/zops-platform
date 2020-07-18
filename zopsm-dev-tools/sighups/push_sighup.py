#!/usr/bin/env python3
import consul
import urllib
import json
import time
import socket
from functools import reduce
import logging

docker_container_names= []
consul_client = consul.Consul(host=socket.gethostbyname(socket.gethostname()), port=8500, scheme='http')

# Get only passing service and add its ServiceID(docker container name) and Service Address to list
def reducer(acc, val):
    try:
        if val['Checks'][1]['Status'] == 'passing':
            acc.append((val['Service']['ID'], val['Service']['Address']))
        return acc
    except AttributeError:
        pass

# Find push service containers and add them to known docker_container_names
push_index, push_status = consul_client.health.service(service='push')
push_container_names = reduce(reducer , push_status, [])
try:
    docker_container_names.extend(push_container_names)
except TypeError:
    logging.critical('Consul Watch: All PUSH containers are in critical state.')
    pass

headers = {
    'Content-Type': 'application/json'
}

create_exec_body = {
    "AttachStdout": True,
    "Tty": True,
    "Cmd": ["kill", "-HUP", "1"],
    "User": "root"
}

start_exec_body = {
    "Detach": False,
    "Tty": False
}

try:
    for container in docker_container_names:
        container_name, container_ip = container
        try:
            # Send containers/{container_name}/exec
            create_exec = urllib.request.Request(
                method='POST',
                url='http://{}:2375/v1.32/containers/{}/exec'.format(container_ip, container_name),
                headers=headers,
                data=json.dumps(create_exec_body).encode('ascii')
            )

            logging.info("Create exec body is sent to {} on {}".format(container_name, container_ip))
            with urllib.request.urlopen(create_exec) as response:
               response_id = response.read()

            exec_id = json.loads(response_id.decode())['Id']

            # Send exec/{id}/start
            start_exec = urllib.request.Request(
                method='POST',
                url='http://{}:2375/v1.32/exec/{}/start'.format(container_ip, exec_id),
                headers=headers,
                data=json.dumps(start_exec_body).encode('ascii')
            )

            urllib.request.urlopen(start_exec)
            logging.info("Start exec body is sent to {} on {}".format(container_name, container_ip))

            time.sleep(5)
        except urllib.error.HTTPError:
            logging.error('Consul Watch: The container {} is not up.'.format(container_name))
            pass
except TypeError:
    logging.info('Consul Watch: No container is found.')
    pass