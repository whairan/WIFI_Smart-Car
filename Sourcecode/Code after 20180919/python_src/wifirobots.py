#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
'''
文 件 名：wifirobots.py
功    能：XiaoRGEEK raspberry pi python主程序。
调用接口：
python wifirobots.py &
'''
import os
import time 
import threading
from subprocess import call

from _XiaoRGEEK_LED_ import Robot_Led
XRLED = Robot_Led()

import _XiaoRGEEK_FUNC_Pathdec_ as PDec

from _XiaoRGEEK_FUNCTION_Default_ import XR_Function_Default
XRFUN = XR_Function_Default()

from _XiaoRGEEK_FUNC_Route_ import Route

import _XiaoRGEEK_GLOBAL_variable_ as G_val

from _XiaoRGEEK_MOTOR_ import Robot_Direction
go = Robot_Direction()

from _XiaoRGEEK_SOCKET_ import XR_SOCKET
soc = XR_SOCKET()


print '....WIFIROBOTS START!!!...'


####################################################
##函数名称 Cruising_Mod()
##函数功能 ：模式切换函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	Cruising_Mod():
	Pre_Cruising_Flag = 0 	#//预循环模式
	print 'Pre_Cruising_Flag %d '%Pre_Cruising_Flag
	while True:
		if (Pre_Cruising_Flag != G_val.Cruising_Flag):			
			if (Pre_Cruising_Flag != 0):
				go.stop()
			Pre_Cruising_Flag = G_val.Cruising_Flag
		if(G_val.Cruising_Flag == 1):		#进入红外跟随模式
			XRFUN.Follow()
		elif (G_val.Cruising_Flag == 2):	#进入红外巡线模式
			XRFUN.TrackLine()
		elif (G_val.Cruising_Flag == 3):	#进入红外避障模式
			XRFUN.Avoiding()
		elif (G_val.Cruising_Flag == 4):	#进入超声波壁障模式##
			XRFUN.AvoidByRadar()
			
		elif (G_val.Cruising_Flag == 5):	#进入超声波测距模式
			XRFUN.Send_Distance()
		elif (G_val.Cruising_Flag == 7):
			try:
				Route()
			except:
				print '07 error'
		elif (G_val.Cruising_Flag == 8):	#退出摄像头循迹或进入调试模式
			time.sleep(3)
			path_sh = 'sh '+ os.path.split(os.path.abspath(__file__))[0] + '/start_mjpg_streamer.sh &'
			call("%s"%path_sh,shell=True)
			G_val.Cruising_Flag = 0
		elif (G_val.Cruising_Flag == 9):	#进入摄像头循迹操作
			PDec.Path_Dect()
		elif (G_val.Cruising_Flag == 0):
			G_val.RevStatus=0
		else:
			time.sleep(0.01)
		time.sleep(0.01)

os.system("sudo hciconfig hci0 name XiaoRGEEK")
time.sleep(0.1)
os.system("sudo hciconfig hci0 reset")
time.sleep(0.3)
os.system("sudo hciconfig hci0 piscan")
time.sleep(0.2)
print 'NOW BT discoverable'

XRLED.FLOW_LED()
time.sleep(0.2)
threads = []
t1 = threading.Thread(target=PDec.Path_Dect_img_processing,args=())
threads.append(t1)
t2=threading.Thread(target=soc.BT_Socket,args=())
threads.append(t2)
t3=threading.Thread(target=soc.TCP_Socket,args=())
threads.append(t3)

path_sh = 'sh '+ os.path.split(os.path.abspath(__file__))[0] + '/start_mjpg_streamer.sh &'
call("%s"%path_sh,shell=True)
time.sleep(1)
for t in threads:
		t.setDaemon(True)
		t.start()
		time.sleep(0.05)
		print 'theads start...'
print 'all theads start...'

while True:
	try:
		Cruising_Mod()
	except:
		print 'Cruising_Mod error...'

