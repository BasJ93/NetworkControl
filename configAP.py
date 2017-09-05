#!/usr/bin/env python

# -*- coding: utf-8 -*-
#"""
#Created on Mon Sep  4 15:05:18 2017
#
#@author: Bas Janssen
#"""

import sys
import pexpect

ap_ip = "192.168.2.200"
ap_user = "root"


#use uci to set the maclist, then deauth the MAC(s)

#rewrite mac list on each update, make shure to keep all the adresses that should be in there, in there.

#uci set wireless.@default_radio0.maclist='AA:BB:CC:DD:EE:FF 00:11:22:33:44:55'
#uci set wireless.@default_radio0.macfilter=deny
#uci commit wireless
#wifi down; wifi


def deauthMAC(MAC, ban_time):
    try:
        try:
            child = pexpect.spawn("ssh {user}@{host}".format(user=ap_user, host=ap_ip))
            child.logfile = sys.stdout
            child.timeout = 4
            child.expect('password:')
        except pexpect.TIMEOUT:
            return "Error: TImeout AP"
        #Login to the switch
        child.sendline(ap_pw)
        child.expect('#')
        child.sendline("ubus call hostapd.wlan0 del_client '{\"addr\":\"" + MAC + "\", \"reason\":1, \"deauth\":true, \"ban_time\":" + ban_time + "}'")
        child.expect('#')
        child.sendline('exit')
        return("success")
    except (pexpect.EOF, pexpect.TIMEOUT):
        return "Error: AP config failed"
    return "success"

if __name__=="__main__":
    deauthMAC("40:88:05:C6:F0:D5", 10000)