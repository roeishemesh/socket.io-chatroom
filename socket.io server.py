import datetime

import eventlet
import socketio
from bidict import *

from data_base import *

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})


@sio.event
def connect(sid, environ):
    print('connect to sid number', sid)


@sio.event
def disconnect(sid):
    query = Users.update(is_online=False).where(
        Users.sid == sid)
    query.execute()
    print('disconnect ', sid)


@sio.on('send user name and password')
def check(sid, data):
    username = data.get("username")
    password = data.get("password")
    user = Users.select().where(Users.username == username, Users.password == password)
    if user.exists():
        query = Users.update(is_online=True, sid=sid, last_login=datetime.datetime.now()).where(
            Users.username == username)
        query.execute()
        return 'connected'
    else:
        return 'wrong login'


@sio.on('send message to chatroom')
def send_message_to(sid, data):
    session = sio.get_session(sid)
    sio.emit('message from client', {"sender": session['username'], "message": data[0]}, room=data[1])
    print(sio.rooms(data[1]))


@sio.on('enter to chatroom')
def enter_room(sid, data):
    sio.emit('admin message', {"username": Users.get(Users.sid == sid).username, "activity": "active_chat"},
             room=data)
    username = Users.get(Users.sid == sid).username
    sio.save_session(sid, {'username': username})
    sio.enter_room(sid, data)


@sio.on("leave room")
def leave_room(sid, data):
    sio.leave_room(sid, room=data)
    sio.emit('admin message', {"username": Users.get(Users.sid == sid).username, "activity": "leave_chat"},
             room=data)


@sio.event
def send_rooms(sid):
    sid_list = [user.sid for user in Users.select().where(Users.is_online == 1)]
    rooms_sid_dict = {}
    rooms_dict = {}
    for key in list(sio.manager.rooms.get("/").keys()):
        if key not in sid_list and key is not None:
            rooms_sid_dict[key] = sio.manager.rooms.get("/").get(key)
            for x in list(rooms_sid_dict.keys()):
                rooms_dict[x] = list(
                    map(lambda a: str(sio.get_session(a).get('username')), (list(bidict.keys(rooms_sid_dict[x])))))
    print(sio.manager.rooms.get("/"))
    print(rooms_sid_dict)
    return rooms_dict


eventlet.wsgi.server(eventlet.listen(('localhost', 5000)), app)

