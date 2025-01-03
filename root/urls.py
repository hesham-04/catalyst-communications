from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import handler404, handler403, handler500

from django.views.static import serve

from root.settings import MEDIA_ROOT, STATIC_ROOT
from src.core.views import handler404, handler403, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('src.urls')),
]

""" STATIC AND MEDIA FILES ----------------------------------------------------------------------------------------- """
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
]

""" HANDLERS FOR 404 AND 500 ERRORS -------------------------------------------------------------------------------- """
handler404 = handler404
handler403 = handler403
handler500 = handler500