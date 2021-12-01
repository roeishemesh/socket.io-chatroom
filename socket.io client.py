import socketio

sio = socketio.Client()


@sio.event()
def connect():
    print("connected to the server")


@sio.event
def disconnect():
    print('disconnected from server')


@sio.on('admin message')
def print_admin_message(admin_dict):
    if admin_dict.get("activity") == "leave_chat":
        print(admin_dict.get("username") + " leave the chat")
    if admin_dict.get("activity") == "active_chat":
        print(admin_dict.get("username") + " is active to chatroom")


@sio.on('wrong login')
def print_message():
    print("your username or password are wrong\nplease try again")
    login()


@sio.on('message from client')
def print_message(msg_dict):
    print(f"{msg_dict.get('sender')}>>>{msg_dict.get('message')}")


def login():
    sio.connect('http://localhost:5000')
    username = input("please enter your username\n")
    password = input("please enter your password\n")
    sio.emit('send user name and password', {"username": username, "password": password})


def send_message(room):
    while True:
        client_msg = input("")
        if client_msg == "Q":
            sio.emit('leave room', data=room)
            break
        else:
            sio.emit('send message to chatroom', data=[client_msg, room])


@sio.on('connected')
def print_message():
    print("LOGIN OK")
    while True:
        print("""hello and welcome to the socket.io chatroom
to View existing rooms      v
to open new room            n
to disconnect               q""")
        client_answer = input("please write your choice here:\n")

        if client_answer == "v":
            rooms = sio.call("send_rooms")
            if bool(rooms) is False:
                print("there isn't open chatroom now please")
                room_name = input("please write the new chatroom name:\n")
                sio.emit('enter to chatroom', data=room_name)
                print(f"welcome to {room_name} chatroom")
                send_message(room_name)

            if bool(rooms):
                print("room name\t number of participants\t participants name's")
                [print(key, "\t\t", len(value), "\t\t\t", ",".join(value)) for key, value in rooms.items()]
                room_name = input(
                    "please write the name of the chatroom that you want to get in or write the name of new chatroom\n")
                sio.emit('enter to chatroom', data=room_name)
                print(f"welcome to {room_name} chatroom if you want to leave the chatroom please write 'Q'")
                send_message(room_name)

        if client_answer == "n":
            room_name = input("please write the new chatroom name:\n")
            sio.emit('enter to chatroom', data=room_name)
            print(f"welcome to {room_name} chatroom")
            send_message(room_name)
        if client_answer == "q":
            sio.disconnect()
            login()
            break


if __name__ == '__main__':
    login()
