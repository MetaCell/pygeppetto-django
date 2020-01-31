from django.conf.urls import url
from django.views.generic import RedirectView

from pygeppetto_server import views

urlpatterns = [
    url(
        r'^geppetto/(?P<path>.*)$',
        RedirectView.as_view(
            url='/static/org.geppetto.frontend/src/main/webapp/%(path)s'
        )
    ),
    url(r'^.*$', views.index, name='index'),
]
