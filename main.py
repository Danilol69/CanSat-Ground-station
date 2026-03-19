from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import math
import sys
import datetime

# Note: Ensure these local files exist in your directory
from communication import Communication
from dataBase import data_base 

# --- GLOBAL VARIABLES (Must be defined before functions) ---
ptr1 = 0        # Pointer for Altitude
ptr6 = 0        # Pointer for Velocity
ptr_common = 0  # Pointer for Temp/Pressure
initialized = False
vzo, vx, vy, vz, vel = 0.0, 0.0, 0.0, 0.0, 0.0

# Global Configuration
pg.setConfigOption('background', (33, 33, 33))
pg.setConfigOption('foreground', (197, 198, 199))

# 1. Interface Initialization
app = QtWidgets.QApplication(sys.argv) 
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()
view.setCentralItem(Layout)
view.show()
view.setWindowTitle('Flight Monitoring')
view.resize(1200, 700)

ser = Communication()
db = data_base() 

# 2. UI Header & Layout
Layout.addLabel("Phoenix A Mission Control", col=0, colspan=10, size='20pt', bold=True)

time_proxy = QtWidgets.QGraphicsProxyWidget()
time_label = QtWidgets.QLabel('Initializing...')
time_label.setStyleSheet("color: white; font-size: 18px; qproperty-alignment: AlignRight;")
time_proxy.setWidget(time_label)
Layout.addItem(time_proxy, col=10, colspan=11) 

Layout.nextRow()

# Buttons Setup
style = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;font-weight:bold;"
lb = Layout.addLayout(colspan=21)

def setup_button(text, callback):
    proxy = QtWidgets.QGraphicsProxyWidget()
    btn = QtWidgets.QPushButton(text)
    btn.setStyleSheet(style)
    btn.clicked.connect(callback)
    proxy.setWidget(btn)
    return proxy

lb.addItem(setup_button('Start Storage', db.start))
lb.nextCol()
lb.addItem(setup_button('Stop Storage', db.stop))

Layout.nextRow()

# 3. Graphs Setup
l1 = Layout.addLayout(colspan=20, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))
l1.nextRow()
l12 = l1.addLayout(rowspan=1, border=(83, 83, 83)) 

# --- Row 1 ---
p1 = l11.addPlot(title="Altitude (m)")
altitude_plot = p1.plot(pen=(29, 185, 84))
altitude_data = np.zeros(30)

p2 = l11.addPlot(title="Speed (m/s)")
vel_plot = p2.plot(pen=(29, 185, 84))
vel_data = np.zeros(30)

# --- Row 2 ---
p3 = l12.addPlot(title="Pressure (hPa)")
pressure_plot = p3.plot(pen=(33, 150, 243))
pressure_data = np.zeros(30)

p4 = l12.addPlot(title="Temperature (°C)")
temp_plot = p4.plot(pen=(255, 87, 34))
temp_data = np.zeros(30)

# --- Row 3 (RSSI Graph spanning full width) ---
l1.nextRow() # Move to the bottom
# Because it's the only plot in this row, pyqtgraph will automatically make it fill both columns!
p5 = l1.addPlot(title="RSSI - Signal Strength (dBm)") 
rssi_plot = p5.plot(pen=(255, 193, 7)) # Yellow/Gold color for the radio wave
rssi_data = np.zeros(30)

# --- Helper Functions ---
def update():
    global ptr_common, ptr1, ptr6
    now = datetime.datetime.now()
    time_label.setText(now.strftime("%d/%m/%Y %H:%M:%S"))
    
    try:
        value_chain = ser.getData()
            
        # IMPORTANT: We now expect 7 values! (Index 0 through 6)
        if value_chain and len(value_chain) >= 7:
            
            # 1. Altitude (Index 4)
            altitude_data[:-1] = altitude_data[1:]
            altitude_data[-1] = float(value_chain[4])
            ptr1 += 1
            altitude_plot.setData(altitude_data)
            altitude_plot.setPos(ptr1, 0)
            
            # 2. Speed (Index 5)
            vel_data[:-1] = vel_data[1:]
            vel_data[-1] = float(value_chain[5])
            ptr6 += 1
            vel_plot.setData(vel_data)
            vel_plot.setPos(ptr6, 0)
            
            # 3. Temp (Index 1)
            temp_data[:-1] = temp_data[1:]
            temp_data[-1] = float(value_chain[1])
            temp_plot.setData(temp_data)
            
            # 4. Pressure (Index 2)
            pressure_data[:-1] = pressure_data[1:]
            pressure_data[-1] = float(value_chain[2])
            pressure_plot.setData(pressure_data)

            # 5. RSSI (Index 6) - The new value!
            rssi_data[:-1] = rssi_data[1:]
            rssi_data[-1] = float(value_chain[6])
            rssi_plot.setData(rssi_data)
            
            # Scroll all graphs
            ptr_common += 1
            temp_plot.setPos(ptr_common, 0)
            pressure_plot.setPos(ptr_common, 0)
            rssi_plot.setPos(ptr_common, 0) # Scroll RSSI too
            
            db.guardar(value_chain)
            
    except Exception as e:
        pass

# 4. Main Loop
if ser.isOpen() or ser.dummyMode():
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(500)
else:
    print("Serial port not detected.")

if __name__ == '__main__':
    if (sys.flags.interactive != 1):
        sys.exit(app.exec_())