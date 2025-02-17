"""
Constants for conversions

and DateFormat Enum to help with interface and parsing.
"""
from datetime import datetime
from enum import Enum

KERBAL_EPOCH = datetime(1951, 1, 1, 0, 0, 0)
KERBIN_DAY_SECONDS = 6 * 3600  # 6 hours = 21,600 seconds
KERBIN_YEAR_DAYS = 426

# Fixed 365-day year for MET conversion.
EARTH_DAY_SECONDS = 60 * 60 * 24
EARTH_YEAR_SECONDS = EARTH_DAY_SECONDS * 365


class DateFormat(Enum):
    KERBIN = 1
    EARTH = 2
    UT_SECONDS = 3


QUIT_SIGNAL = -1
