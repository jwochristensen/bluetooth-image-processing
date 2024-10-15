

#ble file path structure and finding via UUID: https://ukbaz.github.io/howto/python_gio_1.html

import sys
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from example_advertisement import Advertisement
from example_advertisement import register_ad_cb, register_ad_error_cb
from example_gatt_server import Service, Characteristic
from example_gatt_server import register_app_cb, register_app_error_cb
from dbus_next import introspection
import time

#DEVICE_ADDR =                  '94:E9:79:D1:BB:42'
DEVICE_ADDR =                  '48:B3:07:50:E6:43'
#DEVICE_ADDR =                  'CA:41:2A:D0:FB:5E'


BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =              'org.freedesktop.DBus.Properties'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
GATT_SERVICE_IFACE =           'org.bluez.GattService1'
ADAPTER_IFACE =                'org.bluez.Adapter1'

UART_SERVICE_UUID =            '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
UART_RX_CHARACTERISTIC_UUID =  '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
UART_TX_CHARACTERISTIC_UUID =  '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
LOCAL_NAME =                   'rpi-gatt-server'

#SERVICE_PATH

def find_adapter(bus):
	remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),DBUS_OM_IFACE)
	objects = remote_om.GetManagedObjects()
	for o, props in objects.items():
		print('Found adapter:', o)
		if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
			#print('Select adapter:', o, props)
			return o
		print('Skip adapter:', o)
	return None


#bus = dbus.SessionBus()
#bus = dbus.SystemBus()

#adapter = find_adapter(bus) #or need to print this from server script to get exact address?

#the_object = bus.get_object(BLUEZ_SERVICE_NAME, adapter)

#the_interface = dbus.Interface(the_object,  GATT_MANAGER_IFACE)



class Client():
   def __init__(self):
      bus = dbus.SessionBus()
      adapter = find_adapter(bus)
      prop_object = bus.get_object(DBUS_PROP_IFACE, adapter)
      #service = bus.get_object('com.example.service', "/com/example/service")
      self._getall = prop_object.get_dbus_method('GetAll', DBUS_PROP_IFACE + '.GetAll')
      #self._message = service.get_dbus_method('get_message', 'com.example.service.Message')
      #self._quit = service.get_dbus_method('quit', 'com.example.service.Quit')

   def run(self):
      #print "Mesage from service:", self._message()
      #self._quit()
      self._getall()

def bluez_proxy(obj_path, interface):
   proxy = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, obj_path),
                              interface)
   return proxy

def get_characteristic_path(dev_path, uuid):
   #Lookup DBUs path for characteristic UUID
   obj_mgr = bluez_proxy('/',DBUS_OM_IFACE)
   mng_objs = obj_mgr.GetManagedObjects()
   for path in mng_objs:
         print('path:',path)
         chr_uuid = mng_objs[path].get(GATT_CHRC_IFACE, {}).get('UUID')
         if path.startswith(dev_path) and chr_uuid == uuid.casefold():
            return path

def print_mng_object_properties(path):
   #PATH_BASE = '/'

   remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, path),
                              DBUS_OM_IFACE)
   objects = remote_om.GetManagedObjects()
   for o, props in objects.items():
           print('object:', o)
           print('properties:',props)

def get_managed_objects():
   bus = dbus.SystemBus()
   manager = dbus.Interface(bus.get_object("org.bluez", "/"),DBUS_OM_IFACE)
   return manager.GetManagedObjects()

def find_adapter2():
   objects = get_managed_objects()
   for path, interfaces in objects.items():
      if 'org.bluez.Adapter1' in interfaces:
         return path
   raise Exception("Bluetooth adapter not found")

def find_device(adapter_path, device_address):
   objects = get_managed_objects()
   for path, interfaces in objects.items():
      if 'org.bluez.Device1' in interfaces:
         if interfaces['org.bluez.Device1']['Address'] == device_address:
            return path
   raise Exception("Device not found")

def get_service(device_path, uuid):
   bus = dbus.SystemBus()
   objects = get_managed_objects()
   for path, interfaces in objects.items():
      print('path:',path)
      print('interfaces:',interfaces)
      if path.startswith(device_path) and 'org.bluez.GattService1' in interfaces:
         if interfaces['org.bluez.GattService1']['UUID'] == uuid:
            return path
   raise Exception(f"Service with UUID {uuid} not found")

def call_service_method(service_path, method_name):
   bus = dbus.SystemBus()
   service = dbus.Interface(bus.get_object("org.bluez", service_path),GATT_SERVICE_IFACE)
   method = service.get_dbus_method(method_name)
   method()

def introspect_obj(remote_obj):
   # introspection is automatically supported
   print (remote_obj.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable"))

def get_all_chrc_properties(remote_obj):
   properties_iface = dbus.Interface(remote_obj,DBUS_PROP_IFACE)
   chrc_props = properties_iface.GetAll(GATT_CHRC_IFACE)
   print(chrc_props)
   #for prop in chrc_props.items():
      #print(prop)

def get_all_gatt_service_properties(bus):
   OPATH = '/'
   IFACE = DBUS_OM_IFACE
   remote_object = bus.get_object(BLUEZ_SERVICE_NAME, OPATH)
   iface = dbus.Interface(remote_object, IFACE)
   result = iface.GetManagedObjects()
   return result


if __name__ == "__main__":
   bus = dbus.SystemBus()

   # adapter = find_adapter(bus)

   # remote_object = bus.get_object(BLUEZ_SERVICE_NAME, adapter)

   # introspect_obj(remote_object)

   gatt_service_properties = get_all_gatt_service_properties(bus)
   for key, value in gatt_service_properties.items():
      print('key: ',key)
      print('value: ',value)

   print('how to find specific object path, method interface combos to access specific functions? ' 
      'very diffictult to interpret from server code, very difficult to find relevant object attributes')


   #get_all_chrc_properties(remote_object)

   #Client().run()

   # bus = dbus.SystemBus()
   # adapter = find_adapter(bus)

   # device_path = f"{adapter}/dev_{DEVICE_ADDR.replace(':', '_')}"
   # print('device path:',device_path)

   #find UUID path and access characteristic object methods
   #tx_path = get_characteristic_path(device_path, UART_TX_CHARACTERISTIC_UUID)
   #print(tx_path)
   #tx_char_proxy = bluez_proxy(tx_path,GATT_CHRC_IFACE)

   # Example usage:

   # objects = get_managed_objects()
   # for path, interfaces in objects.items():
   #    print('path:',path)
   #    print('interfaces:',interfaces)

   # adapter_path = find_adapter2()
   # print('adapter path:',adapter_path)
   # device_address = DEVICE_ADDR # Replace with the actual device address
   # device_path = find_device(adapter_path, device_address)
   # print('device path:',device_path)
   # service_uuid = UART_SERVICE_UUID # Replace with your service UUID
   # service_path = get_service(device_path, service_uuid)

   # print('service path:',service_path)

   # Call a specific method on the service, e.g., Start or Stop
   #call_service_method(service_path, "Start")


   # remote_object = bus.get_object(BLUEZ_SERVICE_NAME, adapter)
   # prop_manager = dbus.Interface(remote_object, DBUS_PROP_IFACE)
   # all_props = prop_manager.GetAll(ADAPTER_IFACE)
   # #all_props = prop_manager.GetAll(GATT_MANAGER_IFACE)
   # #all_props = prop_manager.GetAll(GATT_SERVICE_IFACE)

   # print('all properties:',all_props)
   #print (remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable"))

   #PATH_BASE = '/org/bluez/example'

   #### GETS ALL OBJECTS ON ADAPTER
   #PATH_BASE = '/'
   #print_mng_object_properties(PATH_BASE)


   # remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, PATH_BASE),
   #                            DBUS_OM_IFACE)
   # objects = remote_om.GetManagedObjects()
   # for o, props in objects.items():
   #         print('object:', o)
   #         print('properties:',props)


#print(vars(the_interface))


# try:
# 	objects = the_interface.GetManagedObjects()
# except Exception as e:
# 	print(e)

# #print object or some loop to find services, characteristics, and descriptors
# for o in objects.items():
# 	print('Managed Object: ', o)

# char_interface = dbus.Interface(the_object, GATT_CHRC_IFACE)

# try:
# 	props = char_interface.get_properties()
# 	for p in props.items():
# 		print('Property: ', p)

# except Exception as e:
# 	print(e)