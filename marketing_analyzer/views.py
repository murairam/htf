import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Analysis

logger = logging.getLogger(__name__)


def index(request):
    """Render the main React application."""
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def submit_analysis(request):
    """
    Handle analysis submission.
    Requires barcode, objectives are optional.
    No image upload - images come from OpenFoodFacts.
    """
    try:
        # Support both form-data and JSON
        if request.content_type and 'application/json' in request.content_type:
            import json
            data = json.loads(request.body)
            barcode = data.get('barcode')
            objectives = data.get('objectives', '')
        else:
            barcode = request.POST.get('barcode')
            objectives = request.POST.get('objectives', '')
        
        # Validation
        if not barcode:
            return JsonResponse({'error': 'Barcode is required'}, status=400)
        
        # Objectives are optional - use empty string if not provided
        objectives = objectives.strip() if objectives else ''
        
        # Create analysis record
        analysis = Analysis.objects.create(
            barcode=barcode,
            objectives=objectives,
            status='pending'
        )
        
        logger.info(f"Created analysis {analysis.analysis_id} for barcode {barcode}")
        
        return JsonResponse({
            'analysis_id': str(analysis.analysis_id),
            'redirect_url': f'/results/{analysis.analysis_id}/'
        })
        
    except Exception as e:
        logger.exception(f"Error creating analysis: {e}")
        return JsonResponse({'error': 'Failed to create analysis'}, status=500)


def results(request, analysis_id):
    """Render the results page for a specific analysis."""
    try:
        analysis = Analysis.objects.get(analysis_id=analysis_id)
        return render(request, 'index.html')
    except Analysis.DoesNotExist:
        return render(request, 'index.html', status=404)
