#include "xinput.h"
#include <string.h>
#include <X11/extensions/XInput2.h>
#define VERSION "1.6.0"

static const char version_id[] = VERSION;

int e_numdevices() {
  Display *display = XOpenDisplay(NULL);
  int ndevices;

  XIQueryDevice(display, XIAllDevices, &ndevices);
  return ndevices;
}

XIDeviceInfo e_list(int i) {
  Display *display;
  display = XOpenDisplay(NULL);
  int ndevices;

  XIDeviceInfo *info = XIQueryDevice(display, XIAllDevices, &ndevices);
  return *(&info[i]);
}

char* e_version() {
  static char r[10]; //should be enough...
  XExtensionVersion   *version;
  Display *display;

  display = XOpenDisplay(NULL);
  //printf("XI version on server: ");
  r[0] = '\0';
  if (display == NULL)
    return("Failed to open display.\n");
  else {
    version = XGetExtensionVersion(display, INAME);
    if (!version || (version == (XExtensionVersion*) NoSuchExtension))
     return("Extension not supported.\n");
    else {
      char major[3];
      snprintf(major,3, "%d", version->major_version);
      char minor[3];
      snprintf(minor, 3, "%d", version->minor_version);
      strncat(r, major, 3);
      strncat(r, ".", 3);
      strncat(r, minor, 3);
      XFree(version);
    }
  }
  return(r);
}
