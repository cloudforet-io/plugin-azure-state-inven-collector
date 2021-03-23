from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, BooleanType, FloatType, DateTimeType, DictType
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse


class Tags(Model):
    key = StringType()
    value = StringType()


class PrivateEndpointProperty(Model):
    id = StringType()


class PrivateLinkServiceConnectionStateProperty(Model):
    status = StringType(choices=('Approved', 'Disconnected', 'Pending', 'Rejected'), serialize_when_none=False)


class PrivateEndpointConnectionProperties(Model):
    private_endpoint = ModelType(PrivateEndpointProperty, serialize_when_none=False)
    private_link_service_connection_state = ModelType(PrivateLinkServiceConnectionStateProperty,
                                                      serialize_when_none=False)
    provisioning_state = StringType(choices=('Approving', 'Dropping', 'Failed', 'Ready', 'Rejecting'))


class ServerPrivateEndpointConnection(Model):
    id = StringType(serialize_when_none=False)
    status = StringType(serialize_when_none=False)
    properties = ModelType(PrivateEndpointConnectionProperties)


class FailoverGroup(Model):
    name = StringType(serialize_when_none=False)
    id = StringType()
    databases = ListType(StringType, serialize_when_none=False)
    replication_state = StringType(serialize_when_none=False)


class SyncGroup(Model):
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    last_sync_time = DateTimeType(serialize_when_none=False)
    sync_state = StringType(choices=('Error', 'Good', 'NotReady', 'Progressing', 'Warning'), serialize_when_none=False)


class SyncAgent(Model):
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    expiry_time = StringType(serialize_when_none=False)
    is_up_to_date = BooleanType(serialize_when_none=False)
    last_alive_time = StringType(serialize_when_none=False)
    state = StringType(choices=('NeverConnected', 'Offline', 'Online'), serialize_when_none=False)
    sync_database_id = StringType(serialize_when_none=False)


class ReplicationLink(Model):
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    partner_database = StringType(serialize_when_none=False)
    percent_complete = IntType(serialize_when_none=False)
    replication_state = StringType(choices=('CATCH_UP', 'PENDING', 'SEEDING', 'SUSPENDED'), serialize_when_none=False)
    role = StringType(choices=('Copy', 'NonReadableSecondary', 'Primary', 'Secondary', 'Source'), serialize_when_none=False)
    start_time = DateTimeType(serialize_when_none=False)


class Database(Model):
    name = StringType(serialize_when_none=False)
    id = StringType()
    location = StringType()
    status = StringType(choices=(
        'AutoClosed', 'Copying', 'Creating', 'Disabled', 'EmergencyMode', 'Inaccessible', 'Offline',
        'OfflineChangingDwPerformanceTiers', 'OfflineSecondary', 'Online',
        'OnlineChangingDwPerformanceTiers', 'Paused', 'Pausing', 'Recovering', 'RecoveryPending', 'Restoring',
        'Resuming', 'Scaling', 'Shutdown', 'Standby', 'Suspect'), serialize_when_none=False)
    replication_link = ListType(ModelType(ReplicationLink), serialize_when_none=False)
    sync_group = ListType(ModelType(SyncGroup), serialize_when_none=False)
    sync_agent = ListType(ModelType(SyncAgent), serialize_when_none=False)


class ElasticPool(Model):
    name = StringType(serialize_when_none=False)
    id = StringType()
    state = StringType(choices=('Creating', 'Disabled', 'Ready'), serialize_when_none=False)
    databases = ListType(ModelType(Database))
    number_of_databases = IntType(serialize_when_none=False, default=0)
    unit_display = StringType(serialize_when_none=False)


class VirtualNetworkRule(Model):
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    state = StringType(choices=('Deleting', 'InProgress', 'Initializing', 'Ready', 'Unknown'), serialize_when_none=False)


class SqlServer(Model):
    name = StringType()
    id = StringType()
    private_endpoint_connections = ListType(ModelType(ServerPrivateEndpointConnection))
    state = StringType(serialize_when_none=False)
    failover_groups = ListType(ModelType(FailoverGroup), serialize_when_none=False)
    databases = ListType(ModelType(Database), serialize_when_none=False)
    elastic_pools = ListType(ModelType(ElasticPool), serialize_when_none=False)
    virtual_network_rules = ListType(ModelType(VirtualNetworkRule), serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": self.id,
            "external_link": f"https://portal.azure.com/#@.onmicrosoft.com/resource{self.id}/overview",
        }


class SqlServerResource(CloudServiceResource):
    cloud_service_group = StringType(default='Sql')
    cloud_service_type = StringType(default='SqlServer')
    data = ModelType(SqlServer)


class SqlServerResponse(CloudServiceResponse):
    match_rules = DictType(ListType(StringType), default={'1': ['reference.resource_id']})
    resource_type = StringType(default='inventory.Server')
    resource = ModelType(SqlServerResource)
