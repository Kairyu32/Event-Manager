from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# The URL patterns for the project
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('eventmanager.urls')),
]

# Serves the media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
