"""
URL configuration for damage_project project.
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.phone_input, name='phone_input'),
    path('verify/', views.verify_code, name='verify_code'),
    path('damage-form/', views.damage_form, name='damage_form'),
    path('calculations/', views.calculations, name='calculations'),
    path('calculation/<uuid:assessment_id>/', views.calculation_detail_page, name='calculation_detail'),
    path('contacts/', views.contacts, name='contacts'),
    path('logout/', views.logout_view, name='logout'),
    # API endpoints
    path('api/calculation/<uuid:assessment_id>/json/', views.calculation_json, name='calculation_json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
