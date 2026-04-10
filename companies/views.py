from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from django.db.models import Q, Count

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
def api_get_stats(request):
    """Get statistics about companies"""
    from django.db.models import Count
    
    # Total companies
    total_companies = Company.objects.count()
    
    # Companies by sector
    sector_stats = Company.objects.values('sector').annotate(count=Count('sector')).order_by('-count')
    
    # Get all sectors for filter dropdown
    all_sectors = Company.objects.values_list('sector', flat=True).distinct().order_by('sector')
    
    return JsonResponse({
        'total_companies': total_companies,
        'sectors': [
            {'name': stat['sector'], 'count': stat['count']} 
            for stat in sector_stats
        ],
        'all_sectors': list(all_sectors),
    })

@require_http_methods(["GET"])
def api_get_companies(request):
    """Get all companies with optional search, filtering, and pagination"""
    search_term = request.GET.get('search', '').strip()
    sector = request.GET.get('sector', '').strip()
    sort_by = request.GET.get('sort', 'name').strip()  # name, founded, sector
    sort_order = request.GET.get('order', 'asc').strip()  # asc or desc
    page = int(request.GET.get('page', '1'))
    limit = int(request.GET.get('limit', '50'))
    
    # Start with all companies
    companies = Company.objects.all()
    
    # Apply search filter
    if search_term:
        from django.db.models import Q
        companies = companies.filter(
            Q(name__icontains=search_term) | 
            Q(sector__icontains=search_term) |
            Q(headquarters__icontains=search_term) |
            Q(description__icontains=search_term)
        )
    
    # Apply sector filter
    if sector:
        companies = companies.filter(sector__iexact=sector)
    
    # Count total before pagination
    total_count = companies.count()
    
    # Apply sorting
    if sort_by == 'founded':
        companies = companies.order_by(f'{"-" if sort_order == "desc" else ""}founded')
    elif sort_by == 'sector':
        companies = companies.order_by(f'{"-" if sort_order == "desc" else ""}sector')
    else:  # default: name
        companies = companies.order_by(f'{"-" if sort_order == "desc" else ""}name')
    
    # Apply pagination
    offset = (page - 1) * limit
    paginated = companies[offset:offset + limit]
    
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
        for c in paginated
    ]
    
    return JsonResponse({
        'companies': companies_data,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total_count,
            'pages': (total_count + limit - 1) // limit  # ceiling division
        }
    })


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


@require_http_methods(["GET"])
@login_required(login_url='/login/')
def api_export_csv(request):
    """Export companies to CSV based on current filters"""
    try:
        # Get filter parameters from query string
        search_term = request.GET.get('search', '').strip()
        sector = request.GET.get('sector', '').strip()
        sort_by = request.GET.get('sort', 'name').strip()
        sort_order = request.GET.get('order', 'asc').strip()
        
        # Start with all companies
        companies = Company.objects.all()
        
        # Apply search filter
        if search_term:
            companies = companies.filter(
                Q(name__icontains=search_term) | 
                Q(sector__icontains=search_term) |
                Q(headquarters__icontains=search_term) |
                Q(description__icontains=search_term)
            )
        
        # Apply sector filter
        if sector:
            companies = companies.filter(sector__iexact=sector)
        
        # Apply sorting
        if sort_by == 'founded':
            companies = companies.order_by(f'{"-" if sort_order == "desc" else ""}founded')
        elif sort_by == 'sector':
            companies = companies.order_by(f'{"-" if sort_order == "desc" else ""}sector')
        else:
            companies = companies.order_by(f'{"-" if sort_order == "desc" else ""}name')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="companies.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow([
            'Company Name',
            'Sector',
            'Headquarters',
            'Founded',
            'Description',
            'Added On',
            'Last Updated'
        ])
        
        # Write data rows
        for company in companies:
            writer.writerow([
                company.name,
                company.sector,
                company.headquarters,
                company.founded,
                company.description or '',
                company.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                company.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error exporting CSV: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
def api_export_summary(request):
    """Export statistics summary"""
    try:
        total_companies = Company.objects.count()
        sector_stats = Company.objects.values('sector').annotate(count=Count('sector')).order_by('-count')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="companies_summary.csv"'
        
        writer = csv.writer(response)
        
        # Summary header
        writer.writerow(['Bangladesh Top Companies - Summary Report'])
        writer.writerow(['Generated on', __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Overall statistics
        writer.writerow(['OVERALL STATISTICS'])
        writer.writerow(['Total Companies', total_companies])
        writer.writerow(['Total Sectors', sector_stats.count()])
        writer.writerow([])
        
        # Sector breakdown
        writer.writerow(['SECTOR BREAKDOWN'])
        writer.writerow(['Sector', 'Count'])
        for sector in sector_stats:
            writer.writerow([sector['sector'], sector['count']])
        
        return response
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error exporting summary: {str(e)}'
        }, status=400)



