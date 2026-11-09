from django.urls import path
from . import views

urlpatterns = [
    path("r/<slug:slug>", views.campaign_redirect, name="campaign-redirect"),
    path("api/traffic/event/", views.event, name="traffic-event"),
]
