import unittest
import os
from datetime import datetime, timedelta
from unittest.mock import patch

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.transaction import Transaction
from spaceone.inventory.connector.virtual_machine_scale_set import VmScaleSetConnector


class TestSnapshotConnector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.inventory')
        config_path = os.environ.get('TEST_CONFIG')
        test_config = utils.load_yaml_from_file(config_path)

        cls.schema = 'azure_client_secret'
        cls.azure_credentials = {
            'secret_data': test_config.get('AZURE_CREDENTIALS', {})
        }

        cls.azure_connector = VmScaleSetConnector(transaction=Transaction(), config={},
                                                secret_data=test_config.get('AZURE_CREDENTIALS', {}))
        # cls.azure_connector = DiskConnector(transaction=Transaction(), config={}, secret_data=cls.azure_credentials['secret_data'])
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def test_list_virtual_machine_scale_sets(self):
        # self.azure_connector.set_connect(self.azure_credentials)
        virtual_machine_scale_sets = self.azure_connector.list_vm_scale_sets()

        for vmss in virtual_machine_scale_sets:
            print('=====')
            print(vmss)
            print('=====')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
