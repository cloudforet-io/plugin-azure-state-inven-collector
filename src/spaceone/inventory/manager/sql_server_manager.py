from spaceone.inventory.libs.manager import AzureManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from pprint import pprint
from spaceone.inventory.connector.sql import SqlConnector
from spaceone.inventory.model.sql_server import *
import time


class SqlServerManager(AzureManager):
    connector_name = 'SqlConnector'

    def collect_power_state(self, params):
        print("** Sql Servers START **")
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

        sql_servers_conn: SqlConnector = self.locator.get_connector(self.connector_name, **params)
        sql_servers = []
        for sql_server in sql_servers_conn.list_servers():
            sql_server_dict = self.convert_nested_dictionary(self, sql_server)

            # update sql_server dict
            sql_server_dict.update({
                'resource_group': self.get_resource_group_from_id(sql_server_dict['id']),  # parse resource_group from ID
                'subscription_id': subscription_info['subscription_id'],
                'subscription_name': subscription_info['subscription_name'],
            })
            '''
            # Get auto scale settings by resource group and vm id
            sql_server_dict.update({
                'virtual_machine_scale_set_power_state': self.list_auto_scale_settings(self, vm_scale_set_conn=sql_servers_conn, resource_group_name=sql_server_dict['resource_group'], vm_scale_set_id=sql_server_dict['id'])
            })
            '''
            # print("sql_server_dict")
            # print(sql_server_dict)

            sql_server_data = SqlServer(sql_server_dict, strict=False)

            # print("sql_server_data")
            # print(sql_server_data.to_primitive())

            sql_server_resource = SqlServerResource({
                'data': sql_server_data,
                'reference': ReferenceModel(sql_server_data.reference()),
            })

            sql_servers.append(SqlServerResponse({'resource': sql_server_resource}))

        print(f'** Sql Server Finished {time.time() - start_time} Seconds **')
        return sql_servers

    @staticmethod
    def get_resource_group_from_id(disk_id):
        resource_group = disk_id.split('/')[4].lower()
        return resource_group


