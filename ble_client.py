import dbus
from uuids import flask_ble_uuids
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
import time

bus = None
mainloop = None


BLUEZ_SERVICE_NAME = "org.bluez"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
BLUEZ_DEVICE = "org.bluez.Device1"

GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"


class BleClient:
    def __init__(self):
        self.bus = None
        self.mainloop = None
        self.service = None

    def _generic_error_cb_(self, error):
        print("D-Buss call failed: " + str(error))
        self.mainloop.quit()

    def _interface_removed_cb_(self, object_path, interface):
        if not self.service:
            return

        if object_path == self.service.service_path:
            print("Service was removed")
            self.mainloop.quit()

    def _tx_prop_changed_cb_(self, iface, changed_props, invalidated_props):
        if iface != GATT_CHRC_IFACE:
            return

        if not len(changed_props):
            return

        value = changed_props.get('Value', None)
        if value == None:
            return
        
        valueAsBytes  = bytearray(value)
        as_string = valueAsBytes.decode("utf-8")
        print("tx: " + as_string)

    def _tx_chr_start_notify_cb_(self):
        print("TX notification enabled")

    def tx_val_cb(value):
        print("new value")

    def start(self):
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.mainloop = GObject.MainLoop()
        bluez = self.bus.get_object(BLUEZ_SERVICE_NAME, "/")
        adapter_object = self.bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez/hci0")
        adapter = dbus.Interface(adapter_object, "org.bluez.Adapter1")
        adapter_props = dbus.Interface(adapter_object, DBUS_PROP_IFACE)
        print("Start BLE Discovery")
        adapter.StartDiscovery()
        print("Try to find GATT service")
        count = 0
        self.om = dbus.Interface(bluez, DBUS_OM_IFACE)
        self.om.connect_to_signal("InterfacesRemoved", self._interface_removed_cb_)
        found_service = False
        service_uuid = flask_ble_uuids["Service"]
        while (count < 10) and (not found_service):
            objects = self.om.GetManagedObjects()
            chrcs = []

            # Check if device1
            for path, interfaces in objects.items():
                if found_service:
                    break
                
                for interface in interfaces.items():
                    if found_service:
                        break
                    
                    if interface[0] == BLUEZ_DEVICE:
                        device_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, path)
                        device = dbus.Interface(device_obj, BLUEZ_DEVICE)
                        device_prop = dbus.Interface(device, DBUS_PROP_IFACE)
                        device_uuids = [
                            str(value)
                            for value in device_prop.Get(BLUEZ_DEVICE, "UUIDs")
                        ]
                        if service_uuid not in device_uuids:
                            continue

                        device.Connect()
                        for chr_path, info in self.om.GetManagedObjects().items():
                            found_uuid = info.get(GATT_CHRC_IFACE, {}).get("UUID", "")
                            if found_uuid == flask_ble_uuids["TX_chr"]:
                                chr_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, chr_path)
                                chr = dbus.Interface(chr_obj, GATT_CHRC_IFACE)
                                chr_props = chr.GetAll(
                                    GATT_CHRC_IFACE, dbus_interface=DBUS_PROP_IFACE
                                )
                                self.tx_chr = (chr, chr_props)
                                self.tx_prop_iface = dbus.Interface(
                                    chr, DBUS_PROP_IFACE
                                )
                                self.tx_prop_iface.connect_to_signal(
                                    "PropertiesChanged", self._tx_prop_changed_cb_
                                )
                                chr.StartNotify(
                                    reply_handler=self._tx_chr_start_notify_cb_,
                                    error_handler=self._generic_error_cb_,
                                    dbus_interface=GATT_CHRC_IFACE,
                                )
                                found_service = True
                                break

            if not found_service:
                time.sleep(1)
                count += 1
                continue
            
        if not found_service:
            print('Service not found ....')
            return

        print('Service found listening....')
        self.mainloop.run()


def main():
    ble_client = BleClient()
    ble_client.start()


if __name__ == "__main__":
    main()
