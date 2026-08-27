from django.contrib import admin
from .models import Computer, ComputerInquiry, App, Graphics

class ComputerAdmin(admin.ModelAdmin):
    list_display = ['title', 'brand', 'price', 'status', 'quantity_available', 'added_date']
    list_filter = ['brand', 'status', 'condition', 'operating_system']
    search_fields = ['title', 'brand', 'model', 'processor', 'description']
    readonly_fields = ['added_date', 'updated_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'brand', 'model', 'condition', 'price', 'original_price')
        }),
        ('Specifications', {
            'fields': ('processor', 'ram', 'storage', 'screen_size', 'screen_resolution', 'graphics', 'battery_life', 'operating_system', 'year')
        }),
        ('Description', {
            'fields': ('description', 'condition_description')
        }),
        ('Images', {
            'fields': ('main_image', 'image_2', 'image_3', 'image_4')
        }),
        ('Status & Inventory', {
            'fields': ('status', 'quantity_available', 'warranty', 'is_featured', 'order')
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('added_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_available', 'mark_as_sold', 'mark_as_featured']
    
    def mark_as_available(self, request, queryset):
        queryset.update(status='available')
    mark_as_available.short_description = "Mark selected computers as Available"
    
    def mark_as_sold(self, request, queryset):
        queryset.update(status='sold')
    mark_as_sold.short_description = "Mark selected computers as Sold"
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = "Mark selected computers as Featured"


class ComputerInquiryAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'computer', 'status', 'created_at']
    list_filter = ['status', 'preferred_contact']
    search_fields = ['client_name', 'client_email', 'client_phone', 'message']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']
    
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('computer', 'client_name', 'client_email', 'client_phone', 'message')
        }),
        ('Contact Preferences', {
            'fields': ('budget', 'preferred_contact')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Tracking', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_interested']
    
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
    mark_as_read.short_description = "Mark as Read"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
    mark_as_replied.short_description = "Mark as Replied"
    
    def mark_as_interested(self, request, queryset):
        queryset.update(status='interested')
    mark_as_interested.short_description = "Mark as Interested"


class AppAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'platform', 'status', 'download_count', 'release_date', 'is_free']
    list_filter = ['platform', 'status', 'is_free', 'is_featured']
    search_fields = ['name', 'description', 'features', 'version']
    readonly_fields = ['download_count', 'created_at', 'last_updated']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'platform', 'version', 'status')
        }),
        ('Description', {
            'fields': ('short_description', 'description', 'features')
        }),
        ('Download File', {
            'fields': ('download_file', 'file_size', 'download_count', 'latest_release_notes')
        }),
        ('Media', {
            'fields': ('app_icon', 'banner_image', 'screenshots')
        }),
        ('Pricing', {
            'fields': ('is_free', 'price')
        }),
        ('Requirements', {
            'fields': ('requirements', 'supported_languages')
        }),
        ('Links', {
            'fields': ('website_url', 'documentation_url', 'github_url')
        }),
        ('Support', {
            'fields': ('support_email', 'support_phone')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'release_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'mark_as_active', 'mark_as_beta', 'mark_as_inactive']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = "⭐ Mark as Featured"
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
    mark_as_active.short_description = "✅ Mark as Active"
    
    def mark_as_beta(self, request, queryset):
        queryset.update(status='beta')
    mark_as_beta.short_description = "🧪 Mark as Beta"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive')
    mark_as_inactive.short_description = "❌ Mark as Inactive"


class GraphicsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'order', 'created_at']
    list_filter = ['category', 'is_featured']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description')
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'mark_as_normal']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = "⭐ Mark as Featured"
    
    def mark_as_normal(self, request, queryset):
        queryset.update(is_featured=False)
    mark_as_normal.short_description = "Mark as Normal"


# Register all models
admin.site.register(Computer, ComputerAdmin)
admin.site.register(ComputerInquiry, ComputerInquiryAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(Graphics, GraphicsAdmin)
