from ksp_time_tool.common.constants import EARTH_DAY_SECONDS, EARTH_YEAR_SECONDS


class METTime:

    def __init__(self, mission_seconds: int):
        self.mission_seconds = mission_seconds
        self._set_time_diff()

    def __str__(self):
        symb = "+" if self.mission_seconds >= 0 else "-"
        return f"T{symb} {self._diff_years}y, {self._diff_days}d," \
            + f" {self._diff_hours}:{self._diff_minutes}:{self._diff_seconds}"

    def _set_time_diff(self):
        calc_seconds = self.mission_seconds if self.mission_seconds >= 0 else -self.mission_seconds
        diff_years = calc_seconds // EARTH_YEAR_SECONDS
        rem = calc_seconds % EARTH_YEAR_SECONDS
        diff_days = rem // EARTH_DAY_SECONDS
        rem %= EARTH_DAY_SECONDS
        diff_hours = rem // (60 * 60)
        rem %= (60 * 60)
        diff_minutes = rem // 60
        rem %= 60
        diff_seconds = rem

        self._diff_years = diff_years
        self._diff_days = diff_days
        self._diff_hours = diff_hours
        self._diff_minutes = diff_minutes
        self._diff_seconds = diff_seconds
