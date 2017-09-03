# -*- coding: utf-8 -*-
"""
https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
Created on Sat Sep  2 16:37:23 2017

@author: bas
"""

from flask import Flask, render_template, request, redirect, session, Markup
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

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
        _name = request.form['inputUser']
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
        _users = conn.execute('''select NAME, STATE from Users;''')
        _overview = "<table class='table table-hover'><tr><th>User</th><th>State</th><th>Remove</th></tr>"
        for row in _users:
            _enabled = ""
            if row[1] > 0:
                _enabled = "checked"
            _overview = _overview + "<tr data-toggle='collapse' data-target='#{_user}' class='clickable'><td>{_user}</td><td><input type='checkbox' name='chkbx_{_user}' value='chkbx_{_user}' {_enabled}></td><td><i class='fa fa-times' aria-hidden='true'></i></span></td></tr><tr><td colspan='3'><table id='{_user}' class='table table-hover collapse'><tr><th>Port/MAC</th><th>Description</th></tr>".format(_user = row[0], _enabled = _enabled)
            _Ports = conn.execute("select Users.NAME as User, Ports.NAME as Port, Ports.DESIGNATION from Users left join Ports on Users.ID=Ports.USER where Users.NAME='{_user}';".format(_user = row[0]))
            for port in _Ports:
                _overview = _overview + "<tr><td>{_port}</td><td>{_portName}</td></tr>".format(_port = str(port[1]), _portName = port[2])
            _MACS = conn.execute("select Users.Name as User, MAC.ADDRESS as MAC, MAC.NAME from Users  left join MAC on Users.ID=MAC.USER where Users.NAME='{_user}';".format(_user = row[0]))
            for mac in _MACS:
                _overview = _overview + "<tr><td>{_MAC}</td><td>{_MACName}</td></tr>".format(_MAC = str(mac[1]), _MACName = mac[2])
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
        #Wrap with try catch
        _user = request.form['inputUser']
        _port = request.form['inputPort']
        _portDesignation = request.form['inputPortDesignation']
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
        #Wrap with try catch
        _user = request.form['inputUser']
        _MAC = request.form['inputMAC']
        _MACDesignation = request.form['inputMACDesignation']
        try:
            conn.cursor().execute("insert into MAC (NAME, ADDRESS, STATE, USER) values ('{_MACDesignation}', '{_MAC}', 1, (select ID from Users where NAME='{user}'));".format(user=_user, _MAC=_MAC, _MACDesignation=_MACDesignation))
            conn.commit()
        except sqlite3.Error as e:
            return render_template('error.html', error = str(e.args[0]))
        return redirect('/controlIndex')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/changeState', methods=['POST'])
def changeState():
    #Wrap with try catch
    chkbx,_user = request.form['user'].split('_')
    _enabled = request.form['enabled']
    conn.cursor().execute("update Users set STATE={_enabled} where NAME='{_user}';".format(_enabled = int(_enabled), _user = _user))
    conn.commit()
    #To be added: call the function to update switch and ap configuration.
    return "OK"

if __name__=="__main__":
    conn = sqlite3.connect('netwerkcontrol.db')
    conn.execute('''PRAGMA foreign_keys = ON;''')
    conn.execute('''create table if not exists Admins(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, NAME TEXT NOT NULL, PASSWORDHASH TEXT NOT NULL);''') #The password must be hashed, plaintext can not be used.
    conn.execute('''create table if not exists Users(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, NAME TEXT NOT NULL, STATE INT);''')
    conn.execute('''create table if not exists Ports(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, NAME TEXT NOT NULL, DESIGNATION TEXT NOT NULL, USER INT NOT NULL, STATE INT, FOREIGN KEY(USER) REFERENCES Users(ID));''')
    conn.execute('''create table if not exists MAC(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, NAME TEXT NOT NULL, ADDRESS TEXT NOT NULL, USER UNT NOT NULL, STATE INT, FOREIGN KEY (USER) REFERENCES Users(ID));''')
    app.run(host='0.0.0.0', port=8000)