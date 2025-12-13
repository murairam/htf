from django.urls import path
from . import views

app_name = 'marketing_analyzer'

urlpatterns = [
    path('', views.home, name='home'),
    path('submit/', views.submit_analysis, name='submit'),
    path('results/<uuid:analysis_id>/', views.results, name='results'),
    path('api/analysis/<uuid:analysis_id>/', views.get_analysis, name='get_analysis'),
]
