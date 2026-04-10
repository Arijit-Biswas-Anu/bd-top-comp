from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import json


# ===== Page Views (Phase 5 - Placeholder) =====

def index(request):
    """Display company listing page"""
    return render(request, 'companies/index.html')


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


def dashboard(request):
    """Admin dashboard placeholder"""
    return render(request, 'companies/index.html')


def logout_view(request):
    """Handle admin logout"""
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out'})


# ===== AJAX API Endpoints (Placeholder for Phase 8+) =====

def api_get_companies(request):
    """Placeholder - will implement in Phase 8"""
    return JsonResponse({'companies': []})


def api_add_company(request):
    """Placeholder - will implement in Phase 9"""
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})


def api_edit_company(request, id):
    """Placeholder - will implement in Phase 10"""
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})


def api_delete_company(request, id):
    """Placeholder - will implement in Phase 11"""
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})


