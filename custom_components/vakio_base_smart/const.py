"""Constants for the Vakio Openair integration."""
import datetime

from homeassistant.const import Platform

DOMAIN = "vakio_base_smart"

PLATFORMS = [Platform.FAN]

# Default consts.
DEFAULT_PORT = 1883
DEFAULT_TOPIC = "vakio"
DEFAULT_TIMEINTERVAL = datetime.timedelta(seconds=5)
DEFAULT_SMART_GATE = 4
DEFAULT_SMART_SPEED = 5
DEFAULT_SMART_EMERG_SHUNT = 10

# CONF consts.
CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_TOPIC = "topic"

# OPT consts
OPT_EMERG_SHUNT = "emerg_shunt"
OPT_SMART_SPEED = "smart_speed"
OPT_SMART_GATE = "gate"
OPT_SMART_TOPIC_PREFIX = "server"
OPT_SMART_TOPIC_ENDPOINT = "openair/mode"


# Errors.
ERROR_AUTH: str = "ошибка аутентификации"
ERROR_CONFIG_NO_TREADY: str = "конфигурация интеграции не готова"

CONNECTION_TIMEOUT = 5

# Base Smart
BASESMART_STATE_ON = "on"
BASESMART_STATE_OFF = "off"

BASESMART_WORKMODE_INFLOW = "inflow"  # Приток
BASESMART_WORKMODE_INFLOW_MAX = "inflow_max"  # Приток MAX
BASESMART_WORKMODE_RECUPERATION_SUMMER = "recuperator"  # Рекуперация лето
BASESMART_WORKMODE_RECUPERATION_WINTER = "winter"  # Рекуперация зима
BASESMART_WORKMODE_OUTFLOW = "outflow"  # Вытяжка
BASESMART_WORKMODE_OUTFLOW_MAX = "outflow_max"  # Вытяжка MAX
BASESMART_WORKMODE_NIGHT = "night"  # Ночной
BASESMART_WORKMODS_LIST = [
    BASESMART_WORKMODE_INFLOW,
    BASESMART_WORKMODE_INFLOW_MAX,
    BASESMART_WORKMODE_RECUPERATION_SUMMER,
    BASESMART_WORKMODE_RECUPERATION_WINTER,
    BASESMART_WORKMODE_OUTFLOW,
    BASESMART_WORKMODE_OUTFLOW_MAX,
    BASESMART_WORKMODE_NIGHT,
]
BASESMART_WORKMODS_NAMES_LIST = [
    "Приток",
    "Приток MAX",
    "Рекуперация (лето)",
    "Рекуперация (зима)",
    "Вытяжка",
    "Вытяжка MAX",
    "Ночной",
]
BASESMART_SPEED_01 = 1
BASESMART_SPEED_02 = 2
BASESMART_SPEED_03 = 3
BASESMART_SPEED_04 = 4
BASESMART_SPEED_05 = 5
BASESMART_SPEED_06 = 6
BASESMART_SPEED_07 = 7
BASESMART_SPEEDS_LIST = [
    BASESMART_SPEED_01,
    BASESMART_SPEED_02,
    BASESMART_SPEED_03,
    BASESMART_SPEED_04,
    BASESMART_SPEED_05,
    BASESMART_SPEED_06,
    BASESMART_SPEED_07,
]
