from django.utils.timezone import now
from .models import Visitor
import re

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip admin, static, media paths
        skip_paths = ['/admin/', '/static/', '/media/', '/favicon.ico']
        path = request.path
        
        for skip in skip_paths:
            if path.startswith(skip):
                return self.get_response(request)
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Get session key
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        
        # Check if unique visitor (same IP + session in last 24 hours)
        is_unique = not Visitor.objects.filter(
            ip_address=ip,
            session_key=session_key,
            visited_at__date=now().date()
        ).exists()
        
        # Save visitor data
        Visitor.objects.create(
            ip_address=ip,
            session_key=session_key,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            referer=request.META.get('HTTP_REFERER', ''),
            page_visited=path[:500],
            method=request.method,
            is_unique=is_unique
        )
        
        response = self.get_response(request)
        return response
