import boto3
import datetime

def lambda_handler(event, context):
    # AWS client setup
    _cli_snap = boto3.client('ec2', region_name='us-west-2')
    _response = _cli_snap.describe_snapshots(
        OwnerIds=[
            'YourId',
        ],
    )

    #date calculations
    _current_day = datetime.datetime.utcnow()
    _days_ini = _current_day - datetime.timedelta(days=5)
    _days_end = _current_day - datetime.timedelta(days=10)
    _months = _current_day - datetime.timedelta(weeks=24)
    _next_month = _current_day.replace(day=28) + datetime.timedelta(days=4)
    _last_day_current_month = _next_month - datetime.timedelta(days=_next_month.day)
    _last_day_previous_month_tmp = _last_day_current_month - datetime.timedelta(weeks=5)
    _next_month = _last_day_previous_month_tmp.replace(day=28) + datetime.timedelta(days=4)
    _last_day_previous_month=_next_month - datetime.timedelta(days=_next_month.day)

    #date formating
    _days_limit_start = _days_ini.strftime('%Y%m%d')
    _days_limit_end = _days_end.strftime('%Y%m%d')
    _months_limit = _months.strftime('%Y%m%d')
    _last_day_current_month_int = _last_day_current_month.strftime('%Y%m%d')
    _last_day_previous_month_int = _last_day_previous_month.strftime('%Y%m%d')

    # generates the dict with the old snapshots to be deleted
    # It retains the last week and six month snapshots (last day of the month)
    _snap_list = _response.get('Snapshots')
    _req_list = {}
    for s in _snap_list:
        if s.get('Description') <= _days_limit_start \
        and s.get('Description') > _days_limit_end \
        and s.get('Description') != _last_day_current_month_int \
        and s.get('Description') != _last_day_previous_month_int:
            _req_list.update(
                        {s.get('Description') : s.get('SnapshotId')}
                    )
        elif s.get('Description') < _months_limit:
            _req_list.update(
                        {s.get('Description') : s.get('SnapshotId')}
                    )
    print 'Snapshots mark for delete request : '
    print _req_list

    #performs the request to delete old snapshots
    for s in _req_list.values():
        _response = _cli_snap.delete_snapshot(
            SnapshotId=s,
            DryRun=False
        )
