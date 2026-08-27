from django.db import models
from django.utils import timezone

class Computer(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
    ]
    
    BRAND_CHOICES = [
        ('dell', 'Dell'),
        ('hp', 'HP'),
        ('lenovo', 'Lenovo'),
        ('apple', 'Apple'),
        ('acer', 'Acer'),
        ('asus', 'ASUS'),
        ('msi', 'MSI'),
        ('other', 'Other'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'Brand New'),
        ('like-new', 'Like New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ]
    
    OS_CHOICES = [
        ('windows', 'Windows 11 Pro'),
        ('windows-home', 'Windows 11 Home'),
        ('macos', 'macOS'),
        ('linux', 'Linux'),
        ('chrome', 'Chrome OS'),
        ('none', 'No OS'),
    ]
    
    title = models.CharField(max_length=200, help_text="e.g., Dell XPS 15 2024")
    brand = models.CharField(max_length=20, choices=BRAND_CHOICES)
    model = models.CharField(max_length=100)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    processor = models.CharField(max_length=200, help_text="e.g., Intel Core i7-13700H")
    ram = models.CharField(max_length=50, help_text="e.g., 16GB DDR5")
    storage = models.CharField(max_length=100, help_text="e.g., 512GB SSD")
    screen_size = models.CharField(max_length=20, help_text="e.g., 15.6 inch")
    screen_resolution = models.CharField(max_length=50, blank=True)
    graphics = models.CharField(max_length=200, blank=True)
    battery_life = models.CharField(max_length=50, blank=True)
    operating_system = models.CharField(max_length=20, choices=OS_CHOICES)
    year = models.IntegerField(help_text="Manufacturing year")
    
    description = models.TextField(blank=True, help_text="Detailed description of the computer")
    condition_description = models.TextField(blank=True, help_text="Describe any wear, scratches, etc.")
    
    main_image = models.ImageField(upload_to='computers/')
    image_2 = models.ImageField(upload_to='computers/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='computers/', blank=True, null=True)
    image_4 = models.ImageField(upload_to='computers/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    quantity_available = models.IntegerField(default=1)
    warranty = models.CharField(max_length=100, blank=True, help_text="e.g., 6 months")
    
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    sold_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-added_date']
    
    def __str__(self):
        return f"{self.title} - "


class ComputerInquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New Inquiry'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('interested', 'Interested'),
        ('not-interested', 'Not Interested'),
    ]
    
    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('whatsapp', 'WhatsApp'),
        ('any', 'Any'),
    ]
    
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name='inquiries')
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_contact = models.CharField(max_length=20, choices=CONTACT_CHOICES, default='email')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True, help_text="Internal notes")
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client_name} - {self.computer.title}"


class App(models.Model):
    PLATFORM_CHOICES = [
        ('android', 'Android (.apk)'),
        ('ios', 'iOS (.ipa)'),
        ('windows', 'Windows (.exe)'),
        ('mac', 'macOS (.dmg)'),
        ('linux', 'Linux (.deb/.rpm)'),
        ('web', 'Web App'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('beta', 'Beta Testing'),
        ('deprecated', 'Deprecated'),
    ]
    
    name = models.CharField(max_length=200, help_text="App Name")
    slug = models.SlugField(unique=True, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    version = models.CharField(max_length=20, help_text="e.g., 2.1.0")
    
    short_description = models.CharField(max_length=300, help_text="Brief description shown in listing")
    description = models.TextField(help_text="Full description of the app")
    features = models.TextField(blank=True, help_text="Key features (comma-separated)")
    
    download_file = models.FileField(upload_to='apps/', help_text="Upload your app file (.apk, .exe, .zip, etc.)")
    file_size = models.CharField(max_length=50, blank=True, help_text="e.g., 25 MB")
    download_count = models.IntegerField(default=0)
    latest_release_notes = models.TextField(blank=True, help_text="What's new in this version")
    
    app_icon = models.ImageField(upload_to='apps/icons/', help_text="App icon (recommended: 512x512)")
    banner_image = models.ImageField(upload_to='apps/banners/', blank=True, null=True)
    screenshots = models.JSONField(default=list, help_text="List of screenshot URLs")
    
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    requirements = models.TextField(blank=True, help_text="System requirements")
    supported_languages = models.CharField(max_length=200, blank=True, help_text="e.g., English, French, Spanish")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    
    website_url = models.URLField(blank=True, help_text="App website or landing page")
    documentation_url = models.URLField(blank=True, help_text="User guide or documentation")
    github_url = models.URLField(blank=True, help_text="GitHub repository")
    
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=20, blank=True)
    
    release_date = models.DateField()
    last_updated = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-release_date']
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_platform_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            import re
            self.slug = re.sub(r'[^\w\s-]', '', self.name).strip().lower()
            self.slug = re.sub(r'[-\s]+', '-', self.slug)
        super().save(*args, **kwargs)
    
    def get_features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split(',') if f.strip()]
        return []


class Graphics(models.Model):
    CATEGORY_CHOICES = [
        ('logo', 'Logo Design'),
        ('flyer', 'Flyer Design'),
        ('banner', 'Banner Design'),
        ('poster', 'Poster Design'),
        ('business_card', 'Business Card'),
        ('social_media', 'Social Media Post'),
        ('branding', 'Branding'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200, help_text="Title of the design")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, help_text="Description of the design")
    image = models.ImageField(upload_to='graphics/', help_text="Upload your design image")
    
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"
