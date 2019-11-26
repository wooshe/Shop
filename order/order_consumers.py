from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.template import loader

from main.utils import message
from order.models import Order
from shopadmin.forms import StatusForm


class OrderConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        print('connect ')

    async def disconnect(self, code):
        print('disconnect ')

    async def receive_json(self, content):

        command = content.get("command", None)

        print('receive_json: ', content)

        try:
            if command == "join":
                user_id = content.get("user_id", None)
                if user_id == 'None':
                    user_id = self.scope["session"].session_key
                await self.join_room(user_id)
            elif command == "join_admin":
                await self.join_room_admin()
            elif command == "send":
                await self.send_room(content)
            elif command == "alarm":
                await self.alarm(content)
        except:
            pass

    async def send_room(self, content):

        to = content.get("to", None)
        sender = content.get("sender", None)

        if sender == "user":

            from_ = content.get("from", None)
            sender = content.get("sender", None)

            await self.channel_layer.group_send(
                sender + from_,
                {
                    "type": "chat_message",
                    "message": content,
                }
            )

            content['message_act'] = 'true'
            content['message'] = message('Новый заказ!', 'not_used')

            await self.channel_layer.group_send(
                'shopmain',
                {
                    "type": "chat_message",
                    "message": content,
                }
            )

        elif sender == "shop":
            await self.channel_layer.group_send(
                'user' + to,
                {
                    "type": "chat_message",
                    "message": content,
                }
            )

            await self.channel_layer.group_send(
                'shopmain',
                {
                    "type": "chat_message",
                    "message": content,
                }
            )
        else:
            obj = "none"

    async def chat_message(self, event):
        print("chat_message: ", event)
        print("chat_message_sender: ", self.channel_name)
        await self.send_json(
            {
                "message": event["message"],
            },
        )

    async def join_room(self, user_id):

        print("join_room: " + "user" + user_id + " channel_joined: " + self.channel_name)

        await self.channel_layer.group_add(
            "user" + user_id,
            self.channel_name
        )

    async def join_room_admin(self):

        print("join_room_shop: " + "shopmain" + " channel_joined: " + self.channel_name)

        await self.channel_layer.group_add(
            "shopmain",
            self.channel_name
        )

    async def alarm(self, content):
        print("alarm: ", content)

        event = content.get("event", None)

        try:
            order_id = content.get("order_id", None)
            order = await self.get_order(order_id)

            if event == "new_item":
                pass

            elif event == "select_status_change":

                select_status_option = content.get("select_status_option", None)
                order.status = select_status_option
                order.save()

            statusForm = StatusForm()
            t_admin = loader.get_template('object_admin.html')
            ctx_admin = {'order': order, 'statusForm': statusForm}
            response_admin = t_admin.render(ctx_admin)
            content["order_model_admin"] = response_admin

            t = loader.get_template('object.html')
            ctx = {'order': order}
            response = t.render(ctx)
            content["order_model"] = response

            await self.send_room(content)

        except:
            pass

    @database_sync_to_async
    def get_order(self, order_id):
        return Order.objects.get(pk=order_id)
