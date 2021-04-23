# plugin-azure-power-state 
![Microsoft Azure Cloud Services](https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/azure-cloud-services.svg) 
 Plugin for Microsoft Azure Virtual Machine, Virtual Machine ScaleSets to Check Running status
- Collecting Virtual Machine State and Virtual Machine Scale Sets state


# Data Sample

## Virtual Machine Instance

- cloud_service_type: Compute
- cloud_service_group: VirtualMachine
- provider: azure

~~~
"data": {
        "compute": {
            "instance_state": "RUNNING",
            "instance_id": "/subscriptions/xxxx/resourceGroups/yyyy/providers/Microsoft.Compute/virtualMachines/zzz"
        },
        "power_state": {
            "status": "RUNNING"
        }    
	....
}
~~~



## Virtual Machine Scale Sets

- cloud_service_type: Compute
- cloud_service_group: VmScaleSets
- provider: azure


~~~
"data" : {
        "virtual_machine_scale_set_power_state": [
                    {
                        "target_resource_uri": "/subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachineScaleSets/VMSS_NAME",
                        "tags": {
                            "key": null,
                            "value": null
                        },
                        "location": "eastus",
                        "profiles": [
                            {
                                "rules": [
                                    {
                                        "metric_trigger": {
                                            "operator": "LessThan",
                                            "statistic": "Average",
                                            "threshold": 25,
                                            "metric_name": "Percentage CPU",
                                            "time_window": 300,
                                            "time_grain": 60,
                                            "time_aggregation": "Average",
                                            "metric_resource_uri": "/subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachineScaleSets/VMSS_NAME",
                                            "metric_namespace": ""
                                        },
                                        "scale_action": {
                                            "value": "1",
                                            "type": "ChangeCount",
                                            "cooldown": 60,
                                            "direction": "Decrease"
                                        }
                                    }
                                ],
                                "capacity": {
                                    "minimum": "1",
                                    "maximum": "3",
                                    "default": "1"
                                },
                                "name": "Profile1"
                            }
                        ],
                        "name": "NAME",
                        "enabled": true
                    }
                ]
~~~
