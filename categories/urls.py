from django.urls import path
from .views import CategoryCreateView, CategoryListView, CategoryUpdateView, CategoryDeleteView

urlpatterns = [
    path('create/', CategoryCreateView.as_view(), name='create-category'),
    path('', CategoryListView.as_view(), name='category-list'),
    path('update/<int:id>/', CategoryUpdateView.as_view(), name='update-category'),
    path('delete/<int:id>/', CategoryDeleteView.as_view(), name='delete-category'),
]
