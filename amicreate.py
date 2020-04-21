# Need to deal with terminated instances that have the tag
import boto3
import datetime
import cfnresponse
import json
 
ec = boto3.client('ec2')
store = boto3.client('ssm')

def lambda_handler(event, context):

    print "This is the event received:\n%s" % (event)
    if event['RequestType'] == "Delete":  # Only run this on stack delete

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
            count += 1
            if count > 1:
                print("Oops more than 1 instance - something's wrong - aborting!")
                return
            print "Found instance %s" % (instance['InstanceId'])
            # Create an AMI from the instance
            JenkinsAMI = ec.create_image(
                BlockDeviceMappings=[
                    {
                        'DeviceName': '/dev/xvda',
                        'Ebs': {
                            'DeleteOnTermination': True
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

            print "AMI %s created from instance %s" % (
                JenkinsAMI['ImageId'],
                instance['InstanceId']
            )

            # Save the AMI id to Parameter store for retrieval by server boot
            saveami = store.put_parameter(
                Name='/JenkinsAMIId',
                Value=JenkinsAMI['ImageId'],
                Type='String',
                Overwrite=True,
                Tier='Standard',
            )
    print "Got to end!"
    cfnresponse.send(event, context, cfnresponse.SUCCESS)   