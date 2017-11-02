#!/usr/bin/env python

# -*- coding: utf-8 -*-
#"""
#Flask code adapted from: https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
#Created on Sat Sep  2 16:37:23 2017
#
#@author: Bas Janssen
#"""

from flask import Flask, render_template, request, redirect, session, Markup
from werkzeug.security import check_password_hash
import sqlite3
from configSwitch import configSwitchPort
from configAP import deauthMAC, updateMACList, restartWiFi
import schedule
import time


app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

@app.route('/')
def amin():
    if session.get('user'):
        return redirect('/controlIndex')
    else:    
        return render_template('index.html')

@app.route('/showAddUser')
def showAddUser():
    if session.get('user'):
        return render_template('adduser.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/addUser', methods=['POST'])
def addUser():
    if session.get('user'):
        try:
            _name = request.form['inputUser']
        except Exception as e:
            return render_template('error.html', error = str(e))
        try:
            conn.cursor().execute("insert into Users (NAME, STATE) values ('{name}', 1);".format(name=_name))
            conn.commit()
        except sqlite3.Error as e:
            return render_template('error.html', error = str(e.args[0]))
        return redirect('/controlIndex')
    else:
        return render_template('error.html',error = 'Unauthorized Access')
        

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    _user = 'Bas'
    try:
        _password = request.form['inputPassword']
    except Exception as e:
        return render_template('error.html', error = str(e))
    
    try:
        _pw_hashes = conn.execute("select PASSWORDHASH from Admins where NAME='{_user}';".format(_user = _user))
        for _pw_hash in _pw_hashes:
            pw_hash = _pw_hash[0]
    except sqlite3.Error as e:
        return render_template('error.html', error = str(e.args[0]))
    if check_password_hash(pw_hash, _password):
        session['user'] = "Bas"
        return redirect('/controlIndex')
    else:
        return render_template('error.html',error = 'Invalid password.')

@app.route('/controlIndex')
def controlIndex():
    if session.get('user'):
        try:
            _users = conn.execute('''select NAME, STATE from Users;''')
        except sqlite3.Error as e:
            return render_template('error.html', error = str(e.args[0]))
        _overview = "<table class='table table-hover'><tr><th>User</th><th>State</th><th>Remove</th></tr>"
        for row in _users:
            _enabled = ""
            if row[1] > 0:
                _enabled = "checked"
            _overview = _overview + "<tr><td data-toggle='collapse' data-target='#{_user}' class='clickable'>{_user}</td><td><input type='checkbox' name='chkbx_{_user}' value='chkbx_{_user}' {_enabled}></td><td><form action='/removeUser' method='post'><input type='hidden' name='user' value='{_user}'><button id='btnRemove' class='btn btn-primary btn-block' type='submit'><i class='material-icons'>clear</i></button></form></td></tr><tr><td colspan='3'><table id='{_user}' class='collapse'><tr><th>Port/MAC</th><th>Description</th><th>State</th><th>Remove</th></tr>".format(_user = row[0], _enabled = _enabled) #table table-hover 
            try:            
                _Ports = conn.execute("select Users.NAME as User, Ports.NAME as Port, Ports.DESIGNATION, Ports.STATE from Users left join Ports on Users.ID=Ports.USER where Users.NAME='{_user}';".format(_user = row[0]))
            except sqlite3.Error as e:
                return render_template('error.html', error = str(e.args[0]))
            for port in _Ports:
                if port[1] is None:
                    _overview = _overview
                else:
                    if port[3] == 0:
                        _icon = "down"
                    else:
                        _icon = "up"
                    _overview = _overview + "<tr><td>{_port}</td><td>{_portName}</td><td><img src='/static/ethernet_link_{_icon}.svg'></td><td><form action='/removePort' method='post'><input type='hidden' name='port' value='{_port}'><button id='btnRemove' class='btn btn-primary btn-block' type='submit'><i class='material-icons' aria-hidden='true'>clear</i></button></form></td></tr>".format(_port = str(port[1]), _portName = port[2], _icon = _icon)
            try:
                _MACS = conn.execute("select Users.Name as User, MAC.ADDRESS as MAC, MAC.NAME, MAC.STATE from Users  left join MAC on Users.ID=MAC.USER where Users.NAME='{_user}';".format(_user = row[0]))
            except sqlite3.Error as e:
                return render_template('error.html', error = str(e.args[0]))
            for mac in _MACS:
                if mac[1] is None:
                    _overview = _overview
                else:
                    if mac[3] == 0:
                        _icon = "signal_wifi_off"
                    elif mac[3] == 1:
                        _icon = "signal_wifi_4_bar"
                    elif mac[3] == 2:
                        _icon = "signal_wifi_4_bar_lock"
                    _overview = _overview + "<tr><td>{_MAC}</td><td>{_MACName}</td><td><i class='material-icons'>{_icon}</i></td><td><form action='/removeMAC' method='post'><input type='hidden' name='mac' value='{_MAC}'><button id='btnRemove' class='btn btn-primary btn-block' type='submit'><i class='material-icons' aria-hidden='true'>clear</i></button></form></td></tr>".format(_MAC = str(mac[1]), _MACName = mac[2], _icon = _icon)
            _overview = _overview + "</table></td></tr>"
        _overview = _overview + "</table>"
        return render_template('controlIndex.html', overview = Markup(_overview))
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/showAddPort')
def showAddPort():
    if session.get('user'):
        return render_template('addport.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/addPort', methods=['POST'])
def addPort():
    if session.get('user'):
        try:
            _user = request.form['inputUser']
            _port = request.form['inputPort']
            _portDesignation = request.form['inputPortDesignation']
        except Exception as e:
            return render_template('error.html', error = str(e))
        try:
            conn.cursor().execute("insert into Ports (NAME, DESIGNATION, STATE, USER) values ('{port}', '{portDesignation}', 1, (select ID from Users where NAME='{user}'));".format(user=_user, port=_port, portDesignation=_portDesignation))
            conn.commit()
        except sqlite3.Error as e:
            return render_template('error.html', error = str(e.args[0]))
        return redirect('/controlIndex')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/showAddMAC')
def showAddMAC():
    if session.get('user'):
        return render_template('addmac.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/addMAC', methods=['POST'])
def addMAC():
    if session.get('user'):
        try:
            _user = request.form['inputUser']
            _MAC = request.form['inputMAC']
            _MACDesignation = request.form['inputMACDesignation']
        except Exception as e:
            return render_template('error.html', error = str(e))
        try:
            conn.cursor().execute("insert into MAC (NAME, ADDRESS, STATE, USER) values ('{_MACDesignation}', '{_MAC}', 1, (select ID from Users where NAME='{user}'));".format(user=_user, _MAC=_MAC, _MACDesignation=_MACDesignation))
            conn.commit()
        except sqlite3.Error as e:
            return render_template('error.html', error = str(e.args[0]))
        return redirect('/controlIndex')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/removeUser', methods=['POST'])
def removeUser():
    if session.get('user'):
        try:
            _user = request.form['user']
        except Exception as e:
            return render_template('error.html', error = str(e))
        try:
            conn.cursor().execute("delete from Users where NAME='{_name}';".format(_name = _user))
        except sqlite3.Error as e:
            return render_template('error.html', error = str(e))
        return redirect('/')
    else:
        return render_template('error.html', error = 'Unauthorized Access')

@app.route('/removePort', methods=['POST'])
def removePort():
    if session.get('user'):
        try:
            _port = request.form['port']
        except Exception as e:
            return render_template('error.html', error = str(e))
        try:
            conn.cursor().execute("delete from Ports where NAME='{_port}';".format(_port = _port))
        except sqlite3.Error as e:
            return render_template('error.html', error = str(e))
        return redirect('/')
    else:
        return render_template('error.html', error = 'Unauthorized Access')

@app.route('/removeMAC', methods=['POST'])
def removeMAC():
    if session.get('user'):
        try:
            _mac = request.form['mac']
        except Exception as e:
            return render_template('error.html', error = str(e))
        try:
            conn.cursor().execute("delete from MAC where ADDRESS='{_mac}';".format(_mac = _mac))
        except sqlite3.Error as e:
            return render_template('error.html', error = str(e))
        return redirect('/')
    else:
        return render_template('error.html', error = 'Unauthorized Access')

@app.route('/changeState', methods=['POST'])
def changeState():
    try:
        chkbx,_user = request.form['user'].split('_')
        _enabled = request.form['enabled']
    except Exception as e:
            return str(e)
    try:
        _ports = conn.cursor().execute("select Users.Name as User, Ports.NAME as Port, Ports.DESIGNATION from Users left join Ports on Users.ID=Ports.USER where Users.NAME='{_user}';".format(_user = _user))
    except sqlite3.Error as e:
            return str(e)
    for port in _ports:
        if port[1] is None:
            print "No ports for user."
        else:
            if int(_enabled) == 0:
                print "Shutting port down for user."
                result = configSwitchPort(port[1], "shutdown")
                if result != "success":
                    return result
                try:
                    conn.cursor().execute("update ports set STATE={_enabled} where NAME='{_name}';".format(_enabled = int(_enabled), _name = port[1]))
                except sqlite3.Error as e:
                    return str(e)
            else:
                print "Enabeling port for user."
                result = configSwitchPort(port[1], "no shutdown")
                if result != "success":
                    return result
                try:
                    conn.cursor().execute("update ports set STATE={_enabled} where NAME='{_name}';".format(_enabled = int(_enabled), _name = port[1]))
                except sqlite3.Error as e:
                    return str(e)
    try:
        _MACS = conn.cursor().execute("select Users.Name as User, MAC.ADDRESS as MAC, MAC.NAME from Users  left join MAC on Users.ID=MAC.USER where Users.NAME='{_user}';".format(_user = _user))
    except sqlite3.Error as e:
            return str(e)
    for MAC in _MACS:
        if MAC[1] is None:
            print "No MACs for user."
        else:
            if int(_enabled) == 0:
                #Currently just deauth the device for 10 seconds
                result = deauthMAC(MAC[1], "10000")
                if result != "success":
                        return result
                try:
                    conn.cursor().execute("update MAC set STATE={_enabled} where ADDRESS='{_MAC}';".format(_enabled = 2, _MAC = MAC[1]))
                    conn.commit()
                except sqlite3.Error as e:
                    return str(e)
            else:
                try:
                    conn.cursor().execute("update MAC set STATE={_enabled} where ADDRESS='{_MAC}';".format(_enabled = 1, _MAC = MAC[1]))
                    conn.commit()
                except sqlite3.Error as e:
                    return str(e)
    result = updateMACList()
    if result != "success":
        return result
    try:
        conn.cursor().execute("update Users set STATE={_enabled} where NAME='{_user}';".format(_enabled = int(_enabled), _user = _user))
        conn.commit()
    except sqlite3.Error as e:
        return str(e)
    
    return "OK"

if __name__=="__main__":
    conn = sqlite3.connect('netwerkcontrol.db')
    conn.execute('''PRAGMA foreign_keys = ON;''')
    conn.execute('''create table if not exists Admins(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, NAME TEXT NOT NULL, PASSWORDHASH TEXT NOT NULL);''') #The password must be hashed, plaintext can not be used.
    conn.execute('''create table if not exists Users(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, NAME TEXT NOT NULL, STATE INT);''')
    conn.execute('''create table if not exists Ports(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, NAME TEXT NOT NULL, DESIGNATION TEXT NOT NULL, USER INT NOT NULL, STATE INT, FOREIGN KEY(USER) REFERENCES Users(ID));''')
    conn.execute('''create table if not exists MAC(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, NAME TEXT NOT NULL, ADDRESS TEXT NOT NULL, USER UNT NOT NULL, STATE INT, FOREIGN KEY (USER) REFERENCES Users(ID));''')
    app.run(host='0.0.0.0', port=8000)
    schedule.every().day.at("03:30").do(restartWiFi)
    
    while True:
        schedule.run_pending()
        time.sleep(1)