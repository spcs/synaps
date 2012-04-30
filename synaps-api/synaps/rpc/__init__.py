# Copyright 2012 Samsung SDS
# All Rights Reserved

from synaps.exception import RpcInvokeException

class RemoteProcedureCall(object):
    def put_metric_data(self, project_id, namespace, metric_name, dimensions,
                        value, unit=None, timestamp=None):
        # TODO: (june.yi) need to send metric to synaps-storm via zmq
        raise RpcInvokeException()
