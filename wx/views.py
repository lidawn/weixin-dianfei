#coding:utf-8
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext,Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode
from django.shortcuts import render
from wx.models import User
from wx.crawler import crawler_dianfei

import urllib,urllib2,time,hashlib,re
import xml.etree.ElementTree as ET

TOKEN = "dianfei521lidawn4"
res_data = {}

def help():
	'''1.绑定寝室请回复: 绑定\n  绑定后回复任意内容查询电费\n2.解除绑定请回复: 解除\n3.提示本条消息请回复: 帮助\n4.反馈建议请点击：<a href="http://form.mikecrm.com/BhpHew">反馈建议</a>
    \n =====================\n
    如果没响应请多试几次，或者用校园网访问：<a href="http://202.114.18.218/Main.aspx">官方网站</a>'''

def checkSignature(request):
	global TOKEN
	signature = request.GET.get("signature",None)
	timestamp = request.GET.get("timestamp",None)
	nonce = request.GET.get("nonce",None)
	echostr = request.GET.get("echostr",None)
	token = TOKEN
	tmplist = [token,timestamp,nonce]
	tmplist.sort()
	tmpstr = "%s%s%s" % tuple(tmplist)
	tmpstr = hashlib.sha1(tmpstr).hexdigest()
	if tmpstr == signature:
		return echostr
	else:
		return None

def intent(content):
	#return 1 : 绑定
	#return 2 : 解除绑定
	#return 3 : 帮助  
	#return 4 : 反馈
	#return 5 : 任意字符
	#return 6 : 详细
	#print "content",content
	intent = content.replace(' ','')
	#print "intent",intent
	if intent == '绑定':
		return 1
	elif intent == '解除' or intent == '解绑':
		return 2
	elif intent == '帮助' or intent == 'help':
		return 3
	elif intent == '反馈' or intent == '建议':
		return 4
	elif intent == '详细' or intent =='xx':
		return 6
	else :
		return 5
	
def handleRequest(request):
	msg = {}
	raw = smart_str(request.body)
	from_weixin = ET.fromstring(raw)
	if from_weixin.tag =='xml':
		for child in from_weixin:
			msg[child.tag] = smart_str(child.text)
	#返回解析的xml
	return msg
		
def responseMsg(request):
	response = '剩余电量:'
	from_weixin = handleRequest(request)
	#关注
	if from_weixin.get('MsgType') == 'event':
		#print 'Msgtype:event:'
		if from_weixin.get('Event') == 'subscribe':
			#print 'event:subscribe'
			content = help.__doc__
			response = content
		#扫码
		elif from_weixin.get('Event') == 'SCAN':
			#print 'event:scan'
			#TODO
			response = 'test'
	#普通消息
	else:
		weixin_id = from_weixin.get('FromUserName')
		if from_weixin.get('MsgType') == 'text':
			#print 'Msgtype:text:'
			text = from_weixin.get('Content') 
			#print 'text:',text
			i = intent(text)
			#print '判断:i',i
		else:
			i = 5
		#检查是否已绑定
		try:
			user = User.objects.get(weixin_id=weixin_id)
		except User.DoesNotExist:
			#用户不存在
			is_bounded = False
			is_user_exist = False
		else:
			is_bounded = user.is_bounded
			is_user_exist = True
		if is_bounded:
			#绑定用户，消息类型：1.绑定 2.解绑 3.帮助 4.反馈 5. 查自己 6.详细
			area = user.quyu.encode("utf-8")
			building = user.louhao.encode("utf-8")
			room = str(user.fangjian)
			if i == 1:
				response = '您已绑定(%s),需要重新绑定请点击<a href=\"http://m1540057b2.iask.in/bound/?wid=%s\">绑定寝室</a>' \
				% (area+building+room ,weixin_id)
			elif i == 2:
				#仅修改is_bounded
				user.is_bounded = False
				user.save()
				response = '已帮您解绑(%s),需要重新绑定请点击<a href=\"http://m1540057b2.iask.in/bound/?wid=%s\">绑定寝室</a>' \
				% (area+building+room ,weixin_id)
			elif i == 3:
				response = help.__doc__
			elif i == 4:
				#TODO
				response = '反馈建议请点击<a href=\"http://form.mikecrm.com/BhpHew\">反馈建议</a>'
			elif i == 5:
				res_data = crawler_dianfei.crawler_once(area,building,room)
				response = '您绑定的寝室号:%s\n===================\n剩余电量:%s\n最后抄表时间:%s\n===================\n详细抄表和购电请回复：详细\n如有疑问,请回复：帮助' \
				%(area+building+room ,res_data.get('sheng_yu_dian_liang').encode('utf-8'),res_data.get('zui_hou_chao_biao_shi_jian').encode('utf-8'))

			elif i == 6:
				res_data = crawler_dianfei.crawler_detail(area,building,room)
				li = res_data.get('chao_biao_ming_xi')
				chao_biao_ming_xi = ''
				for item in li:
					chao_biao_ming_xi += item.get('shu_ju') + ' | ' + item.get('shi_jian')+'\n'

				response = '''您绑定的寝室号：%s\n===================
最近7天抄表：\n-------------------\n数据 | 时间\n-------------------\n%s===================
最近购电明细：\n-------------------\n%s\n===================\n如有疑问，请输入：帮助''' \
				% (area+building+room,
				chao_biao_ming_xi.encode('utf-8'),
				'电量: '+res_data.get('gou_dian_ming_xi').get('chong_zhi').encode('utf-8')\
				+'\n电费: '+res_data.get('gou_dian_ming_xi').get('dian_fei').encode('utf-8')\
				+'\n时间: '+res_data.get('gou_dian_ming_xi').get('shi_jian').encode('utf-8') )
				
		else:
			#未绑定用户，消息类型：1.绑定 2.3.5.6 帮助 4.反馈 
			if i == 1:
				#先存id，再返回链接
				if not is_user_exist:
					user = User(weixin_id=weixin_id,quyu="1",louhao="1",fangjian="1",is_bounded=False)
					user.save()
				response = '绑定寝室请点击<a href=\"http://m1540057b2.iask.in/bound/?wid=%s\">绑定寝室</a>'\
				% weixin_id
			elif i == 2 or i==3 or i==5 or i==6:
				response = help.__doc__
			elif i == 4:
				#TODO
				response = '反馈建议请点击<a href=\"\">反馈建议</a>'
	
	to_weixin  = '''<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content></xml>'''
	to_weixin = to_weixin % (from_weixin['FromUserName'],from_weixin['ToUserName'],str(int(time.time())),'text',response)
	#to_weixin = response
	return to_weixin

@csrf_exempt   
def check(request):
	if request.method == 'GET':
		#验证
		response = HttpResponse(checkSignature(request))
		return response
	elif request.method == 'POST':
		#接受微信消息
		response = HttpResponse(responseMsg(request))
		return response
	else:
		return None
