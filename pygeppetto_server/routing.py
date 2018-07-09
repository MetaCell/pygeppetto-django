from django.conf.urls import url
from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter

from pygeppetto_server.consumers import GeppettoConsumer, \
                        GeppettoGatewayConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
            url(r"^{}$".format(settings.GEPPETTO_SOCKET_URL),
                GeppettoConsumer),
            url(r"^gateway$", GeppettoGatewayConsumer)
                            ])
})
