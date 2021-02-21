#!/bin/bash

g++ -c -fPIC register.cpp -o register.o
g++ -c -fPIC -I /usr/include/python2.7/ manager.cpp -o manager.o
g++ -shared -Wl,-soname,libregister.so -o libregister.so register.o manager.o