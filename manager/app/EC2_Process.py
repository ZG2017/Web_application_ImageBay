from flask import render_template, redirect, url_for, request, session
from app import webapp
import random

import boto3
from app import AWS_config
from datetime import datetime, timedelta
from operator import itemgetter

@webapp.route('/',methods=['GET'])
@webapp.route('/manager',methods=['GET'])
# Display an HTML list of all ec2 instances
def manager():
    error = None
    if 'error' not in session:
        session['error'] = None
    if session['error'] != None:
        error,session['error'] = session['error'],None
        
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    # only show those instances currently running 
    instances = ec2.instances.filter(Filters = [{'Name': 'instance-state-name', 'Values': ['running','pending']},
                                                {'Name': 'tag:Name', 'Values':['worker']}])

    # show all instances
    #instances = ec2.instances.all()

    return render_template("manager.html",
                           error = error, 
                           title = "Manager", 
                           instances = instances, 
                           auto_scaling = AWS_config.Auto_scaling,
                           grow_rate = AWS_config.grow_rate,
                           grow_threshold = AWS_config.grow_threshold,
                           shrink_rate = AWS_config.shrink_rate,
                           shrink_threshold = AWS_config.shrink_threshold)


@webapp.route('/detial/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    ##    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System


    namespace = 'AWS/EC2'
    statistic = 'Average'                   # could be Sum,Maximum,Minimum,SampleCount,Average

    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime = datetime.utcnow() - timedelta(seconds = 20 * 60),
        EndTime = datetime.utcnow() - timedelta(seconds = 0),
        MetricName = metric_name,
        Namespace = namespace,  
        Statistics = [statistic],
        Dimensions = [{'Name': 'InstanceId', 'Value': id}]
    )
    cpu_stats = []
    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))


    return render_template("view.html",title = "Instance Info",instance = instance,cpu_stats = cpu_stats)


@webapp.route('/ec2_examples/refresh',methods=['GET'])
def refresh():
    return redirect(url_for('manager'))


@webapp.route('/ec2_examples/create',methods=['POST'])
# Start a new EC2 instance
def ec2_create():

    # start the conncection
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters = [{'Name': 'instance-state-name', 'Values': ['running','pending']},
                                                {'Name': 'tag:Name', 'Values':['worker']}])

    current_number_of_worker = len([i for i in instances])


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

        instanceID = response[0].instance_id
        # register to load balancer
        client = boto3.client('elb')
        response = client.register_instances_with_load_balancer(
                                                                LoadBalancerName = AWS_config.LoadBalancerName,
                                                                Instances=[
                                                                    {
                                                                        'InstanceId': instanceID
                                                                    },
                                                                ])
    else:
        session['error'] = 'number of instances reaches upper limit! New Instance is not created!'

    return redirect(url_for('manager'))


@webapp.route('/ec2_examples/turn_on_auto_scaling',methods=['POST'])
# turn on the auto scaling
def turn_on_auto_scaling():
    if request.form['grow_rate'] <= 1:
        session['error'] = 'grow rate cannot smaller than or equals to 1!'
        return redirect(url_for('manager'))
    elif request.form['shrink_rate'] <= 1:
        session['error'] = 'shrink rate cannot smaller than or equals to 1!'
        return redirect(url_for('manager'))
    AWS_config.grow_rate = request.form['grow_rate']
    AWS_config.grow_threshold = request.form['grow_threshold']
    AWS_config.shrink_rate = request.form['shrink_rate']
    AWS_config.shrink_threshold = request.form['shrink_threshold']
    AWS_config.Auto_scaling = True
    return redirect(url_for('manager'))


@webapp.route('/ec2_examples/turn_off_auto_scaling',methods=['POST'])
# turn off the auto scaling
def turn_off_auto_scaling():
    AWS_config.Auto_scaling = False
    return redirect(url_for('manager'))



@webapp.route('/ec2_examples/delete/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_destroy(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    instances = ec2.instances.filter(Filters = [{'Name': 'instance-state-name', 'Values': ['running','pending']},
                                                {'Name': 'tag:Name', 'Values':['worker']}])

    current_number_of_worker = len([i for i in instances])

    if current_number_of_worker > AWS_config.MIN_INSTANCES:
        # deregister the instance from load balancer before deletion
        client = boto3.client('elb')
        client.deregister_instances_from_load_balancer(LoadBalancerName = AWS_config.LoadBalancerName,
                                                    Instances=[
                                                    {
                                                            'InstanceId': id
                                                    },
                                                    ])

        
        ec2.instances.filter(InstanceIds=[id]).terminate()
    else:
        session['error'] = 'Must have at least one worker in worker pool!'
    return redirect(url_for('manager'))


@webapp.route('/ec2_examples/random_delete',methods=['POST'])
# randomly terminate a EC2 instance
def ec2_random_destroy():
    # create connection to ec2
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters = [{'Name': 'instance-state-name', 'Values': ['running']},
                                                {'Name': 'tag:Name', 'Values':['worker']}])

    
    instances = [i for i in instances]
    current_number_of_worker = len(instances)

    if current_number_of_worker > AWS_config.MIN_INSTANCES:
        # randomly delete a instance
        chosen_instance = random.choice(instances)

        # deregister the instance from load balancer before deletion
        client = boto3.client('elb')
        client.deregister_instances_from_load_balancer(LoadBalancerName = AWS_config.LoadBalancerName,
                                                    Instances=[
                                                    {
                                                            'InstanceId': chosen_instance.instance_id
                                                    },
                                                    ])


        chosen_instance.terminate()
    else:
        session['error'] = 'Must have at least one worker in worker pool!'

    return redirect(url_for('manager'))