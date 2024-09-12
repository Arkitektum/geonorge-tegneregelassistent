from PyQt5 import QtCore, QtNetwork
from .logging_setup import logger as log


class ApiCallManager(QtCore.QObject):

    response_data = QtCore.pyqtSignal(str)

    def __init__(self):
        super(ApiCallManager, self).__init__()
        self.manager = QtNetwork.QNetworkAccessManager()
        self.loop = QtCore.QEventLoop()

    def get(self, url, params=None):
        qurl = QtCore.QUrl(url)

        if params:
            query = QtCore.QUrlQuery()
            for key, value in params.items():
                query.addQueryItem(key, str(value))
            qurl.setQuery(query)

        request = QtNetwork.QNetworkRequest(qurl)

        self.reply = self.manager.get(request)
        self.reply.finished.connect(self.handle_response)
        self.loop.exec_()

    def handle_response(self):

        if self.reply.error() == QtNetwork.QNetworkReply.NoError:
            self.response_data = self.reply.readAll()
        else:
            log.error(
                "API error response occurred: ", self.reply.errorString())
            self.response_data = None
        self.loop.quit()

    def get_response_data(self):
        return self.response_data
