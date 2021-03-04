import time
import logging
import concurrent.futures
from spaceone.core.service import *
from spaceone.inventory.libs.manager import AzureManager
from spaceone.inventory.manager.virtual_machine_manager import *


_LOGGER = logging.getLogger(__name__)
MAX_WORKER = 20
SUPPORTED_RESOURCE_TYPE = ['inventory.Server', 'inventory.CloudService']
SUPPORTED_SCHEDULES = ['interval']

FILTER_FORMAT = []


@authentication_handler
class CollectorService(BaseService):
    def __init__(self, metadata):
        super().__init__(metadata)

        self.execute_managers = [
            'ComputeInstanceManager',
            'CloudSQLManager',
            'InstanceGroupManager',
        ]

    @check_required(['options'])
    def init(self, params):
        """ init plugin by options
        """
        capability = {
            'filter_format': FILTER_FORMAT,
            'supported_resource_type': SUPPORTED_RESOURCE_TYPE,
            'supported_schedules': SUPPORTED_SCHEDULES
        }
        return {'metadata': capability}

    @transaction
    @check_required(['options', 'secret_data'])
    def verify(self, params):
        """
        Args:
              params:
                - options
                - secret_data
        """
        options = params['options']
        secret_data = params.get('secret_data', {})
        if secret_data != {}:
            google_manager = AzureManager()
            active = google_manager.verify({}, secret_data)

        return {}

    @transaction
    @check_required(['options', 'secret_data', 'filter'])
    def list_resources(self, params):
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
        """

        secret_data = params['secret_data']

        start_time = time.time()

        azure_manager: AzureManager = self.locator.get_manager('AzureManager')
        resource_groups = azure_manager.list_all_resource_groups(secret_data)

        mt_params = [{'secret_data': params['secret_data'], 'resource_group': rg} for rg in resource_groups]

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
            print("[ EXECUTOR START ]")
            future_executors = []
            for mt_param in mt_params:
                print(f'@@@ {mt_param["resource_group"].name} @@@')
                vm_manager: VirtualMachineManager = self.locator.get_manager('VirtualMachineManager')
                future_executors.append(executor.submit(vm_manager.collect_resources, mt_param))

            for future in concurrent.futures.as_completed(future_executors):
                for resource in future.result():
                    yield resource.to_primitive()

        print(f'############## TOTAL FINISHED {time.time() - start_time} Sec ##################')
