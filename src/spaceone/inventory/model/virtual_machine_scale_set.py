import logging

from schematics import Model
from schematics.types import ModelType, StringType, ListType, DictType, IntType, DateTimeType, NumberType, BooleanType, TimedeltaType
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse

_LOGGER = logging.getLogger(__name__)


class Tags(Model):
    key = StringType()
    value = StringType()


####################
class Plan(Model):  # belongs to VmScaleSet
    name = StringType(serialize_when_none=False)
    product = StringType(serialize_when_none=False)
    promotion_code = StringType(serialize_when_none=False)
    publisher = StringType(serialize_when_none=False)


class AdditionalCapabilities(Model):  # belongs to VmScaleSet
    ultra_ssd_enabled = BooleanType(serialize_when_none=False)


class SubResource(Model):  # belongs to VmScaleSet
    id = StringType(serialize_when_none=False)


class BootDiagnostics(Model):
    # belongs to the VmScaleSet >> VirtualMachineScaleSetVMProfile >> DiagnosticsProfile
    enabled = BooleanType(serialize_when_none=False)
    storage_uri = StringType(serialize_when_none=False)


class DiagnosticsProfile(Model):  # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile
    boot_diagnostics = ModelType(BootDiagnostics, serialize_when_none=False)


class HardwareProfile(Model):  # belongs to VMScaleSet >> vm instances
    vm_size = StringType(serialize_when_none=False)


class NetworkInterfaceReference(Model):
    id = StringType(serialize_when_none=False)
    primary = BooleanType(serialize_when_none=False)


class NetworkProfile(Model):  # belongs to VirtualMachineScaleSetVM
    network_interfaces = ListType(ModelType(NetworkInterfaceReference), serialize_when_none=False)


class VirtualMachineScaleSetNetworkConfigurationDNSSettings(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile >> VirtualMachineScaleSetNetworkProfile
    #            >> VirtualMachineScaleSetNetworkConfiguration
    dns_servers = ListType(StringType, serialize_when_none=False)


class VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile >> VirtualMachineScaleSetNetworkProfile >>
    #            VirtualMachineScaleSetNetworkConfiguration >> VirtualMachineScaleSetIPConfiguration >>
    #            VirtualMachineScaleSetPublicIPAddressConfiguration
    domain_name_label = StringType(serialize_when_none=False)


class VirtualMachineScaleSetIpTag(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile >> VirtualMachineScaleSetNetworkProfile >>
    #            VirtualMachineScaleSetNetworkConfiguration >> VirtualMachineScaleSetIPConfiguration >>
    #            VirtualMachineScaleSetPublicIPAddressConfiguration
    ip_tag_type = StringType(serialize_when_none=False)
    tag = StringType(serialize_when_none=False)


class VirtualMachineScaleSetPublicIPAddressConfiguration(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile
    #                       >> VirtualMachineScaleSetNetworkProfile >> VirtualMachineScaleSetNetworkConfiguration
    #                       >> VirtualMachineScaleSetIPConfiguration
    name = StringType()
    dns_settings = ModelType(VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings, serialize_when_none=False)
    idle_timeout_in_minutes = IntType(serialize_when_none=False)
    ip_tags = ListType(ModelType(VirtualMachineScaleSetIpTag), serialize_when_none=False)
    public_ip_address_version = StringType(choices=('IPv4', 'IPv6'), default='IPv4', serialize_when_none=False)
    public_ip_prefix = ModelType(SubResource, serialize_when_none=False)


class ApiEntityReference(Model):  # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile
    id = StringType(serialize_when_none=False)


class VirtualMachineScaleSetIPConfiguration(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile
    #                       >> VirtualMachineScaleSetNetworkProfile >> VirtualMachineScaleSetNetworkConfiguration
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    application_gateway_backend_address_pools = ListType(ModelType(SubResource), serialize_when_none=False)
    application_security_groups = ListType(ModelType(SubResource), serialize_when_none=False)
    load_balancer_backend_address_pools = ListType(ModelType(SubResource), serialize_when_none=False)
    load_balancer_inbound_nat_pools = ListType(ModelType(SubResource), serialize_when_none=False)
    primary = BooleanType(serialize_when_none=False)
    private_ip_address_version = StringType(choices=('IPv4', 'IPv6'), default='IPv4', serialize_when_none=False)
    public_ip_address_configuration = ModelType(VirtualMachineScaleSetPublicIPAddressConfiguration,
                                                serialize_when_none=False)
    subnet = ModelType(ApiEntityReference, serialize_when_none=False)


class VirtualMachineScaleSetNetworkConfiguration(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile >> VirtualMachineScaleSetNetworkProfile
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    dns_settings = ModelType(VirtualMachineScaleSetNetworkConfigurationDNSSettings, serialize_when_none=False)
    enable_accelerated_networking = BooleanType(serialize_when_none=False)
    enable_ip_forwarding = BooleanType(serialize_when_none=False)
    ip_configurations = ListType(ModelType(VirtualMachineScaleSetIPConfiguration), serialize_when_none=False)
    network_security_group = ModelType(SubResource, serialize_when_none=False)
    primary = BooleanType(serialize_when_none=False)


class VirtualMachineScaleSetVMNetworkProfileConfiguration(Model):
    network_interface_configurations = ListType(ModelType(VirtualMachineScaleSetNetworkConfiguration), serialize_when_none=False)


class SshPublicKey(Model):  # belongs to VmScaleSet >> LinuxConfiguration >> SshConfiguration
    key_data = StringType(serialize_when_none=False)
    path = StringType(serialize_when_none=False)


class SshConfiguration(Model):  # belongs to VmScaleSet >> LinuxConfiguration
    public_keys = ListType(ModelType(SshPublicKey), serialize_when_none=False)


class LinuxConfiguration(Model):  # belongs to VmScaleSet >> VirtualMachineScaleSetOSProfile
    disable_password_authentication = BooleanType(serialize_when_none=False)
    provision_vm_agent = BooleanType(serialize_when_none=False, default=True)
    ssh = ModelType(SshConfiguration, serialize_when_none=False)


class AdditionalUnattendedContent(Model):  # belongs to VmScaleSet
    component_name = StringType(choices=('Microsoft-Windows-Shell-Setup', ''), serialize_when_none=False)
    content = StringType(serialize_when_none=False)
    pass_name = StringType(choices=('OobeSystem', '', None), serialize_when_none=False)
    setting_name = StringType(choices=('AutoLogon', 'FirstLogonCommands', '', None), serialize_when_none=False)


class WinRMListener(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile >> WindowsConfiguration >> WinRMConfiguration
    certificate_url = StringType(serialize_when_none=False)
    protocol_types = StringType(choices=('http', 'https'), serialize_when_none=False)


class WinRMConfiguration(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile >> WindowsConfiguration
    listeners = ListType(ModelType(WinRMListener), serialize_when_none=False)


class PatchSettings(Model):  # belongs to  VmScaleSet
    # patch_mode = ModelType(InGuestPatchMode, serialize_when_none=False)
    patch_mode = StringType(choices=('AutomaticByOS', 'Manual', 'AutomaticByPlatform'), serialize_when_none=False)


class WindowsConfiguration(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile
    additional_unattended_content = ListType(ModelType(AdditionalUnattendedContent), serialize_when_none=False)
    enable_automatic_updates = BooleanType(serialize_when_none=False)
    patch_settings = ModelType(PatchSettings, serialize_when_none=False)
    provision_vm_agent = BooleanType(serialize_when_none=False)
    time_zone = StringType(serialize_when_none=False)
    win_rm = ModelType(WinRMConfiguration, serialize_when_none=False)


class VaultCertificate(Model):
    # belongs to VmScaleSet >> >> VirtualMachineScaleSetVMProfile >> VaultSecretGroup
    certificate_store = StringType(serialize_when_none=False)
    certificate_uri = StringType(serialize_when_none=False)


class VaultSecretGroup(Model):  # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile
    source_vault = ModelType(SubResource, serialize_when_none=False)
    vault_certificates = ListType(ModelType(VaultCertificate), serialize_when_none=False)


class OSProfile(Model):  # belongs to VirtualMachineScaleSetVM
    admin_username = StringType(serialize_when_none=False)
    admin_password = StringType(serialize_when_none=False)
    allow_extension_operations = BooleanType(serialize_when_none=False)
    computer_name = StringType(serialize_when_none=False)
    custom_data = StringType(serialize_when_none=False)
    linux_configuration = ModelType(LinuxConfiguration, serialize_when_none=False)
    windows_configuration = ModelType(WindowsConfiguration, serialize_when_none=False)
    require_guest_provision_signal = BooleanType(serialize_when_none=False)
    secrets = ListType(ModelType(VaultSecretGroup), serialize_when_none=False)


class VirtualMachineScaleSetVMProtectionPolicy(Model):
    protect_from_scale_in = BooleanType(default=False)
    protect_from_scale_set_actions = BooleanType(default=False)


class SecurityProfile(Model):  # belongs to VmScaleSet
    encryption_at_host = BooleanType(default=False, serialize_when_none=False)


class DiskEncryptionSetParameters(Model):
    id = StringType(serialize_when_none=False)


class ManagedDiskParameters(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile
    # >> VirtualMachineScaleSetStorageProfile >> VirtualMachineScaleSetDataDisk
    disk_encryption_set = ModelType(DiskEncryptionSetParameters, serialize_when_none=False)
    storage_account_type = StringType(serialize_when_none=False)
    storage_type = StringType(serialize_when_none=False)
    id = StringType(serialize_when_none=False)


class VirtualHardDisk(Model):
    # belongs to VmScaleSet >> VirtualMachineScaleSetVMProfile >> VirtualMachineScaleSetStorageProfile
    #            >> VirtualMachineScaleSetOSDisk
    uri = StringType(serialize_when_none=False)


class DataDisk(Model):
    caching = StringType(choices=('None', 'ReadOnly', 'ReadWrite', None), serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    create_option = StringType(choices=('Attach', 'Empty', 'FromImage', None), default='Empty',
                               serialize_when_none=False)
    disk_iops_read_write = IntType(serialize_when_none=False)
    disk_m_bps_read_write = IntType(serialize_when_none=False)
    disk_size_gb = IntType(serialize_when_none=False)
    lun = IntType(serialize_when_none=False)
    managed_disk = ModelType(ManagedDiskParameters, serialize_when_none=False)
    write_accelerator_enabled = BooleanType(serialize_when_none=False)
    image = ModelType(VirtualHardDisk, serialize_when_none=False)
    to_be_detached = BooleanType(serialize_when_none=False)
    vhd = ModelType(VirtualHardDisk, serialize_when_none=False)



class ImageReference(Model):
    exact_version = StringType(serialize_when_none=False)
    id = StringType(serialize_when_none=False)
    offer = StringType(serialize_when_none=False)
    publisher = StringType(serialize_when_none=False)
    sku = StringType(serialize_when_none=False)
    version = StringType(serialize_when_none=False)


class DiffDiskOptions(Model):  # belongs to VmScaleSet >> DiffDiskSettings
    local = StringType(serialize_when_none=False)


class DiffDiskSettings(Model):
    option = ModelType(DiffDiskOptions, serialize_when_none=False)
    placement = StringType(choices=('CacheDisk', 'ResourceDisk'), serialize_when_none=False)


class KeyVaultSecretReference(Model):
    secret_url = StringType(serialize_when_none=False)
    source_vault = ModelType(SubResource, serialize_when_none=False)


class KeyVaultKeyReference(Model):
    key_url = StringType(serialize_when_none=False)
    source_vault = ModelType(SubResource, serialize_when_none=False)


class DiskEncryptionSettings(Model):
    disk_encryption_key = ModelType(KeyVaultSecretReference, serialize_when_none=False)
    enabled = BooleanType(serialize_when_none=False)
    key_encryption_key = ModelType(KeyVaultKeyReference, serialize_when_none=False)


class OSDisk(Model):
    name = StringType(serialize_when_none=False)
    caching = StringType(choices=('None', 'ReadOnly', 'ReadWrite'), default='None', serialize_when_none=False)
    create_option = StringType(choices=('Attach', 'Empty', 'FromImage'), default='Empty', serialize_when_none=False)
    diff_disk_settings = ModelType(DiffDiskSettings, serialize_when_none=False)
    disk_size_gb = IntType(serialize_when_none=False)
    encryption_settings = ModelType(DiskEncryptionSettings, serialize_when_none=False)
    image = ModelType(VirtualHardDisk, serialize_when_none=False)
    managed_disk = ModelType(ManagedDiskParameters, serialize_when_none=False)
    os_type = StringType(choices=('Linux', 'Windows'), serialize_when_none=False)
    vhd = ModelType(VirtualHardDisk, serialize_when_none=False)
    write_accelerator_enabled = BooleanType(serialize_when_none=False)


class StorageProfile(Model):
    data_disks = ListType(ModelType(DataDisk), serialize_when_none=False)
    image_reference = ModelType(ImageReference, serialize_when_none=False)
    os_disk = ModelType(OSDisk, serialize_when_none=False)


class InstanceViewStatus(Model):
    code = StringType(serialize_when_none=False)
    display_status = StringType(serialize_when_none=False)
    level = StringType(choices=('Error', 'Info', 'Warning'), serialize_when_none=False)
    message = StringType(serialize_when_none=False)
    time = DateTimeType(serialize_when_none=False)


class VirtualMachineExtensionInstanceView(Model):
    name = StringType(serialize_when_none=False)
    statuses = ListType(ModelType(InstanceViewStatus))
    substatuses = ListType(ModelType(InstanceViewStatus))
    type = StringType(serialize_when_none=False)
    type_handler_version = StringType(serialize_when_none=False)
    display_status = StringType(serialize_when_none=False)


class Settings(Model):
    protocol = StringType(serialize_when_none=False)
    port = IntType(serialize_when_none=False)
    requestPath = StringType(serialize_when_none=False)


class VirtualMachineExtension(Model):
    id = StringType(serialize_when_none=False)
    location = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    auto_upgrade_minor_version = BooleanType(serialize_when_none=False)
    enable_automatic_upgrade = BooleanType(serialize_when_none=False)
    force_update_tag = StringType(serialize_when_none=False)
    instance_view = ModelType(VirtualMachineExtensionInstanceView)
    protected_settings = StringType(serialize_when_none=False)
    provisioning_state = StringType(serialize_when_none=False)
    publisher = StringType(serialize_when_none=False)
    settings = ModelType(Settings, serialize_when_none=False)
    type = StringType(serialize_when_none=False)
    type_handler_version = StringType(serialize_when_none=False)
    tags = ModelType(Tags, serialize_when_none=False)

####################


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
    name = StringType()
    location = StringType()
    additional_capabilities = ModelType(AdditionalCapabilities, serialize_when_none=False)
    available_set = ModelType(SubResource, serialize_when_none=False)
    diagnostics_profile = ModelType(DiagnosticsProfile, serialize_when_none=False)
    hardware_profile = ModelType(HardwareProfile, serialize_when_none=False)
    latest_model_applied = BooleanType(default=True, serialize_when_none=False)
    licence_type = StringType(serialize_when_none=False)
    model_definition_applied = StringType(serialize_when_none=False)
    network_profile = ModelType(NetworkProfile, serialize_when_none=False)
    network_profile_configuration = ModelType(VirtualMachineScaleSetVMNetworkProfileConfiguration, serialize_when_none=False)
    os_profile = ModelType(OSProfile, serialize_when_none=False)
    protection_policy = ModelType(VirtualMachineScaleSetVMProtectionPolicy, serialize_when_none=False)
    provisioning_state = StringType(serialize_when_none=False)
    vm_instance_status_display = StringType(serialize_when_none=False)
    security_profile = ModelType(SecurityProfile, serialize_when_none=False)
    storage_profile = ModelType(StorageProfile, serialize_when_none=False)
    resources = ListType(ModelType(VirtualMachineExtension), serialize_when_none=False)
    sku = ModelType(Sku, serialize_when_none=False)
    tags = ModelType(Tags, serialize_when_none=False)
    vm_id = StringType(serialize_when_none=False)
    primary_vnet = StringType(serialize_when_none=False)
    plan = ModelType(Plan, serialize_when_none=False)
    provisioning_state = StringType(choices=('Failed', 'Succeeded'))
    vm_instance_status_profile = ModelType(VirtualMachineExtensionVMInstanceView, serialize_when_none=False)
    vm_instance_status_display = StringType(serialize_when_none=False)
    type = StringType(serialize_when_none=False)
    zones = ListType(StringType, serialize_when_none=False)


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
    resource_type = StringType(default='inventory.CloudService')
    resource = ModelType(VirtualMachineScaleSetResource)
