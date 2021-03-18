from spaceone.inventory.libs.manager import AzureManager
from spaceone.inventory.connector.subscription import SubscriptionConnector
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.subscription import SubscriptionConnector
from datetime import datetime
import time


class SubscriptionManager(AzureManager):
    connector_name = 'SubscriptionConnector'

    def get_subscription_info(self, params):  # id 정제 된 애
        secret_data = params['secret_data']
        subscription_connector: SubscriptionConnector = self.locator.get_connector(self.connector_name,
                                                                                   secret_data=secret_data)
        subscription_info = subscription_connector.get_subscription_info(secret_data['subscription_id'])  # subscription_info = disk_conn.get_subscription_info(subscription)

        return {
            'subscription_id': subscription_info.subscription_id,
            'subscription_name': subscription_info.display_name,
            'tenant_id': subscription_info.tenant_id
        }
