#!/usr/bin/env python3

# PiawareLEDd.py - Daemon 
#   - Connect to dump1090-fa port (127.0.0.1:30003)
#   - Blink LED when packet received
#      * RED - No data
#      * GREEN - Some data
#   - Separate thread for LDR  - modify LED brightness - DAY/NIGHT mode
#
# (C) 2019 Petr KLOSKO
#  https://www.klosko.net/


import os
import sys
import syslog
import socket
import threading
from signal import pause
from gpiozero import LightSensor, RGBLED

DAEMON    = False

def l(message):
  global DAEMON
  if DAEMON:
    syslog.syslog(message)
  else:
    sys.stderr.write(message + "\n")


def day_time():
  global R
  global G
  global B
  R = (1, 0, 0)
  G = (0, 1, 0)
  B = (0, 0, 1)
  l('LDR status:DAY')
  l('Colors R=%s G=%s B=%s' % (str(R), str(G), str(B)))

def night_time():
  global R
  global G
  global B
  R = (0.01, 0, 0)
  G = (0, 0.01, 0)
  B = (0, 0, 0.01)
  l('LDR status:NIGHT')
  l('Colors R=%s G=%s B=%s' % (str(R), str(G), str(B)))

def connect(server_address, ldr):
  global sock
  light = ldr.value
  isLight = ldr.light_detected

  l('Connecting to %s port %s' % server_address)
  l('LDR value %s' % light)
  l('LDR state %s' % isLight)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect(server_address)

def close():
  l('Close connection')
  global sock
  sock.close()
  del sock

def thread_function(name, ldr):
  ldr.when_dark = night_time
  ldr.when_light = day_time
  pause()


def run():
  global R
  global G
  global B
  led = RGBLED(4, 17, 27)
  ldr = LightSensor(22, 50)

  R = (1,0,0)
  G = (0,1,0)
  B = (0,0,1)
  N = (0,0,0)
  Y = (1,1,0)
#  W = (1,1,1)
#  M = (1,0,1)

  night_time
  on_time  = 0.01
  on_time_noacft = 0.20

  server_address = ('localhost', 30003)
  BUFF_LEN = 256
  connCnt = 0

  x = threading.Thread(target=thread_function, args=(1,ldr))
  x.start()

# INIT LED - Blink BLUE while not connected & data
  led.blink(0.25,0.25,0,0,B,N)

  connect(server_address, ldr)
  try:
     while (1):
        data = sock.recv(BUFF_LEN)
        if (len(data) > 10):
          led.blink(on_time,0,0,0,G,N,1)
        else:
          led.blink(on_time,0,0,0,R,N,1)

        if not data:
          led.color = R
          connCnt = connCnt + 1
          if (connCnt > 10):
            l('Error. Try to reconnect .... ')
            close()
# No blink thread = block script for 20sec = time to SDR recovery
            led.blink(1,1,0,0,Y,N,10,False)
            led.blink(0.25,0.25,0,0,B,N)
            connect(server_address, ldr)
        else:
          connCnt = 0

  finally:
    led.color = N
    close()


def create_daemon():
  try:
    pid = os.fork()
    l('PiawareLEDd.py Start: %s' % str(pid))
    if pid > 0:
      sys.exit(0)

  except OSError as e:
    l('PiawareLEDd.py Unable to fork. Error: %s' % str(e))
    sys.exit(1)

  run()


def main():
  global DAEMON
  DAEMON = True
  create_daemon()

if __name__ == '__main__':
        main()

