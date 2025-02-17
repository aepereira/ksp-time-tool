from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QLineEdit


class UTSecondsEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set an integer validator with the desired range
        self.validator = UTSecondsValidator(0, 254001916799, self)
        self.setValidator(self.validator)

    def value(self):
        """
        Returns the current value as an integer.
        """
        text = self.text()
        return int(text) if text.isdigit() else 0


class UTSecondsValidator(QValidator):
    def __init__(self, min_value=0, max_value=254001916799, parent=None):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, input_str, pos):
        """
        Validates the input string.

        Parameters:
            input_str (str): The current input string.
            pos (int): The current cursor position.

        Returns:
            QValidator.State: Acceptable, Intermediate, or Invalid.
        """
        if not input_str:  # Empty input is considered intermediate
            return QValidator.Intermediate, input_str, pos

        if input_str.isdigit():
            value = int(input_str)
            if self.min_value <= value <= self.max_value:
                return QValidator.Acceptable, input_str, pos
            else:
                return QValidator.Invalid, input_str, pos
        else:
            return QValidator.Invalid, input_str, pos
