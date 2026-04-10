from django.db import models


class Company(models.Model):
    """
    Model representing a top Bangladeshi company.
    Stores information about company name, sector, location, founding year, etc.
    """
    
    # Sector choices for companies
    SECTOR_CHOICES = [
        ('Telecom', 'Telecommunications'),
        ('Banking', 'Banking & Finance'),
        ('Pharmaceuticals', 'Pharmaceuticals'),
        ('Energy', 'Energy'),
        ('Retail', 'Retail & Commerce'),
        ('Manufacturing', 'Manufacturing'),
        ('Technology', 'Technology'),
        ('Textiles', 'Textiles'),
        ('Consumer', 'Consumer Goods'),
        ('Agro', 'Agriculture'),
        ('Real Estate', 'Real Estate'),
        ('Other', 'Other'),
    ]
    
    # Company name (unique, required)
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Company name (e.g., Grameenphone Ltd.)"
    )
    
    # Sector/Industry (required)
    sector = models.CharField(
        max_length=50,
        choices=SECTOR_CHOICES,
        help_text="Primary business sector"
    )
    
    # Logo URL (optional)
    logo_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to company logo image"
    )
    
    # Headquarters location (required)
    headquarters = models.CharField(
        max_length=200,
        help_text="Headquarters location (e.g., Dhaka, Bangladesh)"
    )
    
    # Founded year (required)
    founded = models.IntegerField(
        help_text="Year company was founded"
    )
    
    # Company description (optional)
    description = models.TextField(
        blank=True,
        max_length=500,
        help_text="Brief description of the company and its business"
    )
    
    # Auto timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created in the system"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )
    
    class Meta:
        """Model metadata"""
        ordering = ['-created_at']  # Newest first
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
    
    def __str__(self):
        """Return string representation of company"""
        return f"{self.name} ({self.sector})"
    
    def __repr__(self):
        """Return representation of company"""
        return f"<Company: {self.name}>"

