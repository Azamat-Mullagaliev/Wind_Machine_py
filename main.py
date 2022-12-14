from operator import truediv
import time
#for window app
from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import QThread, QIODevice

from zwift import Client

app = QtWidgets.QApplication([])
ui = uic.loadUi("design.ui")
ui.setWindowTitle("Wind machine")

#reading logs for zwift
file1 = open('logs.txt', 'r')
username = file1.readline().rstrip()
password = file1.readline().rstrip()
player_id = file1.readline().rstrip()

client = Client(username, password)
world = client.get_world(1) # get world with id 1
connected = True

file2 = open('settings.txt', 'r')
minHR = int(file2.readline().rstrip()) #100
maxHR = int(file2.readline().rstrip()) #180
minRPM = int(file2.readline().rstrip()) #900
maxRPM = int(file2.readline().rstrip()) #2300

ui.engineSlider.setMinimum(minRPM)
ui.engineSlider.setMaximum(maxRPM)

ui.engineRPMValueLabel.setText(str(ui.engineSlider.value()))
ui.servoPitchValueLabel.setText(str(ui.servoPitchSlider.value()))

def serialSend(data):
    txt = ""
    for val in data:
        txt += str(val)
    serial.write(txt.encode())
    #print(txt)

class zwiftData(QThread):
 
    def __init__(self, parent=None):
        super().__init__()
        self.heartrate = 60
        self.value = 900

    def run(self):
        while True:

            if ui.zwiftModeCheckBox.isChecked()==True:
                try:
                    if not(connected):
                        connected = True
                        ui.zwiftModeCheckBox.setText("Zwift Mode")
                    self.heartrate = world.player_status(player_id).heartrate
                    val = int(self.heartrate)
                    if val < minHR:
                        val = minHR
                    if val > maxHR:
                        val = maxHR
                    val = minRPM + round((val-minHR)/(maxHR-minHR)*(maxRPM-minRPM))
                    self.value = val
                    #serialSend(['e',val]) 
                    ui.engineSlider.setValue(val)
                    ui.engineRPMValueLabel.setText(str(val))
                    ui.heartRateValueLabel.setText(str(self.heartrate))
                except:
                    connected = False
                    ui.zwiftModeCheckBox.setText("Reconnecting")
            time.sleep(3)

zData = zwiftData()
zData.start()

class swingMode(QThread):
    def __init__(self, parent=None):
        super().__init__()
        self.position = ui.servoPitchSlider.value()
        self.isdirectedup = True

    def run(self):
        while True:
            if ui.swingCheckBox.isChecked():
                val = ui.servoPitchSlider.value()

                if val > 30 and val < 60:
                    maxswing = val + 10
                    minswing = val - 10
                elif val < 31:
                    maxswing = 40
                    minswing = 20
                else:
                    maxswing = 70
                    minswing = 50

                if self.position >= maxswing:
                    self.isdirectedup = False
                if self.position <= minswing:
                    self.isdirectedup = True
                if self.isdirectedup:
                    self.position += 1
                else:
                    self.position -= 1
                ui.swingSlider.setValue(self.position)
                #ui.servoPitchSlider.setValue(self.position)
                #ui.servoPitchValueLabel.setText(str(self.position))
                #serialSend(['p',self.position])
                time.sleep(0.15)

sMode = swingMode()
sMode.start()


def swingChange():
    val = ui.swingSlider.value()
    serialSend(['p',val])

def pitchChange():
    val = ui.servoPitchSlider.value()
    ui.servoPitchValueLabel.setText(str(val))
    if ui.swingCheckBox.isChecked() == False:
        serialSend(['p',val])

def engineSpeedChange():
    if ui.zwiftModeCheckBox.isChecked()==False:
        val = ui.engineSlider.value()
        serialSend(['e',val])
        ui.engineRPMValueLabel.setText(str(val))
    else:
        #print(zData.value)
        serialSend(['e',zData.value])

def retract():
    ui.retractButton.setStyleSheet("background-color : red")
    serialSend(['c0'])

def engineStart():
    serialSend(['e1'])

#connect our Arduino
serial = QSerialPort()
serial.setBaudRate(115200)
try:
    serial.setPortName('COM4')
finally:
    serial.setPortName('COM3')
serial.open(QIODevice.ReadWrite)

ui.swingSlider.valueChanged.connect(swingChange)
ui.servoPitchSlider.valueChanged.connect(pitchChange)
ui.engineSlider.valueChanged.connect(engineSpeedChange)
ui.retractButton.clicked.connect(retract)
ui.engineStartButton.clicked.connect(engineStart)

ui.show()
app.exec()
