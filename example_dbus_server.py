import sys
import dbus, dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

SERVICE_NAME =        'com.example.service'
OPATH =               '/com/example/SomeObject'
IFACE =               'com.example.SampleInterface'

class DemoException(dbus.DBusException):
    _dbus_error_name = 'com.example.DemoException'

class ExampleObject(dbus.service.Object):
	def __init__(self, bus_name, object_path):
		#bus_name = dbus.service.BusName(SERVICE_NAME, bus)
		dbus.service.Object.__init__(self, bus_name, object_path) #initialize with bus or bus_name?

	@dbus.service.method(IFACE, in_signature='s', out_signature='as')
	def SendMessage(self, msg):
		print (str(msg))
		return ['hello','this is a test','here is your message:',str(msg)]
		#return ["Hello", " from example-service.py", "with unique name",session_bus.get_unique_name()]

    # @dbus.service.method(IFACE, in_signature='', out_signature='')
    # def RaiseException(self):
    #     raise DemoException('The RaiseException method does what you might expect')

    # @dbus.service.method(IFACE, in_signature='', out_signature='')
    # def Exit(self):
    #     mainloop.quit()

def main():
    global mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    #bus = dbus.SystemBus()

    bus_name = dbus.service.BusName(SERVICE_NAME, bus)
    object = ExampleObject(bus_name, OPATH)

    #for client:
    #service_manager = dbus.Interface(bus.get_object(SERVICE_NAME, OPATH),IFACE)
    #result = service_manager.SendMessage('testing')
    #dbus.service.Object.__init__(self, bus_name, "/com/example/service")
    #https://gist.github.com/caspian311/4676061

    mainloop = GLib.MainLoop()

    try:
    	print ("Running example service.")
    	mainloop.run()

    except KeyboardInterrupt:
        mainloop.quit()

if __name__ == '__main__':
    main()