from django.urls import path
from . import views
from .views import TermListAPIView, TermDetailAPIView, CategoryListAPIView, CategoryDetailAPIView

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('terms/', views.all_terms, name='all_terms'),
    path('category/<int:category_id>/terms/', views.category_terms, name='category_terms'),
    path('terms/<int:term_id>/', views.term_detail, name='term_detail'),
    path('recommendations_list/', views.recommendations_view, name='recommendations_list'),
    path('recommendation_detail/<int:rec_id>/', views.recommendation_detail, name='recommendation_detail'),
    path('api/terms/', TermListAPIView.as_view(), name='api_term_list'),
    path('api/terms/<int:pk>/', TermDetailAPIView.as_view(), name='api_term_detail'),
    path('api/categories/', CategoryListAPIView.as_view(), name='api_category_list'),
    path('api/categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='api_category_detail'),
]
