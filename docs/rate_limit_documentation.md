# Rate Limiting Documentation

## Overview

The Smart Rental Pricing API implements comprehensive rate limiting to ensure fair usage, prevent abuse, and maintain optimal performance for all users.

## 🛡️ Rate Limiting Strategy

### User Identification
- **Authenticated Users**: Rate limits are applied per username
- **Anonymous Users**: Rate limits are applied per IP address
- **Token Format**: `user:username` or `ip:192.168.1.1`

### Global Default Limits
- **Per Hour**: 1000 requests
- **Per Minute**: 50 requests

## 📊 Endpoint-Specific Rate Limits

### Authentication Endpoints

| Endpoint | Rate Limit | Reason |
|----------|------------|---------|
| `POST /signup` | **3/minute** | Prevent account creation abuse |
| `POST /login` | **5/minute** | Prevent brute force attacks |
| `POST /token` | **5/minute** | Prevent brute force attacks |
| `POST /bootstrap-admin` | **1/minute** | Critical security operation |
| `POST /create-user` | **10/minute** | Admin user creation |

### Listing Read Operations

| Endpoint | Rate Limit | Reason |
|----------|------------|---------|
| `GET /listing/{id}` | **100/minute** | Individual listing access |
| `GET /listings` | **50/minute** | Search and pagination |

### Listing Write Operations

| Endpoint | Rate Limit | Reason |
|----------|------------|---------|
| `POST /listing` | **20/minute** | Individual listing creation |
| `POST /listings` | **5/minute** | Bulk creation (expensive) |
| `POST /upsert-listing` | **20/minute** | Create or update operation |
| `PUT /listing/{id}` | **20/minute** | Listing updates |
| `DELETE /listing/{id}` | **10/minute** | Deletion operations |

### Admin Operations

| Endpoint | Rate Limit | Reason |
|----------|------------|---------|
| `DELETE /listings` | **1/minute** | Bulk deletion (dangerous) |
| `GET /export` | **3/minute** | Resource-intensive export |

### Statistics & Meta

| Endpoint | Rate Limit | Reason |
|----------|------------|---------|
| `GET /count` | **30/minute** | Statistics queries |
| `GET /version` | **Global default** | Light operation |

### Health Check

| Endpoint | Rate Limit | Reason |
|----------|------------|---------|
| `GET /healthz` | **100/minute** | Monitoring and uptime checks |

## 🚨 Rate Limit Responses

### HTTP Status Code
When rate limit is exceeded, the API returns:
```
HTTP 429 Too Many Requests
```

### Response Body
```json
{
  "error": "Rate limit exceeded",
  "message": "You have exceeded the rate limit of 5/minute",
  "retry_after": 45
}
```

### Headers
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 45
```

## 🔧 Implementation Details

### Rate Limiting Library
- **Library**: `slowapi` (FastAPI-compatible version of Flask-Limiter)
- **Storage**: In-memory (production should use Redis)
- **Algorithm**: Token bucket algorithm

### Rate Limit Key Function
```python
def get_user_id(request: Request) -> str:
    # Extract username from JWT token if authenticated
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username:
            return f"user:{username}"
    
    # Fall back to IP address for anonymous users
    return f"ip:{get_remote_address(request)}"
```

### Decorator Usage
```python
from app.core.rate_limit import rate_limit

@router.post("/login")
@rate_limit("auth_login")  # 5/minute
async def login(request: Request, data: LoginRequest):
    # Login logic
```

## 🎯 User Role Considerations

### Current Implementation
All authenticated users share the same rate limits regardless of role.

### Future Enhancement: Role-Based Limits
```python
# Potential future implementation
@role_based_rate_limit(
    viewer_limit="10/minute",
    editor_limit="50/minute", 
    admin_limit="100/minute"
)
async def some_endpoint():
    pass
```

## 💡 Best Practices for API Users

### For Developers

1. **Handle 429 Responses**:
   ```python
   import time
   import requests
   
   def api_call_with_retry(url, headers, data=None):
       response = requests.post(url, headers=headers, json=data)
       
       if response.status_code == 429:
           retry_after = int(response.headers.get('Retry-After', 60))
           print(f"Rate limited. Waiting {retry_after} seconds...")
           time.sleep(retry_after)
           return api_call_with_retry(url, headers, data)
       
       return response
   ```

2. **Implement Exponential Backoff**:
   ```python
   def exponential_backoff(attempt):
       return min(300, (2 ** attempt) + random.uniform(0, 1))
   ```

3. **Cache Responses**: Store frequently accessed data locally

4. **Batch Operations**: Use bulk endpoints when available

### For High-Volume Users

1. **Contact Admin**: Request rate limit increases for legitimate use cases
2. **Optimize Queries**: Use filters to reduce data transfer
3. **Schedule Heavy Operations**: Run exports during off-peak hours
4. **Use Webhooks**: Implement push notifications instead of polling

## 🔍 Monitoring Rate Limits

### Check Current Usage
Rate limit headers are included in every response:
```bash
curl -I "https://api.rental-pricing.com/api/v1/listings" \
     -H "Authorization: Bearer YOUR_TOKEN"

# Response headers:
# X-RateLimit-Limit: 50
# X-RateLimit-Remaining: 45
# X-RateLimit-Reset: 1640995260
```

### Rate Limit Status Endpoint (Future)
```
GET /api/v1/rate-limit-status
```

Would return:
```json
{
  "limits": {
    "global": "1000/hour",
    "current_endpoint": "50/minute"
  },
  "usage": {
    "global": {
      "used": 150,
      "remaining": 850,
      "reset_time": "2023-12-01T15:30:00Z"
    },
    "current_endpoint": {
      "used": 5,
      "remaining": 45,
      "reset_time": "2023-12-01T14:35:00Z"
    }
  }
}
```

## ⚙️ Configuration

### Environment Variables
```yaml
# Rate limiting settings (future enhancement)
RATE_LIMIT_STORAGE: "redis://localhost:6379/0"
RATE_LIMIT_STRATEGY: "fixed-window"  # or "sliding-window"
RATE_LIMIT_ENABLED: true

# Per-role multipliers
RATE_LIMIT_VIEWER_MULTIPLIER: 1.0
RATE_LIMIT_EDITOR_MULTIPLIER: 2.0
RATE_LIMIT_ADMIN_MULTIPLIER: 5.0
```

### Production Considerations

1. **Redis Storage**: Replace in-memory storage with Redis for distributed deployments
2. **Rate Limit Persistence**: Store limits in database for easy configuration
3. **Monitoring**: Integrate with monitoring tools (Prometheus, Grafana)
4. **Alerting**: Set up alerts for rate limit violations

## 🚀 Upgrading Rate Limits

### For Users
1. **Contact Administrator**: Provide justification for higher limits
2. **Use Case Documentation**: Explain your integration needs
3. **Alternative Solutions**: Consider if caching or batching can reduce requests

### For Administrators
1. **Review Usage Patterns**: Analyze logs to identify legitimate high-volume users
2. **Whitelist IPs**: For trusted partners or internal systems
3. **Custom Limits**: Set per-user rate limits in database
4. **Monitor Impact**: Ensure higher limits don't affect overall performance

## 🛠️ Debugging Rate Limits

### Common Issues

1. **Shared IP Address**: Multiple users behind NAT/proxy hitting IP-based limits
   - **Solution**: Ensure proper authentication
   - **Alternative**: Request IP whitelisting

2. **Token Expiration**: Rate limits reset when tokens expire and new ones are issued
   - **Expected Behavior**: Each token gets fresh rate limit allocation

3. **Clock Skew**: Time-based windows may not align perfectly
   - **Solution**: Use sliding window algorithm (future enhancement)

### Testing Rate Limits

```bash
# Test authentication rate limit
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/v1/login" \
       -H "Content-Type: application/json" \
       -d '{"username":"test","password":"wrong"}' \
       -w "Status: %{http_code}\n"
done
```

## 📈 Analytics and Reporting

### Rate Limit Metrics (Future Enhancement)

- **Top Rate-Limited Users**: Identify users hitting limits frequently
- **Endpoint Utilization**: Which endpoints are most heavily used
- **Time Patterns**: Peak usage times and patterns
- **Geographic Distribution**: Rate limit usage by region/IP

### Logs Format
```json
{
  "timestamp": "2023-12-01T14:30:00Z",
  "user_id": "user:john_doe",
  "endpoint": "/api/v1/listings",
  "rate_limit": "50/minute",
  "current_usage": 51,
  "action": "rate_limited",
  "retry_after": 45
}
```

## 🧪 Testing Rate Limits

### Automated Test Suite
Run the comprehensive test suite:
```bash
python test_rate_limits.py
```

This will test:
- Authentication endpoint rate limits
- Signup rate limits  
- Health check limits
- Concurrent request handling
- Rate limit recovery

### Manual Testing
```bash
# Test authentication rate limit (5/minute)
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/v1/login" \
       -H "Content-Type: application/json" \
       -d '{"username":"test","password":"wrong"}' \
       -w "Status: %{http_code}\n"
  sleep 1
done
```

## 🚀 Production Setup

### Enable Redis
1. **Start Redis server**:
   ```bash
   # Using Docker Compose
   docker-compose -f docker-compose.rate-limit.yml up -d
   
   # Or install Redis locally
   redis-server
   ```

2. **Set environment variables**:
   ```bash
   export RATE_LIMIT_USE_REDIS=true
   export REDIS_URL=redis://localhost:6379/0
   ```

3. **Restart your application**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Redis Management
- **Redis UI**: Access at http://localhost:8081 (via Docker Compose)
- **CLI**: `redis-cli` for direct Redis access
- **Monitoring**: Check logs for Redis connection status

### Environment Configuration
```bash
# .env file
RATE_LIMIT_USE_REDIS=true
REDIS_URL=redis://localhost:6379/0

# Optional: Performance tuning
REDIS_MAX_CONNECTIONS=20
REDIS_RETRY_ON_TIMEOUT=true
```

---

**Note**: 
- **Development**: Uses in-memory storage (data lost on restart)
- **Production**: Use Redis for persistence and distributed rate limiting
- **Monitoring**: Check `/api/v1/rate-limit-status` for usage analytics