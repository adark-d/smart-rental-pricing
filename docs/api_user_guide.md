# Smart Rental Pricing API - User Guide

A complete guide for users to interact with the Smart Rental Pricing API for managing real estate listings in Ghana.

## 🌟 What You Can Do

The Smart Rental Pricing API allows you to:
- **Browse** thousands of real estate listings across Ghana
- **Search** and filter properties by location, price, and type
- **Add** your own property listings (with proper permissions)
- **Export** data for analysis and reporting
- **Manage** listings with full CRUD operations

## 🎯 Getting Started

### Step 1: Understand User Types

| User Type | What You Can Do | How to Get Access |
|-----------|-----------------|-------------------|
| **Viewer** 👀 | Browse and search all listings | Sign up for free |
| **Editor** ✏️ | Add, edit, and delete your listings | Contact admin for upgrade |
| **Admin** 👑 | Full platform management | System administrator |

### Step 2: Create Your Account

**Endpoint:** `POST /api/v1/signup`

```bash
curl -X POST "https://api.rental-pricing.com/api/v1/signup" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "your_username",
       "password": "your_secure_password"
     }'
```

**Requirements:**
- Username must be unique
- Password must be at least 8 characters
- You'll automatically get "viewer" access

### Step 3: Login and Get Your Access Token

**Endpoint:** `POST /api/v1/login`

```bash
curl -X POST "https://api.rental-pricing.com/api/v1/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "your_username",
       "password": "your_password"
     }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Important:** Save this token! You'll need it for all authenticated requests.

## 🔍 Browsing and Searching Listings

### View All Listings

**Endpoint:** `GET /api/v1/listings`

```bash
curl -X GET "https://api.rental-pricing.com/api/v1/listings" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### Search with Filters

Find exactly what you're looking for:

```bash
# Find rentals in Accra under GHS 2000
curl -X GET "https://api.rental-pricing.com/api/v1/listings?region=Accra&listing_type=rent&max_price=2000" \
     -H "Authorization: Bearer YOUR_TOKEN"

# Find 2-bedroom apartments for sale
curl -X GET "https://api.rental-pricing.com/api/v1/listings?bedrooms=2&listing_type=sale" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### Available Search Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `region` | Location (partial match) | `region=Accra` |
| `listing_type` | "rent" or "sale" | `listing_type=rent` |
| `min_price` | Minimum price | `min_price=500` |
| `max_price` | Maximum price | `max_price=3000` |
| `bedrooms` | Number of bedrooms | `bedrooms=3` |
| `bathrooms` | Number of bathrooms | `bathrooms=2` |
| `skip` | Start from result # | `skip=20` |
| `limit` | Results per page (max 100) | `limit=50` |

### Get a Specific Listing

**Endpoint:** `GET /api/v1/listing/{listing_id}`

```bash
curl -X GET "https://api.rental-pricing.com/api/v1/listing/abc123" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏠 Managing Your Listings (Editor Access Required)

### Add a New Listing

**Endpoint:** `POST /api/v1/listing`

```bash
curl -X POST "https://api.rental-pricing.com/api/v1/listing" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "listing_id": "my_listing_001",
       "title": "Beautiful 3BR House in East Legon",
       "price": 2500,
       "region": "Greater Accra",
       "bedrooms": 3,
       "bathrooms": 2,
       "listing_type": "rent",
       "description": "Spacious house with modern amenities",
       "features": ["parking", "security", "furnished"]
     }'
```

**Required Fields:**
- `listing_id` - Your unique identifier
- `title` - Property title
- `price` - Price in GHS
- `region` - Location
- `listing_type` - "rent" or "sale"

### Update an Existing Listing

**Endpoint:** `PUT /api/v1/listing/{listing_id}`

```bash
curl -X PUT "https://api.rental-pricing.com/api/v1/listing/my_listing_001" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "price": 2800,
       "description": "Updated description with new amenities"
     }'
```

### Create or Update (Upsert)

**Endpoint:** `POST /api/v1/upsert-listing`

This is perfect when you're not sure if a listing exists:

```bash
curl -X POST "https://api.rental-pricing.com/api/v1/upsert-listing" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "listing_id": "my_listing_001",
       "title": "Updated Title",
       "price": 3000,
       "region": "Greater Accra",
       "listing_type": "rent"
     }'
```

### Delete a Listing

**Endpoint:** `DELETE /api/v1/listing/{listing_id}`

```bash
curl -X DELETE "https://api.rental-pricing.com/api/v1/listing/my_listing_001" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### Add Multiple Listings at Once

**Endpoint:** `POST /api/v1/listings`

```bash
curl -X POST "https://api.rental-pricing.com/api/v1/listings" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '[
       {
         "listing_id": "bulk_001",
         "title": "First Property",
         "price": 1500,
         "region": "Ashanti",
         "listing_type": "rent"
       },
       {
         "listing_id": "bulk_002", 
         "title": "Second Property",
         "price": 2000,
         "region": "Greater Accra",
         "listing_type": "sale"
       }
     ]'
```

## 📊 Exporting Data

### Export as CSV

Perfect for Excel analysis:

```bash
curl -X GET "https://api.rental-pricing.com/api/v1/listings?format=csv" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -o listings.csv
```

### Export as JSONL

Great for data processing:

```bash
curl -X GET "https://api.rental-pricing.com/api/v1/listings?format=jsonl" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -o listings.jsonl
```

### Export with Filters

Only export what you need:

```bash
# Export only rentals in Accra
curl -X GET "https://api.rental-pricing.com/api/v1/listings?region=Accra&listing_type=rent&format=csv" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -o accra_rentals.csv
```

## 📈 Statistics and Insights

### Get Platform Statistics

**Basic Counts** - `GET /api/v1/count`

```bash
curl -X GET "https://api.rental-pricing.com/api/v1/count" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_listings": 1250,
  "rent_listings": 800,
  "sale_listings": 450
}
```

**Comprehensive Statistics** - `GET /api/v1/stats`

```bash
curl -X GET "https://api.rental-pricing.com/api/v1/stats" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_listings": 1250,
  "rent_listings": 800,
  "sale_listings": 450,
  "average_prices": {
    "rent": 1850.75,
    "sale": 125000.50
  },
  "recent_listings_7_days": 45,
  "top_regions": [
    {"region": "Greater Accra", "count": 450},
    {"region": "Ashanti", "count": 320},
    {"region": "Western", "count": 180}
  ]
}
```

### Check API Version

**Endpoint:** `GET /api/v1/version`

```bash
curl -X GET "https://api.rental-pricing.com/api/v1/version"
```

## 🔧 Using Programming Languages

### Python Example

```python
import requests

# Setup
API_BASE = "https://api.rental-pricing.com/api/v1"
TOKEN = "your_access_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Login and get token
def login(username, password):
    response = requests.post(f"{API_BASE}/login", json={
        "username": username,
        "password": password
    })
    return response.json()["access_token"]

# Search listings
def search_listings(region=None, max_price=None):
    params = {}
    if region:
        params["region"] = region
    if max_price:
        params["max_price"] = max_price
    
    response = requests.get(f"{API_BASE}/listings", 
                          headers=HEADERS, params=params)
    return response.json()

# Add a listing
def add_listing(listing_data):
    response = requests.post(f"{API_BASE}/listing", 
                           headers=HEADERS, json=listing_data)
    return response.json()

# Example usage
token = login("your_username", "your_password")
HEADERS = {"Authorization": f"Bearer {token}"}

# Search for properties
properties = search_listings(region="Accra", max_price=2000)
print(f"Found {properties['total']} properties")

# Add a new listing
new_listing = {
    "listing_id": "python_001",
    "title": "Cozy Apartment",
    "price": 1800,
    "region": "Greater Accra",
    "listing_type": "rent"
}
result = add_listing(new_listing)
print("Listing added:", result["listing_id"])
```

### JavaScript Example

```javascript
// Setup
const API_BASE = "https://api.rental-pricing.com/api/v1";
let token = "";

// Login function
async function login(username, password) {
    const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await response.json();
    token = data.access_token;
    return token;
}

// Search listings
async function searchListings(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${API_BASE}/listings?${params}`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    return await response.json();
}

// Add listing
async function addListing(listingData) {
    const response = await fetch(`${API_BASE}/listing`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(listingData)
    });
    return await response.json();
}

// Example usage
(async () => {
    await login("your_username", "your_password");
    
    // Search properties
    const properties = await searchListings({
        region: "Accra",
        listing_type: "rent",
        max_price: 2000
    });
    console.log(`Found ${properties.total} properties`);
    
    // Add new listing
    const newListing = {
        listing_id: "js_001",
        title: "Modern Studio",
        price: 1200,
        region: "Greater Accra",
        listing_type: "rent"
    };
    const result = await addListing(newListing);
    console.log("Listing added:", result.listing_id);
})();
```

## 🚨 Common Issues and Solutions

### Authentication Problems

**Problem:** "Could not validate credentials"
**Solution:** 
- Check if your token is expired (tokens last 30 minutes)
- Login again to get a fresh token
- Ensure you're including "Bearer " before your token

### Permission Denied

**Problem:** "Access denied. Required role: editor"
**Solution:**
- Contact your system administrator to upgrade your account
- Viewers can only read data, not create or modify listings

### Duplicate Listing ID

**Problem:** "Listing with ID 'xyz' already exists"
**Solutions:**
- Use a different `listing_id`
- Use the upsert endpoint (`POST /api/v1/upsert-listing`) to update existing listings
- Delete the existing listing first (if you own it)

### Rate Limiting

**Problem:** Too many requests
**Solution:**
- Slow down your requests
- Use batch operations when possible
- Contact support for higher rate limits

## 📞 Getting Help

### Interactive API Documentation
Visit the live API documentation at:
- **Swagger UI:** `https://api.rental-pricing.com/docs`
- **ReDoc:** `https://api.rental-pricing.com/redoc`

### Account Upgrades
To get editor or admin access:
1. Contact your system administrator
2. Provide your username and intended use case
3. Wait for role upgrade confirmation

### Health Check
Check if the API is running:
```bash
curl -X GET "https://api.rental-pricing.com/api/v1/healthz"
```

### Support Channels
- **Technical Issues:** Check the interactive docs first
- **Account Problems:** Contact your system administrator
- **Feature Requests:** Submit through proper channels

## 💡 Best Practices

### Security
- Never share your access tokens
- Use strong, unique passwords
- Login periodically to refresh your token

### Data Management
- Use descriptive listing IDs (e.g., "accra_house_001")
- Include complete property information
- Update listings when details change
- Delete outdated listings

### API Usage
- Use filters to reduce data transfer
- Batch operations when adding multiple listings
- Export data during off-peak hours
- Cache frequently accessed data

### Listing Quality
- Use clear, descriptive titles
- Include accurate pricing
- Specify precise locations
- Add relevant features and amenities
- Keep descriptions informative but concise

## 🎉 Success Stories

**Real Estate Agents:** "The API allows us to bulk upload our entire portfolio and keep it synchronized across platforms."

**Property Developers:** "We use the export feature to analyze market trends and price our new developments competitively."

**Individual Landlords:** "Simple and straightforward - I can manage all my rental properties from one place."

---

*Ready to get started? Sign up today and join thousands of users managing their real estate data efficiently!*