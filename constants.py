from enum import Enum


class SeriesId(Enum):
    GT3_SPRINT = 228
    GT3_FIXED = 444
    GT4_FIXED = 491
    IMSA = 447
    PRODUCTION_CAR_CHALLENGE = 112
    TOURING_CAR_FIXED = 430


class EventType(Enum):
    PRACTICE = 2
    RACE = 5
