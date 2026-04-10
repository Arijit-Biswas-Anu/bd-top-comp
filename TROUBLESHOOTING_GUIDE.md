# Troubleshooting Guide - Bangladesh Top Companies

Common issues and their solutions for the bd-top-comp application.

---

## Table of Contents

1. [Setup Issues](#setup-issues)
2. [Python/Virtual Environment Issues](#pythonvirtual-environment-issues)
3. [Database Issues](#database-issues)
4. [Django Issues](#django-issues)
5. [API Issues](#api-issues)
6. [Performance Issues](#performance-issues)
7. [Security Issues](#security-issues)
8. [Deployment Issues](#deployment-issues)
9. [Frontend Issues](#frontend-issues)
10. [Debugging Tips](#debugging-tips)

---

## Setup Issues

### Issue: "ModuleNotFoundError: No module named 'django'"

**Symptoms**:
```
ModuleNotFoundError: No module named 'django'
```

**Causes**:
- Dependencies not installed
- Wrong virtual environment activated
- Python path issue

**Solutions**:

1. **Install dependencies**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install from requirements
pip install -r requirements.txt
```

2. **Check Python path**:
```bash
# Verify pip is from venv
which pip  # macOS/Linux
where pip  # Windows

# Should show path inside venv/
```

3. **Reinstall virtual environment**:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Issue: "Command not found: python"

**Symptoms**:
```
zsh: command not found: python
```

**Causes**:
- Python not installed
- Python alias not set
- PATH not configured

**Solutions**:

1. **Check Python installation**:
```bash
which python3
python3 --version
```

2. **Create alias** (if Python 3 exists):
```bash
# Add to ~/.zshrc or ~/.bash_profile
alias python=python3

# Then reload
source ~/.zshrc
```

3. **Install Python**:
```bash
# macOS with Homebrew
brew install python3

# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# Windows: Download from python.org
```

---

## Python/Virtual Environment Issues

### Issue: "pip: command not found"

**Solutions**:

```bash
# Use Python module directly
python3 -m pip install -r requirements.txt

# Or reinstall pip
python3 -m ensurepip --upgrade

# Or with get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

---

### Issue: "Permission denied" when installing packages

**Symptoms**:
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions**:

```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# OR use --user flag (not recommended)
pip install --user -r requirements.txt

# OR fix permissions (not recommended)
sudo chown -R $(whoami) /usr/local/lib/python*
```

---

### Issue: "venv: command not found"

**Solutions**:

```bash
# Install venv module
python3 -m pip install virtualenv

# Create virtual environment with virtualenv
virtualenv venv
source venv/bin/activate

# OR use Python venv directly
python3 -m venv venv
```

---

## Database Issues

### Issue: "Could not connect to database"

**Symptoms**:
```
django.db.utils.OperationalError: could not connect to server
```

**Causes**:
- Database server not running
- Wrong connection URL
- Credentials incorrect
- Network/firewall issue

**Solutions**:

1. **Check database server status**:
```bash
# For PostgreSQL
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql

# For SQLite (local)
ls -la db.sqlite3
```

2. **Verify DATABASE_URL**:
```bash
# Check .env file
cat bd_top_comp/.env | grep DATABASE

# Format should be:
# PostgreSQL: postgresql://user:password@localhost:5432/dbname
# SQLite: sqlite:///db.sqlite3
```

3. **Test database connection**:
```bash
# For PostgreSQL
psql -U your_user -d your_database -c "SELECT 1;"

# For SQLite
python3 -c "import sqlite3; sqlite3.connect('db.sqlite3').execute('SELECT 1;').fetchone()"
```

4. **Check credentials**:
```bash
# PostgreSQL - verify user exists
sudo -u postgres psql -c "\du"

# Verify database exists
sudo -u postgres psql -c "\l"
```

---

### Issue: "Database does not exist"

**Symptoms**:
```
FATAL: database "bd_top_comp" does not exist
```

**Solutions**:

1. **Create database** (PostgreSQL):
```bash
sudo -u postgres createdb bd_top_comp
```

2. **Create user and grant permissions**:
```bash
sudo -u postgres createuser bd_comp_user
sudo -u postgres psql -c "ALTER USER bd_comp_user WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE bd_top_comp TO bd_comp_user;"
```

3. **Or use Django to create tables**:
```bash
python manage.py migrate
```

---

### Issue: "no such table: companies_company"

**Symptoms**:
```
ProgrammingError: relation "companies_company" does not exist
```

**Causes**:
- Migrations not applied
- Database not synced
- Wrong database

**Solutions**:

1. **Apply migrations**:
```bash
# Check migration status
python manage.py migrate --plan

# Apply all migrations
python manage.py migrate

# Apply specific migration
python manage.py migrate companies 0001
```

2. **Force migrations**:
```bash
# In case of migration issues
python manage.py migrate --fake-initial
```

3. **Reset database** (development only):
```bash
# SQLite - delete and recreate
rm db.sqlite3
python manage.py migrate

# PostgreSQL - drop and recreate
sudo -u postgres dropdb bd_top_comp
sudo -u postgres createdb bd_top_comp
python manage.py migrate
```

---

### Issue: "migrate: no changes detected"

**Symptoms**:
```
No changes detected
```

**Causes**:
- Models already migrated
- Migration files already exist
- No model changes

**Solutions**:

```bash
# Check if migration was already applied
python manage.py migrate --plan

# Check migrations directory
ls companies/migrations/

# Force creation (use cautiously)
python manage.py makemigrations --noinput
```

---

## Django Issues

### Issue: "SECRET_KEY not provided"

**Symptoms**:
```
ImproperlyConfigured: Requested setting SECRET_KEY, but settings are not configured
```

**Causes**:
- .env file not found
- DJANGO_SETTINGS_MODULE not set
- SECRET_KEY not in environment

**Solutions**:

1. **Create .env file**:
```bash
cp bd_top_comp/.env.example bd_top_comp/.env

# Edit and add SECRET_KEY
echo "SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" >> bd_top_comp/.env
```

2. **Ensure environment loaded**:
```bash
# In settings.py, add:
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
```

3. **Set DJANGO_SETTINGS_MODULE**:
```bash
export DJANGO_SETTINGS_MODULE=bd_top_comp.settings
python manage.py runserver
```

---

### Issue: "DisallowedHost at /"

**Symptoms**:
```
DisallowedHost at /
Invalid HTTP_HOST header: 'localhost:8000'. You may need to add them to ALLOWED_HOSTS.
```

**Solutions**:

1. **Add to ALLOWED_HOSTS** in settings.py:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*.local']

# Or load from environment
import os
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
```

2. **Set in .env**:
```
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

---

### Issue: "CSRF token missing"

**Symptoms**:
```
Forbidden (403) CSRF verification failed
```

**Causes**:
- CSRF middleware missing
- Token not in form
- Session cookie issue

**Solutions**:

1. **Include CSRF token in template**:
```html
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
    <button type="submit">Submit</button>
</form>
```

2. **Or in API request**:
```javascript
const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrf,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

3. **Verify middleware**:
```python
# In settings.py
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]
```

---

## API Issues

### Issue: "404 Not Found" on API endpoints

**Symptoms**:
```
404 Not Found: /api/companies/
```

**Causes**:
- URLs not configured
- API app not included in urls.py
- Wrong URL path

**Solutions**:

1. **Check urls.py**:
```python
# bd_top_comp/urls.py should have:
from django.urls import path, include

urlpatterns = [
    # ...
    path('api/', include('api.urls', namespace='api')),
    # ...
]
```

2. **Verify API app urls.py exists**:
```bash
ls api/urls.py
```

3. **Check URL patterns in api/urls.py**:
```python
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('companies/', views.list_companies, name='companies-list'),
    path('companies/add/', views.add_company, name='companies-add'),
    # ...
]
```

---

### Issue: "405 Method Not Allowed"

**Symptoms**:
```
405 Method Not Allowed: /api/companies/add/
```

**Causes**:
- View doesn't allow HTTP method
- Wrong HTTP method used
- Decorator missing

**Solutions**:

1. **Check view method restrictions**:
```python
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def add_company(request):
    if request.method == 'POST':
        # Handle POST
        pass
    return JsonResponse({'error': 'Invalid method'}, status=405)
```

2. **Check CORS settings**:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

---

### Issue: "JSON parse error"

**Symptoms**:
```
ValueError: Invalid JSON in request body
```

**Causes**:
- Invalid JSON format
- Content-Type header missing
- Encoding issue

**Solutions**:

1. **Verify JSON format**:
```bash
# Test with curl
curl -X POST http://localhost:8000/api/companies/add/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","sector":"Tech"}'
```

2. **Check Content-Type header**:
```javascript
fetch('/api/companies/add/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'  // Important!
    },
    body: JSON.stringify(data)
});
```

3. **Validate JSON**:
```python
import json
try:
    data = json.loads(request.body)
except json.JSONDecodeError as e:
    return JsonResponse({'error': str(e)}, status=400)
```

---

## Performance Issues

### Issue: "Application is slow"

**Symptoms**:
- Pages load slowly
- API endpoints take > 1 second
- Database queries slow

**Solutions**:

1. **Check database queries**:
```python
# settings.py - enable query logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

2. **Use select_related/prefetch_related**:
```python
# Before
companies = Company.objects.all()  # N+1 queries

# After
companies = Company.objects.select_related().prefetch_related()
```

3. **Add database indexes**:
```python
# models.py
class Company(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    sector = models.CharField(max_length=100, db_index=True)
    founded = models.IntegerField(db_index=True)
```

4. **Enable caching**:
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

### Issue: "High memory usage"

**Symptoms**:
- Memory constantly increasing
- Server crashes due to memory
- Out of memory errors

**Solutions**:

1. **Use pagination**:
```python
from django.core.paginator import Paginator

paginator = Paginator(companies, 50)
page_obj = paginator.get_page(page_num)

# Don't do:
companies = Company.objects.all()  # Loads entire database!
```

2. **Use iterator for large datasets**:
```python
# Efficient for large queries
for company in Company.objects.iterator(chunk_size=1000):
    process_company(company)

# Not efficient:
for company in Company.objects.all():
    process_company(company)
```

3. **Monitor memory**:
```bash
# Check process memory
ps aux | grep python

# Use memory profiler
pip install memory_profiler
python -m memory_profiler script.py
```

---

## Security Issues

### Issue: "DEBUG=True in production"

**Symptoms**:
- Detailed error messages showing code
- SQL queries visible
- Security vulnerability

**Solutions**:

```python
# settings.py
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# .env
DEBUG=False  # In production!
```

---

### Issue: "Database credentials in code"

**Symptoms**:
- Database passwords in git history
- Credentials exposed in error messages

**Solutions**:

1. **Use environment variables**:
```python
# settings.py
DATABASE_URL = os.getenv('DATABASE_URL')

# .env (git ignored)
DATABASE_URL=postgresql://user:password@host:5432/db
```

2. **Never commit .env**:
```bash
# .gitignore
.env
*.env
```

3. **Use secret management**:
```python
# For production, use AWS Secrets Manager, HashiCorp Vault, etc.
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='db-password')
```

---

## Deployment Issues

### Issue: "Static files not loading" (404 errors)

**Symptoms**:
- CSS/JS files return 404
- Images not displaying
- Assets missing in production

**Solutions**:

1. **Collect static files**:
```bash
python manage.py collectstatic --noinput
```

2. **Check STATIC_ROOT**:
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Check directory exists
ls -la staticfiles/
```

3. **Configure Nginx/Apache** to serve static files:
```nginx
location /static/ {
    alias /var/www/bd-top-comp/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

### Issue: "502 Bad Gateway" on production

**Symptoms**:
- Bad Gateway error from Nginx
- Gunicorn not responding

**Solutions**:

1. **Check Gunicorn**:
```bash
sudo systemctl status gunicorn
sudo systemctl restart gunicorn

# Check logs
tail -f /var/log/gunicorn/error.log
```

2. **Check Gunicorn socket**:
```bash
# Verify socket exists
ls -la /run/gunicorn.sock

# Check if Nginx can access it
sudo -u www-data test -S /run/gunicorn.sock && echo "Socket accessible"
```

3. **Restart services**:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

### Issue: "Certificate verification failed"

**Symptoms**:
- SSL certificate errors
- HTTPS not working

**Solutions**:

1. **Verify certificate**:
```bash
# Check certificate expiration
openssl s_client -connect yourdomain.com:443 -showcerts

# Renew with Certbot
sudo certbot renew --force-renewal
```

2. **Check Nginx SSL config**:
```nginx
listen 443 ssl http2;
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

---

## Frontend Issues

### Issue: "CORS errors in browser"

**Symptoms**:
```
Access to XMLHttpRequest blocked by CORS policy
```

**Causes**:
- CORS headers not set
- Frontend domain not allowed
- Credentials not included

**Solutions**:

1. **Configure CORS** in settings.py:
```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://yourdomain.com",
]
```

2. **Allow credentials**:
```python
CORS_ALLOW_CREDENTIALS = True
```

3. **Include credentials in fetch**:
```javascript
fetch('/api/endpoint/', {
    method: 'POST',
    credentials: 'include',  // Important!
    headers: {
        'Content-Type': 'application/json'
    }
});
```

---

### Issue: "Page shows 'Page not found'"

**Symptoms**:
- 404 error
- Blank page
- Wrong URL

**Solutions**:

1. **Debug URL routing**:
```python
# urls.py - add debug view
from django.views.debug import technical_404_response

# Run Django in debug mode to see URL resolution
python manage.py runserver --debug

# Check URLs
python manage.py show_urls
```

2. **Check view exists**:
```python
# urls.py
from . import views

# Verify function exists in views.py
```

---

## Debugging Tips

### Enable Debug Mode

```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Use Django Shell

```bash
python manage.py shell

>>> from companies.models import Company
>>> Company.objects.all()
>>> c = Company.objects.first()
>>> c.name
```

### Check Request/Response

```python
# In view
import logging
logger = logging.getLogger(__name__)

@login_required
def my_view(request):
    logger.debug(f"Request: {request.method} {request.path}")
    logger.debug(f"GET params: {request.GET}")
    logger.debug(f"POST params: {request.POST}")
    
    response = JsonResponse({'success': True})
    logger.debug(f"Response status: {response.status_code}")
    return response
```

### Stack Trace Analysis

When you see an error:
1. Read the error message carefully
2. Look at the stack trace from bottom to top
3. Find the line in your code that caused it
4. Check values of variables at that point
5. Use print() or logging to debug

### Use Django Test Client

```bash
python manage.py shell

>>> from django.test import Client
>>> client = Client()
>>> response = client.get('/')
>>> response.status_code
>>> response.content
```

---

## Getting Help

### Resources

1. **Official Documentation**:
   - Django: https://docs.djangoproject.com/
   - DRF: https://www.django-rest-framework.org/
   - PostgreSQL: https://www.postgresql.org/docs/

2. **Community**:
   - Django Discord: https://discord.gg/django
   - Stack Overflow: Tag with `django`
   - GitHub Issues: Report bugs

3. **Logging and Monitoring**:
   - Sentry: Error tracking
   - New Relic: Performance monitoring
   - DataDog: Infrastructure monitoring

---

**Last Updated**: April 10, 2026
**Status**: Production Ready
