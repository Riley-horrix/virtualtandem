#!/bin/sh

cython --embed -o main.c main.py
gcc -Os -I /usr/include/python3.3m -o a.out main.c -lpython3.3m -lpthread -lm -lutil -ldl