import sys
import dbus, dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
from traceback import print_exc


SERVICE_NAME =        'com.example.service'
OPATH =               '/com/example/SomeObject'
IFACE =               'com.example.SampleInterface'

#SERVICE_NAME =                 'com.example.SampleService'
#DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
#IFACE_NAME =                   'com.example.SampleInterface'
#OBJ_PATH =                     '/SomeObject'



def main():

    bus = dbus.SessionBus()

    try:
        remote_object = bus.get_object(SERVICE_NAME, OPATH)
        iface = dbus.Interface(remote_object, IFACE)
        result = iface.SendMessage('test message send')
        print(result)

    except dbus.DBusException as e:
        print(str(e))
        sys.exit(1)


    # introspection is automatically supported
    #print (remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable"))

if __name__ == '__main__':
    main()