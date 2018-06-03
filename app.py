#! /usr/bin/python3.5
# -*- coding:utf-8 -*-

########## Importation ##########

from flask import Flask, render_template, url_for, redirect, request, g, session
import mysql.connector 
from passlib.hash import argon2 
import atexit 
import requests 
import datetime

now = datetime.datetime.now()

######### Def ##########

app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('secret_config')

def connect_db():
    g.mysql_connection = mysql.connector.connect(
        host = app.config['DATABASE_HOST'],
        user = app.config['DATABASE_USER'],
        password = app.config['DATABASE_PASSWORD'],
        database = app.config['DATABASE_NAME']
    ) 
    g.mysql_cursor = g.mysql_connection.cursor()
    return g.mysql_cursor

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db 

def commit():
    g.mysql_connection.commit()

def all_user():
    with app.app_context():
        db = get_db()
        db.execute('SELECT id, email, name, lastname, rfid, password, date, is_admin FROM user')
        user = db.fetchall()
        f = '%Y-%m-%d %H:%M:%S'
        for users in user:
            id = users[0]
            email = users[1]
            name = users[2]
            lastname = users[3]
            rfid = users[4]
            password = users[5]
            date = users[6]
            admin = users[7]
            date = now.strftime(f)
        commit()

########## Routes ##########

@app.route('/')
def index():
    return redirect(url_for('/login/'))

@app.route('/admin/porte/<int:id>', methods=['GET', 'POST'])
def porte():
    db = get_db()
    if request.method == 'POST':
        db.execute('Select id FROM user WHERE id = %(id)s', {'id': rfid})
        commit()
        return render_template('admin.html', user=session['user'])

    else:
        db.execute('SELECT id FROM user WHERE id = %(id)s', {'id': id})
        user = db.fetchone()
        return render_template('porte.html', user=session['user'])

@app.route('/admin/ouverture/')
def ouverture():
    return render_template('ouverture.html')
@app.route('/login/', methods=['GET', 'POST'])
def login():
    email = str(request.form.get('email'))
    password = str(request.form.get('password'))

    db = get_db()
    db.execute('SELECT id, email, password, is_admin FROM user WHERE email = %(email)s', {'email': email})
    users = db.fetchall()

    valid_user = False
    for user in users:
        if argon2.verify(password, user[2]):
            valid_user = user

    if valid_user:
        session['user'] = valid_user
        return redirect(url_for('admin'))

    return render_template('login.html')

@app.route('/admin/')
def admin():

    db = get_db()
    db.execute('SELECT id, email, name, lastname, date FROM user')
    user = db.fetchall()

    if not session.get('user') or not session.get('user')[2]:
        return redirect(url_for('login'))
    return render_template('admin.html', user=session['user'], users=user)

@app.route('/admin/add', methods=['GET', 'POST'])
def admin_add():
    if not session.get('user') or not session.get('user')[2]:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        db = get_db()
        email = str(request.form.get('email'))
        name = str(request.form.get('name'))
        lastname = str(request.form.get('lastname'))
        rfid = str(request.form.get('rfid'))
        password = str(request.form.get('password'))
        date = str(request.form.get('date'))
        admin = str(request.form.get('admin'))
        db.execute('INSERT INTO user (email, name, lastname, rfid, password, date, is_admin) VALUES (%(email)s, %(name)s, %(lastname)s, %(rfid)s, %(password)s, %(date)s, %(admin)s)', {'email': email, 'name': name, 'lastname': lastname, 'rfid': rfid, 'password': password, 'date': date, 'admin': admin})
        commit()
        return redirect(url_for('admin'))

    return render_template('admin_add.html')

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit(id):
    if not session.get('user') or not session.get('user')[2]:
        return redirect(url_for('login'))
    db = get_db()

    if request.method == 'POST':
        
        email = str(request.form.get('email'))
        name = str(request.form.get('name'))
        lastname = str(request.form.get('lastname'))
        rfid = str(request.form.get('rfid'))
        date = str(request.form.get('date'))
        admin = str(request.form.get('admin'))
        db.execute('UPDATE user SET email = %(email)s, name = %(name)s, lastname = %(lastname)s, rfid = %(rfid)s, date = %(date)s, is_admin = %(admin)s WHERE id = %(id)s', {'id': id,'email': email, 'name': name, 'lastname': lastname, 'rfid': rfid, 'date': date, 'admin': admin})
        commit()
        return render_template('admin.html', user=session['user'])

    else:
        db.execute('SELECT id, email, name, lastname, rfid, password, date, is_admin FROM user WHERE id = %(id)s', {'id': id})
        user = db.fetchone()
        return render_template('admin_edit.html', user=session['user'], users=user)

@app.route('/admin/delete/<int:id>', methods=['GET', 'POST'])
def admin_delete(id):
    if not session.get('user') or not session.get('user')[2]:
        return redirect(url_for('login'))
    db = get_db()

    if request.method == 'POST':
        db.execute('DELETE FROM user WHERE id = %(id)s', {'id': id})
        commit()
        return redirect(url_for('admin'))

    else:
        db.execute('SELECT id, email, name, lastname, rfid, password, date FROM user WHERE id = %(id)s', {'id': id})
        user = db.fetchone()
        return render_template('admin_del.html', user=session['user'], users=user)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('login'))

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
