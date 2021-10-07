from django.urls import path, include
from rest_framework.routers import DefaultRouter

from expense import views


router = DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('record', views.RecordViewSet)
router.register('summary', views.RecordSummaryViewSet, basename='summary')

app_name = 'expense'

urlpatterns = [
    path('', include(router.urls))
]
