#!/usr/bin/python3

# before excute this python script
# run following command
# {sudo} pip install -U python-digitalocean paramiko
from time import sleep

import digitalocean
import paramiko
from digitalocean import SSHKey
from paramiko.ssh_exception import NoValidConnectionsError

token = '23a150693c6c35da43b24376f1590f76ccebb1e5a1f3ff94c4275b39630555ee'

name = 'eliot'
username = 'root'
hostname = name  # is the same as the droplet name , keep it simple

rsa_pub = 'rsa.pub'
rsa = 'rsa'

cmds = [
    'uname -a',
    'apt-get -y update ',
    'debconf-set-selections <<< "postfix postfix/mailname string ' + hostname,
    'debconf-set-selections <<< "postfix postfix/main_mailer_type string \'Internet Site\'"',
    'apt-get install -y postfix'
]

CONNECTION_TRIES = 3


def create_rsa():
    print("[+] Loading {} ... ".format(rsa_pub))
    user_ssh_key = open(rsa_pub).read()
    key = SSHKey(token=token,
                 name='RSA-' + name,
                 public_key=user_ssh_key)
    key.create()
    return [key]


def create_droplet():
    print("[+] Creating {} Droplet ... ".format(name))
    droplet = digitalocean.Droplet(token=token,
                                   name=name,
                                   ssh_keys=create_rsa(),
                                   image="ubuntu-14-04-x64",
                                   region='nyc3',
                                   size='s-6vcpu-16gb')
    Created = False
    droplet.create()

    print("[+] Waiting ... ")
    while not Created:
        actions = droplet.get_actions()
        for action in actions:
            action.load()
            # Once it shows complete, droplet is up and running
            print("[+] {} Status : {}".format(name, action.status))
            if "completed" in action.status:
                Created = True

    manager = digitalocean.Manager(token=token)
    droplet = manager.get_all_droplets()[0]
    print("[+] {} with ip {}".format(name, droplet.ip_address))
    return droplet


def connect_to_droplet(server, again=""):
    print("[+] Connecting {} to {}@{} on 22 ...".format(again, username, server), end=" ")
    ssh_session = paramiko.SSHClient()
    ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_session.connect(server, username=username, key_filename=rsa)
    except NoValidConnectionsError:
        if CONNECTION_TRIES > 0:
            print(" fail ... [] ", )
            sleep(2)
            connect_to_droplet(server, "again({})".format(CONNECTION_TRIES))
        else:
            return

    print(" Connected")
    return ssh_session


def run_cmd(ssh):
    for cmd in cmds:
        _, stdout, _ = ssh.exec_command(cmd)
        print("cmd {} -> : {}".format(cmd, stdout.readlines()))


def create_snapshot(droplet):
    snap_name = name + "-snap"
    print("[+] Creating Snapshot created")
    snap_actions = droplet.take_snapshot(snap_name, return_dict=False, power_off=True)
    print("[+] Waiting for Snapshot ... ")
    snap_actions.wait()
    print("[+] Snapshot created")


if __name__ == '__main__':
    droplet = create_droplet()
    sleep(5)  # to make sure it's up
    ssh_session = connect_to_droplet(droplet.ip_address)
    run_cmd(ssh_session)
    create_snapshot(droplet)
    # TODO add regions to snap
