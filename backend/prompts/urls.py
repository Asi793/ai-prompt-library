from django.urls import path
from . import views

urlpatterns = [
    path('prompts/', views.prompt_list, name='prompt-list'),
    path('prompts/<int:prompt_id>/', views.prompt_detail, name='prompt-detail'),
]
