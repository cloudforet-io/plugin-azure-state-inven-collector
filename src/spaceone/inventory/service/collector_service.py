import time
import logging
import concurrent.futures
from spaceone.core.service import *
from spaceone.inventory.libs.manager import AzureManager
from spaceone.inventory.manager.virtual_machine_manager import *
from spaceone.inventory.manager.virtual_machine_scale_set_manager import *
from spaceone.inventory.manager.subscription_manager import *


_LOGGER = logging.getLogger(__name__)
MAX_WORKER = 20
SUPPORTED_FEATURES = ['garbage_collection']
SUPPORTED_RESOURCE_TYPE = ['inventory.Server', 'inventory.CloudService']
SUPPORTED_SCHEDULES = ['interval']

FILTER_FORMAT = []


@authentication_handler
class CollectorService(BaseService):
    def __init__(self, metadata):
        super().__init__(metadata)

        self.execute_managers = [
            'VirtualMachineManager',
            'VmScaleSetManager'
        ]

    @check_required(['options'])
    def init(self, params):
        """ init plugin by options
        """
        capability = {
            'filter_format': FILTER_FORMAT,
            'supported_resource_type': SUPPORTED_RESOURCE_TYPE,
            'supported_features': SUPPORTED_FEATURES,
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
            azure_manager = AzureManager()
            active = azure_manager.verify({}, secret_data)

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
        start_time = time.time()
        params.update({
            'subscription_info': self.get_subscription_info(params)
        })
        secret_data = params['secret_data']

        azure_manager: AzureManager = self.locator.get_manager('AzureManager')
        resource_groups = azure_manager.list_all_resource_groups(secret_data)
        mt_params = [{'secret_data': params['secret_data'], 'resource_group': rg} for rg in resource_groups]

        # TODO: Thread per cloud services
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
            print("[ EXECUTOR START ]")
            future_executors = []
            '''
            for mt_param in mt_params:
                print(f'@@@ {mt_param["resource_group"].name} @@@')
                vm_manager: VirtualMachineManager = self.locator.get_manager('VirtualMachineManager')
                _manager = self.locator.get_manager()
                # future_executors.append(executor.submit(vm_manager.collect_resources, mt_param))
                future_executors.append(executor.submit(_manager.collect_resources, mt_param))
            '''
            for execute_manager in self.execute_managers:
                print(f'@@@ {execute_manager} @@@')
                _manager = self.locator.get_manager(execute_manager)
                future_executors.append(executor.submit(_manager.collect_resources, params))

            try:
                for future in concurrent.futures.as_completed(future_executors):
                    for resource in future.result():
                        yield resource.to_primitive()

            except Exception as e:
                _LOGGER.error(f'failed to result {e}')


        print(f'############## TOTAL FINISHED {time.time() - start_time} Sec ##################')

    def get_subscription_info(self, params):
        subscription_manager: SubscriptionManager = self.locator.get_manager('SubscriptionManager')
        return subscription_manager.get_subscription_info(params)
