import serial
import time

ser = serial.Serial("/dev/ttyTHS1", 115200, timeout=1)
time.sleep(2)

ser.write(b"ACT_EXTEND\n")
time.sleep(4)

ser.write(b"ACT_STOP\n")
time.sleep(6)

ser.write(b"ACT_RETRACT\n")
time.sleep(4)

ser.write(b"ACT_STOP\n")
ser.close()
