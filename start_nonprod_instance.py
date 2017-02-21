import boto3

def lambda_handler(event, context):
    _cli_ec2 = boto3.client('ec2', region_name='us-west-2')
    _reservations =  _cli_ec2.describe_instances(
        Filters=[
            {'Name': 'tag-value', 'Values' : ['non-prod'] }
        ]
    )

    _instances = []
    for r in _reservations.get('Reservations'):
        for i in r.get('Instances'):
            _instances.append(i.get('InstanceId'))

    try:
        _start_response = _cli_ec2.start_instances(
            InstanceIds = _instances
        )
        print _start_response
    except:
        print '[ERROR] : start_instances() failed'
