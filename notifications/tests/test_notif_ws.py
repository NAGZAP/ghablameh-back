from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path
from notifications.consumers import NotificationConsumer
import pytest
import json

@pytest.mark.asyncio
async def test_notification_consumer():
    # Define the route for the test
    routing = URLRouter([
        re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    ])

    # Create a WebsocketCommunicator for the test
    communicator = WebsocketCommunicator(routing, "/ws/notifications/")

    # Connect to the websocket
    connected, _ = await communicator.connect()
    assert connected

    # Send a message to the websocket
    message = {'message': 'Hello, world!'}
    await communicator.send_json_to(message)

    # Receive the message from the websocket
    response = await communicator.receive_json_from()

    # Check that the message is the same as the one we sent
    assert response == message

    # Close the connection
    await communicator.disconnect()