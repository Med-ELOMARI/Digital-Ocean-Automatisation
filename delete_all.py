#!/usr/bin/python3

# before excute this python script
# run following command
# {sudo} pip install -U python-digitalocean

import digitalocean

tokens = ["23a150693c6c35da43b24376f1590f76ccebb1e5a1f3ff94c4275b39630555ee"]


class DigitalDroplets:

    def __init__(self, token):
        self.api_token = token
        print("All the shit  will be delete !!!")

    def fetch_digital_droplets(self):
        manager = digitalocean.Manager(token=self.api_token)
        my_droplets = manager.get_all_droplets()
        for d in my_droplets:
            print(d.name, " ", d.ip_address)

    def destroy_digital_droplets(self):
        manager = digitalocean.Manager(token=self.api_token)
        my_droplets = manager.get_all_droplets()
        for droplet in my_droplets:
            droplet.destroy()

    def delete_ssh_keys(self):
        m = digitalocean.Manager(token=self.api_token)
        ssh_keys = m.get_all_sshkeys()
        for ssh in ssh_keys:
            print("deleting SSH :", ssh.name)
            print(ssh.destroy())

    def delete_snaps(self):
        m = digitalocean.Manager(token=self.api_token)
        snaps = m.get_all_snapshots()
        for snap in snaps:
            print("deleting snap :", snap.name)


if __name__ == "__main__":
    for t in tokens:
        DoDroplet = DigitalDroplets(t)
        # DoDroplet.fetch_digital_droplets()
        DoDroplet.destroy_digital_droplets()
        DoDroplet.delete_ssh_keys()
        DoDroplet.delete_snaps()
