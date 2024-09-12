from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
from os.path import join, dirname

FORM_CLASS, _ = uic.loadUiType(join(
    dirname(__file__), 'tegneregelassistent_dialog_base.ui'))


class tegneregelassistent_dialog_base(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(tegneregelassistent_dialog_base, self).__init__(parent)
        self.setupUi(self)

        # Change the text of the "Cancel" button to "Avbryt"
        if self.button_box:
            cancel_button = self.button_box.button(self.button_box.Cancel)
            if cancel_button:
                cancel_button.setText("Avbryt")
