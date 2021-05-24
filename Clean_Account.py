#!/usr/bin/python3

# before excute this python script
# run following command
# {sudo} pip install -U python-digitalocean

from digitalocean import Manager

tokens = ["xxx"]


class DigitalDroplets:

    def __init__(self, token):
        print("[+] All the shit  will be delete !!! ")
        self.Manager = Manager(token=token)

    def delete_droplets(self):
        print('[+] Droplets : ')
        self.__delete(self.Manager.get_all_droplets())

    def delete_ssh(self):
        print('[+] SSH Keys : ')
        self.__delete(self.Manager.get_all_sshkeys())

    def delete_snapshots(self):
        print('[+] Snapshot : ')
        self.__delete(self.Manager.get_all_snapshots())

    @staticmethod
    def __delete(what_to_delete):
        for item in what_to_delete:
            print("     Deleting {} : {}".format(item.name, item.destroy()))


if __name__ == "__main__":
    for token in tokens:
        DoDroplet = DigitalDroplets(token)
        DoDroplet.delete_droplets()
        DoDroplet.delete_ssh()
        # DoDroplet.delete_snapshots()
