from server import Application
import socket
import win32serviceutil
import servicemanager
import win32event
import win32service


class WinService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'Service'
    _svc_display_name_ = 'Service Display'
    _svc_description_ = 'Service Description'

    @classmethod
    def parse_command_line(cls):
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        pass

    def stop(self):
        pass

    def main(self):
        pass


if __name__ == '__main__':
    WinService.parse_command_line()


class Service(WinService):
    _svc_name_ = 'CiaShopServer'
    _svc_display_name_ = 'CiaShop Consumer Api'
    _svc_description_ = 'Service to communicate with the API provided by the CiaShop platform to integrate ERP.'

    def start(self):
        self.isrunning = True

    def stop(self):
        self.isrunning = False

    def main(self):
        application = Application()
        while self.isrunning:
            application.synchronize()


if __name__ == '__main__':
    Service.parse_command_line()