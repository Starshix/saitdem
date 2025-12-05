from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.urls import reverse

def admin_login_required(request, path=''):
    """Редирект на страницу входа при попытке доступа к админке"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f"{reverse('login')}?next=/admin/")
    return admin.site.login(request)


urlpatterns = [
    path('admin/', include([
        path('login/', admin_login_required, name='admin_login'),
        path('', admin.site.urls),
    ])),
    
    path('', include('portal.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)