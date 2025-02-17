from ksp_time_tool.common.ksp_dates import EarthDate, KerbinDate, UTSeconds
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (QComboBox, QDateEdit, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QTimeEdit, QVBoxLayout,
                             QWidget)


class TimeInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Name input
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit("Time 1")  # Default name
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_input)
        self.layout.addLayout(name_layout)

        # Format dropdown
        self.format_label = QLabel("Format:")
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(["Kerbin", "Earth", "UT Seconds"])
        self.format_dropdown.currentIndexChanged.connect(self.update_input_fields)
        format_layout = QHBoxLayout()
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_dropdown)
        self.layout.addLayout(format_layout)

        # Dynamic input fields container
        self.input_fields_container = QWidget()
        self.input_fields_layout = QVBoxLayout()
        self.input_fields_layout.setContentsMargins(10, 10, 10, 10)
        self.input_fields_layout.setSpacing(5)
        self.input_fields_container.setLayout(self.input_fields_layout)
        self.layout.addWidget(self.input_fields_container)

        # Initialize with Kerbin input fields
        self.update_input_fields()

    def get_ksp_date(self):
        """
        Returns a KSPDate object based on user input and selected format.
        """
        selected_format = self.format_dropdown.currentText()

        if selected_format == "Kerbin":
            year = self.year_input.value()
            day = self.day_input.value()
            hour = self.hour_input.value()
            minute = self.minute_input.value()
            second = self.second_input.value()
            return KerbinDate(year, day, hour, minute, second)

        elif selected_format == "Earth":
            date = self.date_input.date().toPyDate()  # Get QDate as Python date
            time = self.time_input.time().toPyTime()  # Get QTime as Python time
            return EarthDate(date.year, date.month, date.day, time.hour, time.minute, time.second)

        elif selected_format == "UT Seconds":
            ut_seconds = self.ut_seconds_input.value()
            return UTSeconds(ut_seconds)

        else:
            raise ValueError("Invalid date format selected.")

    def update_input_fields(self):
        """
        Updates the input fields based on the selected time format.
        Ensures that previous fields are completely removed.
        """
        # Clear current input fields by removing all child widgets and layouts
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()  # Properly delete the widget
                child_layout = item.layout()
                if child_layout:
                    clear_layout(child_layout)  # Recursively clear nested layouts

        clear_layout(self.input_fields_layout)

        # Add new input fields based on the selected format
        selected_format = self.format_dropdown.currentText()
        if selected_format == "Kerbin":
            self._add_kerbin_input_fields()
        elif selected_format == "Earth":
            self._add_earth_input_fields()
        elif selected_format == "UT Seconds":
            self._add_ut_seconds_input_field()


    def _add_kerbin_input_fields(self):
        """
        Adds input fields for Kerbin date (Year, Day, HH:MM:SS) in a single row.
        """
        kerbin_input_layout = QHBoxLayout()

        # Year input
        year_label = QLabel("Year:")
        self.year_input = QSpinBox()
        self.year_input.setRange(1, 9999)
        self.year_input.setValue(1)

        # Day input
        day_label = QLabel("Day:")
        self.day_input = QSpinBox()
        self.day_input.setRange(1, 426)
        self.day_input.setValue(1)

        # Time inputs (HH:MM:SS)
        time_label = QLabel("Time:")
        self.hour_input = QSpinBox()
        self.hour_input.setRange(0, 5)
        self.hour_input.setValue(0)

        self.minute_input = QSpinBox()
        self.minute_input.setRange(0, 59)
        self.minute_input.setValue(0)

        self.second_input = QSpinBox()
        self.second_input.setRange(0, 59)
        self.second_input.setValue(0)

        time_inputs_layout = QHBoxLayout()
        time_inputs_layout.addWidget(self.hour_input)
        time_inputs_layout.addWidget(QLabel(":"))
        time_inputs_layout.addWidget(self.minute_input)
        time_inputs_layout.addWidget(QLabel(":"))
        time_inputs_layout.addWidget(self.second_input)

        # Add widgets to layout
        kerbin_input_layout.addWidget(year_label)
        kerbin_input_layout.addWidget(self.year_input)
        kerbin_input_layout.addWidget(day_label)
        kerbin_input_layout.addWidget(self.day_input)
        kerbin_input_layout.addStretch()  # Add spacing
        kerbin_input_layout.addWidget(time_label)
        kerbin_input_layout.addLayout(time_inputs_layout)

        # Add layout to main input fields layout
        self.input_fields_layout.addLayout(kerbin_input_layout)

    def _add_earth_input_fields(self):
        """
        Adds input fields for Earth date (Calendar widget for date selection and HH:MM:SS for time).
        """
        earth_input_layout = QHBoxLayout()

        # Date input
        date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate(1951, 1, 1))  # Default to Kerbal epoch

        # Time input
        time_label = QLabel("Time:")
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm:ss")
        self.time_input.setTime(self.time_input.time().fromString("00:00:00", "HH:mm:ss"))

        # Add widgets to horizontal layout
        earth_input_layout.addWidget(date_label)
        earth_input_layout.addWidget(self.date_input)
        earth_input_layout.addWidget(time_label)
        earth_input_layout.addWidget(self.time_input)

        # Add horizontal layout to main input fields layout
        self.input_fields_layout.addLayout(earth_input_layout)

    def _add_ut_seconds_input_field(self):
        """
        Adds an input field for UT Seconds (Universal Time in seconds since the Kerbal epoch).
        """
        # UT Seconds input
        ut_seconds_label = QLabel("UT Seconds:")
        # Will probably want to change this to a QLineInput with custom validation
        # for ints from 0 to largest UT in Kerbal: 19760285526235197.
        self.ut_seconds_input = QSpinBox()
        self.ut_seconds_input.setRange(0, 2147483647)  # Large range for UT seconds
        self.ut_seconds_input.setValue(0)  # Default value

        # Add widgets to the layout
        self.input_fields_layout.addWidget(ut_seconds_label)
        self.input_fields_layout.addWidget(self.ut_seconds_input)
