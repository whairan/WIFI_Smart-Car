#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
'''
文 件 名：_XiaoRGEEK_FUNCTION_Default_.py
功    能：XiaoRGEEK路径规划常规功能函数，包含红外避障、红外巡线、跟随模式、超声波避障、超声波测距、测距上传等等
外部条用：
from _XiaoRGEEK_FUNCTION_Default_ import XR_Function_Default
fun = XR_Function_Default()
fun.Avoiding()		#红外避障模式
fun.TrackLine()		#红外巡线模式
fun.Follow()		#红外跟随模式
fun.Get_Distence()	#获取超声波距离
fun.AvoidByRadar()	#超声波避障模式
fun.Send_Distance()	#超声波测距上传模式
'''
import time
from _XiaoRGEEK_SOCKET_ import XR_SOCKET
soc = XR_SOCKET()
import _XiaoRGEEK_GPIO_ as XR
import _XiaoRGEEK_GLOBAL_variable_ as G_val
from _XiaoRGEEK_MOTOR_ import Robot_Direction
go = Robot_Direction()

####################################################
##函数名称 ：Avoiding()
##函数功能 ：红外避障函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	_Avoiding_(): #红外避障函数
	if XR.DigitalRead(XR.IR_M) == False:
		go.stop()
		time.sleep(0.1)
####################################################
##函数名称 TrackLine()
##函数功能 巡黑线模式
##入口参数 ：无
##出口参数 ：无
####################################################
def _TrackLine_():
	if (XR.DigitalRead(XR.IR_L) == False)&(XR.DigitalRead(XR.IR_R) == False): #黑线为高，地面为低
		go.forward()
		#return
	elif (XR.DigitalRead(XR.IR_L) == False)&(XR.DigitalRead(XR.IR_R) == True):
		go.right()
		#return
	elif (XR.DigitalRead(XR.IR_L) == True)&(XR.DigitalRead(XR.IR_R) == False):
		go.left()
		#return
	elif (XR.DigitalRead(XR.IR_L) == True)&(XR.DigitalRead(XR.IR_R) == True): #两侧都碰到黑线
		go.stop()
		#return
####################################################
##函数名称 Follow()
##函数功能 跟随模式
##入口参数 ：无
##出口参数 ：无
####################################################
def _Follow_(): 
	if(XR.DigitalRead(XR.IR_M) == True): #中间传感器OK
		if(XR.DigitalRead(XR.IRF_L) == False)&(XR.DigitalRead(XR.IRF_R) == False):	#俩边同时探测到障碍物
			go.stop()			#停止 
		if(XR.DigitalRead(XR.IRF_L) == False)&(XR.DigitalRead(XR.IRF_R) == True):		#左侧障碍物
			go.right()		#右转 
		if(XR.DigitalRead(XR.IRF_L) == True)& (XR.DigitalRead(XR.IRF_R) == False):		#右侧障碍物
			go.left()		#左转
		if(XR.DigitalRead(XR.IRF_L) == True)& (XR.DigitalRead(XR.IRF_R) == True):		#无任何障碍物
			go.forward()			#直行 
	else:
		go.stop()
####################################################
##函数名称 ：Get_Distence()
##函数功能 超声波测距，返回距离（单位是厘米）
##入口参数 ：无
##出口参数 ：无
####################################################
def	_Get_Distence_():
	time_count = 0
	time.sleep(0.01)
	XR.GPIOSet(XR.TRIG)
	time.sleep(0.000015)
	XR.GPIOClr(XR.TRIG)
	while not XR.DigitalRead(XR.ECHO):
		pass
	t1 = time.time()
	while XR.DigitalRead(XR.ECHO):
		if(time_count < 0xfff):
			time_count = time_count + 1
			time.sleep(0.000001)
			pass
		else :
			print 'NO ECHO receive! Please check connection '
			break
	t2 = time.time()
	Distence = (t2-t1)*340/2*100
	print 'Distence is %d'%Distence
	if (Distence < 500):
		print 'Distence is %d'%Distence
		return Distence
	else :
		print 'Distence is 0'
		return 0 
####################################################
##函数名称 Avoid_wave()
##函数功能 超声波避障函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	_AvoidByRadar_():
	dis = _Get_Distence_()
	#print 'Distence is %d'%dis
	if 300>dis>G_val.Radar_distence:
		go.forward()
	else:
		go.stop()
####################################################
##函数名称 Send_Distance()
##函数功能 ：超声波距离PC端显示
##入口参数 ：无
##出口参数 ：无
####################################################
def	_Send_Distance_():
	dis_send = int(_Get_Distence_())
	send_buf=[]
	send_flag = False
	if 2<dis_send < 255:
		send_buf=['\xff','\x03','\x00',chr(dis_send),'\xff']
		#send_flag = True
		soc.Sendbuf(send_buf)
	else:
		send_buf=[]
	#time.sleep(0.05)

	
		

class XR_Function_Default:
	def __init__(self):
		pass
	def	Avoiding(self):
		_Avoiding_()
	def TrackLine(self):
		_TrackLine_()
	def Follow(self): 
		_Follow_()
	def Get_Distence(self):
		return _Get_Distence_()
	def AvoidByRadar(self):
		_AvoidByRadar_()
	def Send_Distance(self):
		 _Send_Distance_()
