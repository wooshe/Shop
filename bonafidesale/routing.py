from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.conf.urls import url

from order.order_consumers import OrderConsumer

application = ProtocolTypeRouter({

    'websocket': AllowedHostsOriginValidator(
            URLRouter(
                [
                    url(r'^ws/order_socket/$', OrderConsumer)
                ]
            )
    )

})
