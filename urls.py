from django.contrib import admin
from django.urls import path
from safety_app.views import TriggerSOS, HeatmapData

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sos/', TriggerSOS.as_view()),
    path('api/heatmap/', HeatmapData.as_view()),
]
