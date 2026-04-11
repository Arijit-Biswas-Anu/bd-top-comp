from django.urls import path
from . import views

urlpatterns = [
    # Page routes
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # AJAX API endpoints - Companies (legacy)
    path('api/companies/', views.api_get_companies, name='api_companies'),
    path('api/companies/add/', views.api_add_company, name='api_add_company'),
    path('api/companies/<int:id>/edit/', views.api_edit_company, name='api_edit_company'),
    path('api/companies/<int:id>/delete/', views.api_delete_company, name='api_delete_company'),
    path('api/stats/', views.api_get_stats, name='api_stats'),
    path('api/export/csv/', views.api_export_csv, name='api_export_csv'),
    path('api/export/summary/', views.api_export_summary, name='api_export_summary'),
    
    # Phase 13B: Analytics endpoints (companies)
    path('api/analytics/dashboard/', views.api_analytics_dashboard, name='api_analytics_dashboard'),
    path('api/analytics/comparison/', views.api_company_comparison, name='api_company_comparison'),
    path('api/analytics/sector/', views.api_sector_insights, name='api_sector_insights'),
    path('api/analytics/growth/', views.api_growth_analysis, name='api_growth_analysis'),
    path('api/analytics/stats/', views.api_descriptive_stats, name='api_descriptive_stats'),
    
    # AJAX API endpoints - EdTech Startups
    path('api/startups/', views.api_get_startups, name='api_startups'),
    path('api/startups/add/', views.api_add_startup, name='api_add_startup'),
    path('api/startups/<int:id>/edit/', views.api_edit_startup, name='api_edit_startup'),
    path('api/startups/<int:id>/delete/', views.api_delete_startup, name='api_delete_startup'),
    path('api/startups/stats/', views.api_get_startup_stats, name='api_startup_stats'),
    path('api/startups/export/csv/', views.api_export_startups_csv, name='api_export_startups_csv'),
    path('api/startups/export/summary/', views.api_startups_summary, name='api_startups_summary'),
]
