__author__ = 'jimmy'

import threading
from MessageHandler import *
import traceback


class Dispatcher(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.handlers = {}
        self.register(0, PINGHandler())
        self.register(1, PONGHandler())
        self.register(3, ScanMessageHandler())
        self.register(4, MachineInfoHandler())
        self.register(5, QueryMachinesHandler())
        self.register(7, UploadRequestHandler())
        self.register(8, UploadResponseHandler())
        self.register(9, RunTestHandler())
        self.register(10, TestSuccessHandler())
        self.register(11, UploadOutputResponseHandler())
        self.register(12, DeleteOutputHandler())
        self.register(13, QueryResultsHandler())
        self.register(15, RegisterMachinesListenerHandler())
        self.register(16, QueryOverviewsHandler())
        self.register(17, QueryAnalysisHandler())
        self.register(18, RunServiceHandler())
        self.register(19, QueryServiceResultsHandler())
        self.register(20, AnalysisServiceHandler())
        self.register(22, QueryAResultOverviewHandler())
        self.register(23, QueryModelsResultsHandler())

    def register(self, handleID, handler=MessageHandler()):
        self.handlers[handleID] = handler

    def run(self):
        while True:
            try:
                connection, message = self.queue.get()
                handler = self.handlers[message.type]
                handler.handle(connection, message)
            except:
                traceback.print_exc()
