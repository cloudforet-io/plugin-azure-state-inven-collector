import logging

from spaceone.inventory.libs.connector import AzureConnector
from spaceone.inventory.error import *


__all__ = ['VirtualMachineConnector']
_LOGGER = logging.getLogger(__name__)


class VirtualMachineConnector(AzureConnector):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_connect(kwargs.get('secret_data'))
    '''
    def list_vms(self, resource_group_name, **query):
        return list(self.compute_client.virtual_machines.list(resource_group_name=resource_group_name, **query))
    '''

    def list_vms(self):
        return self.compute_client.virtual_machines.list_all()

    def get_vm(self, resource_group_name, vm_name):
        return self.compute_client.virtual_machines.get(resource_group_name, vm_name, expand='instanceView')

