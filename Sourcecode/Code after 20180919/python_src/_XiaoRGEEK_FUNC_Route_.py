#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
'''
文 件 名：_XiaoRGEEK_FUNC_Route_.py
功    能：XiaoRGEEK路径规划
外部调用：
import _XiaoRGEEK_FUNC_Route_
_XiaoRGEEK_FUNC_Route_.Route()
'''
import time
import _XiaoRGEEK_GPIO_ as XR
import _XiaoRGEEK_GLOBAL_variable_ as G_val
from _XiaoRGEEK_MOTOR_ import Robot_Direction
go = Robot_Direction()

from _XiaoRGEEK_SOCKET_ import XR_SOCKET
soc = XR_SOCKET()
####################################################
##函数名称 
##函数功能 Route() 路径规划
##入口参数 ：无
##出口参数 ：无
####################################################
def Route():
	while G_val.RevStatus !=0 :
		print 'RevStatus==== %d ' %G_val.RevStatus
		TurnA=float(G_val.TurnAngle*6)/1000
		Golen=float(G_val.Golength*10)/1000
		print 'TurnAngle====== %f ' %TurnA
		print 'Golength======= %f ' %Golen
		if G_val.RevStatus==1:
			go.left()
			time.sleep(TurnA)
			go.stop()
			go.forward()
			time.sleep(Golen)
			go.stop()
			G_val.RevStatus = 0
			buf  = ['\xFF','\xA8','\x00','\x00','\xFF']
			soc.Sendbuf(buf)
			time.sleep(0.01)
		elif G_val.RevStatus==2:
			go.right()
			time.sleep(TurnA)
			go.stop()
			go.forward()
			time.sleep(Golen)
			go.stop()
			G_val.RevStatus = 0
			buf  = ['\xFF','\xA8','\x00','\x00','\xFF']
			soc.Sendbuf(buf)
			time.sleep(0.01)
			