import time
#for window app
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QWidget
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

minHR = 80
maxHR = 180
minRPM = 900
maxRPM = 1300

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
                    ui.zwiftModeCheckBox.setChecked(False)
            time.sleep(3)

zData = zwiftData()
zData.start()

def pitchChange():
    val = ui.servoPitchSlider.value()
    serialSend(['p',val])
    ui.servoPitchValueLabel.setText(str(val))

def engineSpeedChange():
    if ui.zwiftModeCheckBox.isChecked()==False:
        val = ui.engineSlider.value()
        serialSend(['e',val])
        ui.engineRPMValueLabel.setText(str(val))
    else:
        print(zData.value)
        serialSend(['e',zData.value])

def retract():
    ui.retractButton.setStyleSheet("background-color : red")
    serialSend(['c0'])

def engineStart():
    serialSend(['e1'])

#connect our Arduino
serial = QSerialPort()
serial.setBaudRate(115200)
serial.setPortName('COM4')
serial.open(QIODevice.ReadWrite)

ui.servoPitchSlider.valueChanged.connect(pitchChange)
ui.engineSlider.valueChanged.connect(engineSpeedChange)
ui.retractButton.clicked.connect(retract)
ui.engineStartButton.clicked.connect(engineStart)

ui.show()
app.exec()
