from crhelper import CfnResource
import json
import boto3
import datetime

helper = CfnResource()
ec = boto3.client('ec2')
store = boto3.client('ssm')

@helper.create
@helper.update
def no_op(_, __):
    pass

@helper.delete
def delete(event, context):

    print ("event: ", json.dumps(event))

    reservations = ec.describe_instances( 
        Filters=[
            {'Name': 'tag-key', 'Values': ['Backup1357']}
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    count = 0
    for instance in instances:
        if instance['State']['Name'] != 'running':      # don't want to backup non-running instances left after rapid restart of stack
            continue
        count += 1                                      # using counts is clunky
        if count > 1:
            print ("Oops more than 1 instance - something's wrong - aborting!")
            return
        print ("Found instance %s" % (instance['InstanceId']))
        # Create an AMI from the instance
        JenkinsAMI = ec.create_image(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 50                    # Need to get this value from somewhere not hard code
                        }
                    },
            ],
            Description='Jenkins AMI from instance',
            InstanceId=instance['InstanceId'],
            # Need unique name here hence addition of datetime
            Name='JenkinsAMI ' + str(datetime.datetime.utcnow()).replace(':' , '-') 
        )

        # Tag the AMI
        ec.create_tags(
            Resources=[
                JenkinsAMI['ImageId']
            ],
            Tags=[
                {'Key': 'Name', 'Value': "Jenkins AMI"},
                {'Key': 'Date', 'Value': "UTC: %s" % (str(datetime.datetime.utcnow()))}
            ]
        )

        print ("AMI %s created from instance %s" % (
            JenkinsAMI['ImageId'],
            instance['InstanceId']
        ))

        # Save the AMI id to Parameter store for retrieval by server boot
        store.put_parameter(
            Name='/JenkinsAMIId',
            Value=JenkinsAMI['ImageId'],
            Type='String',
            Overwrite=True,
            Tier='Standard',
        )


def lambda_handler(event, context):
    helper(event, context)
