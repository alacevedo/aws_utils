import boto3

def lambda_handler(event, context):
    _cli_ec2 = boto3.client('ec2', region_name='us-west-2')
    _cli_r53 = boto3.client('route53', region_name='us-west-2')
    _reservations =  _cli_ec2.describe_instances(
        Filters=[
            {
            'Name': 'tag-value',
            'Values' : ['non-prod']
            }
        ]
    )

    # Builds dict (subdomain : public dns )
    # looks for the tag key "dominio" which stores the sub domain string
    _instances = {}
    for r in _reservations.get('Reservations'):
        for i in r.get('Instances'):
            _ins_id = i.get('PublicDnsName')
            for tag in i.get('Tags'):
                if tag.get('Key') == 'dominio':
                    _instances.update(
                        {
                        tag.get('Value') :
                        _ins_id
                         }
                    )

    # Builds dict (domain : hosted zone id)
    _hosted_zones = _cli_r53.list_hosted_zones()
    _domains = {}
    for r in _hosted_zones.get('HostedZones'):
        _domains.update(
            {
                r.get('Name').rstrip('.') :
                r.get('Id').lstrip('/hostedzone/')
            }
        )

    # Update recordsets
    for dom in _domains.keys():
        for subdom in _instances.keys():
            if dom in subdom:
                try:
                    print '[INFO] : Performing UpdateRecordSet on ' + subdom
                    _change_record_response =
                    _cli_r53.change_resource_record_sets(
                        HostedZoneId = _domains[dom],
                        ChangeBatch = {
                                'Changes': [
                                    {
                                        'Action': 'UPSERT',
                                        'ResourceRecordSet': {
                                            'Name': subdom,
                                            'Type': 'CNAME',
                                            'TTL': 300,
                                            'ResourceRecords': [
                                                {
                                                    'Value': _instances[subdom]
                                                },
                                            ],
                                        }
                                    },
                                ]
                            }
                    )
                except:
                    print '[ERROR] : UpdateRecordSet on' + SubDomain + ' failed'
            else:
                print '[WARN] : No match found on ' + dom + ' and ' + subdom
