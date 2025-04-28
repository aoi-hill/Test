from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import psycopg2
import select
import json
from typing import List
import uvicorn
app = FastAPI()

# Your database connection
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="password",
    host="localhost",
    port="5433"
)

conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("LISTEN notifications_channel;")
print("Listening on 'notifications_channel'...")

# Manage WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_json(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# WebSocket route
@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cur.execute("SELECT * FROM notifications ORDER BY created_at DESC;")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        notifications = [dict(zip(colnames, row)) for row in rows]

        await websocket.send_json({
            "type": "initial_notifications",
            "data": notifications
        })

        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Normal HTTP route
@app.get("/try")
async def func():
    return {"status": "Backend running ✅"}

# Background task to listen for Postgres NOTIFY
async def listen_to_notifications_task():
    while True:
        await asyncio.sleep(0.1)  # prevent tight CPU loop
        if select.select([conn], [], [], 0) == ([], [], []):
            continue
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            payload = notify.payload
            print(json.loads(payload))
            try:
                notification_data = json.loads(payload)
                await manager.send_json({
                    "type": "notification",
                    "data": notification_data
                })
            except json.JSONDecodeError:
                print("Invalid JSON received:", payload)

# Start background task at startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_to_notifications_task())
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
import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Connect to WebSocket
    const socket = io('http://localhost:8000', {
      path: '/ws/notifications',  // Important: This is your backend WebSocket path
      transports: ['websocket'],
    });

    // Handle incoming messages
    socket.on('connect', () => {
      console.log('Connected to WebSocket');
    });

    socket.on('message', (data) => {
      console.log('Received:', data);

      if (data.type === 'initial_notifications') {
        setNotifications(data.data);
      } else if (data.type === 'notification') {
        // Insert new notification at the top
        setNotifications(prev => [data.data, ...prev]);
      }
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h2>Notifications</h2>
      <ul>
        {notifications.map((notification, index) => (
          <li key={index}>
            <pre>{JSON.stringify(notification, null, 2)}</pre>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Notifications;

