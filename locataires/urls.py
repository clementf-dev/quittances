from django.urls import path
from . import views

urlpatterns = [
    path('quittance/<int:quittance_id>/pdf/', views.generer_pdf_quittance, name='pdf_quittance'),
]