import psycopg2
import select
import json
from flask import Flask
from flask_socketio import SocketIO, emit

# Initialize Flask + SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Connect to your Postgres database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="password",
    host="localhost",
    port="5433"
)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Listen to the notifications_channel
cur.execute("LISTEN notifications_channel;")
print("Listening on channel 'notifications_channel'...")

# Background task: Listen to new notifications and send
def listen_to_notifications():
    while True:
        if select.select([conn], [], [], 5) == ([], [], []):
            continue  # Timeout
        else:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                payload = notify.payload

                try:
                    notification_data = json.loads(payload)
                    print("Backend Recieved data =============================")
                    print(notification_data)
                    
                    # Send to all connected clients
                    socketio.emit('notification', notification_data)
                except json.JSONDecodeError:
                    print("Invalid JSON:", payload)

# Send initial table data when a client connects
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
    # Fetch all existing notifications
    cur.execute("SELECT * FROM notifications ORDER BY created_at DESC;")
    rows = cur.fetchall()

    # Get column names
    colnames = [desc[0] for desc in cur.description]

    # Convert rows to list of dictionaries
    notifications = [dict(zip(colnames, row)) for row in rows]

    # Send the initial data
    emit('initial_notifications', notifications)

if __name__ == '__main__':
    socketio.start_background_task(listen_to_notifications)
    socketio.run(app, host='0.0.0.0', port=5000)
===================================================================================================================================================================================

CREATE OR REPLACE FUNCTION notify_changes() 
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    IF TG_OP = 'INSERT' THEN
        payload := json_build_object(
            'action', 'insert',
            'data', row_to_json(NEW)
        );
    ELSIF TG_OP = 'UPDATE' THEN
        payload := json_build_object(
            'action', 'update',
            'data', row_to_json(NEW)
        );
    ELSIF TG_OP = 'DELETE' THEN
        payload := json_build_object(
            'action', 'delete',
            'data', row_to_json(OLD)
        );
    END IF;

    PERFORM pg_notify('notifications_channel', payload::text);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER notifications_changes_trigger
AFTER INSERT OR UPDATE OR DELETE
ON notifications
FOR EACH ROW
EXECUTE FUNCTION notify_changes();

UPDATE notifications
SET read = TRUE
WHERE id = 1;

INSERT INTO notifications (title, message, priority)
VALUES ('New Feature!', 'Check out our new feature.', 'high');
=================================================================================================================================================================================

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-time Notifications</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        #notifications {
            margin-top: 20px;
        }
        .notification {
            border: 1px solid #ddd;
            padding: 10px;
            margin: 5px 0;
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>

<h2>Notifications</h2>
<div id="notifications"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
<script>
    // Establish a connection to the WebSocket server
    const socket = io('http://localhost:5000'); // Replace with your server's URL

    // When the client connects to the server, this event will be triggered
    socket.on('connect', () => {
        console.log('Connected to WebSocket server');
    });

    // When the backend sends initial notifications data (upon client connection)
    socket.on('initial_notifications', (notifications) => {
        console.log('Received initial notifications:', notifications);
        displayNotifications(notifications);
    });

    // When the backend sends a new notification (after INSERT, UPDATE, DELETE on the table)
    socket.on('notification', (notification) => {
        console.log('New notification:', notification);
        displayNotification(notification);
    });

    // Function to display a single notification on the page
    function displayNotification(notification) {
        const notificationsDiv = document.getElementById('notifications');
        const notificationDiv = document.createElement('div');
        notificationDiv.classList.add('notification');
        notificationDiv.textContent = JSON.stringify(notification);  // Just for example, you can format it as needed
        notificationsDiv.appendChild(notificationDiv);
    }

    // Function to display multiple notifications
    function displayNotifications(notifications) {
        notifications.forEach(notification => {
            displayNotification(notification);
        });
    }
</script>

</body>
</html>
