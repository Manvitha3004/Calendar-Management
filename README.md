# Calendar Management App

A full-stack calendar management application with AI-powered email processing, built with React frontend and Python FastAPI backend.

## Features

- 📅 Calendar event management
- 📧 AI-powered email processing and management
- 🤖 Intelligent agent system for task automation
- 🔐 Google OAuth authentication
- 📊 Email analytics and statistics
- ⏰ Smart reminders and notifications

## Tech Stack

### Frontend
- React 18
- Tailwind CSS
- Zustand (State Management)
- React Router
- FullCalendar

### Backend
- FastAPI
- MongoDB (Motor async driver)
- Google APIs (Gmail, Calendar)
- Celery (Task Queue)
- Redis (Message Broker)

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- MongoDB (local or cloud)
- Redis (for background tasks)
- Google Cloud Project with Gmail API enabled

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Calendar-Management
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Environment Configuration

Create a `.env` file in the `backend` directory:

```env
# Database
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=calendar_management_app

# Google OAuth
GOOGLE_CREDENTIALS_PATH=credentials.json

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Optional: Redis for background tasks
REDIS_URL=redis://localhost:6379
```

#### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized JavaScript origins: `http://localhost:3000`
   - Authorized redirect URIs: `http://localhost:3000`
5. Download the credentials JSON file
6. Save it as `credentials.json` in the `backend` directory

#### Start Backend Server

```bash
cd backend
python main.py
```

The backend will run on `http://localhost:4000`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd .. # Go back to root directory
npm install
```

#### Environment Configuration

Create a `.env` file in the root directory:

```env
REACT_APP_API_BASE_URL=http://localhost:4000/api
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here
```

#### Start Frontend Development Server

```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

### 1. Authentication

1. Open `http://localhost:3000` in your browser
2. Click "Sign in with Google"
3. Authorize the application to access your Gmail and Calendar

### 2. Email Management

- **Sync Emails**: Click "Sync Emails" to fetch latest emails from Gmail
- **Generate Drafts**: Use AI to generate reply drafts for emails
- **Create Reminders**: Set reminders for important emails
- **View Analytics**: Monitor email statistics and priorities

### 3. Calendar Management

- **View Events**: Browse your calendar events
- **Create Events**: Add new calendar events
- **Meeting Prep**: Get AI-generated meeting preparation notes
- **Agenda Management**: Organize your daily agenda

## API Endpoints

### Authentication
- `GET /health` - Health check
- `POST /auth/google` - Google OAuth callback

### Events
- `GET /api/events` - List all events
- `POST /api/events` - Create new event
- `PUT /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event
- `GET /api/events/{id}/prep` - Get meeting preparation

### Email Management
- `POST /api/gmail/sync` - Sync emails from Gmail
- `GET /api/gmail/emails/list` - List stored emails
- `POST /api/gmail/emails/{id}/draft` - Generate AI draft
- `GET /api/gmail/drafts` - Get pending drafts
- `POST /api/gmail/drafts/{id}/approve` - Approve/reject draft
- `GET /api/gmail/stats` - Get email statistics

## Development

### Backend Development

```bash
cd backend
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 4000
```

### Frontend Development

```bash
# Start with hot reload
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Troubleshooting

### Common Issues

1. **Backend not connecting to MongoDB**
   - Ensure MongoDB is running
   - Check MONGO_URI in .env file
   - Verify database permissions

2. **Google OAuth not working**
   - Verify credentials.json is in backend directory
   - Check Google Cloud Console OAuth settings
   - Ensure redirect URIs match exactly

3. **Email sync failing**
   - Check Google API quotas
   - Verify Gmail API is enabled
   - Check OAuth token validity

4. **CORS errors**
   - Ensure FRONTEND_URL is set correctly in backend .env
   - Check that both servers are running on correct ports

### Logs

- Backend logs: Check console output where `python main.py` is running
- Frontend logs: Check browser developer console
- Database logs: Check MongoDB logs for connection issues

## Production Deployment

### Backend Deployment

1. Set production environment variables
2. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
3. Set up reverse proxy (nginx)
4. Configure SSL certificates

### Frontend Deployment

1. Build the production bundle:
   ```bash
   npm run build
   ```
2. Serve static files with nginx or similar
3. Update API_BASE_URL to production backend URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.
