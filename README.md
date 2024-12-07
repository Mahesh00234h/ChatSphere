# ChatSphere
# Flask & Socket.IO Chat Application

A real-time chat application built using Flask and Socket.IO. The application includes features like user registration, authentication, real-time messaging, profile management, and special chat rooms. The database is powered by MongoDB, and Cloudinary is used for profile picture storage.

## Features

- **User Registration and Login**: Secure authentication using bcrypt.
- **Real-Time Messaging**: Instant message delivery powered by Socket.IO.
- **User Profiles**: View and update user profiles with profile pictures.
- **Special Chat Rooms**: Private chat rooms for one-on-one conversations.
- **Message Replies**: Reply to specific messages in a conversation.
- **Chat Moderation**: Clear chat feature for administrators.
- **Error Handling**: User-friendly error pages for common HTTP errors.

## Technologies Used

- **Backend**: Flask, Flask-SocketIO
- **Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript (Jinja2 templates)
- **File Storage**: Cloudinary
- **Authentication**: bcrypt

## Prerequisites

- Python 3.8 or higher
- MongoDB instance (local or cloud)
- Cloudinary account for storing profile pictures

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mahesh00234h/ChatSphere.git
   cd flask-socketio-chat
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```env
   SECRET_KEY=your_secret_key
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

5. Run the application:
   ```bash
   flask run
   ```

6. Access the application at `http://127.0.0.1:5000`.

## Usage

1. **Register**: Create a new account with a username, password, and optional profile picture.
2. **Login**: Log in with your credentials to access the chat.
3. **Chat**: Join chat rooms, send messages, and reply to specific messages.
4. **Profile**: View and update your profile.
5. **Special Rooms**: Create private rooms for one-on-one chats.

## Project Structure

```plaintext
flask-socketio-chat/
│
├── templates/         # HTML templates
├── static/            # Static files (CSS, JavaScript, images)
├── app.py             # Main application file
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## Deployment

You can deploy this application on platforms like Heroku, AWS, or any cloud provider. Ensure that environment variables are configured appropriately in the deployment environment.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any queries or suggestions, please contact Mahesh at [your-email@example.com](mailto:your-email@example.com).

---
Happy chatting! 😊
