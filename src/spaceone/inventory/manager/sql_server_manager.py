from spaceone.inventory.libs.manager import AzureManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.sql import SqlConnector
from spaceone.inventory.connector.monitor import MonitorConnector
from spaceone.inventory.model.sql_server import *
import time


class SqlServerManager(AzureManager):
    connector_name = 'SqlConnector'
    monitor_connector_name = 'MonitorConnector'

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
        sql_servers_monitor_conn: MonitorConnector = self.locator.get_connector(self.monitor_connector_name, **params)

        sql_servers = []

        for sql_server in sql_servers_conn.list_servers():
            sql_server_dict = self.convert_nested_dictionary(self, sql_server)

            # update sql_server dict
            sql_server_dict.update({
                'resource_group': self.get_resource_group_from_id(sql_server_dict['id']),  # parse resource_group from ID
                'subscription_id': subscription_info['subscription_id'],
                'subscription_name': subscription_info['subscription_name'],
            })

            databases_list = self.list_databases(self, sql_servers_conn=sql_servers_conn, sql_monitor_conn=sql_servers_monitor_conn, rg_name=sql_server_dict['resource_group'], server_name=sql_server_dict['name'],
                                server_admin_name=sql_server_dict.get('administrator_login'))

            failover_group_list = self.list_failover_groups(self, sql_servers_conn, sql_server_dict['resource_group'],
                                                            sql_server_dict['name'])

            elastic_pools_list = self.list_elastic_pools(self, sql_servers_conn, sql_server_dict['resource_group'],
                                                         sql_server_dict['name'])

            virtual_network_rules_list = self.list_virtual_network_rules(self, sql_servers_conn,
                                                                         sql_server_dict['resource_group'],
                                                                         sql_server_dict['name'])
            sql_server_dict.update({
                'databases': databases_list,
                'failover_groups': failover_group_list,
                'elastic_pools': elastic_pools_list,
                'virtual_network_rules': virtual_network_rules_list
            })

            sql_server_data = SqlServer(sql_server_dict, strict=False)

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

    @staticmethod
    def list_databases(self, sql_servers_conn, sql_monitor_conn, rg_name, server_name, server_admin_name):
        databases_list = list()
        databases = sql_servers_conn.list_databases_by_server(resource_group=rg_name, server_name=server_name)

        for database in databases:
            database_dict = self.convert_nested_dictionary(self, database)

            # Get Sync Groups by databases
            database_dict.update({
                'sync_group': self.get_sync_group_by_databases(self, sql_servers_conn, rg_name, server_name,
                                                               database_dict['name']),
            })

            # Get Sync Agents by servers
            database_dict.update({
                'sync_agent': self.get_sync_agent_by_servers(self, sql_servers_conn, rg_name, server_name)
            })

            # Get Database Replication Type
            database_dict.update({
                'replication_link': self.list_replication_link(self, sql_servers_conn, rg_name, server_name,
                                                               database_dict['name'])
            })

            databases_list.append(database_dict)

        return databases_list

    @staticmethod
    def list_replication_link(self, sql_servers_conn, rg_name, server_name, database_name):
        replication_link_list = list()
        replication_link_obj = sql_servers_conn.list_replication_link(rg_name, server_name, database_name)

        for replication_link in replication_link_obj:
            replication_link_dict = self.convert_nested_dictionary(self, replication_link)
            replication_link_list.append(replication_link_dict)

        return replication_link_list

    @staticmethod
    def get_sync_group_by_databases(self, sql_servers_conn, rg_name, server_name, database_name):
        sync_group_obj = sql_servers_conn.list_sync_groups_by_databases(resource_group=rg_name, server_name=server_name,
                                                                        database_name=database_name)
        sync_group_list = list()
        for sync_group in sync_group_obj:
            sync_group_dict = self.convert_nested_dictionary(self, sync_group)
            sync_group_list.append(sync_group_dict)
        return sync_group_list

    @staticmethod
    def get_sync_agent_by_servers(self, sql_servers_conn, rg_name, server_name):
        sync_agent_list = list()
        sync_agent_obj = sql_servers_conn.list_sync_agents_by_server(rg_name, server_name)

        for sync_agent in sync_agent_obj:
            sync_agent_dict = self.convert_nested_dictionary(sync_agent)
            sync_agent_list.append(sync_agent_dict)

        return sync_agent_list

    @staticmethod
    def list_failover_groups(self, sql_servers_conn, rg_name, server_name):
        failover_groups_list = list()
        failover_groups_obj = sql_servers_conn.list_failover_groups(rg_name, server_name)
        for failover in failover_groups_obj:
            failover_dict = self.convert_nested_dictionary(self, failover)
            failover_groups_list.append(failover_dict)

        return failover_groups_list

    @staticmethod
    def list_elastic_pools(self, sql_servers_conn, rg_name, server_name):
        elastic_pools_list = list()
        elastic_pools = sql_servers_conn.list_elastic_pools_by_server(resource_group=rg_name, server_name=server_name)

        for elastic_pool in elastic_pools:
            elastic_pool_dict = self.convert_nested_dictionary(self, elastic_pool)

            # Get Databases list by elastic pool
            elastic_pool_dict['databases'] = self.get_databases_by_elastic_pools(self, sql_servers_conn,
                                                                                 elastic_pool_dict['name'], rg_name,
                                                                                 server_name)

            # Get pricing tier for display
            if elastic_pool_dict.get('per_database_settings') is not None:
                elastic_pool_dict.update({
                    'number_of_databases': len(elastic_pool_dict['databases']),
                    'unit_display': elastic_pool_dict['sku']['tier'],
                })
            elastic_pools_list.append(elastic_pool_dict)

        return elastic_pools_list

    @staticmethod
    def get_databases_by_elastic_pools(self, sql_servers_conn, elastic_pool_name, rg_name, server_name):
        databases_obj = sql_servers_conn.list_databases_by_elastic_pool(elastic_pool_name, rg_name, server_name)
        databases_list = list()
        for database in databases_obj:
            database_dict = self.convert_nested_dictionary(self, database)
            databases_list.append(database_dict)

        return databases_list

    @staticmethod
    def list_virtual_network_rules(self, sql_servers_conn, rg_name, server_name):
        virtual_network_rule_obj = sql_servers_conn.list_virtual_network_rules_by_server(resource_group=rg_name,
                                                                                         server_name=server_name)
        virtual_network_rules_list = list()

        for virtual_network_rule in virtual_network_rule_obj:
            virtual_network_rule_dict = self.convert_nested_dictionary(self, virtual_network_rule)
            virtual_network_rules_list.append(virtual_network_rule_dict)

        return virtual_network_rules_list
