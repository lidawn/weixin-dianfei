#coding:utf-8
from django import forms 
from django.shortcuts import render
from django.http import HttpResponseRedirect
from wx.crawler import crawler_dianfei
from django.forms.util import ErrorList
from wx.models import User

quyu_text=""
louhao_text=""
fangjian_text=""

class BoundForm(forms.Form):
	#area
	area = forms.CharField(required=True,max_length=20)
	#building
	building = forms.CharField(required=True,max_length=30,error_messages={'required':[u'楼栋号不能为空哦']})
	#room
	room = forms.IntegerField(required=True,error_messages={'required':[u'房间号不能为空哦'],'invalid':[u'房间号应该为数字']})

	def clean(self):
		cleaned_data = self.cleaned_data
		
		area = cleaned_data.get('area')
		building = cleaned_data.get('building')
		room = cleaned_data.get('room')
		if not building or not room:
			raise forms.ValidationError(u":-D")

		#验证该寝室号是否正确，即抓一下网站，看能不能返回。
		check_data = crawler_dianfei.crawler_once(area.encode('utf-8'),building.encode('utf-8'),str(room))
		#未返回数据
		if check_data is None or check_data.get('zui_hou_chao_biao_shi_jian') is None:
			raise forms.ValidationError(u"房间号不存在")

		return cleaned_data

def bound(request):
	#研究一下message机制，不要用全局变量，容易导致不一致
	global quyu_text
	global louhao_text
	global fangjian_text
	#print "get:",request.GET
	#print "request",request
	wid = request.GET.get("wid","anoy")
	#print "wid:",wid
	try:
		user = User.objects.get(weixin_id=wid)
	except User.DoesNotExist:
		#失效页，TODO
		pass
	if request.method=="POST":
		form = BoundForm(request.POST)
		if form.is_valid():
			quyu_text = form.cleaned_data['area']
			louhao_text = form.cleaned_data['building']
			fangjian_text = form.cleaned_data['room']
			#存数据库
			user.quyu = quyu_text
			user.louhao = louhao_text
			user.fangjian  = fangjian_text
			user.is_bounded = True
			user.save()
			return HttpResponseRedirect('/success/')
	else:
		form = BoundForm()

	return render(request,'bound.html',{'form':form,})

def success(request):
	boundmessage = {'text':quyu_text+louhao_text+str(fangjian_text)}
	print boundmessage
	return render(request,'success.html',{'boundmessage':boundmessage,})
