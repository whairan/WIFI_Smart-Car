#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
'''
文 件 名：_XiaoRGEEK_SOCKET_.py
功    能：建立SOCKET服务程序，并监听TCP 2001端口，以及BT 1 端口。
          1、接收并解析上述两个端口的数据，根据指令执行不同功能函数。
          2、上传指定格式的数据到对应端口
调用接口：

from _XiaoRGEEK_SOCKET_ import XR_SOCKET
soc = XR_SOCKET()
soc.BT_Socket()	#开启BT SOCKET服务，并循环监听数据
soc.TCP_Socket()#开启TCP SOCKET服务，并循环监听数据
soc.Sendbuf(['\xFF','\x00','\x00','\x00','\xFF'])	#上传数据
'''
import time
from socket import *
import _XiaoRGEEK_GLOBAL_variable_ as G_val
from _XiaoRGEEK_MOTOR_ import Robot_Direction
go = Robot_Direction()
import binascii
import threading
from _XiaoRGEEK_SERVO_ import XR_Servo
Servo = XR_Servo()
from _XiaoRGEEK_LED_ import Robot_Led
XRLED = Robot_Led()

import bluetooth
from subprocess import call
import _XiaoRGEEK_GPIO_ as XR
import os

#BT_Server
BT_Server=None
BT_Server=bluetooth.BluetoothSocket(bluetooth.RFCOMM);
BT_Server.bind(('',1))
BT_Server.listen(1);
BT_buffer=[]
#tcp_server
TCP_Server=socket(AF_INET,SOCK_STREAM)
TCP_Server.bind(('',2001))
TCP_Server.listen(1)
TCP_buffer=[]
#for all socket


####################################################
##函数功能 ：舵机控制函数,设置角度保护，防止转到死区
##入口参数 ：ServoNum(舵机号)，angle_from_protocol(舵机角度)
##出口参数 ：无
####################################################
def _Angle_cal_(angle_from_protocol):
	angle=hex(eval('0x'+angle_from_protocol))
	angle=int(angle,16)
	if angle > G_val.servo_angle_max:
		angle = G_val.servo_angle_max
	elif angle < G_val.servo_angle_min:
		angle = G_val.servo_angle_min
	return angle

####################################################
##函数名称 Communication_Decode()
##函数功能 ：通信协议解码
##入口参数 ：无
##出口参数 ：无
####################################################    
def _Communication_Decode_(buffer):
	#print 'Communication_decoding...'
	if buffer[0]=='00':
		if buffer[1]=='01':				#前进
			go.forward()
		elif buffer[1]=='02':			#后退
			go.back()
		elif buffer[1]=='03':			#左转
			go.left()
		elif buffer[1]=='04':			#右转
			go.right()
		elif buffer[1]=='00':			#停止
			go.stop()
		else:
			go.stop()
	elif buffer[0]=='02':
		if buffer[1]=='01':#M1_R速度
			speed=hex(eval('0x'+buffer[2]))
			speed=int(speed,16)
			go.M2_Speed(speed)
		elif buffer[1]=='02':#M2_L侧速度
			speed=hex(eval('0x'+buffer[2]))
			speed=int(speed,16)
			go.M1_Speed(speed)
	elif buffer[0]=='01':
		ServoNum = eval('0x'+buffer[1])
		angle  = _Angle_cal_(buffer[2])
		Servo.XiaoRGEEK_SetServoAngle(ServoNum,angle)
		if (angle%2):
			XR.GPIOSet(XR.LED1)
			XR.GPIOSet(XR.LED2)
		else:
			XR.GPIOClr(XR.LED2)
			XR.GPIOClr(XR.LED1)
	elif buffer[0]=='13':
		if buffer[1]=='01':
			G_val.Cruising_Flag = 1#进入红外跟随模式
			print 'Cruising_Flag红外跟随模式 1 '
		elif buffer[1]=='02':#进入红外巡线模式
			G_val.Cruising_Flag = 2
			print 'Cruising_Flag红外巡线模式 %d '%G_val.Cruising_Flag
		elif buffer[1]=='03':#进入红外避障模式
			G_val.Cruising_Flag = 3
			print 'Cruising_Flag红外避障模式 %d '%G_val.Cruising_Flag
		elif buffer[1]=='04':#进入超声波避障模式
			G_val.Cruising_Flag = 4
			print 'Cruising_Flag超声波避障 %d '%G_val.Cruising_Flag
		elif buffer[1]=='05':#进入超声波距离PC显示
			G_val.Cruising_Flag = 5
			print 'Cruising_Flag超声波距离PC显示 %d '%G_val.Cruising_Flag
		elif buffer[1]=='06':
			G_val.Cruising_Flag = 6
			print 'Cruising_Flag超声波摇头避障 %d '%G_val.Cruising_Flag
		elif buffer[1]=='07':
			_Socket_sendbuf_(['\xFF','\xA8','\x00','\x00','\xFF'])
			G_val.Cruising_Flag = 7
		elif buffer[1]=='08':
			if buffer[2]=='00':#Path_Dect 调试模式
				G_val.Path_Dect_on = 0
				G_val.Cruising_Flag = 8
				print 'Cruising_Flag Path_Dect调试模式 8'
			elif buffer[2]=='01':#Path_Dect 循迹模式
				path_sh = 'sh '+ os.path.split(os.path.abspath(__file__))[0] + '/stop_mjpg_streamer.sh &'
				call("%s"%path_sh,shell=True)
				time.sleep(2)
				G_val.Path_Dect_on = 1
				G_val.Cruising_Flag = 9
				print 'Cruising_Flag Path_Dect循迹模式 9 '
		elif buffer[1]=='00':
			G_val.RevStatus=0
			G_val.Cruising_Flag = 0
			print 'Cruising_Flag正常模式 %d '%G_val.Cruising_Flag
	elif buffer[0]=='a0':
		Tangle=hex(eval('0x'+buffer[1]))
		Tangle=int(Tangle,16)
		G_val.TurnAngle=Tangle
		Golen=hex(eval('0x'+buffer[2]))
		Golen=int(Golen,16)
		G_val.Golength=Golen
		G_val.RevStatus=2
	elif buffer[0]=='a1':
		Tangle=hex(eval('0x'+buffer[1]))
		Tangle=int(Tangle,16)
		G_val.TurnAngle=Tangle
		Golen=hex(eval('0x'+buffer[2]))
		Golen=int(Golen,16)
		G_val.Golength=Golen
		G_val.RevStatus=1
	elif buffer[0]=='40':
		temp=hex(eval('0x'+buffer[1]))
		temp=int(temp,16)
		print 'mode_flag====== %d '%temp
		G_val.motor_flag = temp 
	elif buffer[0]=='32':		#存储角度
		Servo.XiaoRGEEK_SaveServo()
		XR.GPIOSet(XR.LED1)
		XR.GPIOClr(XR.LED2)
		time.sleep(0.01)
		XR.GPIOSet(XR.LED2)
		XR.GPIOClr(XR.LED1)
	elif buffer[0]=='33':		#读取角度
		Servo.XiaoRGEEK_ReSetServo()
		XR.GPIOSet(XR.LED1)
		XR.GPIOClr(XR.LED2)
		time.sleep(0.01)
		XR.GPIOSet(XR.LED2)
		XR.GPIOClr(XR.LED1)
	elif buffer[0]=='04':		#开关灯模式 FF040000FF开灯  FF040100FF关灯
		if buffer[1]=='00':
			XRLED.Open_Light()
		elif buffer[1]=='01':
			XRLED.Close_Light()
		else:
			print 'error1 command!'
	elif buffer == ['ef','ef','ee'] :
		print 'Heartbeat Packet!'
	elif buffer[0]=='fc':#FFFC0000FF  shutdown
		XR.GPIOClr(XR.LED0)
		XR.GPIOClr(XR.LED1)
		XR.GPIOClr(XR.LED2)
		time.sleep(0.1)
		XR.GPIOSet(XR.LED0)
		XR.GPIOSet(XR.LED1)
		XR.GPIOSet(XR.LED2)
		time.sleep(0.1)
		XR.GPIOClr(XR.LED0)
		XR.GPIOClr(XR.LED1)
		XR.GPIOClr(XR.LED2)
		time.sleep(0.1)
		XR.GPIOSet(XR.LED0)
		XR.GPIOSet(XR.LED1)
		XR.GPIOSet(XR.LED2)
		os.system("sudo shutdown -h now")
	else:
		print 'error4 command!'


def _Socket_sendbuf_(buf):
	send_buf = buf
	if(G_val.TCP_Client != False):
		for i in range(0,5):
			try:
				G_val.TCP_Client.send(send_buf[i])
				time.sleep(0.005)
			except:
				print 'send error '
	if(G_val.BT_Client != False):
		for i in range(0,5):
			try:
				G_val.BT_Client.send(send_buf[i])
				time.sleep(0.005)
			except:
				print 'send error '
	print 'ssssssss'

def _T_SOCKET_(T_Server,T_buffer,t_name):
	T_rec_flag=0
	T_count=0
	while True:
		print 'waitting for %s connection...'%t_name,"\r"
		if (t_name == 'BT'):
			G_val.BT_Client = False
			G_val.BT_Client,T_ADDR=T_Server.accept();
			T_Client = G_val.BT_Client
			print(str(T_ADDR[0])+' %s Connected!'%t_name),"\r"
		elif(t_name == 'TCP'):
			G_val.TCP_Client = False
			G_val.TCP_Client,T_ADDR=T_Server.accept();
			T_Client = G_val.TCP_Client
			print(str(T_ADDR[0])+' %s Connected!'%t_name),"\r"
		while True:
			try:
				T_data=T_Client.recv(1)
				T_data=binascii.b2a_hex(T_data)
			except:
				print "%s  Error receiving:"%t_name,"\r"
				break
			if not T_data:
				break
			if T_rec_flag==0:
				if T_data=='ff':
					T_buffer[:]=[]
					T_rec_flag=1
					T_count=0
			else:
				if T_data=='ff':
					T_rec_flag=0
					if T_count==3:
						if t_name == 'BT':
							G_val.socket_flag = 1
						elif t_name == 'TCP':
							G_val.socket_flag = 2
						T_count=0
						print t_name + " rec date :" + "\r"
						print T_buffer
						_Communication_Decode_(T_buffer)
						time.sleep(0.001)
				else:
					T_buffer.append(T_data)
					T_count+=1
		T_Client.close()
	go.stop()
	T_Server.close()
	
class XR_SOCKET:
	def __init__(self):
		pass
	def Sendbuf(self,buf):
		_Socket_sendbuf_(buf)
	def BT_Socket(self):
		_T_SOCKET_(BT_Server,BT_buffer,'BT')
	def TCP_Socket(self):
		_T_SOCKET_(TCP_Server,TCP_buffer,'TCP')

