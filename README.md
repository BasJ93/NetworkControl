# NetworkControl

A simple Python Flask webapp to control the network infrastructure for my student home.

This app allows me to control the port state on my Netgear GS724Tv3 switch, and the maclist on the Access Points runnen LEDE.
The switch is controlled over the hidden telnet service running on port 60000. (https://www.simweb.ch/blog/2014/02/hidden-cli-interface-on-netgear-gs110tp/)

The APs are controlled over SSH, and use UCI to configure the maclist. The APs are also commanded to deauth the devices for 24h, using a dbus command.

The app is build using Python 2.7, Flask, sqlite3, bootstrap, jquery and material icons.
