from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.conf.urls import url

from pygeppetto_server.consumers import (
    GeppettoConsumer, GeppettoGatewayConsumer
)

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(
            [
                url(
                    r"^{}$".format(settings.PYGEPPETTO_SOCKET_URL),
                    GeppettoConsumer
                ),
                url(r"^gateway$", GeppettoGatewayConsumer)
            ]
        )
    }
)
