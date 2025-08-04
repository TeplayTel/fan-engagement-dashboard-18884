# Fan Engagement Backend API

A FastAPI-based backend service for the Fan Engagement sports streaming application, providing REST endpoints for match data, emoji reactions, analytics, and real-time WebSocket updates.

## 🚀 Features

- **Match Data API**: Get live, upcoming, and completed matches with filtering capabilities
- **Emoji Reactions**: Submit and track user emoji reactions to matches
- **Real-time Analytics**: Global and match-specific engagement analytics
- **WebSocket Broadcasting**: Real-time updates for reactions and analytics
- **Mock Data**: Complete mock data system for development and testing
- **OpenAPI Documentation**: Comprehensive API documentation with Swagger UI

## 📋 API Endpoints

### Health Check
- `GET /` - API health check and basic information

### Matches
- `GET /matches` - Get all matches with optional filtering
- `GET /matches/{match_id}` - Get specific match details
- `GET /matches/live/current` - Get currently live matches
- `GET /matches/upcoming/next` - Get upcoming matches

### Emoji Reactions
- `POST /reactions/emoji_reaction` - Submit an emoji reaction
- `GET /reactions/emojis` - Get available emoji types
- `GET /reactions/match/{match_id}/recent` - Get recent reactions for a match

### Analytics
- `GET /analytics/global` - Get global platform analytics
- `GET /analytics/match/{match_id}` - Get analytics for specific match
- `GET /analytics/summary` - Get quick analytics summary

### WebSocket
- `WS /ws/analytics` - Real-time analytics and reaction updates
- `GET /ws/info` - WebSocket connection information

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- PostgreSQL database (configured via environment variables)

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your database and server configuration
   ```

3. **Start the Server**
   ```bash
   python run.py
   ```

4. **Verify Installation**
   ```bash
   python health_check.py
   ```

5. **Access the API**
   - API Server: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - WebSocket: ws://localhost:8000/ws/analytics

### ✅ Fixed Issues (2025-08-04)
- **WebSocket Route Error**: Fixed `TypeError: APIRouter.websocket() got an unexpected keyword argument 'operation_id'`
- **Dependency Installation**: All required dependencies are properly installed and working
- **Database Connection**: PostgreSQL connection and table creation working correctly
- **API Endpoints**: All 14 REST endpoints verified and functional

### Development Mode

The server runs in development mode by default with:
- Auto-reload on code changes
- Detailed logging
- CORS enabled for all origins

## 📊 Mock Data

The backend includes comprehensive mock data:

- **8 Premier League Teams**: Arsenal, Chelsea, Manchester United, Liverpool, etc.
- **5 Sample Matches**: Mix of live, upcoming, and completed matches
- **8 Emoji Types**: ❤️, 🔥, 👏, 👍, ⚽, 🎉, 😠, 😢
- **Analytics Data**: Simulated reaction counts and engagement metrics

## 🔌 WebSocket Usage

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analytics');

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
    
    switch(message.type) {
        case 'reaction':
            // New emoji reaction
            break;
        case 'analytics_update':
            // Updated analytics data
            break;
        case 'match_update':
            // Match status/score update
            break;
    }
};
```

## 🧪 Testing

Run the basic test suite:

```bash
python test_api.py
```

This will test:
- Mock data service functionality
- Pydantic model validation
- Basic API operations
- Data serialization

## 📁 Project Structure

```
fan_engagement_backend/
├── src/
│   ├── api/
│   │   ├── routes/          # API route definitions
│   │   │   ├── matches.py   # Match-related endpoints
│   │   │   ├── reactions.py # Emoji reaction endpoints
│   │   │   ├── analytics.py # Analytics endpoints
│   │   │   └── websocket.py # WebSocket endpoints
│   │   ├── main.py          # FastAPI application
│   │   └── generate_openapi.py # OpenAPI schema generator
│   ├── models/
│   │   └── schemas.py       # Pydantic data models
│   └── services/
│       ├── mock_data.py     # Mock data service
│       └── websocket_manager.py # WebSocket connection manager
├── interfaces/
│   └── openapi.json         # Generated OpenAPI specification
├── requirements.txt         # Python dependencies
├── run.py                  # Server startup script
├── test_api.py            # Basic test suite
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🔧 Configuration

Key environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `ENVIRONMENT`: development/production
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)
- `ALLOWED_ORIGINS`: CORS allowed origins

## 🌐 API Documentation

Once the server is running, comprehensive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🚦 Error Handling

The API includes proper error handling with:

- HTTP status codes (404 for not found, 400 for bad requests)
- Detailed error messages
- Validation error responses
- WebSocket connection error management

## 🔄 Real-time Features

### Emoji Reactions
When a user submits an emoji reaction:
1. Reaction is recorded in the system
2. Analytics are updated immediately
3. All connected WebSocket clients receive the update
4. Global analytics are recalculated and broadcast

### Analytics Broadcasting
Analytics updates are automatically broadcast when:
- New emoji reactions are submitted
- Match data changes (scores, status)
- System metrics are updated

## 🎯 Future Enhancements

Planned features for production deployment:

- Database integration (PostgreSQL)
- User authentication and sessions
- Rate limiting and request throttling
- Real sports API integration
- Caching with Redis
- Comprehensive test coverage
- Docker containerization
- Production logging and monitoring

## 📝 License

This project is part of the Fan Engagement application suite.

## 🤝 Contributing

For development and contributions:

1. Ensure all tests pass: `python test_api.py`
2. Follow the existing code structure and patterns
3. Add appropriate documentation for new endpoints
4. Update the OpenAPI schema: `python src/api/generate_openapi.py`

## 📞 Support

For issues and questions related to the Fan Engagement Backend API, please refer to the project documentation or contact the development team.
