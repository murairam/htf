import uuid
from django.db import models


class Analysis(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]
    
    analysis_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barcode = models.CharField(max_length=50)
    objectives = models.TextField()
    image = models.ImageField(upload_to='uploads/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Analyses"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis {self.analysis_id} - {self.status}"
