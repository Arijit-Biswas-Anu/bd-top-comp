# Contributing Guide - Bangladesh Top Companies

Thank you for your interest in contributing to the bd-top-comp project! This guide will help you understand our development workflow and how to make meaningful contributions.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code of Conduct](#code-of-conduct)
4. [How to Contribute](#how-to-contribute)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Git Workflow](#git-workflow)
7. [Testing Requirements](#testing-requirements)
8. [Documentation](#documentation)
9. [Pull Request Process](#pull-request-process)
10. [Review Process](#review-process)

---

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- Basic knowledge of Django
- PostgreSQL (for production-like setup)

### Key Technologies

- **Backend**: Django Web Framework
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Testing**: pytest, factory_boy
- **Frontend**: HTML/CSS/JavaScript (Vanilla or Vue.js)

---

## Development Setup

### Fork and Clone

```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/bd-top-comp.git
cd bd-top-comp

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_REPO/bd-top-comp.git
```

### Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

### Install Dependencies

```bash
# Install development requirements
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Configure Environment

```bash
# Copy example environment file
cp bd_top_comp/.env.example bd_top_comp/.env

# Edit .env with your local settings
nano bd_top_comp/.env
```

### Database Setup

```bash
# Create PostgreSQL database
createdb bd_top_comp_dev

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata initial_companies.json
```

### Run Development Server

```bash
# Start Django server
python manage.py runserver

# Visit http://localhost:8000
```

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Examples of behavior that contributes to a positive environment**:
- Using welcoming and inclusive language
- Being respectful of differing opinions and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Examples of unacceptable behavior**:
- Use of sexualized language or imagery
- Trolling, insulting/derogatory comments
- Harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of inappropriate behavior can be reported to the project maintainers. All complaints will be reviewed and investigated fairly.

---

## How to Contribute

### Types of Contributions

We welcome all types of contributions:

1. **Bug Reports**: Report issues you find
2. **Feature Requests**: Suggest new features
3. **Code Improvements**: Enhance existing code
4. **Documentation**: Improve guides and README
5. **Tests**: Add or improve test coverage
6. **Translations**: Help localize the application

### Reporting Bugs

**Before reporting a bug**:
- Check if issue already exists
- Test with latest version
- Provide clear reproduction steps

**Bug report should include**:
```
**Describe the bug**
Clear description of what happened

**Steps to reproduce**
1. Go to...
2. Click on...
3. See error...

**Expected behavior**
What should happen

**Actual behavior**
What actually happens

**Environment**
- Python version
- Django version
- OS
- Browser (if frontend issue)

**Error message**
Full error traceback if applicable

**Screenshots**
If applicable
```

### Suggesting Features

**Feature request should include**:
```
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
How should the feature work?

**Describe alternatives you've considered**
Are there other approaches?

**Additional context**
Any other relevant information
```

---

## Code Style Guidelines

### Python Code Style

We follow PEP 8. Use tools to enforce:

```bash
# Check code style
flake8 companies/ api/ bd_top_comp/

# Format automatically
black companies/ api/ bd_top_comp/

# Import sorting
isort companies/ api/ bd_top_comp/
```

### Python Style Example

```python
# Good
class CompanyService:
    """Service for managing companies."""
    
    def __init__(self, repository):
        self.repository = repository
    
    def get_companies_by_sector(self, sector: str) -> List[Company]:
        """
        Get all companies in a specific sector.
        
        Args:
            sector: The sector name to filter by
            
        Returns:
            List of companies in the sector
            
        Raises:
            ValueError: If sector is empty
        """
        if not sector:
            raise ValueError("Sector cannot be empty")
        
        return self.repository.filter(sector=sector)

# Bad
def getCompanies(sec):  # Poor naming, no type hints
    if sec == '':
        return []
    companies = Company.objects.filter(sector=sec)  # No docstring
    return companies
```

### Django Conventions

```python
# Models
class Company(models.Model):
    """Model representing a company."""
    
    name = models.CharField(max_length=200, unique=True)
    sector = models.CharField(max_length=100, db_index=True)
    founded = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']
    
    def __str__(self):
        return self.name

# Views
class CompanyListView(generic.ListView):
    """Display list of companies."""
    
    model = Company
    context_object_name = 'companies'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter companies by search query."""
        queryset = Company.objects.all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset

# URLs
urlpatterns = [
    path('companies/', views.CompanyListView.as_view(), name='company-list'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company-detail'),
]
```

### JavaScript/HTML Style

```javascript
// Good
function fetchCompanies(filters = {}) {
    const params = new URLSearchParams(filters);
    return fetch(`/api/companies/?${params}`)
        .then(response => response.json())
        .catch(error => console.error('Error:', error));
}

// Use semicolons, meaningful variable names, comments
const companies = [];
let isLoading = false;

function displayCompanies(data) {
    // Clear existing companies
    companies.length = 0;
    companies.push(...data);
    renderList();
}
```

```html
<!-- Good -->
<div class="company-card" id="company-{{ company.id }}">
    <h3>{{ company.name }}</h3>
    <p class="sector">{{ company.sector }}</p>
    <button 
        class="btn btn-primary"
        onclick="viewDetails({{ company.id }})"
        aria-label="View {{ company.name }} details"
    >
        View Details
    </button>
</div>

<!-- Bad -->
<div onclick="viewDetails(this.id)">
    <h3 id="comp">{{ company.name }}</h3>
</div>
```

### CSS/SCSS

```css
/* Use BEM naming convention */
.company-card {
    background: white;
    border: 1px solid #ddd;
    padding: 16px;
}

.company-card__title {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 8px 0;
}

.company-card__sector {
    color: #666;
    font-size: 14px;
}

.company-card--featured {
    border-color: #007bff;
    box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
}
```

---

## Git Workflow

### Branch Naming

Use descriptive branch names with prefixes:

```bash
# Feature
git checkout -b feature/add-company-export

# Bug fix
git checkout -b bugfix/fix-pagination-issue

# Documentation
git checkout -b docs/update-api-docs

# Refactoring
git checkout -b refactor/optimize-queries
```

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Build/dependency changes

**Examples**:

```bash
# Good commits
git commit -m "feat(companies): add bulk import from CSV file"
git commit -m "fix(api): correct pagination calculation
- Previously, total_pages was incorrectly calculated
- Now correctly divides total_results by per_page"
git commit -m "docs: add API authentication examples"
git commit -m "refactor(models): optimize company queries with select_related"

# Bad commits
git commit -m "fixed it"
git commit -m "updated code"
git commit -m "changes"
```

### Before Committing

```bash
# Run tests
pytest

# Check code style
flake8 .
black --check .
isort --check .

# Pre-commit hook (recommended)
pre-commit run --all-files
```

---

## Testing Requirements

### Test Coverage

- **Minimum coverage**: 85%
- **Target coverage**: 90%+

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run with coverage report
pytest --cov=companies --cov=api --cov-report=html

# Run tests matching pattern
pytest -k "test_search"

# Run with detailed output
pytest -vv
```

### Adding Tests

**When adding features, include tests**:

```python
# tests/unit/test_new_feature.py
import pytest
from django.test import TestCase
from myapp.models import MyModel

pytestmark = pytest.mark.django_db

class TestNewFeature:
    """Test new feature."""
    
    def test_feature_works(self):
        """Test that feature works as expected."""
        result = perform_feature()
        assert result is True
    
    def test_edge_case(self):
        """Test edge case."""
        with pytest.raises(ValueError):
            perform_feature(invalid_input)
```

### Test Guidelines

- Write tests for new features
- Update existing tests when modifying code
- Delete tests for removed features
- Aim for high coverage on critical paths
- Test error cases, not just happy paths

---

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def calculate_company_metrics(companies: List[Company]) -> Dict[str, Any]:
    """
    Calculate comprehensive metrics for a list of companies.
    
    This function analyzes companies and returns various statistical
    measures including distribution and averages.
    
    Args:
        companies: List of Company objects to analyze
        
    Returns:
        Dictionary containing:
            - 'total': Total number of companies
            - 'by_sector': Dict of sector -> count
            - 'avg_founded': Average founding year
            
    Raises:
        ValueError: If companies list is empty
        TypeError: If companies contains non-Company objects
        
    Examples:
        >>> companies = [Company(...), Company(...)]
        >>> metrics = calculate_company_metrics(companies)
        >>> print(metrics['total'])
        2
    """
    if not companies:
        raise ValueError("Companies list cannot be empty")
    
    # Implementation
    return metrics
```

### Updating Documentation

When adding features:

1. **Update API docs** if adding/changing endpoints
2. **Update README** if feature is user-facing
3. **Update guides** if affecting deployment or usage
4. **Add docstrings** to all functions and classes
5. **Update CHANGELOG** with summary

---

## Pull Request Process

### Before Creating PR

1. **Update from upstream**:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Run tests locally**:
```bash
pytest
black .
flake8 .
```

3. **Create feature branch**:
```bash
git checkout -b feature/my-feature
```

### Creating PR

1. **Push to your fork**:
```bash
git push origin feature/my-feature
```

2. **Create PR on GitHub** with:
   - Clear title following conventional commits
   - Detailed description of changes
   - Reference to related issues
   - Screenshots/video if UI changes
   - Database migration notice if applicable

3. **PR Description Template**:
```markdown
## Description
Brief summary of changes

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Breaking change

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Screenshots
If UI changes, add screenshots

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Changes are backward compatible
```

---

## Review Process

### What Reviewers Look For

1. **Code Quality**
   - Follows style guidelines
   - Proper error handling
   - No code duplication

2. **Functionality**
   - Feature works as intended
   - Edge cases handled
   - No breaking changes

3. **Testing**
   - Tests are comprehensive
   - Coverage maintained/improved
   - Tests pass

4. **Documentation**
   - Code is well-documented
   - User-facing docs updated
   - Examples provided

### Responding to Reviews

- **Thank reviewers** for their feedback
- **Ask questions** if feedback is unclear
- **Don't take it personally** - it's about improving code
- **Make changes** or explain why you disagree
- **Request re-review** after making changes

### Example Feedback Response

```markdown
Thanks for the review! 

On point 1: I've updated the error handling to check for empty lists.
On point 2: Good catch! I've added a test for this edge case now.
On point 3: I'm not sure about this one. Could you clarify what you mean?

I've pushed the changes. Please take another look when you have time.
```

---

## Becoming a Maintainer

### Requirements

- **Consistent contributions** (50+ merged PRs or equivalent)
- **Good judgment** in code reviews
- **Responsiveness** to issues and PRs
- **Alignment** with project vision

### Responsibilities

- Review and merge PRs
- Respond to issues
- Help other contributors
- Maintain code quality
- Update documentation
- Plan releases

### Current Maintainers

- Core Team (@github-handle)

---

## Release Process

### Version Numbering

We follow Semantic Versioning: `MAJOR.MINOR.PATCH`

- `MAJOR`: Incompatible API changes
- `MINOR`: New functionality, backward compatible
- `PATCH`: Bug fixes

### Steps to Release

1. **Update version**:
```python
# bd_top_comp/__init__.py
__version__ = "1.0.0"
```

2. **Update CHANGELOG.md**:
```markdown
## [1.0.0] - 2026-04-10

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix 1
- Bug fix 2

### Changed
- Behavioral change 1

### Deprecated
- Old feature X (will be removed in 2.0.0)
```

3. **Tag release**:
```bash
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

4. **Deploy** to staging and production

---

## Getting Help

### Resources

- **Email**: dev@example.com
- **Discord**: [Join our Discord](https://discord.gg/example)
- **Discussions**: [GitHub Discussions](https://github.com/example/discussions)
- **Issues**: [GitHub Issues](https://github.com/example/issues)

### Asking Questions

When asking for help:
1. Provide context and what you've tried
2. Share error messages and logs
3. Link to relevant code/issues
4. Be specific about what you need help with

---

## Recognition

We recognize all contributions through:
- **Contributors list** in README
- **Credits** in release notes
- **Special thanks** for major features

Thank you for being part of this project! 🎉

---

**Last Updated**: April 10, 2026
**Status**: Active
