import boto3
import datetime
 
ec = boto3.client('ec2')
store = boto3.client('ssm')

def lambda_handler(event, context):

    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['Backup1357']},
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])
    if len(instances) != 1:
        print ("ERROR: found more than 1 instance to backup & that is not the intent")
        return None
    else:
        # If everything looks ok proceed
        for instance in instances:
            print "Found instance %s" % (instance['InstanceId'])

            # Create an AMI from the instance
            JenkinsAMI = client.create_image(
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
                Name='Jenkins AMI'
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
            saveami = client.put_parameter(
                Name='/JenkinsAMIId',
                Value=JenkinsAMI['ImageId'],
                Type='String',
                Overwrite=True,
                Tier='Standard',
            )           


lambda_handler(None, None)
