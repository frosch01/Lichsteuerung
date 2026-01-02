"""Interface to MQTT broker, fetch Victron VenusOS topics"""
import asyncio

from aiomqtt import Client, MqttError
from gpio_map import S0Event
from sun import SunEvent
from io_control import DetectorEvent

RECONNECT_TIME_SECS=5.

class MqttIf():
    """Interface singleton class to MQTT broker
    """
    def __init__(self):
        self.event_queue = asyncio.Queue()
        self.cancel = False
        self.task = None

    async def main(self):
        """ Connect to broker, publish and receive topics"""
        while not self.cancel:
            try:
                async with Client("ekrano.fritz.box") as client:
                    print("MQTT interface is connected!")
                    await asyncio.gather(
                        self.__publish_s0_events(client),
                        # self.__mqtt_receive(client),
                    )
            except MqttError:
                    print(f"MQTT connection lost; Reconnecting in {RECONNECT_TIME_SECS} seconds ...")
                    await asyncio.sleep(RECONNECT_TIME_SECS)

    async def __publish_s0_events(self, client: Client):
        """Fetch events from event queue and publish on MQTT"""
        loop = asyncio.get_running_loop()
        while not self.cancel:
            json = ""
            topic = ""
            event = await self.event_queue.get()
            match event:
                case S0Event():
                    json = f'{{ "time": {event.event.timestamp_ns}}}'
                    topic = "outside/sensor/motion/" + \
                            ("yard", "terrasse", "garage")[event.s0_index]

                case SunEvent():
                    print("received sun event", event)

                case DetectorEvent():
                    json = f'{{"s0":{event.s0},"gpio":{event.gpio},"time":{event.timestamp}}}'
                    topic ="outside/sensor/motion/" + event.name

                case _:
                    print("received unknown event: ", event)

            # Publish topic via MQTT broker
            if topic:
                await client.publish(topic, payload=json)

    async def __mqtt_receive(self, client: Client):
        """Subscribe and receive some battery related VensuOS MQTT topics"""
        while not self.cancel:
            #await client.subscribe("#")
            await client.subscribe("N/c0619ab8cd80/battery/512/Dc/0/#")
            #await client.subscribe("N/c0619ab8cd80/battery/512/+")
            async for message in client.messages:
                print(message.topic, message.payload)

    @property
    def queue(self):
        """The queue for pushing events to MQTT

        The events expected to be pushed shall have types S0Event or SunEvent
        """
        return self.event_queue
