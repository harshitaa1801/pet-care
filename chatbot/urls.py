from django.urls import path
from .views import generate_response, query_assistant, submit_answers

urlpatterns = [
    path('generate/', generate_response, name='generate_response'),
    path('query/', query_assistant, name='query_assistant'),
    path('submit/', submit_answers, name='submit_answers'),
]
