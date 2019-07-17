import json
import boto3
from botocore.exceptions import ClientError, ParamValidationError

# This function is useful when you want to take a snapshot based on an event
# I use it to take snapshots on the last day of the month using the following
# cloudwatch schedule expression: 0 8 L * ? *


def lambda_handler(event, context):
    _cli = boto3.client('ec2')
    _volumes =  _cli.describe_volumes(
            Filters=[{
                'Name': 'tag:monthlyBackup',
                'Values' : ['true']
                }])
    
    print(_volumes)
    print ('\n-----------')
    
    _volumesDict = []
    
    for i in _volumes.get('Volumes'):
        
        _volumesDict.append(i.get('VolumeId'))
        print(i.get('VolumeId'))
        
        try:
            _response = _cli.create_snapshot(
            VolumeId = i.get('VolumeId'),
            DryRun = False
            )
            _info = '[INFO] : creating snapshot for ' + i.get('VolumeId')
            print(_info)
            
        except ClientError as e:
            _error = '[ERROR] : creating snapshot failed for ' + i.get('VolumeId')
            print(_error)
            return {
                    'statusCode': 500,
                    'body': 'failed to create snapshots'
                    }
                    
    return {
        'statusCode': 200,
        'snapshots_taken_on': _volumesDict
        }
