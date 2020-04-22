# Need to deal with terminated instances that have the tag
import boto3
import datetime
import json

SUCCESS = "SUCCESS"
FAILED = "FAILED"
def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }

    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))

ec = boto3.client('ec2')
store = boto3.client('ssm')

def lambda_handler(event, context):

    print ("This is the whole event received:")
    print ("event: ", json.dumps(event))
    if event['RequestType'] == "Delete":  # Only run this on stack delete - should wrap this in try?

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
            saveami = store.put_parameter(
                Name='/JenkinsAMIId',
                Value=JenkinsAMI['ImageId'],
                Type='String',
                Overwrite=True,
                Tier='Standard',
            )
    responseData = {}
    responseData['Test'] = "test data"
    print ("Got to end!")
    send(event, context, SUCCESS, responseData)
    return None