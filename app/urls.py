from django.urls import path, include
from django.conf.urls import handler404
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.AdminSite.site_header = 'Premio Eficiencia Operacional'
admin.AdminSite.site_title = 'Painel do Admin do Sistema'
admin.AdminSite.index_title ='Painel do Administrador do Sistema'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns

handler500 ='core.views.handler500'
handler400 ='core.views.handler400'
handler401 ='core.views.handler401'
handler402 ='core.views.handler402'
handler403 ='core.views.handler403'
handler404 ='core.views.handler404'
