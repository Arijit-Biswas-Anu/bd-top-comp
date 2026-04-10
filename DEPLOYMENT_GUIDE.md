# Deployment Guide - Bangladesh Top Companies

Complete guide for deploying the bd-top-comp application to various environments.

---

## Table of Contents

1. [Development Deployment](#development-deployment)
2. [Staging Deployment](#staging-deployment)
3. [Production Deployment](#production-deployment)
4. [Database Migrations](#database-migrations)
5. [Environment Configuration](#environment-configuration)
6. [Security Setup](#security-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)
10. [Cloud Deployments](#cloud-deployments)

---

## Development Deployment

### Local Setup

**Prerequisites**:
- Python 3.9+
- pip or pip3
- Virtual environment tool (venv)
- Git

**Steps**:

1. **Clone the repository**:
```bash
git clone <repository-url>
cd prev_lab_proj
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp bd_top_comp/.env.example bd_top_comp/.env
# Edit .env with your local settings
```

5. **Run migrations**:
```bash
python manage.py migrate
```

6. **Create superuser**:
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@localhost
# Password: admin123
```

7. **Load initial data** (optional):
```bash
python manage.py loaddata initial_companies.json
```

8. **Collect static files** (optional):
```bash
python manage.py collectstatic --noinput
```

9. **Run development server**:
```bash
python manage.py runserver
```

Access at: `http://localhost:8000`

### Development Settings

**.env.development**:
```
DEBUG=True
SECRET_KEY=development-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,*.local
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=console
ENVIRONMENT=development
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Staging Deployment

### Prerequisites

- Ubuntu 20.04+ or similar server
- Python 3.9+
- PostgreSQL 12+
- Gunicorn
- Nginx
- Supervisor (optional)
- SSL Certificate

### Setup Steps

1. **Server preparation**:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.9 python3-pip python3-venv \
    postgresql postgresql-contrib nginx supervisor
```

2. **Clone repository**:
```bash
cd /var/www
sudo git clone <repository-url> bd-top-comp
sudo chown -R $USER:$USER bd-top-comp
cd bd-top-comp
```

3. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure PostgreSQL**:
```bash
sudo -u postgres createdb bd_top_comp_staging
sudo -u postgres createuser bd_comp_user
sudo -u postgres psql -c "ALTER USER bd_comp_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE bd_top_comp_staging TO bd_comp_user;"
```

5. **Environment configuration**:
```bash
cat > bd_top_comp/.env << 'EOF'
DEBUG=False
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=staging.yourdomain.com,api.staging.yourdomain.com
DATABASE_URL=postgresql://bd_comp_user:your_secure_password@localhost:5432/bd_top_comp_staging
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ENVIRONMENT=staging
CORS_ALLOWED_ORIGINS=https://staging.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
EOF
```

6. **Database migrations**:
```bash
python manage.py migrate
```

7. **Create superuser**:
```bash
python manage.py createsuperuser
```

8. **Collect static files**:
```bash
python manage.py collectstatic --noinput
```

### Gunicorn Configuration

**gunicorn_config.py**:
```python
import multiprocessing

bind = "127.0.0.1:8001"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
access_log = "/var/log/gunicorn/access.log"
error_log = "/var/log/gunicorn/error.log"
log_level = "info"
```

### Supervisor Configuration

**/etc/supervisor/conf.d/bd-top-comp.conf**:
```ini
[program:bd-top-comp]
directory=/var/www/bd-top-comp
command=/var/www/bd-top-comp/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --chdir /var/www/bd-top-comp \
    bd_top_comp.wsgi:application
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gunicorn/app.log
```

**Enable supervisor**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start bd-top-comp
```

### Nginx Configuration

**/etc/nginx/sites-available/bd-top-comp-staging**:
```nginx
upstream gunicorn {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name staging.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name staging.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/staging.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/staging.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/bd-top-comp/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/bd-top-comp/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**Enable nginx site**:
```bash
sudo ln -s /etc/nginx/sites-available/bd-top-comp-staging \
    /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Production Deployment

### Architecture

```
    ┌─────────────────┐
    │   CDN / Cache   │
    │  (Cloudflare)   │
    └────────┬────────┘
             │
    ┌────────▼────────────┐
    │      Nginx Reverse  │
    │      Proxy (SSL)    │
    └────────┬────────────┘
             │
    ┌────────▼────────────────┐
    │  Gunicorn Workers Pool  │
    │   (Django App, 4-8)     │
    └────────┬────────────────┘
             │
    ┌────────▼────────────────┐
    │   PostgreSQL Database   │
    │  (Master + Replica)     │
    └─────────────────────────┘
             │
         ┌───┴────┐
         │        │
    ┌────▼──┐ ┌──▼────┐
    │Backup │ │ Cache  │
    │(S3)   │ │ (Redis)│
    └───────┘ └────────┘
```

### Prerequisites

- AWS EC2 (or equivalent cloud provider)
- Application Load Balancer (ALB)
- RDS PostgreSQL
- Redis (ElastiCache or self-hosted)
- S3 for media/backups
- CloudFront or similar CDN
- SSL certificates (ACM)
- Monitoring (CloudWatch, New Relic, DataDog)

### AWS Deployment Steps

1. **Set up CloudFormation stack** (infrastructure as code):
```yaml
# Infrastructure template
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  InstanceType:
    Type: String
    Default: t3.medium
  # ... more parameters
Resources:
  # Define VPC, RDS, ALB, etc.
```

2. **Configure RDS PostgreSQL**:
```bash
# Create RDS instance via AWS CLI
aws rds create-db-instance \
    --db-instance-identifier bd-top-comp-prod \
    --db-instance-class db.t3.small \
    --engine postgres \
    --master-username bduser \
    --allocated-storage 50
```

3. **Set up ElastiCache Redis**:
```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id bd-top-comp-cache \
    --engine redis \
    --cache-node-type cache.t3.micro
```

4. **Configure EC2 instances**:
```bash
# Launch instances with auto-scaling group
aws autoscaling create-launch-configuration \
    --launch-configuration-name bd-top-comp-lc \
    --image-id ami-xxxxxxxxx \
    --instance-type t3.medium
```

5. **Environment setup**:
```bash
cat > bd_top_comp/.env.production << 'EOF'
DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/bd_top_comp
REDIS_URL=redis://elasticache-endpoint:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-key
ENVIRONMENT=production
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
AWS_STORAGE_BUCKET_NAME=bd-top-comp-media
AWS_S3_REGION_NAME=us-east-1
USE_S3=True
DEBUG_PROPAGATE_EXCEPTIONS=False
LOGGING_LEVEL=info
SENTRY_DSN=https://your-sentry-dsn
EOF
```

6. **Deploy with CI/CD** (GitHub Actions example):
```yaml
# .github/workflows/deploy-prod.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to AWS
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          # Deployment scripts
```

---

## Database Migrations

### Running Migrations

```bash
# Create migration files for changes
python manage.py makemigrations

# Check migration plan
python manage.py migrate --plan

# Apply migrations
python manage.py migrate

# Apply specific migration
python manage.py migrate app_name 0001
```

### Database Backup

**Before production migrations**:
```bash
# PostgreSQL backup
pg_dump -U bd_comp_user bd_top_comp_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# S3 backup
aws s3 cp backup_*.sql s3://bd-top-comp-backups/
```

### Zero-Downtime Migration Strategy

For production:

1. **Pre-deployment**:
   - Take database snapshot
   - Test migrations on staging
   - Prepare rollback plan

2. **During deployment**:
   - Run migrations before deploying code
   - Use feature flags for model changes
   - Keep backward-compatible changes

3. **Post-deployment**:
   - Monitor application logs
   - Verify data integrity
   - Keep migration executable for rollback

---

## Environment Configuration

### Settings by Environment

| Setting | Dev | Staging | Production |
|---------|-----|---------|------------|
| DEBUG | True | False | False |
| ALLOWED_HOSTS | localhost | staging.domain | yourdomain.com |
| Cache | locmem | redis | redis |
| Database | SQLite | PostgreSQL | PostgreSQL |
| Media | local | S3 | S3 |
| Email | Console | SMTP | SendGrid/SES |
| SSL | No | Let's Encrypt | AWS ACM |
| Logging | Console | File + Cloud | CloudWatch |

### Environment Variables Template

**.env**:
```
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Cache & Session
REDIS_URL=redis://host:6379/0
CACHE_TTL=3600

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password

# AWS S3
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=bucket-name
AWS_S3_REGION_NAME=us-east-1

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=info
```

---

## Security Setup

### SSL/TLS Certificate Setup

**Using Let's Encrypt (Certbot)**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

**Auto-renewal with cron**:
```bash
# Add to crontab
0 1 * * * certbot renew --quiet && systemctl reload nginx
```

### Django Security Settings

**settings.py**:
```python
# HTTPS/SSL
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Headers
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
}

# Authentication
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

### Database Security

```sql
-- Create read-only role for backups
CREATE ROLE backup_user WITH LOGIN PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE bd_top_comp TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw deny 5432/tcp     # PostgreSQL (internal only)
```

---

## Monitoring & Maintenance

### Application Monitoring

**Health check endpoint**:
```python
# Add to urls.py
from django.http import JsonResponse

def health(request):
    return JsonResponse({'status': 'ok', 'version': '1.0'})
```

**Nginx health check**:
```nginx
location /health/ {
    access_log off;
}
```

### Log Aggregation

**Centralized logging with ELK Stack**:
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        },
    },
    'handlers': {
        'elasticsearch': {
            'level': 'INFO',
            'class': 'pythonjsonlogger.handlers.ElasticsearchHandler',
            'hosts': ['elasticsearch:9200'],
        },
    },
    'root': {
        'handlers': ['elasticsearch'],
        'level': 'INFO',
    }
}
```

### Performance Monitoring

```python
# Middleware for performance tracking
import time
from django.utils.deprecation import MiddlewareMixin

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        duration = time.time() - request.start_time
        if duration > 1.0:  # Log slow requests
            logger.warning(f"Slow request: {request.path} ({duration}s)")
        return response
```

### Database Maintenance

```bash
# Weekly maintenance task
# Analyze and vacuum PostgreSQL
psql -U bd_comp_user -d bd_top_comp -c "VACUUM ANALYZE;"

# Update statistics
psql -U bd_comp_user -d bd_top_comp -c "ANALYZE;"

# Reindex tables
psql -U bd_comp_user -d bd_top_comp -c "REINDEX DATABASE bd_top_comp;"
```

### Automated Backups

**Backup script**:
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/var/backups/bd-top-comp"
TODAY=$(date +%Y%m%d)

# Database backup
pg_dump -U bd_comp_user bd_top_comp | gzip > $BACKUP_DIR/db_$TODAY.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/db_$TODAY.sql.gz s3://bd-top-comp-backups/

# Keep only 30 days of backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

**Cron job**:
```
# Daily backup at 2 AM
0 2 * * * /opt/scripts/backup.sh
```

---

## Troubleshooting

### Common Issues

#### 1. 502 Bad Gateway

**Check Gunicorn**:
```bash
sudo supervisorctl status bd-top-comp
sudo supervisorctl restart bd-top-comp
tail -f /var/log/gunicorn/error.log
```

#### 2. Database Connection Error

```bash
# Test connection
psql -h localhost -U bd_comp_user -d bd_top_comp -c "SELECT 1;"

# Check environment variables
echo $DATABASE_URL
```

#### 3. Static Files Not Loading

```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Check permissions
sudo chown -R www-data:www-data /var/www/bd-top-comp/staticfiles/
```

#### 4. High Memory Usage

```bash
# Restart Gunicorn workers
sudo supervisorctl restart bd-top-comp

# Check process memory
ps aux | grep gunicorn
```

#### 5. Slow Database Queries

```bash
# Enable slow query log
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 second
SELECT pg_reload_conf();

# Analyze queries
EXPLAIN ANALYZE SELECT * FROM companies;
```

---

## Rollback Procedures

### Code Rollback

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or reset to specific commit
git reset --hard commit-hash
git push -f origin main
```

### Database Rollback

```bash
# Reverse specific migration
python manage.py migrate app_name 0001

# From backup
psql -U bd_comp_user bd_top_comp < backup_YYYYMMDD_HHMMSS.sql
```

### Deployment Rollback Script

```bash
#!/bin/bash
# rollback.sh
git reset --hard HEAD~1
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart bd-top-comp
```

---

## Cloud Deployments

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bd_top_comp.wsgi:application"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: bd_top_comp
      POSTGRES_USER: bduser
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://bduser:password@db:5432/bd_top_comp
    depends_on:
      - db
    command: gunicorn --bind 0.0.0.0:8000 bd_top_comp.wsgi:application

volumes:
  postgres_data:
```

### Heroku Deployment

**Procfile**:
```
web: gunicorn bd_top_comp.wsgi
worker: celery -A bd_top_comp worker -l info
release: python manage.py migrate
```

```bash
heroku create bd-top-comp-app
git push heroku main
heroku run python manage.py createsuperuser
```

### Railway.app Deployment

```yaml
# railway.toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "python manage.py migrate && gunicorn bd_top_comp.wsgi"
```

### Render Deployment

(Similar to Railway with build commands)

---

## Monitoring & Alerting

### Sentry for Error Tracking

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    environment=ENVIRONMENT
)
```

### Uptime Monitoring

- Pingdom
- UptimeRobot
- AWS CloudWatch

Configure to check `/api/stats/` endpoint every 5 minutes.

---

## Checklist for First Production Deployment

- [ ] Database backups configured
- [ ] SSL certificates installed and auto-renewal enabled
- [ ] Environment variables securely set
- [ ] Static files collected and served via CDN
- [ ] Logging and monitoring configured
- [ ] Database indexes created
- [ ] Admin user created
- [ ] Superuser password changed
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured
- [ ] CSRF and CORS settings configured
- [ ] Email service configured
- [ ] Health check endpoint working
- [ ] Load testing completed
- [ ] Security headers configured
- [ ] Firewall rules configured
- [ ] Backup and restore tested
- [ ] Rollback procedures documented
- [ ] Monitoring alerts configured
- [ ] Disaster recovery plan in place

---

**Last Updated**: April 10, 2026
**Status**: Production Ready
