from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from movies.views import register, verify_code, CinemasView

urlpatterns = [
path('register/', register, name="megaregister"),
path('verify/', verify_code, name="megaverify"),
path("cinemas/", CinemasView.as_view(), name="cinemas"),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
path('accounts/', include('allauth.urls')),
    path('pages/', include('django.contrib.flatpages.urls'), name='pages'),
    path('contact/', include("contact.urls")),
    path("", include("movies.urls")),
    # path('i18n/', include('django.conf.urls.i18n')),

]

# urlpatterns += i18n_patterns(
#     path('accounts/', include('allauth.urls')),
#     path('pages/', include('django.contrib.flatpages.urls')),
#     path('contact/', include("contact.urls")),
#     path("", include("movies.urls")),
# )




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
