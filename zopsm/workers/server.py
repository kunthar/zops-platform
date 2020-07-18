#!/usr/bin/env python3
import pika
import json
import os
import random
import time
import consul
import inspect
from zopsm.lib.sd_consul import consul_client, EnvironmentVariableNotFound
from zopsm.lib import sd_riak
from zopsm.lib import sd_rabbit
from zopsm.lib import sd_redis
from zopsm.workers.base_jobs import BaseWorkerJobs
from zopsm.workers.push_jobs import PushWorkerJobs
from zopsm.workers.messaging_jobs import MessageWorkerJobs
from zopsm.workers.rpc_server import RpcServer
from threading import Thread
from json import JSONDecodeError
from zopsm.lib.log_handler import zlogger
from zopsm.lib.settings import WORKING_ENVIRONMENT
from zopsm.saas.log_handler import saas_logger

container_name = os.getenv('CONTAINER_NAME', 'dev_workers_1')
host_ipv4 = os.getenv('DOCKER_HOST_IPV4')
if host_ipv4 is None:
    raise EnvironmentVariableNotFound('DOCKER_HOST_IPV4 should not be empty.')

if WORKING_ENVIRONMENT in ["zopsm", "develop"]:
    check = consul.Check.docker(
        container_id=f'{container_name}',
        shell='/bin/sh',
        script='python3 /usr/local/lib/python3.6/site-packages/zopsm/workers/rpc_ping.py',
        interval='10s',
        deregister='2m')
    consul_client.agent.service.register(
        name='worker',
        service_id=f'{container_name}',
        address=f'{host_ipv4}',
        check=check)
    zlogger.info(f"\n##########\n Registered {container_name} worker service to Consul. \n###########\n")


class RPCServer(RpcServer):
    def __init__(self, riak_pb, rabbit_cl, redis_master):

        # self.QUEUE = 'rpc_queue_%s' % os.getenv('WORKER_NAME', random.randint(999, 99999))
        self.EXCHANGE = os.getenv("RABBIT_EXCHANGE", "inter_comm")
        self.VIRTUAL_HOST = os.getenv('RABBIT_VIRTUAL_HOST', 'zopsm')
        self.CREDENTIALS = sd_rabbit.rabbit_credential
        # This should match with client side
        self.push_inst = PushWorkerJobs()
        self.msg_inst = MessageWorkerJobs()
        self.jobs = {
            "push": self.push_inst,
            "roc": self.msg_inst,
            "sms": ""
        }
        bwj = BaseWorkerJobs()
        all_base_methods = inspect.getmembers(bwj, inspect.ismethod)
        base_jobs = [method[0] for method in all_base_methods]
        base_jobs.append('__setitem__')  # added because push and message worker classes use this.
        all_push_methods = inspect.getmembers(self.push_inst, inspect.ismethod)
        push_jobs = [method[0] for method in all_push_methods
                     if method[0] not in base_jobs]
        all_message_methods = inspect.getmembers(self.msg_inst, inspect.ismethod)
        message_jobs = [method[0] for method in all_message_methods
                        if method[0] not in base_jobs]

        push_jobs.extend(message_jobs)  # all methods from push and message worker classes to bind
        push_jobs.append('ping')
        self.ROUTING_KEYS = push_jobs
        super(RPCServer, self).__init__()

    def on_request(self, ch, method, props, body):
        """
        Publishes response by using do_job method
        Args:
            ch: Channel
            method: Method
            props: Properties
            body: Message Body

        Returns:
            None
        """

        err = None
        err_msg = ""
        result = {}
        id = None
        params = {}

        try:
            body = json.loads(body)
            try:
                rabbit_cl = sd_rabbit.get_suitable_client(json.loads(sd_rabbit.rabbit_nodes))
                jobs_inst = self.jobs[body['params']['service']]
                jobs_inst.update_instances(sd_riak.riak_pb, rabbit_cl, sd_redis.redis_master)
                worker_method = getattr(jobs_inst, body['method'])

                try:
                    params = body['params']
                    result = worker_method(**params)
                    id = body['id']
                except TypeError as e:
                    err_msg = "Invalid params: {}".format(e)
                    err = {"code": -32602, "message": "Invalid Params"}
                except ConnectionRefusedError as e:
                    err_msg = "RiakNode Connection Refused Error: {}".format(e)
                    err = {
                        "error": {"code": -32001, "message": "Internal Error"}}
                except KeyError as e:
                    err_msg = "Object Not Found: {}".format(e)
                    err = {"code": -32002, "message": "Object Not Found"}
            except KeyError as e:
                err_msg = "Invalid Request: {}".format(e)
                err = {"code": -32600, "message": "Invalid Request"}
            except ImportError as e:
                err_msg = "Method not found: {}".format(e)
                err = {"code": -32601, "message": "Method Not Found"}
        except JSONDecodeError as e:
            err_msg = "Parse error: {}".format(e)
            err = {"code": -32700, "message": "Parse Error"}
        except Exception as e:
            err_msg = "Internal error: {}".format(e)
            err = {"code": -32603, "message": "Internal Error"}

        # Reserved for implementation - defined server - errors.
        # http://www.jsonrpc.org/specification#error_object
        # TODO: -32000 to -32099	Server error

        response = {
            "jsonrpc": "2.0",
            "id": id
        }

        if err or (result and 'error' in result):
            response['error'] = err or result['error']
            msg = "Blocking {blocking}, {method} with correlation id:{corr_id} of " \
                    "project:{project_id} and user:{usr_id}, resulted in an error:{err_msg}".format(
                        method=params.get('method'),
                        corr_id=params.get('id'),
                        project_id=params.get('project_id'),
                        err_msg=err_msg or response['error']['message'],
                        usr_id=params.get('subscriber_id') or params.get('target_id'),
                        blocking=not params.get('trackable')
            )
            zlogger.error(msg)
            if params and params['trackable']:
                zlogger.info("",
                    extra={
                        "purpose": "event",
                        "params": {
                            "trackingId": params.get('id'),
                            "data": {
                                "title": response['error']['message'],
                                "description": "Event has failed.",
                                "code": 500,
                            },
                            "usr_id": params.get('subscriber_id') or params.get('target_id'),
                        },
                        "method": "fails_non_blocking_jobs",
                    }
                )
        else:
            response['result'] = result

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=json.dumps(response))

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        """
        Overrided this method to use on_request callback
        Original method in rpc_server.py

        """
        self.add_on_cancel_callback()
        self._channel.basic_qos(prefetch_count=1)
        self._consumer_tag = self._channel.basic_consume(consumer_callback=self.on_request,
                                                         queue=self.QUEUE)
        zlogger.info("Started consuming...")


def main():
    t1 = Thread(target=sd_rabbit.watch_rabbit)
    t2 = Thread(target=sd_riak.watch_riak)
    t4 = Thread(target=sd_redis.watch_redis)

    t1.start()
    t2.start()
    t4.start()

    
    while not getattr(sd_rabbit, 'rabbit_nodes') or \
            not getattr(sd_riak, 'riak_pb') or not getattr(sd_riak, 'log_bucket') or \
            not getattr(sd_redis, 'redis_master'):
        zlogger.info("Still waiting for rabbit_nodes, riak_pb, log_bucket, redis_master")
        time.sleep(0.1)

    rabbit_cl = sd_rabbit.get_suitable_client(json.loads(sd_rabbit.rabbit_nodes))

    rpcserver = RPCServer(sd_riak.riak_pb, rabbit_cl, sd_redis.redis_master)
    t3 = Thread(target=rpcserver.run)
    t3.start()
    zlogger.info("Started RpcServer...")


if __name__ == '__main__':
    main()
