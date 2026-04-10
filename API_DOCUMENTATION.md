# API Documentation - Bangladesh Top Companies

Comprehensive API documentation for all endpoints in the bd-top-comp application.

## Base URL

```
http://localhost:8000
```

## Response Format

All API endpoints return JSON responses with the following format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2026-04-10T12:00:00Z"
}
```

## Authentication

Most endpoints require admin authentication via Django session. Include session cookie in requests.

**Login**:
```bash
POST /login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

---

## Company Endpoints

### List Companies

**Endpoint**: `GET /api/companies/`

**Description**: Retrieve paginated list of companies with filtering, sorting, and pagination.

**Authentication**: Optional (some features require login)

**Parameters**:
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 50)
- `search` (string, optional): Search term (searches name, sector, headquarters, description)
- `sector` (string, optional): Filter by sector
- `sort` (string, optional): Sort field - `name`, `founded`, `sector` (default: name)
- `order` (string, optional): Sort order - `asc`, `desc` (default: asc)

**Example Request**:
```bash
GET /api/companies/?page=1&limit=10&search=tech&sector=Technology&sort=founded&order=desc
```

**Example Response**:
```json
{
  "success": true,
  "companies": [
    {
      "id": 1,
      "name": "Grameen Bank",
      "sector": "Banking & Finance",
      "logo_url": "https://example.com/logo.png",
      "headquarters": "Dhaka",
      "founded": 1983,
      "description": "Pioneering microfinance institution...",
      "created_at": "2026-01-15T10:30:00Z",
      "updated_at": "2026-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 2,
    "total_results": 14,
    "per_page": 10
  },
  "filters_applied": {
    "search": "tech",
    "sector": "Technology",
    "sort_by": "founded",
    "sort_order": "desc"
  }
}
```

---

### Add Company

**Endpoint**: `POST /api/companies/add/`

**Description**: Add a new company (authenticated admin only)

**Authentication**: Required ✅

**Request Body**:
```json
{
  "name": "New Company Ltd",
  "sector": "Technology",
  "logo_url": "https://example.com/logo.png",
  "headquarters": "Dhaka",
  "founded": 2015,
  "description": "A technology company..."
}
```

**Parameters**:
- `name` (string, required): Company name (max 200 chars, unique)
- `sector` (string, required): Business sector
- `logo_url` (URL, required): Company logo URL
- `headquarters` (string, required): Headquarters location
- `founded` (integer, required): Year founded
- `description` (text, required): Company description

**Example Response**:
```json
{
  "success": true,
  "message": "Company added successfully!",
  "company": {
    "id": 15,
    "name": "New Company Ltd",
    "sector": "Technology",
    "created_at": "2026-04-10T12:00:00Z"
  }
}
```

**Error Response** (400):
```json
{
  "success": false,
  "message": "Company name already exists"
}
```

---

### Edit Company

**Endpoint**: `POST /api/companies/<id>/edit/`

**Description**: Update company information

**Authentication**: Required ✅

**URL Parameters**:
- `id` (integer): Company ID

**Request Body**:
```json
{
  "name": "Updated Company Name",
  "sector": "Technology",
  "logo_url": "https://example.com/new-logo.png",
  "headquarters": "Dhaka",
  "founded": 2015,
  "description": "Updated description..."
}
```

**Example Response**:
```json
{
  "success": true,
  "message": "Company updated successfully!",
  "company": {
    "id": 15,
    "name": "Updated Company Name",
    "updated_at": "2026-04-10T12:00:00Z"
  }
}
```

---

### Delete Company

**Endpoint**: `POST /api/companies/<id>/delete/`

**Description**: Delete a company

**Authentication**: Required ✅

**URL Parameters**:
- `id` (integer): Company ID

**Example Response**:
```json
{
  "success": true,
  "message": "Company deleted successfully!"
}
```

---

## Statistics Endpoints

### Get Statistics

**Endpoint**: `GET /api/stats/`

**Description**: Get sector distribution and company statistics

**Authentication**: Optional

**Example Response**:
```json
{
  "success": true,
  "total_companies": 14,
  "sector_distribution": [
    {
      "sector": "Banking & Finance",
      "count": 2,
      "percentage": 14.3
    },
    {
      "sector": "Technology",
      "count": 1,
      "percentage": 7.1
    }
  ],
  "all_sectors": [
    "Banking & Finance",
    "Technology",
    "Telecommunications",
    "Energy",
    "Consumer Goods",
    "Manufacturing",
    "Shipping"
  ]
}
```

---

## Export Endpoints

### Export to CSV

**Endpoint**: `GET /api/export/csv/`

**Description**: Export companies as CSV file with applied filters and sorting

**Authentication**: Required ✅

**Parameters**:
- `search` (string, optional): Search filter
- `sector` (string, optional): Sector filter
- `sort` (string, optional): Sort field
- `order` (string, optional): Sort order

**Example Request**:
```bash
GET /api/export/csv/?search=tech&sector=Technology&sort=founded&order=desc
```

**Response**: CSV file download
```
Company Name,Sector,Headquarters,Founded,Description,Added On,Last Updated
Grameen Bank,Banking & Finance,Dhaka,1983,...,2026-01-15,2026-01-15
...
```

---

### Export Summary

**Endpoint**: `GET /api/export/summary/`

**Description**: Export statistics summary as CSV

**Authentication**: Required ✅

**Example Response**: CSV file download
```
Bangladesh Top Companies - Summary Report
Generated on,2026-04-10 12:00:00

OVERALL STATISTICS
Total Companies,14
Total Sectors,7

SECTOR BREAKDOWN
Sector,Count
Banking & Finance,2
Technology,1
...
```

---

## Analytics Endpoints

### Dashboard Analytics

**Endpoint**: `GET /api/analytics/dashboard/`

**Description**: Comprehensive analytics for dashboard visualization

**Authentication**: Required ✅

**Example Response**:
```json
{
  "success": true,
  "statistics": {
    "total_companies": 14,
    "total_sectors": 7,
    "avg_founded_year": 1995,
    "founded_year_range": {
      "min": 1970,
      "max": 2010
    }
  },
  "sector_distribution": [
    {
      "sector": "Banking & Finance",
      "count": 2
    },
    {
      "sector": "Technology",
      "count": 1
    }
  ],
  "decade_stats": {
    "1970s": 1,
    "1980s": 3,
    "1990s": 6,
    "2000s": 4
  },
  "recent_companies": [
    {
      "id": 14,
      "name": "Company Name",
      "sector": "Technology",
      "founded": 2005,
      "created_at": "2026-04-10"
    }
  ],
  "top_sectors": [
    {
      "sector": "Banking & Finance",
      "count": 2
    }
  ]
}
```

---

### Company Comparison

**Endpoint**: `GET /api/analytics/comparison/`

**Description**: Compare multiple companies

**Authentication**: Required ✅

**Parameters**:
- `ids` (int[], optional): Company IDs to compare (if not provided, returns all)

**Example Request**:
```bash
GET /api/analytics/comparison/?ids=1&ids=2&ids=3
```

**Example Response**:
```json
{
  "success": true,
  "companies": [
    {
      "id": 1,
      "name": "Grameen Bank",
      "sector": "Banking & Finance",
      "founded": 1983,
      "headquarters": "Dhaka"
    },
    {
      "id": 2,
      "name": "Bangladesh Bank",
      "sector": "Banking & Finance",
      "founded": 1971,
      "headquarters": "Dhaka"
    }
  ],
  "metrics": {
    "total": 2,
    "avg_founded": 1977,
    "oldest": 1971,
    "newest": 1983,
    "sectors": ["Banking & Finance"]
  }
}
```

---

### Sector Insights

**Endpoint**: `GET /api/analytics/sector/`

**Description**: Detailed insights for a specific sector

**Authentication**: Required ✅

**Parameters**:
- `sector` (string, required): Sector name

**Example Request**:
```bash
GET /api/analytics/sector/?sector=Technology
```

**Example Response**:
```json
{
  "success": true,
  "insights": {
    "sector": "Technology",
    "company_count": 1,
    "companies": [
      {
        "id": 10,
        "name": "Robi Axiata",
        "founded": 2004,
        "headquarters": "Dhaka"
      }
    ],
    "founded_range": {
      "oldest": 2004,
      "newest": 2004,
      "average": 2004
    },
    "decade_distribution": {
      "2000s": 1
    }
  }
}
```

**Error Response** (404):
```json
{
  "success": false,
  "message": "No companies found in sector: InvalidSector"
}
```

---

### Growth Analysis

**Endpoint**: `GET /api/analytics/growth/`

**Description**: Analyze company addition trends over last 30 days

**Authentication**: Required ✅

**Example Response**:
```json
{
  "success": true,
  "growth_data": [
    {
      "date": "2026-03-15",
      "additions": 1
    },
    {
      "date": "2026-03-16",
      "additions": 2
    },
    {
      "date": "2026-03-20",
      "additions": 1
    }
  ],
  "metrics": {
    "total_additions_30d": 10,
    "avg_daily_additions": 0.33,
    "days_with_additions": 5
  }
}
```

---

### Descriptive Statistics

**Endpoint**: `GET /api/analytics/stats/`

**Description**: Comprehensive statistical analysis of companies

**Authentication**: Required ✅

**Example Response**:
```json
{
  "success": true,
  "statistics": {
    "founded_year_statistics": {
      "count": 14,
      "mean": 1995.2,
      "median": 1996,
      "std_dev": 10.5,
      "min": 1970,
      "max": 2010,
      "range": 40,
      "q1": 1988,
      "q3": 2002
    },
    "sector_statistics": {
      "total_unique": 7,
      "distribution": [
        {
          "sector": "Banking & Finance",
          "count": 2
        }
      ]
    },
    "all_companies": 14
  }
}
```

---

## Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 302 | Found | Redirect (e.g., to login) |
| 400 | Bad Request | Invalid parameters or validation error |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

---

## Common Errors

### Authentication Required
```json
{
  "success": false,
  "message": "Login required"
}
```
**Solution**: Login at `/login/` first

### Validation Error
```json
{
  "success": false,
  "message": "Company name is required"
}
```
**Solution**: Provide all required fields

### Not Found
```json
{
  "success": false,
  "message": "Company not found"
}
```
**Solution**: Check company ID

---

## Usage Examples

### cURL

**Get all companies**:
```bash
curl -X GET http://localhost:8000/api/companies/
```

**Search companies**:
```bash
curl -X GET "http://localhost:8000/api/companies/?search=tech&sector=Technology"
```

**Export CSV**:
```bash
curl -X GET http://localhost:8000/api/export/csv/ \
  -b "sessionid=YOUR_SESSION_ID" \
  -o companies.csv
```

**Get analytics**:
```bash
curl -X GET http://localhost:8000/api/analytics/dashboard/ \
  -b "sessionid=YOUR_SESSION_ID" \
  -H "Content-Type: application/json"
```

### JavaScript/Fetch

**Get companies with filters**:
```javascript
fetch('/api/companies/?search=tech&sort=founded&order=desc')
  .then(response => response.json())
  .then(data => console.log(data));
```

**Add company**:
```javascript
fetch('/api/companies/add/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken()
  },
  body: JSON.stringify({
    name: 'New Company',
    sector: 'Technology',
    logo_url: 'https://example.com/logo.png',
    headquarters: 'Dhaka',
    founded: 2020,
    description: 'Description...'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Get analytics**:
```javascript
fetch('/api/analytics/dashboard/')
  .then(response => response.json())
  .then(data => {
    console.log('Total companies:', data.statistics.total_companies);
    console.log('Sectors:', data.sector_distribution);
  });
```

### Python Requests

**Get companies**:
```python
import requests

response = requests.get('http://localhost:8000/api/companies/')
data = response.json()
print(f"Total companies: {data['pagination']['total_results']}")

for company in data['companies']:
    print(f"- {company['name']} ({company['sector']})")
```

---

## Rate Limiting

Currently, the API has no rate limiting. In production, implement:
- Django-ratelimit or DRF throttling
- Redis-based rate limiter
- Per-IP or per-user limits

---

## Versioning

Currently on API Version 1.0

Future versions may include:
- `/api/v2/companies/` with backwards compatibility
- Query parameter versioning
- Accept header versioning

---

## CSRF Protection

All POST requests require CSRF token:

```javascript
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
         document.cookie.split(';')
           .find(c => c.trim().startsWith('csrftoken='))
           ?.split('=')[1];
}
```

---

## WebSocket Support

Not currently implemented. Planned for real-time updates:
- Live company updates
- Real-time chat for admin users
- WebSocket authentication

---

## Pagination Guide

**How pagination works**:
1. Default limit is 50 items per page
2. Pages are 1-indexed (page 1, 2, 3, etc.)
3. Response includes `total_pages` and `total_results`
4. Use `?page=N&limit=L` to navigate

**Example - Get page 2 with 10 items per page**:
```bash
GET /api/companies/?page=2&limit=10
```

---

## Filtering & Searching

**Search** searches across:
- Company name
- Sector
- Headquarters
- Description

**Sector filter** is exact match (case-insensitive)

**Combine filters**:
```bash
GET /api/companies/?search=tech&sector=Technology&sort=founded&order=desc
```

---

## Sorting Options

| Field | Type | Example |
|-------|------|---------|
| name | Text | A → Z |
| founded | Year | 1970 → 2010 |
| sector | Text | A → Z |

Order: `asc` (ascending) or `desc` (descending)

---

## Future API Enhancements

Planned for future versions:
- GraphQL support
- Webhook integrations
- Advanced filtering API
- Batch operations endpoint
- File upload for logo imports
- API key authentication
- OAuth2 support
- OpenAPI/Swagger documentation endpoint
- API metrics and analytics

---

**Last Updated**: April 10, 2026
**API Version**: 1.0
**Status**: Stable
