from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from root.settings import MEDIA_ROOT, STATIC_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('src.urls')),
]

""" STATIC AND MEDIA FILES ----------------------------------------------------------------------------------------- """
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
]
