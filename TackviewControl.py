import socket
import re
import math
import sys

RE_TIME = "#([0-9\.]+)"
RE_T3   = "T=([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)$"
RE_T5   = "T=([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)$"
RE_T6   = "T=([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)$"
RE_T9   = "T=([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)\|([\-0-9\.]*)$"
RE_IAS  = "IAS=([\-0-9\.]+)"
RE_AOA  = "AOA=([\-0-9\.]*)"

USERNAME = "user1"

class TacviewIntercept():
  ROLL_GAIN = 1/10.0
  PITCH_PGAIN = -1/150.0
  PITCH_IGAIN = 1/60.0
  PITCH_DGAIN = 2.0
  ALT_PGAIN = 1/10
  
  def __init__(self,degAoaCommand,altCommand,pitchGain=1,rollGain=1):
    self.degRollCommand = 70
    self.feetAltCommand = altCommand
    self.aoaCommand = degAoaCommand
    self.pitchGain = pitchGain
    self.rollGain =rollGain
    
    self.time= 0.0
    self.lat = 0.0
    self.lon = 0.0
    self.alt = 0.0
    self.u   = 0.0
    self.v   = 0.0
    self.roll= 0.0
    self.pitch=0.0
    self.yaw  =0.0
    self.heading = 0.0
    self.ias  =0.0
    self.aoa  =0.0
    
    self.vvPitchSum = 0.0
    self.vvPitchPrev = None
    
    self.aoaSum = 0.0
    self.aoaPrev = None
    
    self.vvDiffSum = 0.0
    
    self.t0 = 0.0
    self.yawT0 = 0.0
    self.turnRate = 0.0

  def updateFlightStatus(self,str):
    lines = str.split('\n')
    for line in lines:
      elements = line.split(',')
      
      for element in elements:
        match = re.match(RE_TIME,element)
        if(match):
          self.time = float(match.group(1))
          
        match = re.match(RE_T3,element)
        if(match):
          if(match.group(1) != ""):
            self.lon = float(match.group(1))
          if(match.group(2) != ""):
            self.lat = float(match.group(2))
          if(match.group(3) != ""):
            self.alt = float(match.group(3))
          
        match = re.match(RE_T5,element)
        if(match):
          if(match.group(1) != ""):
            self.lon = float(match.group(1))
          if(match.group(2) != ""):
            self.lat = float(match.group(2))
          if(match.group(3) != ""):
            self.alt = float(match.group(3))
          if(match.group(4) != ""):
            self.u = float(match.group(4))
          if(match.group(5) != ""):
            self.v = float(match.group(5))
          
        match = re.match(RE_T6,element)
        if(match):
          if(match.group(1) != ""):
            self.lon = float(match.group(1))
          if(match.group(2) != ""):
            self.lat = float(match.group(2))
          if(match.group(3) != ""):
            self.alt = float(match.group(3))
          if(match.group(4) != ""):
            self.roll = float(match.group(4))
          if(match.group(5) != ""):
            self.pitch = float(match.group(5))
          if(match.group(6) != ""):
            self.yaw = float(match.group(6))
          
        match = re.match(RE_T9,element)
        if(match):
          if(match.group(1) != ""):
            self.lon = float(match.group(1))
          if(match.group(2) != ""):
            self.lat = float(match.group(2))
          if(match.group(3) != ""):
            self.alt = float(match.group(3))
          if(match.group(4) != ""):
            self.roll = float(match.group(4))
          if(match.group(5) != ""):
            self.pitch = float(match.group(5))
          if(match.group(6) != ""):
            self.yaw = float(match.group(6))
          if(match.group(7) != ""):
            self.u = float(match.group(7))
          if(match.group(8) != ""):
            self.v = float(match.group(8))
          if(match.group(9) != ""):
            self.heading = float(match.group(9))
        
        match = re.match(RE_AOA,element)
        if(match):
          self.aoa = float(match.group(1))
        
        match = re.match(RE_IAS,element)
        if(match):
          self.ias = float(match.group(1))
    
    
  def toControlString(self,pitch,roll,throttle):
    return "Axis.Pitch.Value,{:.5f}\x00Axis.Roll.Value,{:.5f}\x00Axis.Throttle.Value,{:.5f}\x00".format(pitch,roll,throttle)
  
  def calcControlCommand(self):
    altCommand = self.feetAltCommand

    vvPitchCommand = (altCommand - self.alt*3.28084) * 3 /1000
    if(vvPitchCommand < -3):
      vvPitchCommand = -3
    elif(vvPitchCommand > 3):
      vvPitchCommand = 3
    
    vvPitch = self.pitch - math.cos(self.roll*math.pi/180) * self.aoa
    
    vvPitchP = vvPitchCommand - vvPitch
    if(vvPitchP < -3):
      vvPitchP = -3
    elif(vvPitchP > 3):
      vvPitchP = 3
    
    if(self.vvPitchPrev is None):
      self.vvPitchPrev = vvPitch
    
    
    self.degRollCommand += -vvPitchP * 0.04*self.rollGain + (vvPitch-self.vvPitchPrev) * 4 * self.rollGain
    if(self.degRollCommand > 88):
      self.degRollCommand = 88
    elif(self.degRollCommand < 10):
      self.degRollCommand = 10
    
    self.vvPitchPrev = vvPitch
    
    
    roll = (self.degRollCommand - self.roll) * self.ROLL_GAIN*0.6

    aoaCommand = self.aoaCommand
    
    
    if(self.aoaPrev is None):
      self.aoaPrev = self.aoa
    
    
    self.aoaSum += (aoaCommand - self.aoa)*0.04*self.pitchGain - (self.aoa-self.aoaPrev) * 0
    
    if(self.aoaSum > 100):
      self.aoaSum = 100
    elif(self.aoaSum < -50):
      self.aoaSum = -50
    
    self.aoaPrev = self.aoa
    
    
    pitch = ((aoaCommand - self.aoa) * self.PITCH_PGAIN + self.aoaSum * self.PITCH_IGAIN)*1.0
    
    print("aos sum: {:.3f}, roll command: {:.3f}, vv pitch command {:.3f}, vvPitchP {:.3f}".format(self.aoaSum,self.degRollCommand,vvPitchCommand,vvPitchP))
    
    
    if(roll > 0.5):
      roll = 0.5
    elif(roll < -0.5):
      roll = -0.5
    if(pitch > 1.0):
      pitch = 1.0
    elif(pitch < -1.0):
      pitch = -1.0
    throttle = 1.0
    
    
    return self.toControlString(pitch,roll,throttle)
    
  
  
  def receive(self):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as monitor:
      monitor.connect(("127.0.0.1",42672))
      
      
      data = monitor.recv(1024)
      print(repr(data))
      monitor.sendall(("XtraLib.Stream.0\nTacview.RealTimeTelemetry.0\n" + USERNAME + "\n0\x00").encode("utf-8"))
      
      
      with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as control:
        control.connect(("127.0.0.1",42675))
        data = control.recv(1024)
        print(repr(data))
        control.sendall(("XtraLib.Text.0\nTacview.RemoteControl.0\n" + USERNAME + "\n\x00").encode("utf-8"))
      
        while(True):
          data = monitor.recv(1024)
          #print(repr(data))
          self.updateFlightStatus(data.decode('utf-8'))
          
          #print(data)
          print("time:",self.time,", lat:",self.lat,", lon:",self.lon,", alt:",self.alt,"roll:",self.roll,", pitch:",self.pitch,", yaw:",self.yaw,", u:",self.u,", v:",self.v,", heading:",self.heading, ", ias",self.ias*1.94384,", aoa",self.aoa)
          
          control.sendall(self.calcControlCommand().encode('utf-8'))
          
          if(self.time - self.t0 > 10):
            yawDiff = self.yaw - self.yawT0
            if(yawDiff > 180):
              yawDiff -= 360
            elif(yawDiff < -180):
              yawDiff += 360
              
            self.turnRate = (yawDiff)/(self.time - self.t0)
            self.t0 = self.time
            self.yawT0 = self.yaw
          print("turn rate: ",self.turnRate, "[deg/s]")



if __name__ == "__main__":
  args = sys.argv
  if(len(args) < 3):
    print("usage: Python3 TackviewControl.py degAoaCommand feetAltitudeCommand [pitchGain] [rollGain]")
    sys.exit(1)
  
  degAoaCommand = float(args[1])
  feetAltitudeCommand = float(args[2])
  
  pitchGain = 1
  if(len(args)>3):
    pitchGain = float(args[3])
  
  rollGain = 1
  if(len(args)>4):
    rollGain = float(args[4])
  
  print("aoa command",degAoaCommand)
  print("alt command",feetAltitudeCommand)
  print(pitchGain)
  print(rollGain)
  
  inst = TacviewIntercept(degAoaCommand,feetAltitudeCommand,pitchGain,rollGain)
  inst.receive()









