from django.urls import path, include

urlpatterns = [
    path('', include('src.web.dashboard.urls')),
    path('invoice/', include('src.services.invoice.urls')),
    path('customer/', include('src.services.customer.urls')),
    path('projects/', include('src.services.project.urls')),
]
