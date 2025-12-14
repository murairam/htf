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
    Handle unified analysis submission.
    Requires: business_objective (required)
    Requires: at least one of barcode, product_link, or product_description
    """
    try:
        # Support both form-data and JSON
        if request.content_type and 'application/json' in request.content_type:
            import json
            data = json.loads(request.body)
            business_objective = data.get('business_objective', '')
            barcode = data.get('barcode')
            product_link = data.get('product_link')
            product_description = data.get('product_description')
        else:
            business_objective = request.POST.get('business_objective', '')
            barcode = request.POST.get('barcode')
            product_link = request.POST.get('product_link')
            product_description = request.POST.get('product_description')
        
        # Validation: business_objective is required
        if not business_objective or not business_objective.strip():
            return JsonResponse({'error': 'business_objective is required'}, status=400)
        
        business_objective = business_objective.strip()
        
        # Validation: at least one input method required
        has_barcode = barcode and barcode.strip()
        has_link = product_link and product_link.strip()
        has_description = product_description and product_description.strip()
        
        if not (has_barcode or has_link or has_description):
            return JsonResponse({
                'error': 'At least one of barcode, product_link, or product_description must be provided'
            }, status=400)
        
        # Create analysis record
        analysis = Analysis.objects.create(
            barcode=barcode.strip() if has_barcode else None,
            product_link=product_link.strip() if has_link else None,
            product_description=product_description.strip() if has_description else None,
            objectives=business_objective,  # objectives field stores business_objective
            status='pending'
        )
        
        identifier = barcode or product_link or "description"
        logger.info(f"Created analysis {analysis.analysis_id} for {identifier}")
        
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


@csrf_exempt
@require_http_methods(["GET"])
def get_analysis_result(request, analysis_id):
    """
    Get saved analysis result for reload-safe results page.
    Returns the stored JSON result if available.
    """
    try:
        analysis = Analysis.objects.get(analysis_id=analysis_id)
        
        if analysis.result_data:
            return JsonResponse({
                'success': True,
                'analysis_id': str(analysis.analysis_id),
                'status': analysis.status,
                'result': analysis.result_data
            })
        else:
            # Result not yet available
            return JsonResponse({
                'success': False,
                'analysis_id': str(analysis.analysis_id),
                'status': analysis.status,
                'message': 'Analysis result not yet available'
            })
    except Analysis.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Analysis not found'
        }, status=404)
    except Exception as e:
        logger.exception(f"Error fetching analysis result: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch analysis result'
        }, status=500)
