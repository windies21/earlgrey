# Copyright 2017 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# The original codes exist in aio_pika.patterns.master

import logging
from typing import Optional, TYPE_CHECKING

from aio_pika.channel import Channel
from aio_pika.message import Message, DeliveryMode, ReturnedMessage
from aio_pika.patterns.base import Base

if TYPE_CHECKING:
    from aio_pika import Queue


class ClientAsync(Base):
    CONTENT_TYPE = 'application/python-pickle'
    DELIVERY_MODE = DeliveryMode.PERSISTENT

    def __init__(self, channel: Channel, queue_name):
        self.channel = channel
        self.queue_name = queue_name
        self.queue: Optional[Queue] = None

        self.channel.add_on_return_callback(self._on_message_returned)

    async def initialize_queue(self, **kwargs):
        self.queue = await self.channel.declare_queue(name=self.queue_name, **kwargs)

    async def close(self):
        pass

    async def call(self, func_name: str, kwargs=None, priority=128):
        message = Message(
            body=self.serialize(kwargs or {}),
            content_type=self.CONTENT_TYPE,
            delivery_mode=self.DELIVERY_MODE,
            priority=priority,
            headers={
                'FuncName': func_name
            }
        )

        await self.channel.default_exchange.publish(
            message, self.queue_name, mandatory=True
        )

    @staticmethod
    def _on_message_returned(sender, message: ReturnedMessage, *args, **kwargs):
        logging.warning(
            f"Message returned. Probably destination queue does not exists: ({sender}) {message}"
        )
