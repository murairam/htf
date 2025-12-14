from django.urls import path
from . import views

app_name = 'marketing_analyzer'

urlpatterns = [
    path('', views.index, name='home'),
    path('submit/', views.submit_analysis, name='submit'),
    path('results/<uuid:analysis_id>/', views.results, name='results'),
    path('api/results/<uuid:analysis_id>/', views.get_analysis_result, name='get_result'),
]
