"""Service classes for interacting with Vakio devices."""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import random
from typing import Any

import paho.mqtt.client as mqtt

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    BASESMART_STATE_OFF,
    BASESMART_STATE_ON,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_TOPIC,
    CONF_USERNAME,
    DEFAULT_TIMEINTERVAL,
    DOMAIN,
    OPT_SMART_TOPIC_ENDPOINT,
    OPT_SMART_TOPIC_PREFIX,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

SPEED_ENDPOINT = "speed"
STATE_ENDPOINT = "state"
WORKMODE_ENDPOINT = "workmode"
ENDPOINTS = [
    SPEED_ENDPOINT,
    STATE_ENDPOINT,
    WORKMODE_ENDPOINT,
]


class MqttClient:
    """MqttClient class for connecting to a broker."""

    def __init__(
        self,
        hass: HomeAssistant,
        data: dict(str, Any),  # type: ignore
        coordinator: Coordinator | None = None,
    ) -> None:
        """Initialize."""
        self.hass = hass
        self.data = data

        self.client_id = f"python-mqtt-{random.randint(0, 1000)}"
        self._client = mqtt.Client(client_id=self.client_id)
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

        self._coordinator = coordinator
        self.is_run = False
        self.subscribes_count = 0
        if len(self.data.keys()) == 5:
            self._client.username_pw_set(
                self.data[CONF_USERNAME], self.data[CONF_PASSWORD]
            )

        self._paho_lock = asyncio.Lock()  # Prevents parallel calls to the MQTT client
        self.is_connected = False

    def on_message(self, client, userdata, message: mqtt.MQTTMessage):
        """Реакция на сообщение."""
        key = str.split(message.topic, "/")[-1]
        self._client.unsubscribe(topic=message.topic)
        value = message.payload.decode()
        if value is not None:
            with contextlib.suppress(ValueError):
                value = int(value)

        self._coordinator.condition[key] = value  # type: ignore
        # for k, val in self._coordinator.condition.items():
        #     _LOGGER.error("%s: %s", k, val)

    def on_connect(self, client, userdata, flags, rc):  # pylint: disable=invalid-name
        """Реакция на подключение."""
        self.is_connected = True

    async def connect(self) -> bool:
        """Connect with the broker."""
        try:
            await self.hass.async_add_executor_job(
                self._client.connect, self.data[CONF_HOST], self.data[CONF_PORT]
            )
            self._client.loop_start()
            return True
        except OSError as err:
            _LOGGER.error("Failed to connect to MQTT server due to exception: %s", err)

        return False

    async def disconnect(self) -> None:
        """Disconnect from the broker."""

        def stop() -> None:
            """Stop the MQTT client."""
            self._client.loop_stop()

        async with self._paho_lock:
            self.is_connected = False
            await self.hass.async_add_executor_job(stop)
            self._client.disconnect()

    async def try_connect(self) -> bool:
        """Try to create connection with the broker."""
        self._client.on_connect = None

        try:
            self._client.connect(self.data[CONF_HOST], self.data[CONF_PORT])
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    async def subscribe(self) -> None:
        """Подписка на топики."""
        self.subscribes_count += 1
        async with self._paho_lock:
            _, mid = await self.hass.async_add_executor_job(
                self._client.subscribe,
                [(f"{self.data[CONF_TOPIC]}/{endpoint}", 0) for endpoint in ENDPOINTS],
            )
        for endpoint in ENDPOINTS:
            _LOGGER.debug("Subscribe to %s, mid: %s, qos: %s", endpoint, mid, 0)

    async def get_condition(
        self,
    ) -> dict(str, Any):  # type: ignore
        """Get condition of device."""
        await self.subscribe()
        return self._coordinator.condition  # type: ignore

    async def publish(self, endpoint: str, msg: str, prefix: str | None = None) -> bool:
        """Publish commands to topic."""
        topic = self.data[CONF_TOPIC] + "/" + endpoint
        if prefix is not None:
            topic = prefix + "/" + topic

        qos = 0
        retain = True
        async with self._paho_lock:
            await self.hass.async_add_executor_job(
                self._client.publish, topic, msg, qos, retain
            )

        return True


class Coordinator(DataUpdateCoordinator):
    """Class for interact with Broker and HA."""

    def __init__(self, hass: HomeAssistant, data: dict(str, Any)) -> None:  # type: ignore
        """Функция инициализации."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=DEFAULT_TIMEINTERVAL
        )
        self._data = data
        self.mqttc = MqttClient(self.hass, data, self)
        self.last_update = None
        self.condition = {
            SPEED_ENDPOINT: None,
            WORKMODE_ENDPOINT: None,
            STATE_ENDPOINT: None,
        }
        self.is_logged_in = False

    async def async_login(self) -> bool:
        """Авторизация в брокере."""
        if self.is_logged_in is True:
            return True

        status = await self.mqttc.connect()
        await self.mqttc.subscribe()
        if not status:
            _LOGGER.error("Auth error")
        self.is_logged_in = True
        return status

    async def _async_update_data(self) -> bool:
        """Get all data."""
        await self.mqttc.get_condition()
        return True

    async def _async_update(self, now) -> None:
        """Async Update.

        Функция регистритуется в hass, во всех датчиках и устройствах и контролирует
        обновление данных через API не чаще чем раз в 2 секунды.
        """
        await self.mqttc.get_condition()

    async def speed(self, value: int | None = None) -> int | bool | None:
        """Speed of fan."""
        if value is None:
            return self.condition[SPEED_ENDPOINT]

        return await self.mqttc.publish(SPEED_ENDPOINT, value)  # type: ignore

    async def state(self, value: str | None = None) -> str | bool | None:
        """State of device."""
        if value is None:
            return self.condition[STATE_ENDPOINT]

        return await self.mqttc.publish(STATE_ENDPOINT, value)

    async def workmode(self, value: str | None = None) -> str | bool | None:
        """Workmode of device: manual or super_auto."""
        if value is None:
            return self.condition[WORKMODE_ENDPOINT]

        return await self.mqttc.publish(WORKMODE_ENDPOINT, value)

    def get_speed(self) -> int | bool | None:
        """Speed of fan."""
        return self.condition[SPEED_ENDPOINT]

    def get_state(self) -> str | bool | None:
        """State of device."""
        return self.condition[STATE_ENDPOINT]

    def get_workmode(self) -> str | bool | None:
        """Workmode of device: manual or super_auto."""
        return self.condition[WORKMODE_ENDPOINT]

    async def turn_on(self) -> bool:
        """Включение устройства."""
        return await self.state(BASESMART_STATE_ON)  # type: ignore

    async def turn_off(self) -> bool:
        """Выключение устройства."""
        return await self.state(BASESMART_STATE_OFF)  # type: ignore

    def is_on(self) -> bool:
        """Возвращается `bool` значение 'Включено ли устройство'."""
        current_state = self.get_state()
        return current_state == BASESMART_STATE_ON

    async def update_smart_mode(self, emerg_hunt: int, gate: int, speed: int) -> None:
        """Изменение параметров режима SMART."""
        command = {
            "settings": [
                {"gate": gate},
                {"smart_speed": speed},
                {"emerg_shunt": emerg_hunt},
            ]
        }
        command_json = json.dumps(command)
        await self.mqttc.publish(
            OPT_SMART_TOPIC_ENDPOINT, command_json, OPT_SMART_TOPIC_PREFIX
        )
