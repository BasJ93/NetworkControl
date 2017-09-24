#!/usr/bin/env python

# -*- coding: utf-8 -*-
#"""
#Created on Mon Sep  4 15:05:18 2017
#
#@author: Bas Janssen
#"""

import sys
import pexpect
import sqlite3

ap_ip = "192.168.10.100"
ap_user = "root"

#use uci to set the maclist, then deauth the MAC(s)

#rewrite mac list on each update, make shure to keep all the adresses that should be in there, in there.

#uci set wireless.default_radio0.maclist='AA:BB:CC:DD:EE:FF 00:11:22:33:44:55'
#uci set wireless.default_radio0.macfilter=deny
#uci commit wireless
#wifi down; wifi


def deauthMAC(MAC, ban_time):
    try:
        try:
            child = pexpect.spawn("ssh {user}@{host}".format(user=ap_user, host=ap_ip))
            child.logfile = sys.stdout
            child.timeout = 4
            #This will not be true after we implement SSH keys
        except pexpect.TIMEOUT:
            return "Error: TImeout AP"
        #Login to the AP, not required with an SSH key
        child.expect('#')
        child.sendline("ubus call hostapd.wlan0 del_client '{\"addr\":\"" + MAC + "\", \"reason\":1, \"deauth\":true, \"ban_time\":" + ban_time + "}'")
        child.expect('#')
        child.sendline('exit')
        return("success")
    except (pexpect.EOF, pexpect.TIMEOUT):
        return "Error: AP config failed"
    return "success"

def updateMACList():
    conn = sqlite3.connect('netwerkcontrol.db')
    _blockedMACs = ""
    try:
        MACs = conn.execute('select ADDRESS from MAC where not STATE="1"')
    except sqlite3.Error as e:
            return str(e)
    for MAC in MACs:
        if MAC[0] is None:
            print "No MACs blocked."
            _blockedMACs = ""
        else:
            _blockedMACs = _blockedMACs + " " + MAC[0]
    uci_maclist = "uci set wireless.default_radio0.maclist='{_blockedMACs}'".format(_blockedMACs = _blockedMACs)
    print uci_maclist
    try:
        try:
            child = pexpect.spawn("ssh {user}@{host}".format(user=ap_user, host=ap_ip))
            child.logfile = sys.stdout
            child.timeout = 4
            #This will not be true after we implement SSH keys
        except pexpect.TIMEOUT:
            return "Error: TImeout AP"
        #Login to the AP, not required with an SSH key
        child.expect('#')
        child.sendline(uci_maclist)
        child.expect('#')
        child.sendline("uci set wireless.default_radio0.macfilter=deny")
        child.expect('#')
        child.sendline("uci commit wireless")
        child.expect('#')
        child.sendline('exit')
        return("success")
    except (pexpect.EOF, pexpect.TIMEOUT):
        return "Error: AP config failed"
    return "success"
    conn.close()
    
def restartWiFi():
    try:
        try:
            child = pexpect.spawn("ssh {user}@{host}".format(user=ap_user, host=ap_ip))
            child.logfile = sys.stdout
            child.timeout = 4
            #This will not be true after we implement SSH keys
        except pexpect.TIMEOUT:
            return "Error: TImeout AP"
        #Login to the AP, not required with an SSH key
        child.expect('#')
        child.sendline("wifi down; wifi")
        child.expect('#')
        child.sendline('exit')
        return("success")
    except (pexpect.EOF, pexpect.TIMEOUT):
        return "Error: AP config failed"
    return "success"

if __name__=="__main__":
    updateMACList()#deauthMAC("40:88:05:C6:F0:D5", 10000)