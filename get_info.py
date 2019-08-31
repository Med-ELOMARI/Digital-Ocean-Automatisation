import digitalocean

tokens = ["23a150693c6c35da43b24376f1590f76ccebb1e5a1f3ff94c4275b39630555ee"]

for token in tokens:
    print("*" * 80)
    Manager = digitalocean.Manager(token=token)
    print("[+] Info On account : ", Manager.get_account().email)
    print("               - Account Status : ", Manager.get_account().status)
    print("               - Droplet limit : ", Manager.get_account().droplet_limit)
    print("               - Status message : ", Manager.get_account().status_message)
    if "locked" in Manager.get_account().status:
        continue
    print("               - Number of Droplets : ", len(Manager.get_all_droplets()))
    for i, ssh in enumerate(Manager.get_all_sshkeys()):
        print("               - SSH {} : {}".format(i + 1, ssh.name))
    for i, snap in enumerate(Manager.get_all_snapshots()):
        print("               - Snapshot {} : {}".format(i + 1, snap.name))
