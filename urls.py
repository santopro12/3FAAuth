# filepath: d:\New folder\three_step_auth\urls.py (Project Level)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('your_app_name.urls')),  # Include your app's URLs
]