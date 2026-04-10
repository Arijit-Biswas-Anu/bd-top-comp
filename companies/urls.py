from django.urls import path
from . import views

urlpatterns = [
    # Page routes
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # AJAX API endpoints
    path('api/companies/', views.api_get_companies, name='api_companies'),
    path('api/companies/add/', views.api_add_company, name='api_add_company'),
    path('api/companies/<int:id>/edit/', views.api_edit_company, name='api_edit_company'),
    path('api/companies/<int:id>/delete/', views.api_delete_company, name='api_delete_company'),
]
