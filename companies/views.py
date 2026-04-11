from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from django.db.models import Q, Count

from .models import Company, Startup


# ===== Page Views =====

def index(request):
    """Display EdTech startups listing page"""
    return render(request, 'companies/index_startups.html')


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


# ===== PHASE 13B: ANALYTICS ENDPOINTS =====

@require_http_methods(["GET"])
@login_required(login_url='/login/')
def api_analytics_dashboard(request):
    """Get comprehensive analytics for dashboard"""
    try:
        companies = Company.objects.all()
        
        # Calculate statistics
        total_companies = companies.count()
        total_sectors = companies.values('sector').distinct().count()
        
        # Founded year range
        founded_years = companies.exclude(founded__isnull=True).values_list('founded', flat=True)
        if founded_years:
            min_year = min(founded_years)
            max_year = max(founded_years)
            avg_year = sum(founded_years) / len(founded_years)
        else:
            min_year = max_year = avg_year = None
        
        # Sector distribution
        sector_distribution = list(
            companies.values('sector').annotate(count=Count('sector')).order_by('-count')
        )
        
        # Companies by founded decade
        decade_stats = {}
        for company in companies.filter(founded__isnull=False):
            decade = (company.founded // 10) * 10
            decade_key = f"{decade}s"
            decade_stats[decade_key] = decade_stats.get(decade_key, 0) + 1
        
        # Recently added companies (last 5)
        recent_companies = companies.order_by('-created_at')[:5]
        recent_list = [{
            'id': c.id,
            'name': c.name,
            'sector': c.sector,
            'founded': c.founded,
            'created_at': c.created_at.strftime('%Y-%m-%d')
        } for c in recent_companies]
        
        # Top sectors
        top_sectors = sorted(sector_distribution, key=lambda x: x['count'], reverse=True)[:5]
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total_companies': total_companies,
                'total_sectors': total_sectors,
                'avg_founded_year': round(avg_year) if avg_year else None,
                'founded_year_range': {
                    'min': min_year,
                    'max': max_year
                }
            },
            'sector_distribution': sector_distribution,
            'decade_stats': decade_stats,
            'recent_companies': recent_list,
            'top_sectors': top_sectors
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching analytics: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
@login_required(login_url='/login/')
def api_company_comparison(request):
    """Compare multiple companies"""
    try:
        company_ids = request.GET.getlist('ids', [])
        
        if not company_ids:
            # Compare all companies if no specific IDs provided
            companies = Company.objects.all()
        else:
            companies = Company.objects.filter(id__in=company_ids)
        
        comparison_data = [{
            'id': c.id,
            'name': c.name,
            'sector': c.sector,
            'headquarter': c.headquarters,
            'founded': c.founded,
            'description': c.description[:100] + '...' if c.description and len(c.description) > 100 else c.description,
            'created_at': c.created_at.strftime('%Y-%m-%d'),
            'updated_at': c.updated_at.strftime('%Y-%m-%d')
        } for c in companies.order_by('name')]
        
        # Calculate comparison metrics
        if companies:
            founded_years = [c.founded for c in companies if c.founded]
            comparison_metrics = {
                'total': companies.count(),
                'avg_founded': round(sum(founded_years) / len(founded_years)) if founded_years else None,
                'oldest': min(founded_years) if founded_years else None,
                'newest': max(founded_years) if founded_years else None,
                'sectors': list(companies.values_list('sector', flat=True).distinct())
            }
        else:
            comparison_metrics = {}
        
        return JsonResponse({
            'success': True,
            'companies': comparison_data,
            'metrics': comparison_metrics
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error comparing companies: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
@login_required(login_url='/login/')
def api_sector_insights(request):
    """Get detailed insights for a specific sector"""
    try:
        sector = request.GET.get('sector', '').strip()
        
        if not sector:
            return JsonResponse({
                'success': False,
                'message': 'Sector parameter required'
            }, status=400)
        
        companies = Company.objects.filter(sector__iexact=sector)
        
        if not companies:
            return JsonResponse({
                'success': False,
                'message': f'No companies found in sector: {sector}'
            }, status=404)
        
        # Calculate metrics
        founded_years = [c.founded for c in companies if c.founded]
        company_list = [{
            'id': c.id,
            'name': c.name,
            'founded': c.founded,
            'headquarters': c.headquarters
        } for c in companies.order_by('name')]
        
        insights = {
            'sector': sector,
            'company_count': companies.count(),
            'companies': company_list,
            'founded_range': {
                'oldest': min(founded_years) if founded_years else None,
                'newest': max(founded_years) if founded_years else None,
                'average': round(sum(founded_years) / len(founded_years)) if founded_years else None
            },
            'decade_distribution': {
                f"{(year // 10) * 10}s": sum(1 for y in founded_years if (y // 10) * 10 == (year // 10) * 10)
                for year in founded_years
            }
        }
        
        return JsonResponse({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching sector insights: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
@login_required(login_url='/login/')
def api_growth_analysis(request):
    """Analyze company growth over time (by addition date)"""
    try:
        from django.db.models.functions import TruncDate
        from django.db.models import Count
        import datetime
        
        # Get last 30 days of additions
        thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        
        daily_additions = Company.objects.filter(
            created_at__gte=thirty_days_ago
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        # Format for chart
        growth_data = [{
            'date': str(item['date']),
            'additions': item['count']
        } for item in daily_additions]
        
        # Calculate growth metrics
        total_additions = sum(item['count'] for item in daily_additions)
        avg_daily = round(total_additions / max(1, len(growth_data))) if growth_data else 0
        
        return JsonResponse({
            'success': True,
            'growth_data': growth_data,
            'metrics': {
                'total_additions_30d': total_additions,
                'avg_daily_additions': avg_daily,
                'days_with_additions': len(growth_data)
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error analyzing growth: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
@login_required(login_url='/login/')
def api_descriptive_stats(request):
    """Get descriptive statistics about companies"""
    try:
        companies = Company.objects.all()
        
        founded_years = [c.founded for c in companies if c.founded]
        
        if not founded_years:
            return JsonResponse({
                'success': False,
                'message': 'No founded year data available'
            }, status=400)
        
        founded_years.sort()
        n = len(founded_years)
        
        # Calculate statistics
        mean = sum(founded_years) / n
        median = (founded_years[n // 2] + founded_years[(n - 1) // 2]) / 2 if n > 0 else 0
        variance = sum((x - mean) ** 2 for x in founded_years) / n if n > 0 else 0
        std_dev = variance ** 0.5
        
        stats = {
            'founded_year_statistics': {
                'count': n,
                'mean': round(mean, 2),
                'median': round(median, 2),
                'std_dev': round(std_dev, 2),
                'min': min(founded_years),
                'max': max(founded_years),
                'range': max(founded_years) - min(founded_years),
                'q1': sorted(founded_years)[n // 4] if n > 0 else None,
                'q3': sorted(founded_years)[3 * n // 4] if n > 0 else None
            },
            'sector_statistics': {
                'total_unique': Company.objects.values('sector').distinct().count(),
                'distribution': list(
                    Company.objects.values('sector').annotate(count=Count('sector')).order_by('-count')
                )
            },
            'all_companies': companies.count()
        }
        
        return JsonResponse({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error calculating statistics: {str(e)}'
        }, status=400)


# ===== STARTUP ENDPOINTS (EdTech Startups) =====

@require_http_methods(["GET"])
def api_get_startup_stats(request):
    """Get statistics about EdTech startups"""
    # Total startups
    total_startups = Startup.objects.count()
    
    # Startups by sector
    sector_stats = Startup.objects.values('sector').annotate(count=Count('sector')).order_by('-count')
    
    # Get all sectors for filter dropdown
    all_sectors = Startup.objects.values_list('sector', flat=True).distinct().order_by('sector')
    
    return JsonResponse({
        'total_startups': total_startups,
        'sectors': [
            {'name': stat['sector'], 'count': stat['count']} 
            for stat in sector_stats
        ],
        'all_sectors': list(all_sectors),
    })


@require_http_methods(["GET"])
def api_get_startups(request):
    """Get all startups with optional search, filtering, and pagination"""
    search_term = request.GET.get('search', '').strip()
    sector = request.GET.get('sector', '').strip()
    sort_by = request.GET.get('sort', 'name').strip()  # name, year_founded, sector
    sort_order = request.GET.get('order', 'asc').strip()  # asc or desc
    page = int(request.GET.get('page', '1'))
    limit = int(request.GET.get('limit', '50'))
    
    # Start with all startups
    startups = Startup.objects.all()
    
    # Apply search filter
    if search_term:
        startups = startups.filter(
            Q(name__icontains=search_term) | 
            Q(sector__icontains=search_term) |
            Q(founders__icontains=search_term) |
            Q(headquarters__icontains=search_term)
        )
    
    # Apply sector filter (handle multi-sector entries with "contains")
    if sector:
        startups = startups.filter(sector__icontains=sector)
    
    # Count total before pagination
    total_count = startups.count()
    
    # Apply sorting
    if sort_by == 'year_founded':
        startups = startups.order_by(f'{"-" if sort_order == "desc" else ""}year_founded')
    elif sort_by == 'sector':
        startups = startups.order_by(f'{"-" if sort_order == "desc" else ""}sector')
    else:  # default: name
        startups = startups.order_by(f'{"-" if sort_order == "desc" else ""}name')
    
    # Apply pagination
    offset = (page - 1) * limit
    paginated = startups[offset:offset + limit]
    
    startups_data = [
        {
            'id': s.id,
            'name': s.name,
            'sector': s.sector,
            'founders': s.founders,
            'logo_url': s.logo_url or '',
            'headquarters': s.headquarters,
            'year_founded': s.year_founded,
            'total_funding': s.total_funding or '',
        }
        for s in paginated
    ]
    
    return JsonResponse({
        'startups': startups_data,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total_count,
            'pages': (total_count + limit - 1) // limit  # ceiling division
        }
    })


@csrf_exempt
@login_required(login_url='/login/')
def api_add_startup(request):
    """Add new startup (admin only)"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'sector', 'founders', 'headquarters', 'year_founded']
        for field in required_fields:
            if field not in data or not str(data.get(field, '')).strip():
                return JsonResponse({
                    'success': False,
                    'message': f'{field.capitalize()} is required'
                }, status=400)
        
        # Check if startup already exists
        if Startup.objects.filter(name=data['name']).exists():
            return JsonResponse({
                'success': False,
                'message': 'Startup with this name already exists'
            }, status=400)
        
        # Create startup
        startup = Startup.objects.create(
            name=data['name'].strip(),
            sector=data['sector'].strip(),
            founders=data['founders'].strip(),
            logo_url=data.get('logo_url', '').strip() or None,
            headquarters=data['headquarters'].strip(),
            year_founded=int(data['year_founded']),
            total_funding=data.get('total_funding', '').strip()
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Startup added successfully!',
            'startup': {
                'id': startup.id,
                'name': startup.name,
                'sector': startup.sector,
                'founders': startup.founders,
                'logo_url': startup.logo_url or '',
                'headquarters': startup.headquarters,
                'year_founded': startup.year_founded,
                'total_funding': startup.total_funding or '',
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
def api_edit_startup(request, id):
    """Edit existing startup (admin only)"""
    try:
        startup = get_object_or_404(Startup, id=id)
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'name' in data and data['name']:
            # Check if new name is unique (excluding current startup)
            if Startup.objects.filter(name=data['name']).exclude(id=id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'A startup with this name already exists'
                }, status=400)
            startup.name = data['name'].strip()
        
        if 'sector' in data and data['sector']:
            startup.sector = data['sector'].strip()
        
        if 'founders' in data and data['founders']:
            startup.founders = data['founders'].strip()
        
        if 'logo_url' in data:
            startup.logo_url = data.get('logo_url', '').strip() or None
        
        if 'headquarters' in data and data['headquarters']:
            startup.headquarters = data['headquarters'].strip()
        
        if 'year_founded' in data and data['year_founded']:
            startup.year_founded = int(data['year_founded'])
        
        if 'total_funding' in data:
            startup.total_funding = data.get('total_funding', '').strip()
        
        startup.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Startup updated successfully!',
            'startup': {
                'id': startup.id,
                'name': startup.name,
                'sector': startup.sector,
                'founders': startup.founders,
                'logo_url': startup.logo_url or '',
                'headquarters': startup.headquarters,
                'year_founded': startup.year_founded,
                'total_funding': startup.total_funding or '',
            }
        })
    except Startup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Startup not found'
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
def api_delete_startup(request, id):
    """Delete startup (admin only)"""
    try:
        startup = get_object_or_404(Startup, id=id)
        startup_name = startup.name
        startup.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Startup "{startup_name}" deleted successfully!'
        })
    except Startup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Startup not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_http_methods(["GET"])
@login_required(login_url='/login/')
def api_export_startups_csv(request):
    """Export startups to CSV based on current filters"""
    try:
        # Get filter parameters from query string
        search_term = request.GET.get('search', '').strip()
        sector = request.GET.get('sector', '').strip()
        sort_by = request.GET.get('sort', 'name').strip()
        sort_order = request.GET.get('order', 'asc').strip()
        
        # Start with all startups
        startups = Startup.objects.all()
        
        # Apply search filter
        if search_term:
            startups = startups.filter(
                Q(name__icontains=search_term) | 
                Q(sector__icontains=search_term) |
                Q(founders__icontains=search_term) |
                Q(headquarters__icontains=search_term)
            )
        
        # Apply sector filter
        if sector:
            startups = startups.filter(sector__icontains=sector)
        
        # Apply sorting
        if sort_by == 'year_founded':
            startups = startups.order_by(f'{"-" if sort_order == "desc" else ""}year_founded')
        elif sort_by == 'sector':
            startups = startups.order_by(f'{"-" if sort_order == "desc" else ""}sector')
        else:
            startups = startups.order_by(f'{"-" if sort_order == "desc" else ""}name')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="edtech_startups.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow([
            'Startup Name',
            'Sector',
            'Founders',
            'Headquarters',
            'Founded Year',
            'Total Funding',
            'Added On',
            'Last Updated'
        ])
        
        # Write data rows
        for startup in startups:
            writer.writerow([
                startup.name,
                startup.sector,
                startup.founders,
                startup.headquarters,
                startup.year_founded,
                startup.total_funding or '',
                startup.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                startup.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error exporting CSV: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
def api_startups_summary(request):
    """Export EdTech startups summary"""
    try:
        total_startups = Startup.objects.count()
        sector_stats = Startup.objects.values('sector').annotate(count=Count('sector')).order_by('-count')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="edtech_startups_summary.csv"'
        
        writer = csv.writer(response)
        
        # Summary header
        writer.writerow(['Bangladesh EdTech Startups - Summary Report'])
        writer.writerow(['Generated on', __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Overall statistics
        writer.writerow(['OVERALL STATISTICS'])
        writer.writerow(['Total Startups', total_startups])
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

