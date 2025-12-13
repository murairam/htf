import uuid
from django.db import models


class Analysis(models.Model):
    """Model to store product analysis requests and results."""
    
    analysis_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barcode = models.CharField(max_length=50)
    objectives = models.TextField()
    result_data = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('error', 'Error'),
        ]
    )
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analysis'
        verbose_name_plural = 'Analyses'
    
    def __str__(self):
        return f"Analysis {self.analysis_id} - {self.barcode}"
