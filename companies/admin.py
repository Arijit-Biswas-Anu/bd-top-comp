from django.contrib import admin
from .models import Company, Startup


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Custom admin interface for managing companies.
    Provides search, filtering, and list display options.
    """
    
    # Columns to display in the admin list view
    list_display = ('name', 'sector', 'headquarters', 'founded', 'created_at')
    
    # Add search functionality
    search_fields = ('name', 'sector', 'headquarters', 'description')
    
    # Add filtering by sector and founded year
    list_filter = ('sector', 'founded', 'created_at')
    
    # Read-only fields (cannot be edited)
    readonly_fields = ('created_at', 'updated_at')
    
    # Organize form fields into sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sector', 'headquarters', 'founded')
        }),
        ('Media & Description', {
            'fields': ('logo_url', 'description'),
            'classes': ('collapse',)  # Collapsible section
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Default ordering in list view
    ordering = ('-created_at',)


@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    """
    Custom admin interface for managing EdTech startups.
    Provides search, filtering, and list display options.
    """
    
    # Columns to display in the admin list view
    list_display = ('name', 'sector', 'founders', 'headquarters', 'year_founded', 'total_funding', 'created_at')
    
    # Add search functionality
    search_fields = ('name', 'sector', 'founders', 'headquarters', 'total_funding')
    
    # Add filtering by sector and founded year
    list_filter = ('sector', 'year_founded', 'created_at')
    
    # Read-only fields (cannot be edited)
    readonly_fields = ('created_at', 'updated_at')
    
    # Organize form fields into sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sector', 'founders', 'headquarters', 'year_founded')
        }),
        ('Funding & Media', {
            'fields': ('total_funding', 'logo_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Default ordering in list view
    ordering = ('-created_at',)
