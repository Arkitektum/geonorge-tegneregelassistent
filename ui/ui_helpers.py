from qgis.core import Qgis, QgsMessageLog
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QTimer


class UIHelpers:

    def __init__(self, iface):
        self.iface = iface

    def message_bar_critial(self, message):
        self.iface.messageBar().pushMessage(
                "Error", message, level=Qgis.Critical)
        return

    def message_bar_info(self, message):
        self.iface.messageBar().pushMessage(
                message, level=Qgis.Info)
        return

    def message_bar_warning(self, message):
        self.iface.messageBar().pushMessage(
                message, level=Qgis.Warning)
        return

    def message_bar_success(self, message):
        self.iface.messageBar().pushMessage(
                message, level=Qgis.Success)
        return

    def log_message_info(self, message):
        QgsMessageLog.logMessage(message, level=Qgis.Info)
        return

    def log_message_warning(self, message):
        QgsMessageLog.logMessage(message, level=Qgis.Warning)
        return

    def log_message_critical(self, message):
        QgsMessageLog.logMessage(message, level=Qgis.Critical)
        return

    def show_progress_bar(self, total_steps, message):
        self.iface.messageBar().clearWidgets()
        progress_message_bar = self.iface.messageBar().createMessage(
            message)
        progress_bar = QProgressBar()
        progress_bar.setMaximum(total_steps)
        progress_message_bar.layout().addWidget(progress_bar)
        self.iface.messageBar().pushWidget(progress_message_bar)
        return progress_message_bar, progress_bar

    def close_progress_bar(self, progress_message_bar, delay=None):
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(progress_message_bar.close)
        if delay:
            timer.start(delay)
        self.iface.messageBar().clearWidgets()
        return
