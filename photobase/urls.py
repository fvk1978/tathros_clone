"""photobase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib.gis import admin
from django.conf import settings
from django.conf.urls.static import static
from proto.views import api, auth, search, panel
from proto.views import static as static_views


urlpatterns = [
    # admin
    url(r'^admin/', admin.site.urls),
    url(r'^select2/', include('django_select2.urls')),

    # static pages
    url(r'^faq/$', static_views.FAQ.as_view(), name='faq'),
    url(r'^pricing/$', static_views.Info.as_view(), name='info'),
    url(r'^contact/$', static_views.Contact.as_view(), name='contact'),
    url(r'^terms/$', static_views.Terms.as_view(), name='terms'),
    url(r'^privacy/$', static_views.Privacy.as_view(), name='privacy'),
    url(r'^impressum/$', static_views.Impressum.as_view(), name='impressum'),

    # photo search
    url(r'^$', search.PhotoListInitial.as_view(), name='home'),
    url(r'^photographers/$', search.PhotographersByPhoto.as_view(),
        name='photographers'),
    url(r'^partial_photos/$', search.PartialPhotos.as_view(),
        name='partial_photos'),
    url(r'^partial_photographers/$', search.PartialPhotographers.as_view(),
        name='partial_photographers'),
    url(r'^api/photos/$', api.PhotoList.as_view(),
        name='api_photos'),

    # user auth
    url(r'^login/$', auth.Login.as_view(), name='login'),
    url(r'^register/$', auth.Register.as_view(), name='register'),
    url(r'^logout/$', auth.Lougout.as_view(), name='logout'),

    # settings panel
    url(r'^settings/personal/?$', panel.PersonalSettings.as_view(),
        name='settings_personal'),
    url(r'^settings/scoreboard/?$', panel.ScoreBoard.as_view(),
        name='settings_scoreboard'),
    url(r'^settings/portfolio/?$', panel.Portfolio.as_view(),
        name='settings_portfolio'),
    url(r'^settings/portfolio/category/(?P<pk>\d+)/(?P<slug>[\w-]+)/?$',
        panel.CategoryDetail.as_view(),
        name='settings_category'),
    url(r'^settings/portfolio/upload/?$', panel.Upload.as_view(),
        name='settings_upload'),
    url(r'^settings/portfolio/edit/(?P<pk>\d+)/?$', panel.Update.as_view(),
        name='settings_edit'),
    url(r'^settings/portfolio/delete/(?P<pk>\d+)/?$', panel.Delete.as_view(),
        name='settings_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
