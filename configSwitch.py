#!/usr/bin/env python

# -*- coding: utf-8 -*-
#"""
#Created on Sun Sep  3 20:28:53 2017
#
#@author: Bas Janssen
#"""

#This function can be used to change the state of a port on a Netgear GS724Tv3 switch over telnet using the hidden cli.

import sys
import pexpect

switch_ip = "192.168.10.7"
switch_port = "60000"
switch_user = "admin"
switch_pw = "password"


def configSwitchPort(user_port, port_state):
    child = pexpect.spawn("telnet {ip} {port}".format(ip=switch_ip, port=switch_port))
    child.logfile = sys.stdout
    child.timeout = 4
    child.expect('Applying Interface configuration, please wait ...')
    child.sendline(switch_user)
    child.expect('Password:')
    child.sendline(switch_pw)
    child.expect('>')
    child.sendline('enable')
    child.expect('Password:')
    child.sendline('')
    child.expect('#')
    child.sendline('configure')
    child.expect('#') #(Config)
    child.sendline("interface {port}".format(port=user_port))
    child.expect("(interface {port})".format(port=user_port))
    #change port state here (shutdown or no shutdown)
    child.sendline("{port_state}".format(port_state=port_state))
    child.sendline("exit")
    child.sendline("exit")
    child.sendline("logout")
    child.expect("(y/n)")
    child.send("n")

if __name__=="__main__":
    configSwitchPort("0/1", "no shutdown")