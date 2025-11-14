# Trade Opportunities API

A FastAPI-based service that provides AI-powered trade opportunity analysis for specific sectors in the Indian market.

## 🚀 Features

- **AI-Powered Analysis**: Uses Google Gemini API for comprehensive market analysis
- **Sector-Specific Reports**: Detailed markdown reports for various Indian market sectors
- **Authentication & Security**: JWT-based authentication with rate limiting
- **Real-time Data**: Web scraping and market data integration
- **Professional Reports**: Structured markdown analysis suitable for trading decisions
- **In-memory Storage**: Fast, lightweight data management

## 📋 Requirements

- Python 3.8+
- Google Gemini API key (free tier available)
- Internet connection for data collection

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trade-opportunities-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file and add your configuration:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key_for_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Get Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a free account
   - Generate an API key
   - Add it to your `.env` file

## 🚦 Usage

### 1. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Authentication

**Demo Users Available:**
- Username: `demo`, Password: `demo123`
- Username: `trader`, Password: `trader123`

**Get Access Token:**
```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/json" \
     -u demo:demo123
```

### 4. Analyze a Sector

```bash
curl -X GET "http://localhost:8000/analyze/pharmaceuticals" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and status |
| POST | `/token` | Get authentication token |
| POST | `/register` | Register new user |
| GET | `/analyze/{sector}` | **Main endpoint** - Analyze sector |
| GET | `/user/stats` | User statistics and history |
| GET | `/sectors` | List available sectors |
| GET | `/health` | Health check |

### Example Request

```python
import requests

# Get token
auth_response = requests.post(
    "http://localhost:8000/token",
    auth=("demo", "demo123")
)
token = auth_response.json()["access_token"]

# Analyze sector
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/analyze/technology",
    headers=headers
)

analysis = response.json()
print(analysis["analysis"])  # Markdown report
```

## 🎯 Available Sectors

- `pharmaceuticals` - Pharmaceutical and healthcare
- `technology` - IT and software technology  
- `agriculture` - Agriculture and food processing
- `banking` - Banking and financial services
- `automotive` - Automotive and transportation
- `energy` - Energy and renewable resources
- `telecommunications` - Telecom and communication
- `retail` - Retail and consumer goods
- `real-estate` - Real estate and construction
- `textiles` - Textiles and apparel

## 🔒 Security Features

### Authentication
- JWT-based authentication system
- Secure password hashing with bcrypt
- Token expiration management

### Rate Limiting
- 5 requests per minute per user
- IP-based rate limiting for unauthenticated users
- Automatic rate limit reset

### Input Validation
- Sector name length validation (2-50 characters)
- Request sanitization
- Error handling for malformed requests

### Security Headers
- CORS configuration
- Bearer token authentication
- Secure error responses

## 📈 Sample Output

```markdown
# Trade Opportunities Analysis: Technology Sector India

*Analysis Date: January 15, 2024*

## Executive Summary

The technology sector in India presents compelling trade opportunities...

## Market Overview
- **Sector Growth**: 12.3% CAGR
- **Market Cap**: ₹8,90,000 Cr
- **Key Players**: TCS, Infosys, Wipro, HCL Tech

## Trade Opportunities
1. **Long-term Investment Plays**
2. **Short-term Trading Opportunities** 
3. **Derivative Strategies**

## Risk Assessment
- Regulatory Changes
- Global Competition
- Economic Cycles

[Full detailed analysis continues...]
```

## 🏗️ Architecture

```
trade-opportunities-api/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # Pydantic data models
│   ├── auth.py              # Authentication and JWT handling
│   ├── rate_limiter.py      # Rate limiting implementation
│   ├── data_collector.py    # Web scraping and data collection
│   └── ai_analyzer.py       # Gemini AI integration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # Documentation
```

## 🧪 Testing

### Manual Testing

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Authentication Test**
   ```bash
   curl -X POST "http://localhost:8000/token" -u demo:demo123
   ```

3. **Analysis Test**
   ```bash
   curl -X GET "http://localhost:8000/analyze/pharmaceuticals" \
        -H "Authorization: Bearer YOUR_TOKEN"
   ```

### Rate Limit Testing

Make 6 requests quickly to test rate limiting:
```bash
for i in {1..6}; do
  curl -X GET "http://localhost:8000/analyze/technology" \
       -H "Authorization: Bearer YOUR_TOKEN"
  echo "Request $i completed"
done
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `SECRET_KEY` | JWT signing key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |

### Rate Limiting

- **Default**: 5 requests per minute
- **Configurable** in `rate_limiter.py`
- **Per-user** tracking with JWT
- **IP-based** for unauthenticated requests

## 🚀 Deployment

### Local Development
```bash
uvicorn app.main:app --reload --port 8000
```

### Production Deployment
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Gemini API Not Working**
   - Check API key in `.env` file
   - Verify API key permissions
   - Falls back to mock analysis

2. **Rate Limit Errors**
   - Wait for rate limit reset
   - Check user authentication
   - Verify rate limit configuration

3. **Authentication Failures**
   - Use correct demo credentials
   - Check token expiration
   - Verify JWT secret key

### Debug Mode

Set environment variable for detailed logging:
```bash
export PYTHONPATH=.
python -m app.main
```

## 📝 API Response Format

### Successful Analysis Response
```json
{
  "sector": "Technology",
  "analysis": "# Trade Opportunities Analysis...",
  "timestamp": "2024-01-15T10:30:00",
  "sources_used": ["DuckDuckGo Search", "Market Research"],
  "request_id": "uuid-string",
  "data_points_analyzed": 25,
  "from_cache": false,
  "user": "demo"
}
```

### Error Response
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Limit: 5 per 60 seconds",
  "reset_time": "2024-01-15T10:31:00"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is for educational and demonstration purposes.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Test with provided demo credentials
4. Verify environment configuration

---

**Note**: This is a demonstration API. For production use, implement additional security measures, database persistence, and comprehensive error handling.