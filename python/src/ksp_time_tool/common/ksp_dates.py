"""
Classes that handle date logic.
"""
import calendar
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from ksp_time_tool.common.constants import (KERBAL_EPOCH,
                                            KERBIN_DAY_SECONDS,
                                            KERBIN_YEAR_DAYS, DateFormat)
from ksp_time_tool.common.visitors import KSPDateVisitor


class KSPDate(ABC):

    @abstractmethod
    def get_date_format(self):
        pass

    @abstractmethod
    def convert_to_kerbin(self):
        pass

    @abstractmethod
    def convert_to_earth(self):
        pass

    @abstractmethod
    def convert_to_seconds(self):
        pass

    @abstractmethod
    def accept_visitor(self, visitor: KSPDateVisitor):
        pass


class KerbinDate(KSPDate):

    def __init__(self, year: int, day: int, hour: int, minute: int, second: int):
        self._date_format = DateFormat.KERBIN
        self.year = year
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

        self._as_seconds = None
        self._as_earth_date = None

    def __str__(self):
        return f"Year {self.year}, Day {self.day} {self.hour}:{self.minute}:{self.second}"

    def get_date_format(self):
        return self._date_format

    def convert_to_kerbin(self):
        return self

    def convert_to_earth(self):
        return self._as_earth_date or self._convert_to_earth()

    def convert_to_seconds(self):
        return self._as_seconds or self._convert_to_seconds()

    def accept_visitor(self, visitor: KSPDateVisitor):
        visitor.visit_kerbin_date(self)

    def _convert_to_earth(self):
        """
        Converts to an Earth date.

        Sets and returns self._as_earth_date.
        """
        seconds = self.convert_to_seconds()
        self._as_earth_date = seconds.convert_to_earth()
        return self._as_earth_date

    def _convert_to_seconds(self):
        """
        Converts a Kerbin date (year, day, hour, minute, second) to seconds since
        the Kerbal epoch. Kerbin Year 1, Day 1 at midnight corresponds to 0 seconds.

        Sets and returns self.as_seconds.
        """
        # Compute the total number of complete Kerbin days that have passed.
        # (subtract 1 because both years and days are 1-indexed)
        total_days = (self.year - 1) * KERBIN_YEAR_DAYS + (self.day - 1)
        seconds_from_days = total_days * KERBIN_DAY_SECONDS
        seconds_from_time = self.hour * 3600 + self.minute * 60 + self.second
        total_seconds = seconds_from_days + seconds_from_time
        self._as_seconds = UTSeconds(total_seconds)
        return self._as_seconds


class EarthDate(KSPDate):

    def __init__(self, year: int, month: int, day: int, hour: int, minute: int, second: int):
        self._date_format = DateFormat.EARTH
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

        self._as_seconds = None
        self._as_kerbin_date = None

    def __str__(self):
        return f"{self.day} {calendar.month_abbr[self.month]}" +\
            f" {self.year} {self.hour}:{self.minute}:{self.second}"

    def get_date_format(self):
        return self._date_format

    def convert_to_kerbin(self):
        return self._as_kerbin_date or self._convert_to_kerbin()

    def convert_to_seconds(self):
        return self._as_seconds or self._convert_to_seconds()

    def convert_to_earth(self):
        return self

    def accept_visitor(self, visitor: KSPDateVisitor):
        visitor.visit_earth_date(self)

    def _convert_to_seconds(self):
        """
        Converts an Earth date (year, month, day, hour, minute, second) to
        the number of seconds since the Kerbal epoch (1 Jan 1951 00:00:00).
        """
        dt = datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
        delta = dt - KERBAL_EPOCH
        total_seconds = int(delta.total_seconds())
        self._as_seconds = UTSeconds(total_seconds)
        return self._as_seconds

    def _convert_to_kerbin(self):
        """
        Converts to a Kerbin date.

        Sets and returns self._as_kerbin_date.
        """
        seconds = self.convert_to_seconds()
        self._as_kerbin_date = seconds.convert_to_kerbin()
        return self._as_kerbin_date


class UTSeconds(KSPDate):

    def __init__(self, seconds: int):
        self._date_format = DateFormat.UT_SECONDS
        self.seconds = seconds

        self._as_kerbin_date = None
        self._as_earth_date = None

    def __str__(self):
        return f"UT Seconds: {self.seconds}"

    def get_date_format(self):
        return self._date_format

    def convert_to_kerbin(self):
        return self._as_kerbin_date or self._convert_to_kerbin()

    def convert_to_earth(self):
        return self._as_earth_date or self._convert_to_earth()

    def convert_to_seconds(self):
        return self

    def accept_visitor(self, visitor: KSPDateVisitor):
        visitor.visit_ut_seconds(self)

    def _convert_to_kerbin(self):
        """
        Converts UT seconds (seconds since the Kerbal epoch) to a Kerbin date.
        Sets and returns self._as_earth_date.
        """
        # Calculate the total number of Kerbin days that have fully elapsed.
        total_kerbin_days = self.seconds // KERBIN_DAY_SECONDS
        # Kerbin years are 1-indexed.
        kerbin_year = total_kerbin_days // KERBIN_YEAR_DAYS + 1
        kerbin_day = total_kerbin_days % KERBIN_YEAR_DAYS + 1

        # Remaining seconds in the current Kerbin day
        remaining_seconds = self.seconds % KERBIN_DAY_SECONDS
        hour = remaining_seconds // 3600
        minute = (remaining_seconds % 3600) // 60
        second = remaining_seconds % 60

        # Set and return self._as_kerbin_date
        self._as_kerbin_date = KerbinDate(
            kerbin_year,
            kerbin_day,
            hour,
            minute,
            second
        )
        return self._as_kerbin_date

    def _convert_to_earth(self):
        """
        Converts UT seconds (seconds since the Kerbal epoch) to an Earth date.
        Sets and returns self._as_earth_date.
        """
        dt = KERBAL_EPOCH + timedelta(seconds=self.seconds)
        self._as_earth_date = EarthDate(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second
        )
        return self._as_earth_date
