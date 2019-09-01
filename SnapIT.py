#!/usr/bin/python3

# before excute this python script
# run following command
# {sudo} pip install -U python-digitalocean paramiko
from time import sleep
from timeit import default_timer as timer

import paramiko
from digitalocean import SSHKey, Droplet, Manager, DataReadError
from paramiko.ssh_exception import NoValidConnectionsError, SSHException

tokens = ['23a150693c6c35da43b24376f1590f76ccebb1e5a1f3ff94c4275b39630555ee']

name = 'eliot'
username = 'root'
hostname = name  # is the same as the droplet name , keep it simple

rsa_pub = 'rsa.pub'
rsa = 'rsa'

cmds = [
    'uname -a',
    'apt-get -y update ',
    'debconf-set-selections <<< "postfix postfix/mailname string ' + hostname + '"',
    'debconf-set-selections <<< "postfix postfix/main_mailer_type string \'Internet Site\'"',
    'apt-get install -y postfix &',
    'echo "Leave me here"'
]

CONNECTION_TRIES = 3


def create_rsa():
    start = timer()
    ssh_name = 'RSA-' + name
    print("[+] Loading {} ... ".format(rsa_pub), end=" ")
    user_ssh_key = open(rsa_pub).read()
    key = SSHKey(token=token,
                 name=ssh_name,
                 public_key=user_ssh_key)
    try:
        key.create()
        print(timer() - start)
        return [key]

    except DataReadError:
        print("[!] SSH {} Key is already in use on your account ( Generate new rsa file )".format(ssh_name))
        exit(0)


def create_droplet(in_token):
    start = timer()
    key = create_rsa()
    print("[+] Creating {} Droplet ... ".format(name))
    new_droplet = Droplet(token=in_token,
                          name=name,
                          ssh_keys=key,
                          image="ubuntu-14-04-x64",
                          region='nyc3',
                          size='s-6vcpu-16gb')
    new_droplet.create()

    print("[+] Waiting Creation ... ", end=" ")
    actions = new_droplet.get_actions()
    for action in actions:
        action.load()
        action.wait()
    print("Done {}".format(timer() - start))

    new_droplet = new_droplet.load()

    print("[+] {} with ip {}".format(name, new_droplet.ip_address))

    return new_droplet


def connect_to_droplet(server, again=""):
    start = timer()
    print("[+] Connecting {} to {}@{} on 22 ...".format(again, username, server), end=" ")
    ssh_session = paramiko.SSHClient()
    ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_session.connect(server, username=username, key_filename=rsa)
    except (NoValidConnectionsError, SSHException):
        if CONNECTION_TRIES > 0:
            print(" fail ... [] ", )
            sleep(2)
            connect_to_droplet(server, "again({})".format(CONNECTION_TRIES))
        else:
            return

    print(" Connected {}".format(timer() - start))
    return ssh_session


def run_cmd(ssh):
    for cmd in cmds:
        print("{}@{}:$ {} : ".format(hostname, username, cmd))
        _, stdout, _ = ssh.exec_command(cmd)
        print(stdout.readlines())


def create_snapshot(droplet):
    start = timer()
    snap_name = name + "-snap"
    print("[+] Creating Snapshot ( ila fik matsena ... if not , close and run the last part of the code )")
    snap_actions = droplet.take_snapshot(snap_name, return_dict=False, power_off=True)
    print("[+] Waiting for Snapshot ... ", end="")
    snap_actions.wait()
    print(" Created {}".format(timer() - start))

    snap = droplet.get_snapshots()[0]

    return snap.load()


def add_regions(snap):
    print("[+] Adding Regions {}: ".format(snap.name))
    print("    Current regions : {} ".format(" ".join(snap.regions)))

    available_regions = Manager(token=token).get_all_regions()

    print("    Available regions : {} ".format(" ".join([v.slug for v in available_regions])))

    if set(snap.regions) == set([region.slug for region in available_regions]):
        print("    All Available Regions already Added ")
        return

    new_regions = [new for new in available_regions if (new.slug not in snap.regions)]

    for region in new_regions:
        print("       - Adding {} : {} ".format(region.name, region.slug), end=" ... ")
        try:
            adding = snap.get_data(
                "images/%s/actions/" % snap.id,
                type='POST',
                params={"type": "transfer", "region": region.slug}
            )
            # get_data returns a dict not actions to use for waiting
            # TODO Get transfer status
            # adding.wait()
            print(" Done")
        except DataReadError:
            print("This image has already been transfered to this region")
            continue
    print("[!] wait for region transfer not implemented yet")
    print("[!] you should wait for transfer to finish ")


if __name__ == '__main__':
    for token in tokens:
        start = timer()

        # step 1 : created Droplet
        droplet = create_droplet(token)

        sleep(10)  # to make sure it's up

        # step 2 : Connect to droplet
        ssh_session = connect_to_droplet(droplet.ip_address)

        # step 3 : run commands
        run_cmd(ssh_session)

        # step 4 : create snapshot
        snap = create_snapshot(droplet)

        # step 5 : add all regions
        add_regions(snap)

        # in case of errors in add_regions let's iterate over all existing snapshots and add regions , makhasrin walo
        for snap in Manager(token=token).get_all_snapshots():
            add_regions(snap)

        print("[+] Total time {}".format(timer() - start))
