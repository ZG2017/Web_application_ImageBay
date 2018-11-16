from flask import render_template, redirect, url_for, request
from app import webapp
from app import AWS_config
import random

import boto3
from datetime import datetime, timedelta


def get_cpu_utilization():
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    # get all currently running
    instances = ec2.instances.filter(Filters = [{'Name': 'instance-state-name', 'Values': ['running']},
                                                {'Name': 'tag:Name', 'Values':['worker']}])   
    instances = [i for i in instances]

    counter = 0
    cpu_stats = []
    tmp = 0
    for instance in instances:
        tmp_instance = ec2.Instance(instance.id)
        client = boto3.client('cloudwatch')
        cpu = client.get_metric_statistics(Period = 1 * 60,
                                           StartTime = datetime.utcnow() - timedelta(seconds = 3 * 60),
                                           EndTime = datetime.utcnow() - timedelta(seconds = 0),
                                           MetricName = 'CPUUtilization',
                                           Namespace = 'AWS/EC2',  # Unit='Percent',
                                           Statistics = ["Average"],
                                           Dimensions = [{'Name': 'InstanceId', 'Value': tmp_instance.id}])
        
        counter += 1
        for point in cpu['Datapoints']:
            tmp = point['Average']
        cpu_stats.append(tmp)
    print(len(cpu_stats))
    if len(cpu_stats) == 0:
        return -1,counter
    else:
        return sum(cpu_stats)/len(cpu_stats),counter

def auto_check_func():
    if AWS_config.Auto_scaling:
        average_cpu_utilization,instances_counter = get_cpu_utilization()
        if average_cpu_utilization == -1:
            return print('No data point')
        else:
            if average_cpu_utilization >= AWS_config.grow_threshold and instances_counter < AWS_config.MAX_INSTANCES:
                # create a new instance
                ec2_create_by_rate(AWS_config.grow_rate)
                print('new instances created!')
            elif average_cpu_utilization <= AWS_config.shrink_threshold and instances_counter > AWS_config.MIN_INSTANCES:
                ec2_destroy_by_rate(AWS_config.shrink_rate)
                print('instances destroyed!')
        print(average_cpu_utilization,instances_counter)


# Start multiple new EC2 instances by rate
def ec2_create_by_rate(rate):
    # create connection to ec2
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters = [{'Name': 'instance-state-name', 'Values': ['running','pending']},
                                                {'Name': 'tag:Name', 'Values':['worker']}])

    current_number_of_worker = len([i for i in instances])
    # number of instances we need to create
    need_to_create_counter = int(current_number_of_worker * (rate-1))

    Ids = []

    # create instances
    for i in range(need_to_create_counter):
        if current_number_of_worker < AWS_config.MAX_INSTANCES:
            response = ec2.create_instances(ImageId = AWS_config.amiId,
                                            InstanceType = AWS_config.InstanceType,
                                            KeyName = AWS_config.KeyName,
                                            MinCount = 1,
                                            MaxCount = 1,
                                            TagSpecifications = AWS_config.TagSpecifications,
                                            Monitoring = AWS_config.Monitoring,
                                            Placement = AWS_config.Placement,
                                            SecurityGroupIds = AWS_config.SecurityGroupId,
                                            SubnetId = AWS_config.SubnetId,
                                            UserData = AWS_config.UserData)
            Ids.append(response[0].instance_id)
            current_number_of_worker += 1
    
    # register to load balancer
    client = boto3.client('elb')
    for Id in Ids: 
        response = client.register_instances_with_load_balancer(
                                                                LoadBalancerName = AWS_config.LoadBalancerName,
                                                                Instances=[
                                                                    {
                                                                        'InstanceId': Id
                                                                    },
                                                                ])

# Terminate multiple EC2 instances by rate
def ec2_destroy_by_rate(rate):
    # create connection to ec2
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters = [{'Name': 'instance-state-name', 'Values': ['running','pending']},
                                                {'Name': 'tag:Name', 'Values':['worker']}])
    instances = [i for i in instances]
    current_number_of_worker = len(instances)

    # deregister the instance from load balancer before deletion
    client = boto3.client('elb')

    # chosen instances
    need_to_destory_counter = int(current_number_of_worker * (rate-1)/rate)
    need_to_destory_instances = random.sample(instances,need_to_destory_counter)

    for instance in need_to_destory_instances:
        if current_number_of_worker > AWS_config.MIN_INSTANCES:
            client.deregister_instances_from_load_balancer(LoadBalancerName = AWS_config.LoadBalancerName,
                                                        Instances=[
                                                        {
                                                            'InstanceId': instance.instance_id
                                                        },
                                                        ])

            instance.terminate()
            current_number_of_worker -= 1
