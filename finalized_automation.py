# workflow:

# Jetson Orin Nano
#   ├─ State machine (automation)
#   ├─ Timeouts & safety
#   └─ UART commands
#           ↓
# STM32
#   ├─ Read MPU6050 (gyro)
#   ├─ Angle calculation
#   ├─ Worm gear motor control
#   ├─ Linear actuator control
#   └─ Send DONE / ERROR
