import boto3
import collections
import datetime
 
ec = boto3.client('ec2')

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
    if len(instances) > 1:
        print ("ERROR: found more than 1 instance to backup")
        return None

    for instance in instances:
        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            print "Found EBS volume %s on instance %s" % (vol_id, instance['InstanceId'])

            snap = ec.create_snapshot(
                Description='Jenkins snapshot',
                VolumeId=vol_id,
            )

            ec.create_tags(
                Resources=[
                    snap['SnapshotId'],
                ],
                Tags=[
                    {'Key': 'Name', 'Value': "Jenkins snap"},
                    {'Key': 'Date', 'Value': "UTC: %s" % (str(datetime.datetime.utcnow()))}
                ]
            )            

            print "Snapshot %s of volume %s from instance %s" % (
                snap['SnapshotId'],
                vol_id,
                instance['InstanceId'],
            )
lambda_handler(None, None)
