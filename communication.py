import random
import serial
import serial.tools.list_ports


class Communication:
    baudrate = ''
    portName = ''
    dummyPlug = False
    ports = serial.tools.list_ports.comports()
    ser = serial.Serial()

    def __init__(self):
        self.baudrate = 115200
        print("the available ports are (if none appear, press any letter): ")
        for port in sorted(self.ports):
            # obtener la lista de puetos: https://stackoverflow.com/a/52809180
            print(("{}".format(port)))
        self.portName = input("write serial port name (ex: /dev/ttyUSB0): ")
        try:
            self.ser = serial.Serial(self.portName, self.baudrate)
        except serial.serialutil.SerialException:
            print("Can't open : ", self.portName)
            self.dummyPlug = True
            print("Dummy mode activated")

    def close(self):
        if(self.ser.isOpen()):
            self.ser.close()
        else:
            print(self.portName, " it's already closed")

    def getData(self):
        if self.dummyPlug == False: # Check the variable directly
            try:
                # 1. Read the line from the USB cable
                value = self.ser.readline() 
                
                # 2. Decode and clean (remove \r\n characters)
                decoded_bytes = value.decode("utf-8").strip()
                
                # 3. Split the string by commas
                value_chain = decoded_bytes.split(",")
                
                # Validation: If it's empty or garbled, don't return it
                if len(value_chain) < 6:
                    return None
                    
                return value_chain
            except Exception as e:
                print(f"Serial Error: {e}")
                return None
        else:
            # fake data when pico (receiver) is not connected
            # time, temp, press, hum, alt, speed, rssi
            return [0, 25.0, 1013.25, 40.0, 100.0, -2.5, -45.0]

    def isOpen(self):
        return self.ser.isOpen()

    def dummyMode(self):
        return self.dummyPlug
