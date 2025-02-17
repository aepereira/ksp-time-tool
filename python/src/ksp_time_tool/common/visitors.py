"""
Visitor classes to add additional properties and behaviors to dates.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ksp_time_tool.common.met_time import METTime

if TYPE_CHECKING:
    from ksp_time_tool.common.ksp_dates import (EarthDate, KerbinDate, KSPDate,
                                                UTSeconds)


class KSPDateVisitor(ABC):

    @abstractmethod
    def visit_kerbin_date(self, host: "KerbinDate"):
        pass

    @abstractmethod
    def visit_earth_date(self, host: "EarthDate"):
        pass

    @abstractmethod
    def visit_ut_seconds(self, host: "UTSeconds"):
        pass


class KSPDateNameVisitor(KSPDateVisitor):

    def __init__(self, name):
        self.name = name

    def visit_kerbin_date(self, host: "KerbinDate"):
        self._set_host_name(host)

    def visit_earth_date(self, host: "EarthDate"):
        self._set_host_name(host)

    def visit_ut_seconds(self, host: "UTSeconds"):
        self._set_host_name(host)

    def _set_host_name(self, host: "KSPDate"):
        host.name = self.name


class KSPDateMETVisitor(KSPDateVisitor):

    def __init__(self, mission_start_seconds):
        self.mission_start_seconds = mission_start_seconds

    def visit_kerbin_date(self, host: "KerbinDate"):
        self._set_host_met_time(host)

    def visit_earth_date(self, host: "EarthDate"):
        self._set_host_met_time(host)

    def visit_ut_seconds(self, host: "UTSeconds"):
        self._set_host_met_time(host)

    def _set_host_met_time(self, host: "KSPDate"):
        host.met_time = METTime(host.convert_to_seconds().seconds - self.mission_start_seconds)
