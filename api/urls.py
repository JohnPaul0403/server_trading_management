from django.urls import path, include
from . import views

urlpatterns = [
    path('status/', views.get_status_app, name='status'),
    path('auth/', include("authentication.urls")),
    path('trading/', include("trading.urls"))
]
