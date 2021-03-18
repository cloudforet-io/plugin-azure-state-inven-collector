import time
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.libs.manager import AzureManager
from spaceone.inventory.connector.virtual_machine import VirtualMachineConnector
from spaceone.inventory.model.virtual_machine import *


class VirtualMachineManager(AzureManager):
    connector_name = 'VirtualMachineConnector'

    def collect_power_state(self, params):
        """
        Args:
            params:
                - secret_data
                - resource_group
        Response:
            [VirtualMachineResponse, ...]
        """

        vm_conn: VirtualMachineConnector = self.locator.get_connector(self.connector_name, **params)
        vm_conn.set_connect(params['secret_data'])

        # print("** VM Start **")
        start_time = time.time()

        vms = []
        for vm in vm_conn.list_vms():
            vm_info = vm_conn.get_vm(vm.id.split('/')[4], vm.name)
            power_state, instance_state = self._get_status_map(vm_info.instance_view.statuses)

            compute_vm = {
                'compute': Compute({'instance_state': instance_state, 'instance_id': vm.id}, strict=False),
                'power_state': PowerState({'status': power_state}, strict=False)
            }
            compute_vm_data = Server(compute_vm, strict=False)

            # print("vm_data")
            # print(compute_vm_data.to_primitive())

            compute_vm_resource = VirtualMachineResource({
                'data': compute_vm_data,
                'reference': ReferenceModel(compute_vm_data.reference())
            })

            vms.append(VirtualMachineResponse({'resource': compute_vm_resource}))

        print(f' Virtual Machine Finished {time.time() - start_time} Seconds')
        return vms

    def _get_status_map(self, statuses):
        power_state = 'UNHEALTHY'

        vm_state = self.get_instance_state(statuses)

        if vm_state in ['RUNNING']:
            power_state = 'RUNNING'
        elif vm_state in ['STOPPED', 'DEALLOCATED']:
            power_state = 'STOPPED'
        elif vm_state in ['STARTING']:
            power_state = 'IN_PROGRESS'
        return power_state, vm_state

    @staticmethod
    def get_instance_state(statuses):
        for status in statuses:
            if status.code.find('PowerState') != -1:
                return status.code.split('/')[-1].upper()

        return None
