from __future__ import absolute_import

from django.conf.urls import url
from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter

from pygeppetto_server.consumers import GeppettoConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
            url(r"^{}$".format(settings.GEPPETTO_SOCKET_URL), GeppettoConsumer)
        ])
})
