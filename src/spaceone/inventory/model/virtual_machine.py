import logging

from schematics import Model
from schematics.types import ModelType, StringType, ListType, DictType
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse

_LOGGER = logging.getLogger(__name__)



class Compute(Model):
    instance_id = StringType()
    instance_state = StringType(choices=('STARTING', 'RUNNING', 'STOPPING', 'STOPPED', 'DEALLOCATING', 'DEALLOCATED'))


class PowerState(Model):
    status = StringType(choices=('RUNNING', 'STOPPED', 'UNHEALTHY', 'IN_PROGRESS'))


class Server(Model):
    compute = ModelType(Compute)
    power_state = ModelType(PowerState, serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": self.compute.instance_id,
        }


class VirtualMachineResource(CloudServiceResource):
    cloud_service_group = StringType(default='Compute')
    cloud_service_type = StringType(default='VirtualMachine')
    data = ModelType(Server)


class VirtualMachineResponse(CloudServiceResponse):
    match_rules = DictType(ListType(StringType), default={'1': ['reference.resource_id']})
    resource_type = StringType(default='inventory.Server')
    resource = ModelType(VirtualMachineResource)
