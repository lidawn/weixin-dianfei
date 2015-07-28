#coding:utf-8
#原始数据
import urllib,urllib2,re
import params_post as pp
import params_post_detail as ppd

AREAS = ['东区','西区','韵苑二期','韵苑一期','紫菘']
VIEWSTATE = pp.pair_original['viewstate']
EVENTVALIDATION = pp.pair_original['eventvalidation']
#每次传入的参数都必须是完整的。
#先从原网页中得到原始view和id，编译得到区的view和id，再查楼栋的view和id，再查电费。三次失败时，调用该函数。
def crawler_forth():
	pass

#根据原始view和id，遍历得到区的view和id，再查楼栋的view和id，再查电费。两次失败时，调用该函数。
def crawler_thrice():
	pass

#根据post两次查询，先根据区域得到具体楼栋的view和id，在根据此id查电费。
def crawler_twice():
	#TODO
	pass

#根据post_detail一次查询
def crawler_once(programId,txtyq,Txtroom):
	res_data = {}
	url = 'http://202.114.18.218/Main.aspx'
	values_3 = {'__EVENTTARGET':'',
	'__EVENTARGUMENT':'',
	'__LASTFOCUS':'',
	'__VIEWSTATE':'',#need
	'__EVENTVALIDATION':'',#need
	'programId':'',#need
	'txtyq':'',#need
	'txtld':'',#need
	'Txtroom':'',#need
	'ImageButton1.x':'16',
	'ImageButton1.y':'12',
	'TextBox2':'',
	'TextBox3':''}
	i=0
	values_3['programId'] = programId
	values_3['txtyq'] = txtyq
	values_3['Txtroom'] = Txtroom
	values_3['txtld'] = Txtroom[0]+'层'

	values_3['__VIEWSTATE'] =  ppd.pairs[programId][txtyq]['viewstate']
	#values_3['__VIEWSTATE'] =  ppd.pairs[programId][txtyq]['viewstate']
	values_3['__EVENTVALIDATION'] = ppd.pairs[programId][txtyq]['eventvalidation']
	#获取电量
	#层数大于规定时，urllib会出错
	#层数对但是房间错，返回空值
	data = urllib.urlencode(values_3)
	req = urllib2.Request(url,data)
	try:
		response = urllib2.urlopen(req)
		the_page = response.read()
		pattern = re.compile(r'name=\"TextBox2\"?.*value=\"(.*)\" readonly=',re.I)
		zui_hou_chao_biao_shi_jian = pattern.findall(the_page)
		#print zui_hou_chao_biao_shi_jian
		res_data['zui_hou_chao_biao_shi_jian'] = zui_hou_chao_biao_shi_jian
		pattern = re.compile(r'name=\"TextBox3\"?.*value=\"(.*)\" readonly=',re.I)
		sheng_yu_dian_liang = pattern.findall(the_page)
		res_data['sheng_yu_dian_liang'] = sheng_yu_dian_liang
		#print sheng_yu_dian_liang
	except Exception,e:
		print e
	#['2015-7-26 7:09:09']
	#['191.4']
	#pattern = re.compile(r'<td>(.*)</td>',re.I)
	#td_data = pattern.findall(the_page)
	#chao_biao_shu_ju = td_data[5:12]
	#gou_dian_ming_xi = td_data[12]
	return res_data

print crawler_once('韵苑二期','韵苑15栋','1')
