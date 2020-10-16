#!/usr/bin/env python3
# Simple MAC changer program

import subprocess
import optparse
import re
import random

global rand


def change(interface, new_mac):
    print("[+]MAC changed for " + interface + " to " + new_mac)
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])


def get_args():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Select the interface to change MAC")
    parser.add_option("-m", "--mac", dest="new_mac", help="Enter the new MAC")
    parser.add_option("-r", "--random", action="store_true", dest="rand_mac", help="Random MAC Address")
    (option, arguments) = parser.parse_args()
    if not option.interface:
        parser.error("[-]Please specify an interface")
    elif str(option.new_mac) == "None" and str(option.rand_mac) == "None":
        parser.error("[-]Please input the new MAC or use -r or --random ")
    return option


def current_mac(interface):
    try:
        subprocess.check_output(["ifconfig", interface])
    except subprocess.CalledProcessError:
        print("[-]No such Device.\n")
        exit(0)
    else:
        ifconfig_result = subprocess.check_output(["ifconfig", interface])
        mac_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig_result))
        if mac_search_result:
            return mac_search_result.group(0)
        else:
            print("[-]No MAC exist for the interface")


def vendor_info(address):
    with open("OUI.list", "r") as file:
        for mak in list(file):
            catch_vendor = re.search(r"(\w\w \w\w \w\w)(.*)", str(mak))
            mac_li = catch_vendor.group(1)
            mac_li = mac_li.split(" ")
            mac_li = ':'.join(mac_li)
            present_mak = re.search(r"\w\w:\w\w:\w\w", str(address.upper()))
            present_mak = present_mak.group(0)
            if str(mac_li) == present_mak:
                return catch_vendor.group(2)


def random_mac(interface):
    with open("OUI.list", "r") as file:
        select_one = random.choice(list(file))
        add_part = re.search(r"\w\w \w\w \w\w", str(select_one))
        mac = add_part.group(0)
        mac = mac.split(" ")
        mac = ':'.join(mac)
        create_random_mac = "%s:%02x:%02x:%02x" % (
        str(mac).lower(), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", create_random_mac])
    subprocess.call(["ifconfig", interface, "up"])
    global rand
    rand = create_random_mac


options = get_args()

present_mac = current_mac(options.interface)

print("Current MAC= " + str(present_mac) + " (" + str(vendor_info(present_mac)) + ")")

if present_mac is None:
    print("[-]Enter a valid interface and try again!")
else:
    #   Backup in case of any errors or if we want to return to your old MAC address.
    backup_cmd = "echo '" + present_mac + "' > backup_mac.txt"
    subprocess.check_output(backup_cmd, shell=True)
    if options.rand_mac is True:
        # Call random_mac function.
        random_mac(options.interface)
        # new_rand = random_mac()
        present_mac = current_mac(options.interface)
    else:
        change(options.interface, options.new_mac)
        present_mac = current_mac(options.interface)

    if present_mac == options.new_mac:
        print("[+]New MAC = " + str(present_mac) + " (" + str(vendor_info(present_mac)) + ")")
    elif present_mac == rand:
        print("[+]New MAC = " + str(present_mac) + " (" + str(vendor_info(present_mac)) + ")")
    else:
        print("[-]MAC did not change")

