from flask import Flask, render_template, request, session, jsonify, escape, make_response, redirect, url_for
from flask_socketio import SocketIO ,join_room, leave_room
import os
import sqlite3
from uuid import uuid4
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "mykey"
socketio = SocketIO(app,cors_allowed_origins="*")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat')
def chat():
    if 'username' in session:
        db = sqlite3.connect("./sql.db")
        cursor = db.cursor()

        query = f"select channel.id from channel inner join channel_members on channel.id=channel_members.channel_id inner join user on channel_members.user_id = user.id where user.id={session['uid']}"
        # query = f"select * from user"
        rows = cursor.execute(query)
        users=[]
        channels = rows.fetchall()
        for channel in channels:
            members = get_channel_members(channel[0])
            for member in members:
                if not member[0] == session['username']:
                    users.append(member)
        return render_template('chat.html', users= users, session=session)
    else:
        return redirect(url_for('index'))


def get_channel_members(id):
    db = sqlite3.connect("./sql.db")
    cursor = db.cursor()
    query = f"select username,channel_id from channel_members inner join user on user.id=channel_members.user_id where channel_members.channel_id = {id}"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows
@socketio.on('connect')
def connect():
    if 'username' in session:
        join_room(session['username'])
    return None


def messageRecieved(methods=['GET','POST']):
    print('message was received')

def get_user_id(username):
    db = sqlite3.connect("./sql.db")
    cursor = db.cursor()
    query = f"select id from user where username='{username}'"
    rows = cursor.execute(query)
    return rows.fetchone()[0] ;

def get_user_by_id(id):
    db = sqlite3.connect("./sql.db")
    cursor = db.cursor()
    query = f"select username from user where id='{id}'"
    rows = cursor.execute(query)
    return rows.fetchone()[0] ;

@socketio.on('send')
def handel_send(json,methods=['GET','POST']):
    db = sqlite3.connect("./sql.db")
    cursor = db.cursor()
    if 'username' in session:
        resp = {'message': json['message'], 'user': session['username']}
        socketio.emit('my response', resp, callback=messageRecieved , to=json['room'])
        query = f"insert into message(channel_id,user_id, message, date) values({json['room']},{session['uid']}, '{json['message']}', '{str(datetime.now())}') "
        print(query)
        cursor.execute(query)
        db.commit()

@app.route('/message/<string:user>')
def message(user):
    db = sqlite3.connect("./sql.db")
    cursor = db.cursor()
    query = f"select * from message  where receiver={2} and sender={get_user_id(user)}"

    cont = cursor.execute(query)
    rows = cont.fetchall()
    print(rows)
    ret = []
    for row in rows:
        ret.append({
            'message': row[3],
            'author':get_user_by_id(row[1]),
            'receiver': get_user_by_id(row[2]),
            'date': row[4],
        })
    return jsonify(ret)

# @socketio.on('my response')
# def my_response():


def get_channel_by_id(id):
    db = sqlite3.connect('./sql.db')
    cursor = db.cursor()
    query = f"select * from channel where id ='{id}'"
    rows = cursor.execute(query)
    return rows.fetchone()

def get_all_channel():
    db = sqlite3.connect('./sql.db')
    cursor = db.cursor()
    query = f"select channel_id from channel_members where user_id = {session['uid']}"
    cursor.execute(query)
    rows = cursor.fetchall()
    print(rows)
    channels = []
    for row in rows:
        channels.append(row[0])
    return channels
def channel_exists(user):
    db = sqlite3.connect('./sql.db')
    cursor = db.cursor()
    query = f"select channel.id from channel inner join channel_members on channel.id=channel_members.channel_id inner join user on channel_members.user_id = user.id where channel_members.user_id={get_user_id(user)}"
    cursor.execute(query)
    rows = cursor.fetchall()
    my_channels = get_all_channel()
    for row in rows:
        for channels in my_channels:
            if channels == row[0]:
                return True
    
    return False


@app.route('/create-channel', methods=['POST'])
def create_channel():
    user = request.form['username']
    db = sqlite3.connect('./sql.db')
    cursor = db.cursor()
    if not channel_exists(user):
        query = f"insert into channel (name) values('{str(uuid4())}')"
        cursor.execute(query)
        channel_id = cursor.lastrowid
        db.commit()
    
        add_user(user, channel_id)
    return redirect(url_for('chat'))

def add_user(user,channel_id):
    db = sqlite3.connect('./sql.db')
    cursor = db.cursor()
    if get_user_id(user):
        query = f"insert into channel_members(user_id, channel_id) values({get_user_id(user)},{channel_id})"
        cursor.execute(query)
        cursor.execute(f"insert into channel_members(user_id, channel_id) values({session['uid']},{channel_id})")
        db.commit()


@app.route('/open-channel/<string:user>')
def open_channel(user):
    if not get_channel_by_id(user):
        # create_channel(user)
        print('Channel doesnt exists')
    db = sqlite3.connect('./sql.db')
    cursor = db.cursor()
    query = f"select username, message,date from message inner join user on message.user_id=user.id where channel_id={get_channel_by_id(user)[0]}"
    cur = cursor.execute(query)
    rows = cur.fetchall()
    messages = []
    for message in rows:
        messages.append({
            "username": message[0],
            "message": message[1],
            "date": message[2]
        })
    return jsonify(messages)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    # socketio.emit('my response',{'message':session['username']+' has entered the room'}, to=room)




@app.route('/login', methods=['GET', 'POST'])
def login():
    db = sqlite3.connect("./sql.db")
    cursor = db.cursor()

    try:
        query = f"SELECT * FROM user WHERE username='{escape(request.form['username'])}' and password='{escape(request.form['password'])}'"
        rows = cursor.execute(query)
        user = rows.fetchone()
        if user:
            session['username'] = user[1]
            session['uid'] = user[0]
            res = make_response(redirect(url_for('chat')))
            return res
        else:
            return render_template("login.html", error="Wrong username or password")
    except:
            app.log_exception('Login exception')
            return render_template('login.html')
    return render_template('login.html')

def user_exists(username):
    db = sqlite3.connect('./sql.db')
    cursor = db.cursor()
    query = "select * from user where username='{}'".format(escape(request.form['username']))
    rows = cursor.execute(query)
    user = rows.fetchone()
    return True if user else False

@app.route('/register', methods=['POST', 'GET'])
def register():
    db = sqlite3.connect('./sql.db')
    cursor = db.cursor()
    

    if request.method == 'POST':
        if user_exists(request.form['username']):
            return render_template('register.html', error='Username alerady exists')
        query = "insert into user (username, email, password) values ('{}','{}', '{}')".format(escape(request.form['username']), escape(request.form['email']),escape(request.form['password']))
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('login'))
    else:
        return render_template('register.html')


if __name__ == '__main__':
    socketio.run(app, port=5893)
