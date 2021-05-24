from digitalocean import Manager

tokens = ["xxx"]

for token in tokens:
    print("*" * 80)
    manager = Manager(token=token)
    print("[+] Info On account : ", manager.get_account().email)
    print("               - Account Status : ", manager.get_account().status)
    print("               - Droplet limit : ", manager.get_account().droplet_limit)
    print("               - Status message : ", manager.get_account().status_message)
    if "locked" in manager.get_account().status:
        continue

    print("               - Number of Droplets : ", len(manager.get_all_droplets()))
    for i, ssh in enumerate(manager.get_all_sshkeys()):
        print("               - SSH {} : {}".format(i + 1, ssh.name))
    for i, snap in enumerate(manager.get_all_snapshots()):
        print("               - Snapshot {} : {}".format(i + 1, snap.name))
