from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Company


# ===== Page Views =====

def index(request):
    """Display company listing page"""
    return render(request, 'companies/index.html')


@csrf_exempt
def login_view(request):
    """Handle admin login page"""
    if request.method == 'GET':
        # If already logged in, redirect to home
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'companies/login.html')
    
    elif request.method == 'POST':
        # AJAX login request
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid username or password'
                }, status=401)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request'
            }, status=400)


@login_required(login_url='/login/')
def dashboard(request):
    """Admin dashboard (protected)"""
    return render(request, 'companies/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """Handle admin logout"""
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out'})


# ===== AJAX API Endpoints =====

@require_http_methods(["GET"])
def api_get_companies(request):
    """Get all companies or search by name/sector"""
    search_term = request.GET.get('search', '').strip()
    
    if search_term:
        from django.db.models import Q
        companies = Company.objects.filter(
            Q(name__icontains=search_term) | 
            Q(sector__icontains=search_term)
        )
    else:
        companies = Company.objects.all()
    
    companies_data = [
        {
            'id': c.id,
            'name': c.name,
            'sector': c.sector,
            'logo_url': c.logo_url or '',
            'headquarters': c.headquarters,
            'founded': c.founded,
            'description': c.description or '',
        }
        for c in companies
    ]
    
    return JsonResponse({'companies': companies_data})


@csrf_exempt
@login_required(login_url='/login/')
def api_add_company(request):
    """Add new company (admin only)"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'sector', 'headquarters', 'founded']
        for field in required_fields:
            if field not in data or not str(data.get(field, '')).strip():
                return JsonResponse({
                    'success': False,
                    'message': f'{field.capitalize()} is required'
                }, status=400)
        
        # Check if company already exists
        if Company.objects.filter(name=data['name']).exists():
            return JsonResponse({
                'success': False,
                'message': 'Company with this name already exists'
            }, status=400)
        
        # Create company
        company = Company.objects.create(
            name=data['name'].strip(),
            sector=data['sector'].strip(),
            logo_url=data.get('logo_url', '').strip() or None,
            headquarters=data['headquarters'].strip(),
            founded=int(data['founded']),
            description=data.get('description', '').strip()
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Company added successfully!',
            'company': {
                'id': company.id,
                'name': company.name,
                'sector': company.sector,
                'logo_url': company.logo_url or '',
                'headquarters': company.headquarters,
                'founded': company.founded,
                'description': company.description or '',
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': f'Invalid data: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
@csrf_exempt
@login_required(login_url='/login/')
def api_edit_company(request, id):
    """Edit existing company (admin only)"""
    try:
        company = get_object_or_404(Company, id=id)
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'name' in data and data['name']:
            # Check if new name is unique (excluding current company)
            if Company.objects.filter(name=data['name']).exclude(id=id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'A company with this name already exists'
                }, status=400)
            company.name = data['name'].strip()
        
        if 'sector' in data and data['sector']:
            company.sector = data['sector'].strip()
        
        if 'logo_url' in data:
            company.logo_url = data.get('logo_url', '').strip() or None
        
        if 'headquarters' in data and data['headquarters']:
            company.headquarters = data['headquarters'].strip()
        
        if 'founded' in data and data['founded']:
            company.founded = int(data['founded'])
        
        if 'description' in data:
            company.description = data.get('description', '').strip()
        
        company.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Company updated successfully!',
            'company': {
                'id': company.id,
                'name': company.name,
                'sector': company.sector,
                'logo_url': company.logo_url or '',
                'headquarters': company.headquarters,
                'founded': company.founded,
                'description': company.description or '',
            }
        })
    except Company.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Company not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': f'Invalid data: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
@csrf_exempt
@login_required(login_url='/login/')
def api_delete_company(request, id):
    """Delete company (admin only)"""
    try:
        company = get_object_or_404(Company, id=id)
        company_name = company.name
        company.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Company "{company_name}" deleted successfully!'
        })
    except Company.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Company not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)



