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


class Startup(models.Model):
    """
    Model representing a Bangladesh EdTech startup.
    Stores information about EdTech startup name, sector, founders, location, funding, etc.
    """
    
    # Sector choices for EdTech startups
    EDTECH_SECTORS = [
        ('K-12', 'K-12 Education'),
        ('test-prep', 'Test Preparation'),
        ('upskilling', 'Upskilling & Professional Development'),
        ('coding', 'Coding & Programming'),
        ('skills-learning', 'Skills Learning'),
        ('language', 'Language Learning'),
        ('tuition', 'Tuition & Tutoring'),
        ('edtech-other', 'Other EdTech'),
    ]
    
    # Startup name (unique, required)
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="EdTech startup name"
    )
    
    # Sector/Industry (required) - can be multiple separated by commas
    sector = models.CharField(
        max_length=200,
        help_text="EdTech sectors (e.g., K-12, test prep, upskilling)"
    )
    
    # Founders (required)
    founders = models.CharField(
        max_length=300,
        help_text="Founder name(s)"
    )
    
    # Logo URL (optional)
    logo_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to startup logo image"
    )
    
    # Headquarters location (required)
    headquarters = models.CharField(
        max_length=200,
        help_text="Headquarters location"
    )
    
    # Founded year (required)
    year_founded = models.IntegerField(
        help_text="Year startup was founded"
    )
    
    # Total funding (optional)
    total_funding = models.CharField(
        max_length=100,
        blank=True,
        help_text="Total funding received (e.g., $9.26M)"
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
        verbose_name = 'EdTech Startup'
        verbose_name_plural = 'EdTech Startups'
    
    def __str__(self):
        """Return string representation of startup"""
        return f"{self.name} ({self.sector})"
    
    def __repr__(self):
        """Return representation of startup"""
        return f"<Startup: {self.name}>"

