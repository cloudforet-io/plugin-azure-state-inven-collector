from spaceone.core.manager import BaseManager
from spaceone.inventory.libs.connector import AzureConnector


class AzureManager(BaseManager):
    connector_name = None
    cloud_service_types = []
    response_schema = None
    collected_region_codes = []

    def verify(self, options, secret_data, **kwargs):
        """ Check collector's status.
        """
        connector: AzureConnector = self.locator.get_connector('AzureConnector', secret_data=secret_data)
        connector.verify()

    def collect_power_state(self, params) -> list:
        raise NotImplemented

    def collect_resources(self, params) -> list:
        return self.collect_power_state(params)

    def list_all_resource_groups(self, secret_data):
        connector: AzureConnector = self.locator.get_connector('AzureConnector')
        connector.set_connect(secret_data)

        return connector.list_resource_groups()

    @staticmethod
    def convert_tag_format(tags):
        convert_tags = []

        if tags:
            for k, v in tags.items():
                convert_tags.append({
                    'key': k,
                    'value': v
                })

        return convert_tags

    @staticmethod
    def convert_dictionary(obj):
        return vars(obj)

    @staticmethod
    def convert_nested_dictionary(self, vm_object):
        vm_dict = self.convert_dictionary(vm_object)
        for k, v in vm_dict.items():
            if isinstance(v, object):  # object
                if isinstance(v, list):  # if vm_object is list
                    for list_obj in v:
                        vm_converse_list = list()
                        if hasattr(list_obj, '__dict__'):
                            vm_converse_dict = self.convert_nested_dictionary(self, list_obj)
                            vm_converse_list.append(vm_converse_dict)
                        vm_dict[k] = vm_converse_list

                elif hasattr(v, '__dict__'):  # if vm_object is not a list type, just an object
                    vm_converse_dict = self.convert_nested_dictionary(self, v)
                    vm_dict[k] = vm_converse_dict

        return vm_dict
