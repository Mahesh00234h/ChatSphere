from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from pymongo import MongoClient
from bson import ObjectId
import bcrypt
import cloudinary
import cloudinary.uploader
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
socketio = SocketIO(app, manage_session=False)
rooms = defaultdict(set)


client = MongoClient("YOUR MONGODB CONNECTION STRING")
db = client.chatapp
users = db.users
messages = db.messages


cloudinary.config(
    cloud_name="YOUR CLOUD NAME",
    api_key="YOUR API KEY",
    api_secret="YOUR API SECRET",
    secure=True
)

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        existing_user = users.find_one({"username": request.form["username"]})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt())
            profile_pic_url = ""
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                upload_result = cloudinary.uploader.upload(file)
                profile_pic_url = upload_result['secure_url']
            users.insert_one({
                "username": request.form["username"],
                "password": hashpass,
                "insta_ID": request.form["insta-ID"],
                "profile_pic": profile_pic_url
                
            })
            session["username"] = request.form["username"]
            return redirect(url_for("chat"))
        return render_template('Username_Already_Exists.html'), 400
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        login_user = users.find_one({"username": request.form["username"]})
        if login_user:
            if bcrypt.checkpw(request.form["password"].encode("utf-8"), login_user["password"]):
                session["username"] = request.form["username"]
                return redirect(url_for("chat"))
        return render_template('401.html'), 401
    return render_template("login.html")


@app.route("/chat")
def chat():
    if "username" in session:
        user_data = users.find_one({"username": session["username"]})
        profile_pic_url = user_data.get('profile_pic', None)
        all_messages = messages.find()
        return render_template("chat.html", username=session["username"], messages=all_messages, profile_pic_url=profile_pic_url)
    return redirect(url_for("login"))

@app.route('/profile')
@app.route('/profile/<username>')
def profile(username=None):
    if username is None:
        if "username" not in session:
            return redirect(url_for('login'))
        username = session["username"]
    
    user = users.find_one({"username": username})
    
    if not user:
        return "User not found", 404

    user_details = {
        'profile_pic_url': user.get('profile_pic', ''),
        'username': user['username'],
        'insta_ID': user.get('insta-ID', 'N/A'),  
        'join_date': user['_id'].generation_time.strftime('%Y-%m-%d')
    }

    return render_template('profile.html', **user_details)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/search')
def search():
    if "username" not in session:
        return redirect(url_for('login'))

    query = request.args.get('query')
    search_results = users.find({"username": {"$regex": query, "$options": "i"}})
    
    results = []
    for user in search_results:
        results.append({"username": user["username"]})

    return render_template('profile.html', search_results=results, username=session["username"], email=session.get("email"), profile_pic_url=session.get("profile_pic_url"))

@app.route('/create_room', methods=['POST'])
def create_room():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    target_username = data.get("username")
    if not target_username:
        return jsonify({"error": "Username not provided"}), 400

    current_user = session["username"]
    room_name = f"special_room_{current_user}_{target_username}"
    rooms[room_name] = {
        "admin": current_user,
        "members": {current_user, target_username}
    }

    return jsonify({"message": f"Special room created with {target_username}"}), 200

@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    current_user = session["username"]
    if current_user == username:
        return jsonify({"error": "You cannot follow yourself"}), 400

    users.update_one({"username": current_user}, {"$addToSet": {"following": username}})
    return jsonify({"message": f"Followed {username}"}), 200

@app.route("/logout")
def logout():
    username = session.pop("username", None)
    if username:
        for room, users_set in rooms.items():
            if username in users_set:
                users_set.remove(username)
                emit('leave_room_announcement', {'username': username, 'online_users': list(users_set)}, room=room, broadcast=True)
        print(f'User {username} logged out')
    return redirect(url_for("home"))

@socketio.on('join_room')
def handle_join_room_event(data):
    join_room(data['room'])
    rooms[data['room']].add(data['username'])
    emit('join_room_announcement', {'username': data['username'], 'online_users': list(rooms[data['room']])}, room=data['room'], broadcast=True)

@socketio.on('leave_room')
def handle_leave_room_event(data):
    leave_room(data['room'])
    if data['username'] in rooms[data['room']]:
        rooms[data['room']].remove(data['username'])
    emit('leave_room_announcement', {'username': data['username'], 'online_users': list(rooms[data['room']])}, room=data['room'], broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username:
        for room, users_set in rooms.items():
            if username in users_set:
                users_set.remove(username)
                emit('leave_room_announcement', {'username': username, 'online_users': list(users_set)}, room=room, broadcast=True)
        print(f'User {username} disconnected')

@socketio.on('send_message')
def handle_send_message_event(data):
    username = data['username']
    message = data['message']
    room = data['room']
    image_url = data.get('image_url')
    reply_to = data.get('reply_to')

    message_data = {
        'username': username,
        'message': message,
        'room': room,
        'image_url': image_url,
        'reply_to': reply_to
    }
    
    if reply_to:
        reply_to_message = messages.find_one({'_id': ObjectId(reply_to)})
        if reply_to_message:
            message_data['reply_to'] = {
                'username': reply_to_message['username'],
                'message': reply_to_message['message']
            }

    message_id = messages.insert_one(message_data).inserted_id

    message_data['_id'] = str(message_id)
    emit('receive_message', message_data, room=room)

@socketio.on('clear_chat')
def handle_clear_chat_event(data):
    messages.delete_many({"room": data['room']})
    emit('clear_chat', room=data['room'], broadcast=True)

@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400

@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

@app.errorhandler(503)
def service_unavailable(error):
    return render_template('503.html'), 503




if __name__ == "__main__":
    socketio.run(app, debug=True)
