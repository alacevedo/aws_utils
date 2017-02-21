import boto3

def lambda_handler(event, context):
    _cli = boto3.client('ec2', region_name='us-west-2')
    _reservations =  _cli.describe_instances(
        Filters=[
            {'Name': 'tag-value', 'Values' : ['non-prod'] }
        ]
    )

    _instances = []
    for r in _reservations.get('Reservations'):
        for i in r.get('Instances'):
            _instances.append(i.get('InstanceId'))

    try:
        _stop_response = _cli.stop_instances(
            DryRun = False
            , InstanceIds = _instances
            , Force = False
        )
        print _stop_response
    except:
        print '[ERROR] : stop_instances failed'
