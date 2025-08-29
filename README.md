# SkyPost - Email Backend Microservice

A simplified Mailgun/Gmail-like backend service built with Sanic (Python) that provides email messaging capabilities with JWT authentication, WebSocket notifications, and PostgreSQL storage.

## Features

- **User Management**: Registration, login with JWT authentication
- **Email/Messaging**: Send messages with subject, body, attachments
- **Inbox/Outbox**: Fetch received and sent messages
- **Real-time Notifications**: WebSocket support for new message notifications
- **File Attachments**: Support for file uploads with metadata storage
- **Database**: PostgreSQL with async support via Gino ORM

## Quick Start

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your database and configuration details
   ```

2. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb skypost_db
   
   # Run migrations
   alembic upgrade head
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Messages
- `POST /mail/send` - Send a message
- `GET /mail/inbox` - Get inbox messages
- `GET /mail/outbox` - Get sent messages
- `GET /mail/message/{id}` - Get specific message

### WebSocket
- `WS /ws/notifications` - Real-time notifications

## Project Structure

See the organized folder structure with models, routes, services, and utilities properly separated for maintainability.

## Future Enhancements

- SMTP integration for real email delivery
- Message threading and replies
- Advanced search and filtering
- Email templates
- Bulk messaging
- Rate limiting and quotas
