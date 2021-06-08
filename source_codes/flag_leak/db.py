import sqlite3

def create_table():
    db = sqlite3.connect("./sql.db")
    cursor = db.cursor()
    #try:
    cursor.execute("create Table user (id integer primary key ,username text, email text, password text)")
    cursor.execute("create table channel(id integer primary key, name text)")
    cursor.execute("create table channel_members(id integer primary key, channel_id integer, user_id integer)")
    cursor.execute("create table message(id integer primary key, channel_id,user_id integer, message text, date text)")
    db.commit()
    '''except:
        print('Error')
        pass'''
    return None


create_table()