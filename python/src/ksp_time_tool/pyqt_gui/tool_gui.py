import sys

from ksp_time_tool.common.ksp_dates import KSPDate
from ksp_time_tool.common.visitors import KSPDateNameVisitor, KSPDateMETVisitor
from ksp_time_tool.pyqt_gui.time_input_widgets import TimeInputWidget
from ksp_time_tool.common.ksp_connection_manager import KSPConnectionManager
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QListWidgetItem, QMainWindow, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)


class KSPTimeTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KSP Time Tool")
        self.setGeometry(100, 100, 800, 600)

        # Connection Manager (handles KRPC connection)
        self.ksp_connection_manager = KSPConnectionManager()

        # QTimer for polling time updates
        self.time_poll_timer = QTimer(self)
        self.time_poll_timer.setInterval(50)  # Poll every 50 ms
        self.time_poll_timer.timeout.connect(self.update_current_time)

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Current time and vessel display
        self.current_time_label = QLabel("Current Time: Not Connected")
        self.current_time_label.setAlignment(Qt.AlignCenter)
        self.current_vessel_label = QLabel("Current Vessel: None")
        vessel_label_font = self.current_vessel_label.font()
        vessel_label_font.setBold(True)
        self.current_vessel_label.setFont(vessel_label_font)
        self.current_vessel_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.current_time_label)
        main_layout.addWidget(self.current_vessel_label)

        # Connect to KSP button and vessel dropdown
        connect_button = QPushButton("Connect to KSP")
        connect_button.clicked.connect(self.connect_to_ksp)
        main_layout.addWidget(connect_button)

        self.vessel_dropdown = QComboBox()
        self.vessel_dropdown.currentIndexChanged.connect(self.select_vessel)
        main_layout.addWidget(self.vessel_dropdown)

        # Time input widget (contextual inputs for Kerbin/Earth/UT Seconds)
        self.time_input_widget = TimeInputWidget()
        main_layout.addWidget(self.time_input_widget)

        # Add New Time button
        add_time_button = QPushButton("Add New Time")
        add_time_button.clicked.connect(self.add_new_time)
        main_layout.addWidget(add_time_button)

        # Add global checkbox for linking all times to vessel
        self.global_link_checkbox = QCheckBox("Link All Times to Vessel")
        self.global_link_checkbox.setToolTip("Check/uncheck all individual link checkboxes")
        self.global_link_checkbox.stateChanged.connect(self.toggle_all_links)
        self.global_link_checkbox.setEnabled(False)
        main_layout.addWidget(self.global_link_checkbox)

        # Time list display
        self.time_list_widget = QListWidget()
        main_layout.addWidget(self.time_list_widget)

        # Add horizontal layout for Create Alarms and Sort buttons
        button_layout = QHBoxLayout()

        create_alarms_button = QPushButton("Create Alarms for All")
        create_alarms_button.clicked.connect(self.create_alarms_for_all)
        button_layout.addWidget(create_alarms_button)

        sort_button = QPushButton("Sort")
        sort_button.setToolTip("Sort times in ascending UT order")
        sort_button.clicked.connect(self.sort_times)
        button_layout.addWidget(sort_button)

        main_layout.addLayout(button_layout)

    def connect_to_ksp(self):
        if self.ksp_connection_manager.connect():
            QMessageBox.information(self, "Connection Successful", "Connected to KSP!")
            self.update_vessels()
            self.update_current_time()
            if not self.ksp_connection_manager.vessels:
                QMessageBox.warning(self, "No Vessels Found", "No vessels are currently available.")
            # Start polling for time updates (even if no vessels are found)
            self.time_poll_timer.start()
            print("Started polling for time updates.")
        else:
            QMessageBox.critical(self, "Connection Failed", "Could not connect to KSP.")
            return

    def handle_connection_error(self, error):
        QMessageBox.critical(self, "KSP Client Connection Error", f"{error}")
        self.vessel_dropdown.clear()
        self.global_link_checkbox.setEnabled(False)
        self.toggle_all_links(False, disable=True)
        self.time_poll_timer.stop()

    def update_vessels(self):
        vessels = self.ksp_connection_manager.get_vessels()
        self.vessel_dropdown.clear()
        for vessel in vessels:
            self.vessel_dropdown.addItem(vessel.name)

    def select_vessel(self, index):
        """
        Updates the current vessel selection and enables/disables link checkboxes.
        """
        if index >= 0:
            prev_vessel = self.ksp_connection_manager.get_active_vessel()
            try:
                selected_vessel = self.ksp_connection_manager.select_vessel(index)
            except RuntimeError as r_e:
                selected_vessel = None
                self.handle_connection_error(r_e)

            if selected_vessel:
                self.current_vessel_label.setText(f"Current Vessel: {selected_vessel.name}")
                self.global_link_checkbox.setEnabled(True)  # Enable global checkbox
                # Enable checkboxes for individual list items
                for i in range(self.time_list_widget.count()):
                    list_item = self.time_list_widget.item(i)
                    custom_widget = self.time_list_widget.itemWidget(list_item)  # Get custom widget

                    if custom_widget:
                        link_checkbox = custom_widget.findChild(QCheckBox)  # Find the checkbox
                        if link_checkbox:
                            link_checkbox.setEnabled(True)  # Enable the checkbox
                # Toggle all checkboxes if we switched to a different vessel:
                if selected_vessel != prev_vessel:
                    self.global_link_checkbox.setChecked(False)
                    self.toggle_all_links(False)
                self.update_current_time()
            else:
                self.global_link_checkbox.setEnabled(False)  # Disable global checkbox if no vessel

    def update_current_time(self):
        try:
            time_info = self.ksp_connection_manager.get_current_time_info()
        except RuntimeError as r_e:
            time_info = None
            self.handle_connection_error(r_e)

        if time_info:
            current_time_text = (
                f"{time_info['kerbin']}\n"
                f"{time_info['earth']}\n"
                f"{time_info['ut_seconds']}"
            )
            if time_info.get('met'):
                current_time_text += f"\nMET: {time_info['met']}"
            self.current_time_label.setText(current_time_text)

            mission_start_seconds = time_info.get('mission_start_seconds')

            # Iterate over time list and update their MET times if we have mission_start_seconds info.
            if mission_start_seconds:
                # Extract all items and their associated data
                for i in range(self.time_list_widget.count()):
                    list_item = self.time_list_widget.item(i)
                    ksp_date = list_item.data(Qt.UserRole)  # Retrieve associated KSPDate object
                    custom_widget = self.time_list_widget.itemWidget(list_item)  # Retrieve custom widget

                    if ksp_date and custom_widget:
                        # This updates the met_time property of ksp_date.
                        visitor = KSPDateMETVisitor(mission_start_seconds)
                        ksp_date.accept_visitor(visitor)
                        # Update the last line in the item_text for this list item
                        item_text = (
                            f"{ksp_date.convert_to_kerbin()}<br>"
                            f"{ksp_date.convert_to_earth()}<br>"
                            f"{ksp_date.convert_to_seconds()}<br>"
                            f"MET: {ksp_date.met_time}"
                        )

                        # Update the custom widget's display to reflect the new MET time
                        text_label = custom_widget.findChild(QLabel, "text_label")  # Assuming QLabel is used for text
                        if text_label:
                            text_label.setText(item_text)

    def add_new_time(self):
        """
        Adds a new time entry to the list widget based on the input from the time input widget.
        Each entry includes a name, time details, and buttons for removal and alarm creation.
        """
        try:
            # Get the KSPDate object from the time input widget
            ksp_date = self.time_input_widget.get_ksp_date()
            name = self.time_input_widget.name_input.text()  # Get the name of the time entry
            list_item, frame = self.create_list_item(name, ksp_date)

            # Add the frame to the QListWidget and set its size hint
            self.time_list_widget.addItem(list_item)
            self.time_list_widget.setItemWidget(list_item, frame)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add new time: {e}")

    def create_list_item(self, name: str, ksp_date: KSPDate, link_checked: bool = False):
        # Prepare the text for display in the list item
        item_text = (
            f"{ksp_date.convert_to_kerbin()}<br>"
            f"{ksp_date.convert_to_earth()}<br>"
            f"{ksp_date.convert_to_seconds()}<br>"
            f"MET: {getattr(ksp_date, 'met_time', '')}"
        )

        # Create a QListWidgetItem
        list_item = QListWidgetItem()
        list_item.setData(Qt.UserRole, ksp_date)  # Associate KSPDate with this item

        # Create a custom widget for better layout and visual separation
        custom_widget = QWidget()
        custom_layout = QVBoxLayout()
        custom_layout.setContentsMargins(10, 5, 5, 10)  # Add padding around each item

        # Add buttons and checkbox in a horizontal layout
        button_layout = QHBoxLayout()

        link_checkbox = QCheckBox("Link to Vessel")
        link_checkbox.setEnabled(self.global_link_checkbox.isEnabled())  # Grey out if no vessel
        link_checkbox.setToolTip("Link this alarm to the currently selected vessel")
        if link_checkbox.isEnabled() and link_checked:
            link_checkbox.setChecked(link_checked)

        remove_button = QPushButton("X")
        remove_button.setFixedSize(20, 20)  # Smaller button size
        remove_button.setToolTip("Remove this time entry")
        remove_button.clicked.connect(lambda: self.remove_item(list_item))

        clock_button = QPushButton("⏰")
        clock_button.setFixedSize(20, 20)  # Smaller button size
        clock_button.setToolTip("Create an in-game alarm for this time")
        clock_button.clicked.connect(lambda: self.create_alarm(ksp_date, link_checkbox.isChecked()))

        button_layout.addWidget(clock_button)
        button_layout.addWidget(link_checkbox)
        button_layout.addStretch()
        button_layout.addWidget(remove_button)

        custom_layout.addLayout(button_layout)

        # Add editable name field with styling
        name_edit = QLineEdit(name)
        name_edit.setStyleSheet("""
            QLineEdit {
                font-size: 12px;
                font-weight: bold;
                border: 1px solid lightgray;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 1px solid blue;
            }
        """)
        name_edit.setFrame(True)  # Show a border around the field
        name_edit.setPlaceholderText("Click to edit name")  # Placeholder text
        name_edit.setToolTip("Click to edit this time's name")
        custom_layout.addWidget(name_edit)

        # Save the updated name when editing is finished
        name_edit.editingFinished.connect(lambda: self.update_item_name(list_item, name_edit.text()))

        # Add text display (name and time details)
        text_label = QLabel(item_text)
        text_label.setObjectName("text_label")  # Assign a unique object name
        text_label.setStyleSheet("font-size: 12px;")  # Adjust font size for readability
        custom_layout.addWidget(text_label)

        # Wrap everything in a frame for visual separation
        frame = QFrame()
        frame.setLayout(custom_layout)
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid gray;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QLabel {
                padding: 5px;
            }
            QPushButton {
                background-color: lightgray;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: gray;
                color: white;
            }
            QCheckBox {
                margin-left: 5px;
            }
        """)

        # Set a dynamic minimum height for proper spacing
        frame_height = max(100, name_edit.sizeHint().height() + button_layout.sizeHint().height() + 30)
        frame.setMinimumHeight(frame_height)
        list_item.setSizeHint(frame.sizeHint())
        self.update_item_name(list_item, name_edit.text())

        return list_item, frame

    def update_item_name(self, list_item, new_name):
        """
        Updates the name of a list item when edited.
        """
        ksp_date = list_item.data(Qt.UserRole)  # Get associated KSPDate object
        if ksp_date:
            # Update the name in the KSPDate object
            visitor = KSPDateNameVisitor(new_name)
            ksp_date.accept_visitor(visitor)

    def remove_item(self, list_item):
        """
        Removes a time entry from the list widget.
        """
        row = self.time_list_widget.row(list_item)
        self.time_list_widget.takeItem(row)

    def sort_times(self):
        """
        Sorts the times in ascending order based on UT seconds.
        """
        items = []

        # Extract all items and their associated data
        for i in range(self.time_list_widget.count()):
            list_item = self.time_list_widget.item(i)
            ksp_date = list_item.data(Qt.UserRole)  # Retrieve associated KSPDate object
            custom_widget = self.time_list_widget.itemWidget(list_item)  # Retrieve custom widget

            if ksp_date and custom_widget:
                # Extract relevant data from the custom widget
                name_edit = custom_widget.findChild(QLineEdit)
                link_checkbox = custom_widget.findChild(QCheckBox)

                name_text = name_edit.text() if name_edit else "Unnamed"
                link_checked = link_checkbox.isChecked() if link_checkbox else False

                # Store all necessary data for recreation
                items.append((ksp_date.convert_to_seconds().seconds, ksp_date, name_text, link_checked))

        # Sort items by UT seconds (ascending order)
        items.sort(key=lambda x: x[0])

        # Clear the list widget
        self.time_list_widget.clear()

        # Recreate and re-add sorted items
        for _, ksp_date, name_text, link_checked in items:
            # Recreate the custom widget
            new_list_item, new_frame = self.create_list_item(name_text, ksp_date, link_checked=link_checked)

            # Add the frame to the QListWidget and set its size hint
            self.time_list_widget.addItem(new_list_item)
            self.time_list_widget.setItemWidget(new_list_item, new_frame)

    def create_alarm(self, ksp_date, link_to_vessel):
        """
        Creates an in-game alarm for a specific KSPDate object.
        """
        success = self.ksp_connection_manager.create_alarm(ksp_date, link_to_vessel)

        if success:
            QMessageBox.information(self, "Alarm Created", "Alarm successfully created!")
        else:
            QMessageBox.warning(self, "Error", "Failed to create alarm.")

    def create_alarms_for_all(self):
        """
        Creates alarms for all times in the list widget.
        """
        link_to_vessel = self.global_link_checkbox.isChecked()
        success_count = 0
        failure_count = 0

        for i in range(self.time_list_widget.count()):
            # Get the QListWidgetItem and its associated KSPDate object
            list_item = self.time_list_widget.item(i)
            ksp_date = list_item.data(Qt.UserRole)  # Retrieve the KSPDate object

            try:
                # Create an alarm for this date
                if self.ksp_connection_manager.create_alarm(ksp_date, link_to_vessel):
                    success_count += 1
                else:
                    failure_count += 1

            except Exception as e:
                print(f"Failed to create alarm for item {i}: {e}")
                failure_count += 1

        # Show a summary message box with the results
        QMessageBox.information(
            self,
            "Alarms Created",
            f"Successfully created {success_count} alarms.\nFailed to create {failure_count} alarms."
        )

    def toggle_all_links(self, state, disable=False):
        """
        Toggles all individual "Link to Vessel" checkboxes based on the global checkbox state.
        """
        for i in range(self.time_list_widget.count()):
            list_item = self.time_list_widget.item(i)
            custom_widget = self.time_list_widget.itemWidget(list_item)
            if custom_widget:
                link_checkbox = custom_widget.findChild(QCheckBox)
                if link_checkbox:
                    link_checkbox.setChecked(state == Qt.Checked)
                    if disable:
                        link_checkbox.setEnabled(False)

    def export_dates(self):
        QMessageBox.information(self, "Export", "Export functionality not yet implemented.")

    def import_dates(self):
        QMessageBox.information(self, "Import", "Import functionality not yet implemented.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KSPTimeTool()
    window.show()
    sys.exit(app.exec_())
