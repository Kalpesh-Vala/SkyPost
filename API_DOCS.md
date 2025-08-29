# SkyPost API Documentation

## Authentication Endpoints

### Register User
- **POST** `/auth/register`
- **Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- **Response**: User object with JWT token

### Login
- **POST** `/auth/login`
- **Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: User object with JWT token

### Get Profile
- **GET** `/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Current user profile

### Update Profile
- **PUT** `/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: 
  ```json
  {
    "first_name": "Updated Name",
    "bio": "My bio"
  }
  ```

### Change Password
- **POST** `/auth/change-password`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: 
  ```json
  {
    "current_password": "oldpass",
    "new_password": "newpass123"
  }
  ```

## Mail Endpoints

### Send Message
- **POST** `/mail/send`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: 
  ```json
  {
    "to_email": "recipient@example.com",
    "subject": "Hello",
    "body": "Message content"
  }
  ```
- **File Upload**: Support multipart/form-data for attachments

### Get Inbox
- **GET** `/mail/inbox?page=1&per_page=20&search=keyword`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Paginated list of received messages

### Get Outbox
- **GET** `/mail/outbox?page=1&per_page=20&search=keyword`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Paginated list of sent messages

### Get Message
- **GET** `/mail/message/{id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Full message details with attachments

### Message Statistics
- **GET** `/mail/stats`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: 
  ```json
  {
    "inbox_count": 25,
    "outbox_count": 10,
    "unread_count": 5,
    "total_messages": 35
  }
  ```

### Mark as Read
- **PUT** `/mail/message/{id}/read`
- **Headers**: `Authorization: Bearer <token>`

### Delete Message
- **DELETE** `/mail/message/{id}`
- **Headers**: `Authorization: Bearer <token>`

### Download Attachment
- **GET** `/mail/attachment/{id}/download`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: File download

## WebSocket Endpoints

### Real-time Notifications
- **WS** `/ws/notifications?token=<jwt_token>`
- **Authentication**: Via query parameter or initial message
- **Messages**: 
  - Connection: `{"type": "connection_established"}`
  - New message: `{"type": "new_message", "data": {...}}`
  - Ping/Pong: `{"type": "ping"}` / `{"type": "pong"}`

### Connection Stats
- **GET** `/ws/connections`
- **Response**: WebSocket connection statistics

## Example Usage

### 1. Register and Login
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 2. Send Message
```bash
curl -X POST http://localhost:8000/mail/send \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"to_email":"recipient@example.com","subject":"Hello","body":"Test message"}'
```

### 3. Get Inbox
```bash
curl -X GET http://localhost:8000/mail/inbox \
  -H "Authorization: Bearer <your_token>"
```

### 4. WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications?token=<your_token>');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Notification:', data);
};
```

## Error Responses

All endpoints return standardized error responses:
```json
{
  "success": false,
  "message": "Error description",
  "error_code": "OPTIONAL_ERROR_CODE"
}
```

## Success Responses

All endpoints return standardized success responses:
```json
{
  "success": true,
  "message": "Success message",
  "data": { ... }
}
```

For paginated responses:
```json
{
  "success": true,
  "message": "Success message",
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```
