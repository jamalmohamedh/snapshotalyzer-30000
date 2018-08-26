import boto3
import botocore
import click

session = boto3.Session(profile_name='jammy')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances=[]

    if project:
        filters=[{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
    """Jammy manages Snapshot"""

@cli.group('snapshots')
def snapshots():
    """Command for Snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True, help="List all snapshots for volumes")
def list_snapshots(project, list_all):
    "List EC2 Snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.progress,
                    s.state,
                    s.start_time.strftime("%c")
                )))

                if s.state == 'completed'and not list_all: break
    return


@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None, help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 Volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted",
            )))
    return

@cli.group('instances')
def instances():
    """Commands for Instances"""

@instances.command('snapshot', help="Create snapshots for all volumes")
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create Snapshot for EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print( "skipping {0}, Snapshot already in progress ".format(v.id))
                continue
            print("  Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created for snapshotalyzer-30000")

        print("Starting {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job is done!")

    return

@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
        )))
    return

@instances.command('stop')
@click.option('--project', default=None, help='Only instances for the project')
def stop_instances(project):
    "Stop the instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping{0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.CLientError as e:
            print(" couldn't stop{0} ".format(i.id) +str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None, help='Only instances for the project')
def stop_instances(project):
    "Start the instances"

    instances = filter_instances(project)

    for i in instances:
        print("Starting{0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.CLientError as e:
            print(" couldn't start{0} ".format(i.id) +str(e))
            continue

    return


if __name__ == '__main__':
    cli()
