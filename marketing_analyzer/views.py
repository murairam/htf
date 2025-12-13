import json
import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Analysis


def home(request):
    """Serve the React app for the home page."""
    # In production, serve the Vite-built index.html with hashed assets
    if not settings.DEBUG:
        index_path = os.path.join(settings.BASE_DIR, 'backend', 'static', 'react', 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                return HttpResponse(f.read(), content_type='text/html')
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def submit_analysis(request):
    """
    Handle form submission with image, barcode, and objectives.
    Create an Analysis record and return the analysis_id.
    """
    try:
        # Get form data
        barcode = request.POST.get('barcode')
        objectives = request.POST.get('objectives')
        image = request.FILES.get('image')
        
        # Validate required fields
        if not all([barcode, objectives, image]):
            return JsonResponse({
                'error': 'Missing required fields: barcode, objectives, or image'
            }, status=400)
        
        # Create analysis record
        analysis = Analysis.objects.create(
            barcode=barcode,
            objectives=objectives,
            image=image,
            status='pending'
        )
        
        # Return analysis_id for WebSocket connection
        return JsonResponse({
            'analysis_id': str(analysis.analysis_id),
            'status': 'created'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


def results(request, analysis_id):
    """Serve the React app for the results page."""
    # In production, serve the Vite-built index.html with hashed assets
    if not settings.DEBUG:
        index_path = os.path.join(settings.BASE_DIR, 'backend', 'static', 'react', 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                return HttpResponse(f.read(), content_type='text/html')
    return render(request, 'index.html')


@require_http_methods(["GET"])
def get_analysis(request, analysis_id):
    """
    API endpoint to retrieve analysis data.
    Used by frontend to fetch existing results.
    """
    try:
        analysis = get_object_or_404(Analysis, analysis_id=analysis_id)
        
        response_data = {
            'analysis_id': str(analysis.analysis_id),
            'barcode': analysis.barcode,
            'objectives': analysis.objectives,
            'image_url': analysis.image.url if analysis.image else None,
            'status': analysis.status,
            'result_data': analysis.result_data,
            'created_at': analysis.created_at.isoformat(),
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
