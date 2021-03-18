import logging

from schematics import Model
from schematics.types import ModelType, StringType, ListType, DictType, IntType, DateTimeType, NumberType, BooleanType, TimedeltaType
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse

_LOGGER = logging.getLogger(__name__)


class Tags(Model):
    key = StringType()
    value = StringType()


class EmailNotification(Model):
    custom_emails = ListType(StringType, serialize_when_none=False)
    send_to_subscription_administrator = BooleanType(serialize_when_none=False)
    send_to_subscription_co_administrators = BooleanType(serialize_when_none=False)


class OperationType(Model):
    scale = StringType(serialize_when_none=False)


class WebhookNotification(Model):
    properties = StringType(serialize_when_none=False)


class AutoscaleNotification(Model):
    email = ModelType(EmailNotification, serialize_when_none=False)
    operation = ModelType(OperationType, serialize_when_none=False)
    webhooks = ListType(ModelType(WebhookNotification), serialize_when_none=False)


class ScaleAction(Model):
    direction = StringType(choices=('Decrease', 'Increase', 'None'), serialize_when_none=False)
    type = StringType(choices=('ChangeCount', 'ExactCount', 'PercentChangeCount'), serialize_when_none=False)
    value = StringType(serialize_when_none=False)
    cooldown = TimedeltaType(serialize_when_none=False)


class ScaleRuleMetricDimension(Model):
    dimension_name = StringType(serialize_when_none=False)
    operator = StringType(choices=('Equals', 'NotEquals'), serialize_when_none=False)
    values = ListType(StringType, serialize_when_none=False)


class MetricTrigger(Model):
    dimensions = ListType(ModelType(ScaleRuleMetricDimension), serialize_when_none=False)
    metric_name = StringType(serialize_when_none=False)
    metric_namespace = StringType(serialize_when_none=False)
    metric_resource_uri = StringType(serialize_when_none=False)
    operator = StringType(
        choices=('Equals', 'GreaterThan', 'GreaterThanOrEqual', 'LessThan', 'LessThanOrEqual', 'NotEquals'),
        serialize_when_none=False)
    statistic = StringType(choices=('Average', 'Max', 'Min', 'Sum'), serialize_when_none=False)
    threshold = IntType(serialize_when_none=False)
    time_aggregation = StringType(choices=('Average', 'Count', 'Last', 'Maximum', 'Minimum', 'Total'),
                                  serialize_when_none=False)
    time_grain = TimedeltaType(serialize_when_none=False)
    time_window = TimedeltaType(serialize_when_none=False)


class ScaleRule(Model):
    metric_trigger = ModelType(MetricTrigger)
    scale_action = ModelType(ScaleAction)


class ScaleCapacity(Model):
    default = StringType(serialize_when_none=False)
    maximum = StringType(serialize_when_none=False)
    minimum = StringType(serialize_when_none=False)


class TimeWindow(Model):
    end = StringType(serialize_when_none=False)
    start = StringType(serialize_when_none=False)
    time_zone = StringType(serialize_when_none=False)


class RecurrentSchedule(Model):
    days = ListType(StringType, serialize_when_none=False)
    hours = ListType(IntType, serialize_when_none=False)
    minutes = ListType(IntType, serialize_when_none=False)
    time_zone = StringType(serialize_when_none=False)


class Recurrence(Model):
    frequency = StringType(choices= ('Day', 'Hour', 'Minute', 'Month', 'None', 'Second', 'Week', 'Year'), serialize_when_none=False)
    schedule = ModelType(RecurrentSchedule)


class Sku(Model):  # belongs to VmScaleSet
    capacity = IntType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    tier = StringType(choices=('Standard', 'Basic', None), default='Standard', serialize_when_none=False)


class AutoscaleProfile(Model):
    capacity = ModelType(ScaleCapacity, serialize_when_none=False)
    fixed_date = ModelType(TimeWindow, serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    recurrence = ModelType(Recurrence, serialize_when_none=False)
    rules = ListType(ModelType(ScaleRule), serialize_when_none=False)


class InstanceViewStatus(Model):
    code = StringType(serialize_when_none=False)
    display_status = StringType(serialize_when_none=False)
    level = StringType(choices=('Error', 'Info', 'Warning'), serialize_when_none=False)
    message = StringType(serialize_when_none=False)
    time = DateTimeType(serialize_when_none=False)


class VirtualMachineExtensionVMInstanceView(Model):
    statuses = ListType(ModelType(InstanceViewStatus), serialize_when_none=False)
    display_status = StringType(serialize_when_none=False)


class VirtualMachineScaleSetVM(Model):
    instance_id = IntType()
    id = StringType()
    provisioning_state = StringType(choices=('Failed', 'Succeeded'))
    # vm_instance_status_profile = ModelType(VirtualMachineExtensionVMInstanceView, serialize_when_none=False)
    vm_instance_status_display = StringType(serialize_when_none=False)


class VirtualMachineScaleSetPowerState(Model):
    location = StringType()
    profiles = ListType(ModelType(AutoscaleProfile), serialize_when_none=False)
    enabled = BooleanType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    notifications = ListType(ModelType(AutoscaleNotification), serialize_when_none=False)
    target_resource_uri = StringType(serialize_when_none=False)
    tags = ModelType(Tags, serialize_when_none=False)


class VirtualMachineScaleSet(Model):
    id = StringType()
    resource_group = StringType()
    name = StringType()
    instance_count = IntType()
    sku = ModelType(Sku, serialize_when_none=False)
    vm_instances = ListType(ModelType(VirtualMachineScaleSetVM), serialize_when_none=False)
    virtual_machine_scale_set_power_state = ListType(ModelType(VirtualMachineScaleSetPowerState))
    provisioning_state = StringType(choices=('Failed', 'Succeeded'))

    def reference(self):
        return {
            "resource_id": self.id,
        }


class VirtualMachineScaleSetResource(CloudServiceResource):
    cloud_service_group = StringType(default='Compute')
    cloud_service_type = StringType(default='VirtualMachineScaleSet')
    data = ModelType(VirtualMachineScaleSet)


class VirtualMachineScaleSetResponse(CloudServiceResponse):
    match_rules = DictType(ListType(StringType), default={'1': ['reference.resource_id']})
    resource_type = StringType(default='inventory.VirtualMachineScaleSet')
    resource = ModelType(VirtualMachineScaleSetResource)
