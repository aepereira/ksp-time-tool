import krpc
import krpc.error
from ksp_time_tool.common.ksp_dates import UTSeconds
from ksp_time_tool.common.met_time import METTime


def check_connection(method):
    """
    Decorator for methods below that require a live kRPC connection.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (
            krpc.error.ConnectionError,
            krpc.error.RPCError,
            krpc.error.EncodingError,
            krpc.error.StreamError
        )as c_e:
            # Return connection manager to initial state.
            self.reset()
            raise RuntimeError(f"Error with KSP connection: {c_e}") from c_e
        except OSError as os_e:
            # Return connection manager to initial state.
            self.reset()
            raise RuntimeError(f"Error probably related to KSP connection: {os_e}") from os_e
    return wrapper


class KSPConnectionManager:
    def __init__(self):
        self.connection = None
        self.vessels = []
        self.active_vessel = None
        self.mission_start_seconds = None

    def connect(self):
        """
        Connects to the KSP game using KRPC.
        Returns True if successful, False otherwise.
        """
        try:
            self.connection = krpc.connect(name="KSP Time Tool")
            self.update_vessels()
            return True
        except Exception as e:
            print(f"Failed to connect to KSP: {e}")
            return False

    @check_connection
    def update_vessels(self):
        """
        Updates the list of available vessels from the KRPC connection.
        """
        if not self.connection:
            raise RuntimeError("Not connected to KSP.")
        self.vessels = self.connection.space_center.vessels

    def get_vessels(self):
        """
        Returns the list of available vessels.
        """
        return self.vessels

    def get_active_vessel(self):
        """
        Returns the currently selected vessel.
        """
        return self.active_vessel

    @check_connection
    def select_vessel(self, index):
        """
        Selects a vessel by its index in the list of vessels.
        Returns the selected vessel object.
        """
        if index < 0 or index >= len(self.vessels):
            raise IndexError("Invalid vessel index.")
        self.active_vessel = self.vessels[index]
        # Get UT (Universal Time) in seconds
        ut_seconds = self.connection.space_center.ut
        met_seconds = int(self.active_vessel.met)
        self.mission_start_seconds = round(ut_seconds - met_seconds)
        return self.active_vessel

    @check_connection
    def get_current_time_info(self):
        """
        Retrieves the current time information from the KRPC connection.
        Returns a dictionary with Kerbin time, Earth time, UT seconds, and MET (if available).
        """
        if not self.connection:
            raise RuntimeError("Not connected to KSP.")

        # Get UT (Universal Time) in seconds
        ut_seconds = self.connection.space_center.ut
        ut_date = UTSeconds(int(ut_seconds))

        # Convert UT seconds to Kerbin and Earth formats
        kerbin_date = ut_date.convert_to_kerbin()
        earth_date = ut_date.convert_to_earth()

        # Get MET (Mission Elapsed Time) if an active vessel is selected
        met_time = None
        if self.active_vessel:
            met_seconds = int(self.active_vessel.met)
            met_time = METTime(met_seconds)      

        return {
            "kerbin": str(kerbin_date),
            "earth": str(earth_date),
            "ut_seconds": str(ut_date),
            "met": str(met_time),
            "mission_start_seconds": self.mission_start_seconds
        }

    @check_connection
    def create_alarm(self, ksp_date, link_to_vessel=False):
        """
        Creates an in-game alarm at the specified date using KRPC.

        Parameters:
            ksp_date (KSPDate): The date for the alarm.
            link_to_vessel (bool): Whether to link the alarm to the active vessel.

        Returns True if successful, False otherwise.

        Note: This function requires that you have a mod like Kerbal Alarm Clock
              that supports KRPC integration for alarms.
              If such functionality is not available, this method will need
              further implementation based on your setup.
        """
        try:
            if not self.connection:
                raise RuntimeError("Not connected to KSP.")

            # Ensure we have a valid active vessel if linking alarms
            if link_to_vessel and not self.active_vessel:
                raise ValueError("No active vessel selected for linking alarms.")

            # Convert the provided date to UT seconds
            alarm_ut_seconds = ksp_date.convert_to_seconds().seconds

            # Ensure the alarm is in the future
            current_ut_seconds = self.connection.space_center.ut
            if alarm_ut_seconds <= current_ut_seconds:
                raise ValueError("Cannot set an alarm in the past.")

            # Set the alarm.
            alarm_manager = self.connection.space_center.AlarmManager
            alarm_title = getattr(ksp_date, "name", None)
            seconds_til_alarm = alarm_ut_seconds - current_ut_seconds
            if link_to_vessel and self.active_vessel:
                alarm_manager.add_vessel_alarm(seconds_til_alarm, self.active_vessel,
                                               title=alarm_title or "KSP Time Tool Alarm")
            else:
                alarm_manager.add_alarm(seconds_til_alarm,
                                        title=alarm_title or "KSP Time Tool Alarm")

            print(f"Alarm created at: {ksp_date.convert_to_earth()} (Linked to vessel: {link_to_vessel})")
            return True

        except Exception as e:
            print(f"Failed to create alarm: {e}")
            return False

    def reset(self):
        self.connection = None
        self.vessels = []
        self.active_vessel = None
        self.mission_start_seconds = None
