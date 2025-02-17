from ksp_time_tool.common.constants import DateFormat
from ksp_time_tool.common.ksp_dates import EarthDate, KerbinDate, UTSeconds


class CLIInputHandler:

    def __init__(self, input_format: DateFormat):
        self.input_format = input_format
        self._set_handler()

    def _set_handler(self):
        if self.input_format == DateFormat.KERBIN:
            self._handler = KerbinCLIInputHandler()
        elif self.input_format == DateFormat.EARTH:
            self._handler = EarthCLIInputHandler()
        elif self.input_format == DateFormat.UT_SECONDS:
            self._handler = UTSecondsCLIInputHandler()
        else:
            self._handler = None

    def get_user_input(self):
        return self._handler.get_user_input() if self._handler else None


class KerbinCLIInputHandler:

    def __init__(self):
        pass

    def get_user_input(self):
        year = int(input('Year: '))
        day = int(input('Day: '))
        hour = int(input('Hour: '))
        minute = int(input('Minute: '))
        second = int(input('Second: '))
        return KerbinDate(
            year,
            day,
            hour,
            minute,
            second
        )


class EarthCLIInputHandler:

    def __init__(self):
        pass

    def get_user_input(self):
        year = int(input('Year: '))
        month = int(input('Month (number): '))
        day = int(input('Day: '))
        hour = int(input('Hour: '))
        minute = int(input('Minute: '))
        second = int(input('Second: '))
        return EarthDate(
            year,
            month,
            day,
            hour,
            minute,
            second
        )


class UTSecondsCLIInputHandler:

    def __init__(self):
        pass

    def get_user_input(self):
        seconds = int(input('UT Seconds: '))
        return UTSeconds(seconds)
