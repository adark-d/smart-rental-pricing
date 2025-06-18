# Smart Rental Pricing API

A comprehensive FastAPI application for managing real estate listings in Ghana with role-based authentication and full CRUD operations.

## 🏗️ Architecture Overview

```
app/
├── api/v1/endpoints/    # API route handlers
├── core/               # Configuration and security
├── crud/               # Database operations
├── db/                 # Database setup and sessions
├── models/             # SQLAlchemy database models
├── schema/             # Pydantic data validation schemas
└── main.py            # FastAPI application entry point
```

## 🔐 Authentication & Authorization

### User Roles

The application implements a three-tier role-based access control system:

| Role | Permissions | Description |
|------|-------------|-------------|
| **viewer** | Read-only access | Can view listings and basic statistics |
| **editor** | CRUD operations | Can create, update, and delete individual listings |
| **admin** | Full access | Can manage users, bulk operations, and export data |

### Authentication Flow

1. **JWT Token-based Authentication**: All protected endpoints require a valid JWT token
2. **Username-based Login**: Authentication uses username (not email) for login
3. **Role-based Authorization**: Endpoints are protected based on user roles
4. **Secure Password Storage**: Passwords are hashed using bcrypt with 8-character minimum

## 📚 API Endpoints

### Authentication Endpoints

#### Public Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/api/v1/signup` | Register new user (viewer role) | `{"username": "string", "password": "string"}` |
| `POST` | `/api/v1/login` | Login with username/password | `{"username": "string", "password": "string"}` |
| `POST` | `/api/v1/token` | OAuth2 compatible login | Form data: `username` & `password` |

#### Admin Bootstrap

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `POST` | `/api/v1/bootstrap-admin` | Create first admin user (self-disabling) | **Public** (one-time only) |

#### Admin Only

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `POST` | `/api/v1/create-user` | Create user with specific role | **Admin** |

### Listing Management Endpoints

#### Read Operations (Viewer+)

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `GET` | `/api/v1/listing/{listing_id}` | Get single listing by ID | **Viewer** |
| `GET` | `/api/v1/listings` | Query listings with filters & pagination | **Viewer** |

#### Write Operations (Editor+)

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `POST` | `/api/v1/listing` | Create new listing | **Editor** |
| `POST` | `/api/v1/listings` | Batch create multiple listings | **Editor** |
| `POST` | `/api/v1/upsert-listing` | Create or update listing (idempotent) | **Editor** |
| `PUT` | `/api/v1/listing/{listing_id}` | Update existing listing | **Editor** |
| `DELETE` | `/api/v1/listing/{listing_id}` | Delete single listing | **Editor** |

#### Bulk Operations (Admin Only)

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `DELETE` | `/api/v1/listings?confirm=true` | Delete ALL listings | **Admin** |

### Metadata & Statistics

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `GET` | `/api/v1/version` | API version information | **Public** |
| `GET` | `/api/v1/count` | Listing statistics (total, rent, sale) | **Viewer** |
| `GET` | `/api/v1/export` | Export all listings as JSON | **Admin** |

### Health Check

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| `GET` | `/api/v1/healthz` | Service health status | **Public** |

## 🔄 User Management Workflow

### Initial Setup

1. **Start the application**
2. **Create first admin user** using the bootstrap endpoint:
   ```bash
   POST /api/v1/bootstrap-admin
   {
     "username": "admin",
     "password": "securepassword123"
   }
   ```
3. **Bootstrap endpoint automatically disables** after first admin is created

### Adding Users

#### For Regular Users
- Users can self-register via `/api/v1/signup` (automatically get "viewer" role)
- Admin can upgrade user roles using database operations or future role management endpoints

#### For Privileged Users
Admin creates users with specific roles:
```bash
POST /api/v1/create-user
Authorization: Bearer <admin-jwt-token>
{
  "username": "editor_user",
  "password": "password123",
  "role": "editor"
}
```

### Authentication Process

1. **Login to get JWT token**:
   ```bash
   POST /api/v1/login
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

2. **Use token in subsequent requests**:
   ```bash
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

## 📋 Data Models

### User Model

```python
class User:
    id: UUID                    # Unique identifier
    username: str              # Unique username (used for login)
    email: str | None          # Optional email
    hashed_password: str       # Bcrypt hashed password
    is_active: bool           # Account status (default: True)
    role: UserRole            # Enum: "viewer", "editor", "admin"
    created_at: datetime      # Account creation timestamp
```

### Listing Model

```python
class Listing:
    listing_id: str           # Unique listing identifier
    title: str               # Property title
    price: int               # Price in local currency
    region: str              # Geographic region
    bedrooms: int | None     # Number of bedrooms
    bathrooms: int | None    # Number of bathrooms
    listing_type: str        # "rent" or "sale"
    description: str | None  # Property description
    features: list | None    # Additional features
    scraped_at: datetime     # Data collection timestamp
```

## 🔍 Query Parameters & Filters

### Listing Queries (`GET /api/v1/listings`)

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `skip` | int | Pagination offset (default: 0) | `skip=20` |
| `limit` | int | Results per page (max: 100, default: 20) | `limit=50` |
| `region` | string | Filter by region (fuzzy match) | `region=Accra` |
| `min_price` | int | Minimum price filter | `min_price=1000` |
| `max_price` | int | Maximum price filter | `max_price=5000` |
| `listing_type` | string | Filter by type: "rent" or "sale" | `listing_type=rent` |
| `scraped_after` | datetime | Filter by scrape date (after) | `scraped_after=2023-01-01T00:00:00` |
| `scraped_before` | datetime | Filter by scrape date (before) | `scraped_before=2023-12-31T23:59:59` |
| `format` | string | Export format: "json", "csv", "jsonl" | `format=csv` |

### Example Query
```
GET /api/v1/listings?region=Accra&listing_type=rent&min_price=500&max_price=2000&limit=10
```

## 🛡️ Security Features

### Password Requirements
- Minimum 8 characters
- Bcrypt hashing with salt
- Secure password verification

### Token Security
- JWT tokens with configurable expiration
- Username-based subject claims
- Secure token validation

### Role-Based Protection
```python
# Example of endpoint protection
@router.delete("/listings")
async def delete_all_listings(
    user: User = Depends(require_role("admin"))  # Only admins can access
):
    # Bulk delete logic
```

### Input Validation
- Pydantic schemas for request/response validation
- SQL injection prevention via SQLAlchemy ORM
- Type safety with Python type hints

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Required dependencies (see `pyproject.toml`)

### Environment Variables
Configure the following in your environment or `configs/settings.yaml`:
```yaml
POSTGRES_USER: your_db_user
POSTGRES_PASSWORD: your_db_password
POSTGRES_HOST: localhost
POSTGRES_PORT: 5432
POSTGRES_DB: rental_pricing

JWT_SECRET_KEY: your-secret-key
JWT_ALGORITHM: HS256
JWT_EXPIRATION_MINUTES: 30
```

### Running the Application

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access API documentation**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### First-Time Setup

1. **Create admin user**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/bootstrap-admin" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "securepassword123"}'
   ```

2. **Login and get token**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "securepassword123"}'
   ```

3. **Use token for authenticated requests**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/listings" \
        -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

## 📊 Response Formats

### Standard JSON Response
```json
{
  "total": 150,
  "skip": 0,
  "limit": 20,
  "results": [
    {
      "listing_id": "abc123",
      "title": "Modern 2BR Apartment",
      "price": 1500,
      "region": "Greater Accra",
      "bedrooms": 2,
      "bathrooms": 2,
      "listing_type": "rent",
      "scraped_at": "2023-12-01T10:30:00"
    }
  ]
}
```

### CSV Export (with `format=csv`)
```csv
listing_id,title,price,region,bedrooms,bathrooms,listing_type,scraped_at
abc123,Modern 2BR Apartment,1500,Greater Accra,2,2,rent,2023-12-01T10:30:00
```

### JSONL Export (with `format=jsonl`)
```jsonl
{"listing_id": "abc123", "title": "Modern 2BR Apartment", "price": 1500}
{"listing_id": "def456", "title": "Luxury Villa", "price": 5000}
```

## 🔧 Development Notes

### Database Migrations
- Use Alembic for database schema changes
- Models use SQLAlchemy 2.0+ async syntax
- Enum constraints for user roles

### Error Handling
- Consistent HTTP status codes
- Descriptive error messages
- Proper exception handling throughout

### Code Organization
- Clean separation of concerns
- Dependency injection for database sessions
- Type hints for better IDE support

## 🤝 Contributing

1. Follow existing code patterns and naming conventions
2. Add proper type hints and docstrings
3. Update this README for any new endpoints or changes
4. Ensure all new endpoints include proper role-based authorization

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.