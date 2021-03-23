from spaceone.inventory.libs.manager import AzureManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from pprint import pprint
from spaceone.inventory.connector.virtual_machine_scale_set import VmScaleSetConnector
from spaceone.inventory.model.virtual_machine_scale_set import *
import time


class VmScaleSetManager(AzureManager):
    connector_name = 'VmScaleSetConnector'

    def collect_power_state(self, params):
        print("** VmScaleSet START **")
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
                - subscription_info
        Response:
            CloudServiceResponse
        """
        secret_data = params['secret_data']
        subscription_info = params['subscription_info']

        vm_scale_set_conn: VmScaleSetConnector = self.locator.get_connector(self.connector_name, **params)
        vm_scale_sets = []
        for vm_scale_set in vm_scale_set_conn.list_vm_scale_sets():
            vm_scale_set_dict = self.convert_nested_dictionary(self, vm_scale_set)

            # update vm_scale_set_dict
            vm_scale_set_dict.update({
                'resource_group': self.get_resource_group_from_id(vm_scale_set_dict['id']),  # parse resource_group from ID
            })

            # Add vm instances list attached to VMSS
            vm_instances_list = list()
            instance_count = 0
            for vm_instance in vm_scale_set_conn.list_vm_scale_set_vms(vm_scale_set_dict['resource_group'],
                                                                       vm_scale_set_dict['name']):
                instance_count += 1
                vm_scale_set_dict.update({
                    'instance_count': instance_count
                })

                vm_instance_dict = self.get_vm_instance_status_profile(self, vm_instance, vm_scale_set_conn, vm_scale_set_dict['resource_group'], vm_scale_set_dict['name'])
                vm_instance_dict.update({
                    'vm_instance_status_display': vm_instance_dict['vm_instance_status_profile']['vm_agent']['display_status']
                })
                vm_instances_list.append(vm_instance_dict)

            vm_scale_set_dict['vm_instances'] = vm_instances_list

            # Get auto scale settings by resource group and vm id
            vm_scale_set_dict.update({
                'virtual_machine_scale_set_power_state': self.list_auto_scale_settings(self, vm_scale_set_conn=vm_scale_set_conn, resource_group_name=vm_scale_set_dict['resource_group'], vm_scale_set_id=vm_scale_set_dict['id'])
            })

            # print("vm_scale_set_dict")
            # print(vm_scale_set_dict)

            vm_scale_set_data = VirtualMachineScaleSet(vm_scale_set_dict, strict=False)

            vm_scale_set_resource = VirtualMachineScaleSetResource({
                'data': vm_scale_set_data,
                'reference': ReferenceModel(vm_scale_set_data.reference()),
            })

            vm_scale_sets.append(VirtualMachineScaleSetResponse({'resource': vm_scale_set_resource}))

        print(f'** VmScaleSet Finished {time.time() - start_time} Seconds **')
        return vm_scale_sets

    @staticmethod
    def get_resource_group_from_id(disk_id):
        resource_group = disk_id.split('/')[4].lower()
        return resource_group

    # Get instances of a virtual machine from the VM scale set
    @staticmethod
    def get_vm_instance_status_profile(self, vm_instance, vm_instance_conn, resource_group, vm_scale_set_name):
        vm_instance_dict = self.convert_nested_dictionary(self, vm_instance)
        vm_instance_dict.update({
            'vm_instance_status_profile': self.get_vm_instance_view_dict(self, vm_instance_conn, resource_group, vm_scale_set_name, vm_instance.instance_id),
        })
        return vm_instance_dict

    # Get instance view of a virtual machine from a VM scale set instance
    @staticmethod
    def get_vm_instance_view_dict(self, vm_instance_conn, resource_group, vm_scale_set_name, instance_id):
        vm_instance_status_profile = vm_instance_conn.get_vm_scale_set_instance_view(resource_group, vm_scale_set_name, instance_id)
        vm_instance_status_profile_dict = self.convert_nested_dictionary(self, vm_instance_status_profile)

        for status in vm_instance_status_profile_dict['vm_agent']['statuses']:
            vm_instance_status_profile_dict['vm_agent'].update({
                    'display_status': status['display_status']
            })

        return vm_instance_status_profile_dict

    @staticmethod
    def get_instance_state(statuses):
        for status in statuses:
            if status.code.find('PowerState') != -1:
                return status.code.split('/')[-1].upper()
        return None

    @staticmethod
    def list_auto_scale_settings(self, vm_scale_set_conn, resource_group_name, vm_scale_set_id):
        auto_scale_settings_list = list()
        auto_scale_settings_obj = vm_scale_set_conn.list_auto_scale_settings(resource_group=resource_group_name)  # List all of the Auto scaling Rules in this resource group

        for auto_scale_setting in auto_scale_settings_obj:
            auto_scale_setting_dict = self.convert_nested_dictionary(self, auto_scale_setting)
            if auto_scale_setting_dict['target_resource_uri'].lower() == vm_scale_set_id.lower():  # Compare resources' id
                auto_scale_settings_list.append(auto_scale_setting_dict)

        return auto_scale_settings_list
