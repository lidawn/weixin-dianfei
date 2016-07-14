# -*- coding: utf-8 -*-
#socket client端
from socket import *
def sendMessage(text):
	serverHost = '211.69.198.208'
	serverPort = 19911
	#建立一个tcp/ip套接字对象
	sockobj = socket(AF_INET, SOCK_STREAM)
	#连结至服务器及端口
	sockobj.connect((serverHost, serverPort))
	sockobj.send(text)
	#从服务端接收到的数据，上限为1k
	data = sockobj.recv(1024)
	#确认他是引用的，是'x'
	print 'Client received:', repr(data)
	#关闭套接字
	sockobj.close()