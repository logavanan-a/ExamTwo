from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import models
import hashlib
from datetime import timedelta
import json
from .models import *


# Helper function to generate short URL
def generate_short_url(long_url):
    hash_object = hashlib.sha256(long_url.encode())
    return hash_object.hexdigest()[:6]

# Views
@csrf_exempt
def shorten_url(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original_url = data.get('original_url')
            expiration_hours = data.get('expiration_hours', 24)

            # Validate URL
            validate = URLValidator()
            validate(original_url)

            # Generate short URL
            short_url = generate_short_url(original_url)
            creation_time = now()
            expiration_time = creation_time + timedelta(hours=expiration_hours)

            # Check if the URL already exists
            url, created = URL.objects.get_or_create(
                original_url=original_url,
                defaults={
                    'short_url': short_url,
                    'creation_time': creation_time,
                    'expiration_time': expiration_time
                }
            )

            return JsonResponse({'short_url': f'https://short.ly/{url.short_url}'}, status=201 if created else 200)
        except ValidationError:
            return JsonResponse({'error': 'Invalid URL format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def redirect_url(request, short_url):
    try:
        url = URL.objects.get(short_url=short_url)
        if now() > url.expiration_time:
            return JsonResponse({'error': 'URL has expired'}, status=410)

        # Log the access
        Analytics.objects.create(
            short_url=url,
            access_time=now(),
            ip_address=get_client_ip(request)
        )

        return redirect(url.original_url)
    except URL.DoesNotExist:
        return JsonResponse({'error': 'URL not found'}, status=404)

def get_analytics(request, short_url):
    try:
        url = URL.objects.get(short_url=short_url)
        logs = Analytics.objects.filter(short_url=url)

        analytics = [
            {
                'access_time': log.access_time.strftime('%Y-%m-%d %H:%M:%S'),
                'ip_address': log.ip_address
            }
            for log in logs
        ]

        return JsonResponse({'analytics': analytics}, status=200)
    except URL.DoesNotExist:
        return JsonResponse({'error': 'URL not found'}, status=404)

# Utility function to get client IP address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



