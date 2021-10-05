from django.urls import path, include
from rest_framework.routers import DefaultRouter

from expense import views


router = DefaultRouter()
router.register('category', views.CategoryViewSet)

app_name = 'expense'

urlpatterns = [
    path('', include(router.urls))
]
