#!/bin/sh

rm xinput2wrapper.o xinput2wrapper.so.1 &> /dev/null || true
gcc -Wall -fPIC -c xinput2wrapper.c
gcc -shared -Wl,-soname,xinput2wrapper.so.1,--export-dynamic -o xinput2wrapper.so.1 xinput2wrapper.o -lX11 -lXext -lXi -lXrandr -lXinerama
rm xinput2wrapper.o
pyuic4 mpxgui.ui -o mpxgui_ui.py