from django.urls import path

from . import views

urlpatterns = [
    path("hooks/sync_database", views.sync_database_hook),
]
