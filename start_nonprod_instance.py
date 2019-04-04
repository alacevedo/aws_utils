import json
import boto3
from botocore.exceptions import ClientError, ParamValidationError

def lambda_handler(event, context):
    _cli = boto3.client('ec2', region_name='us-east-2')
    _reservations =  _cli.describe_instances(
        Filters=[
            {'Name': 'tag:StopAtNight', 'Values' : ['true'] }
        ]
    )
    print _reservations
    print '\n-----------'

    _instances = []
    for r in _reservations.get('Reservations'):
        for i in r.get('Instances'):
            _instances.append(i.get('InstanceId'))
    print _instances
    print '\n-----------'
    try:
        _start_response = _cli.start_instances(
            InstanceIds = _instances,
            DryRun = True
        )
        print _start_response
        return {
            'statusCode': 200,
            'body': json.dumps(_start_response)    
        }
    except ClientError as e: 
        _error = '[ERROR] : stop instances failed'
        return {
            'statusCode': 500,
            'body': json.dumps(e)    
}
