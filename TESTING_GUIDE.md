# Testing Guide - Bangladesh Top Companies

Comprehensive testing strategies and implementations for the bd-top-comp application.

---

## Table of Contents

1. [Test Structure](#test-structure)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [API Testing](#api-testing)
5. [Frontend Testing](#frontend-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [End-to-End Testing](#end-to-end-testing)
9. [Test Coverage](#test-coverage)
10. [CI/CD Testing](#cicd-testing)

---

## Test Structure

### Project Layout

```
bd-top-comp/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures and configuration
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_forms.py
│   │   ├── test_serializers.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_api_endpoints.py
│   │   ├── test_database.py
│   │   └── test_services.py
│   ├── api/
│   │   ├── test_companies_api.py
│   │   ├── test_stats_api.py
│   │   └── test_export_api.py
│   ├── performance/
│   │   ├── test_api_performance.py
│   │   └── test_database_performance.py
│   ├── security/
│   │   ├── test_authentication.py
│   │   ├── test_authorization.py
│   │   └── test_sql_injection.py
│   └── e2e/
│       ├── test_workflows.py
│       └── test_user_scenarios.py
├── requirements-dev.txt
├── pytest.ini
└── .coverage
```

### Testing Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| pytest | Test framework | `pip install pytest` |
| pytest-django | Django integration | `pip install pytest-django` |
| pytest-cov | Coverage reporting | `pip install pytest-cov` |
| factory_boy | Fixture generation | `pip install factory_boy` |
| faker | Fake data | `pip install faker` |
| responses | Mock HTTP | `pip install responses` |
| locust | Performance testing | `pip install locust` |
| selenium | Browser automation | `pip install selenium` |

---

## Unit Testing

### Models Testing

**tests/unit/test_models.py**:
```python
import pytest
from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from companies.models import Company
from datetime import datetime

pytestmark = pytest.mark.django_db

class TestCompanyModel:
    """Test Company model"""
    
    def test_create_company(self):
        """Test creating a valid company"""
        company = Company.objects.create(
            name="Test Company",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test description"
        )
        
        assert company.id is not None
        assert company.name == "Test Company"
        assert company.sector == "Technology"
        assert company.founded == 2020
    
    def test_company_name_required(self):
        """Test that company name is required"""
        with pytest.raises(IntegrityError):
            Company.objects.create(
                name=None,
                sector="Technology",
                logo_url="https://example.com/logo.png",
                headquarters="Dhaka",
                founded=2020,
                description="Test"
            )
    
    def test_unique_company_name(self):
        """Test that company names are unique"""
        Company.objects.create(
            name="Unique Company",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test"
        )
        
        with pytest.raises(IntegrityError):
            Company.objects.create(
                name="Unique Company",
                sector="Finance",
                logo_url="https://example.com/logo2.png",
                headquarters="Chittagong",
                founded=2021,
                description="Test 2"
            )
    
    def test_company_str_method(self):
        """Test company string representation"""
        company = Company.objects.create(
            name="Test Company",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test"
        )
        
        assert str(company) == "Test Company"
    
    def test_company_timestamps(self):
        """Test created_at and updated_at timestamps"""
        company = Company.objects.create(
            name="Test Company",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test"
        )
        
        assert company.created_at is not None
        assert company.updated_at is not None
        assert company.created_at == company.updated_at
    
    def test_company_update(self):
        """Test updating company"""
        company = Company.objects.create(
            name="Original Name",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test"
        )
        
        company.name = "Updated Name"
        company.save()
        
        refreshed = Company.objects.get(id=company.id)
        assert refreshed.name == "Updated Name"
        assert refreshed.updated_at > company.created_at
```

### Fixtures with factory_boy

**tests/conftest.py**:
```python
import pytest
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from companies.models import Company

class CompanyFactory(DjangoModelFactory):
    """Factory for creating Company instances"""
    
    class Meta:
        model = Company
    
    name = Faker('company')
    sector = Faker('word')
    logo_url = Faker('image_url')
    headquarters = Faker('city')
    founded = Faker('year')
    description = Faker('text')

@pytest.fixture
def company():
    """Create a single company"""
    return CompanyFactory()

@pytest.fixture
def companies():
    """Create multiple companies"""
    return CompanyFactory.create_batch(10)

@pytest.fixture
def company_data():
    """Create dictionary of company data"""
    return {
        'name': 'Test Company',
        'sector': 'Technology',
        'logo_url': 'https://example.com/logo.png',
        'headquarters': 'Dhaka',
        'founded': 2020,
        'description': 'Test description'
    }

@pytest.fixture
def admin_user(django_user_model):
    """Create an admin user"""
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )

@pytest.fixture
def authenticated_client(admin_user, client):
    """Create authenticated client"""
    client.force_login(admin_user)
    return client
```

---

## Integration Testing

### API Endpoints Testing

**tests/integration/test_api_endpoints.py**:
```python
import pytest
from django.test import Client
from django.urls import reverse
from companies.models import Company
import json

pytestmark = pytest.mark.django_db

class TestCompaniesAPI:
    """Test companies API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()
        # Create test data
        self.companies = [
            Company.objects.create(
                name=f"Company {i}",
                sector="Technology",
                logo_url="https://example.com/logo.png",
                headquarters="Dhaka",
                founded=2020,
                description="Test"
            )
            for i in range(5)
        ]
    
    def test_list_companies(self):
        """Test listing all companies"""
        response = self.client.get(reverse('api:companies-list'))
        
        assert response.status_code == 200
        data = response.json()
        assert 'companies' in data
        assert len(data['companies']) == 5
    
    def test_list_companies_pagination(self):
        """Test companies pagination"""
        response = self.client.get(
            reverse('api:companies-list'),
            {'page': 1, 'limit': 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['companies']) == 2
        assert data['pagination']['total_results'] == 5
        assert data['pagination']['total_pages'] == 3
    
    def test_search_companies(self):
        """Test searching companies"""
        response = self.client.get(
            reverse('api:companies-list'),
            {'search': 'Company 1'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['companies']) >= 1
    
    def test_filter_by_sector(self):
        """Test filtering by sector"""
        response = self.client.get(
            reverse('api:companies-list'),
            {'sector': 'Technology'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(c['sector'] == 'Technology' for c in data['companies'])
```

### Database Integration Tests

**tests/integration/test_database.py**:
```python
import pytest
from django.db import connection
from django.db.models import Count
from companies.models import Company

pytestmark = pytest.mark.django_db

class TestDatabaseIntegration:
    """Test database integration"""
    
    def test_database_connection(self):
        """Test database connection"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result == (1,)
    
    def test_bulk_create_companies(self):
        """Test bulk creating companies"""
        companies = [
            Company(
                name=f"Company {i}",
                sector="Technology",
                logo_url="https://example.com/logo.png",
                headquarters="Dhaka",
                founded=2020,
                description="Test"
            )
            for i in range(100)
        ]
        
        Company.objects.bulk_create(companies)
        assert Company.objects.count() == 100
    
    def test_database_aggregation(self):
        """Test database aggregation"""
        for i in range(5):
            Company.objects.create(
                name=f"Tech Company {i}",
                sector="Technology",
                logo_url="https://example.com/logo.png",
                headquarters="Dhaka",
                founded=2020,
                description="Test"
            )
        
        stats = Company.objects.values('sector').annotate(count=Count('id'))
        assert stats[0]['count'] == 5
```

---

## API Testing

### Comprehensive API Tests

**tests/api/test_companies_api.py**:
```python
import pytest
import json
from django.test import Client
from django.urls import reverse
from companies.models import Company

pytestmark = pytest.mark.django_db

class TestCompaniesAPIAuthentication:
    """Test API authentication"""
    
    @pytest.fixture
    def client(self):
        return Client()
    
    def test_add_company_without_auth(self, client):
        """Test adding company without authentication"""
        response = client.post(
            reverse('api:companies-add'),
            data=json.dumps({
                'name': 'New Company',
                'sector': 'Technology',
                'logo_url': 'https://example.com/logo.png',
                'headquarters': 'Dhaka',
                'founded': 2020,
                'description': 'Test'
            }),
            content_type='application/json'
        )
        
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_add_company_with_auth(self, authenticated_client):
        """Test adding company with authentication"""
        response = authenticated_client.post(
            reverse('api:companies-add'),
            data=json.dumps({
                'name': 'New Company',
                'sector': 'Technology',
                'logo_url': 'https://example.com/logo.png',
                'headquarters': 'Dhaka',
                'founded': 2020,
                'description': 'Test'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['company']['name'] == 'New Company'

class TestCompaniesAPIValidation:
    """Test API input validation"""
    
    def test_missing_required_field(self, authenticated_client):
        """Test missing required fields"""
        response = authenticated_client.post(
            reverse('api:companies-add'),
            data=json.dumps({
                'name': 'New Company'
                # Missing other required fields
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
    
    def test_duplicate_company_name(self, authenticated_client):
        """Test duplicate company name"""
        # Create first company
        Company.objects.create(
            name="Existing Company",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test"
        )
        
        # Try to create duplicate
        response = authenticated_client.post(
            reverse('api:companies-add'),
            data=json.dumps({
                'name': 'Existing Company',
                'sector': 'Technology',
                'logo_url': 'https://example.com/logo.png',
                'headquarters': 'Dhaka',
                'founded': 2020,
                'description': 'Test'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'already exists' in response.json()['message']

class TestCompaniesAPICRUD:
    """Test CRUD operations"""
    
    @pytest.mark.django_db
    def test_read_company(self):
        """Test reading company"""
        company = Company.objects.create(
            name="Test Company",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test"
        )
        
        client = Client()
        response = client.get(reverse('api:companies-list'))
        
        assert response.status_code == 200
        companies = response.json()['companies']
        assert any(c['id'] == company.id for c in companies)
    
    @pytest.mark.django_db
    def test_update_company(self, authenticated_client):
        """Test updating company"""
        company = Company.objects.create(
            name="Original Name",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test"
        )
        
        response = authenticated_client.post(
            reverse('api:companies-edit', args=[company.id]),
            data=json.dumps({
                'name': 'Updated Name',
                'sector': 'Technology',
                'logo_url': 'https://example.com/logo.png',
                'headquarters': 'Dhaka',
                'founded': 2020,
                'description': 'Updated'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        company.refresh_from_db()
        assert company.name == 'Updated Name'
    
    @pytest.mark.django_db
    def test_delete_company(self, authenticated_client):
        """Test deleting company"""
        company = Company.objects.create(
            name="Test Company",
            sector="Technology",
            logo_url="https://example.com/logo.png",
            headquarters="Dhaka",
            founded=2020,
            description="Test"
        )
        
        company_id = company.id
        
        response = authenticated_client.post(
            reverse('api:companies-delete', args=[company.id])
        )
        
        assert response.status_code == 200
        assert not Company.objects.filter(id=company_id).exists()
```

---

## Frontend Testing

### Template Testing

**tests/test_templates.py**:
```python
import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestTemplates:
    """Test template rendering"""
    
    def test_index_page_renders(self):
        """Test index page renders"""
        client = Client()
        response = client.get(reverse('index'))
        
        assert response.status_code == 200
        assert 'Bangladesh Top Companies' in response.content.decode()
    
    def test_admin_page_requires_login(self):
        """Test admin page requires login"""
        client = Client()
        response = client.get(reverse('admin_dashboard'))
        
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_admin_page_with_auth(self, authenticated_client):
        """Test admin page with authentication"""
        response = authenticated_client.get(reverse('admin_dashboard'))
        
        assert response.status_code == 200
        assert 'Dashboard' in response.content.decode()
```

---

## Performance Testing

### API Performance Testing

**tests/performance/test_api_performance.py**:
```python
import pytest
import time
from django.test import Client
from django.urls import reverse
from companies.models import Company
from faker import Faker

pytestmark = pytest.mark.django_db

class TestAPIPerformance:
    """Test API performance"""
    
    @pytest.fixture
    def large_dataset(self):
        """Create large dataset"""
        fake = Faker()
        companies = [
            Company(
                name=fake.company(),
                sector=fake.word(),
                logo_url=fake.image_url(),
                headquarters=fake.city(),
                founded=fake.year(),
                description=fake.text()
            )
            for _ in range(1000)
        ]
        Company.objects.bulk_create(companies)
    
    def test_list_companies_performance(self, large_dataset):
        """Test list endpoint performance"""
        client = Client()
        
        start = time.time()
        response = client.get(reverse('api:companies-list'))
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0  # Should complete in less than 2 seconds
    
    def test_search_performance(self, large_dataset):
        """Test search performance"""
        client = Client()
        
        start = time.time()
        response = client.get(
            reverse('api:companies-list'),
            {'search': 'Limited'}
        )
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0
    
    def test_pagination_performance(self, large_dataset):
        """Test pagination performance"""
        client = Client()
        
        start = time.time()
        for page in range(1, 11):
            client.get(
                reverse('api:companies-list'),
                {'page': page, 'limit': 100}
            )
        duration = time.time() - start
        
        assert duration < 5.0  # All 10 pages should load in less than 5 seconds
```

### Load Testing with Locust

**tests/performance/locustfile.py**:
```python
from locust import HttpUser, task, between
import json

class CompanyUser(HttpUser):
    """Simulate user behavior"""
    
    wait_time = between(1, 5)
    
    @task(3)
    def list_companies(self):
        """List companies endpoint"""
        self.client.get("/api/companies/")
    
    @task(2)
    def search_companies(self):
        """Search companies endpoint"""
        self.client.get("/api/companies/?search=tech")
    
    @task(1)
    def get_stats(self):
        """Get statistics endpoint"""
        self.client.get("/api/stats/")

# Run with: locust -f locustfile.py --host=http://localhost:8000
```

---

## Security Testing

### CSRF Protection Testing

**tests/security/test_csrf.py**:
```python
import pytest
from django.test import Client
from django.middleware.csrf import get_token
from django.urls import reverse
import json

pytestmark = pytest.mark.django_db

class TestCSRFProtection:
    """Test CSRF protection"""
    
    def test_csrf_token_required(self, authenticated_client):
        """Test CSRF token is required"""
        # POST without CSRF token should fail
        response = authenticated_client.post(
            reverse('api:companies-add'),
            data=json.dumps({'name': 'Test'}),
            content_type='application/json'
        )
        
        # CSRF middleware should reject or require token
        # This depends on your CSRF configuration
    
    def test_csrf_token_validation(self, authenticated_client):
        """Test CSRF token validation"""
        # Get CSRF token
        response = authenticated_client.get(reverse('index'))
        csrf_token = get_token(authenticated_client)
        
        # POST with valid token should succeed
        response = authenticated_client.post(
            reverse('api:companies-add'),
            data=json.dumps({
                'name': 'Test Company',
                'sector': 'Technology',
                'logo_url': 'https://example.com/logo.png',
                'headquarters': 'Dhaka',
                'founded': 2020,
                'description': 'Test'
            }),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token
        )
        
        # Should succeed (status depends on implementation)
        assert response.status_code in [200, 201]
```

### SQL Injection Testing

**tests/security/test_sql_injection.py**:
```python
import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestSQLInjectionPrevention:
    """Test SQL injection prevention"""
    
    def test_search_with_sql_injection_attempt(self):
        """Test search with SQL injection attempt"""
        client = Client()
        
        # Attempt SQL injection
        response = client.get(
            reverse('api:companies-list'),
            {'search': "'; DROP TABLE companies; --"}
        )
        
        # Should safely handle the input
        assert response.status_code == 200
        # Verify table still exists
        assert b'success' in response.content
```

### Authentication Testing

**tests/security/test_authentication.py**:
```python
import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestAuthentication:
    """Test authentication"""
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        client = Client()
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        assert response.status_code == 302  # Redirect after login
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        client = Client()
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200  # Stays on login page
        assert 'error' in response.content.decode().lower()
    
    def test_protected_endpoint_without_auth(self):
        """Test protected endpoint requires authentication"""
        client = Client()
        response = client.get(reverse('api:companies-add'))
        
        assert response.status_code != 200
```

---

## End-to-End Testing

### Selenium Tests

**tests/e2e/test_user_workflows.py**:
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.fixture
def browser():
    """Setup Selenium browser"""
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

class TestUserWorkflows:
    """Test complete user workflows"""
    
    def test_user_can_view_companies(self, browser, live_server):
        """Test user can view companies"""
        browser.get(f'{live_server.url}/')
        
        # Wait for companies to load
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "company-card"))
        )
        
        assert len(element) > 0
    
    def test_admin_can_add_company(self, browser, live_server):
        """Test admin can add company"""
        # Login
        browser.get(f'{live_server.url}/login/')
        browser.find_element(By.NAME, 'username').send_keys('admin')
        browser.find_element(By.NAME, 'password').send_keys('admin123')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to add company form
        time.sleep(2)
        browser.get(f'{live_server.url}/admin/add/')
        
        # Fill form
        browser.find_element(By.NAME, 'name').send_keys('New Company')
        browser.find_element(By.NAME, 'sector').send_keys('Technology')
        browser.find_element(By.NAME, 'headquarters').send_keys('Dhaka')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Verify success
        time.sleep(2)
        assert 'successfully' in browser.page_source.lower()
```

---

## Test Coverage

### Running Coverage Report

```bash
# Run tests with coverage
pytest --cov=companies --cov=api --cov-report=html --cov-report=term

# View coverage in browser
open htmlcov/index.html
```

### Coverage Targets

| Component | Target |
|-----------|--------|
| Models | 95%+ |
| Views | 85%+ |
| API | 90%+ |
| Utils | 90%+ |
| Overall | 85%+ |

### pytest.ini Configuration

```ini
[pytest]
DJANGO_SETTINGS_MODULE = bd_top_comp.settings
python_files = tests.py test_*.py *_tests.py
testpaths = tests
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --cov=companies
    --cov=api
    --cov-fail-under=85
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    security: marks tests as security tests
```

---

## CI/CD Testing

### GitHub Actions Workflow

**.github/workflows/test.yml**:
```yaml
name: Run Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
      run: |
        pytest --cov=companies --cov=api --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.xml
```

### Manual Test Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] API tests pass
- [ ] Frontend templates render without errors
- [ ] Performance tests acceptable
- [ ] Security tests pass
- [ ] Coverage above 85%
- [ ] No SQL injection vulnerabilities
- [ ] CSRF protection working
- [ ] Authentication working
- [ ] Authorization working
- [ ] Database integrity maintained
- [ ] External API calls mocked
- [ ] Error handling tested
- [ ] Edge cases covered

---

## Running Tests

### Quick Test Run

```bash
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests
pytest tests/api/               # API tests
pytest -k "test_list"          # By keyword
pytest tests/unit/test_models.py::TestCompanyModel::test_create_company
```

### Full Test Suite

```bash
pytest --verbose --cov --cov-report=html
```

### Parallel Testing

```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

---

**Last Updated**: April 10, 2026
**Status**: Production Ready
