from django.urls import path, include
from .views import SmartQueryViewSet, QueryView, AnswerView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("query", QueryView, basename="query")
router.register("answer", AnswerView, basename="answer")
router.register("smart-query", SmartQueryViewSet, basename="smart-query")

urlpatterns = [
    path("api/",  include(router.urls)),
]
