#!/usr/bin/env python3
libname = "xinput2wrapper.so.1"

import os
import ctypes
import decimal

# From X11/extensions/XI2.h
XIMasterPointer                         =1
XIMasterKeyboard                        =2
XISlavePointer                          =3
XISlaveKeyboard                         =4
XIFloatingSlave                         =5

# not sure in the future they will be consecutive, so rather a dict than an array
usestrings = {1: "XIMasterPointer", 2: "XIMasterKeyboard", 3: "XISlavePointer", 4: "XISlaveKeyboard", 5: "XIFloatingSlave"}

#typedef struct
#{
#    int         type;
#    int         sourceid;
#} XIAnyClassInfo;
class XIAnyClassInfo_struct(ctypes.Structure):
        _fields_ = [
                ("type", ctypes.c_int),
                ("sourceid", ctypes.c_int)
        ]

#typedef struct
#{
#    int                 deviceid;
#    char                *name;
#    int                 use;
#    int                 attachment;
#    Bool                enabled;
#    int                 num_classes;
#    XIAnyClassInfo      **classes;
#} XIDeviceInfo;
class XIDeviceInfo_struct(ctypes.Structure):
    _fields_ = [
            ("deviceid", ctypes.c_int),
            ("name", ctypes.c_char_p),
            ("use", ctypes.c_int),
            ("attachment", ctypes.c_int),
            ("enabled", ctypes.c_int),
            ("classes", ctypes.POINTER(XIAnyClassInfo_struct))
            ]

lib = ctypes.cdll.LoadLibrary(libname)
lib.e_version.restype = ctypes.c_char_p
xinput_version = lib.e_version().decode("utf8")
lib.e_numdevices.restype = ctypes.c_int
lib.e_list.restype = XIDeviceInfo_struct

if decimal.Decimal(xinput_version) >= decimal.Decimal(2):
    print ("XInput version good:", str(xinput_version))
else:
    exit(1)

def XIDeviceInfoList():
  numdevices = lib.e_numdevices()
  l = dict()
  for i in range(numdevices):
    info = lib.e_list(ctypes.c_int(i))
    l[info.deviceid] = {
    'deviceid': info.deviceid,
    'name': info.name.decode("utf8"),
    'use' : info.use,
    'attachment' : info.attachment,
    'enabled' : bool(info.enabled),
    'type' : info.classes.contents.type,
    'sourceid' : info.classes.contents.sourceid
    }
  return l

if __name__ == "__main__":
  numdevices = lib.e_numdevices()
  for i in range(numdevices):
      info = lib.e_list(ctypes.c_int(i))
      print ("Device id: " + str(info.deviceid))
      print ("Device name: " + str(info.name.decode("utf8")))
      print ("Device use: " + str(info.use) + " -> " + usestrings[info.use])
      print ("Device attachment: " + str(info.attachment))
      print ("Device enabled: " + str(bool(info.enabled)))
      print ("Device type: " + str(info.classes.contents.type))
      print ("Device sourceid: " + str(info.classes.contents.sourceid))
      print ("----")