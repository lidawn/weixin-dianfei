#coding:utf-8
#原始数据
import urllib,urllib2,re
import params_post as pp
import params_post_detail as ppd

import requests
from bs4 import BeautifulSoup as BS


user_agent = '''Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'''
headers = {
	'user-Agent':user_agent,
	'connection':'keep-alive',
	'Referer':'http://202.114.18.218/Main.aspx',
	#'Referer':'http://www.cninfo.com.cn',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding': 'gzip,deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
	#原来是你的锅
	'Content-Type': 'application/x-www-form-urlencoded',
	'Host': '202.114.18.218',
	'Origin': 'http://202.114.18.218'
}


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
	gou_dian_ming_xi = {}
	chao_biao_ming_xi = []
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
	'ImageButton1.x':'35',
	'ImageButton1.y':'8',
	'TextBox2':'',
	'TextBox3':''
	}
	i=0
	values_3['programId'] = programId
	values_3['txtyq'] = txtyq
	values_3['Txtroom'] = Txtroom
	values_3['txtld'] = Txtroom[0]+'层'

	values_3['__VIEWSTATE'] =  ppd.pairs[programId][txtyq]['viewstate']
	values_3['__EVENTVALIDATION'] = ppd.pairs[programId][txtyq]['eventvalidation']
	
	try:
		resp = requests.post(url,headers=headers,data=values_3)
		content = BS(resp.content)
		res_data['zui_hou_chao_biao_shi_jian'] = content.find('input',{'name':'TextBox2'}).get('value')
		res_data['sheng_yu_dian_liang'] = content.find('input',{'name':'TextBox3'}).get('value')
	except Exception,e:
		print e
	
	return res_data

#根据post_detail一次查询
def crawler_detail(programId,txtyq,Txtroom):
	res_data = {}
	gou_dian_ming_xi = {}
	chao_biao_ming_xi = []
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
	'ImageButton1.x':'35',
	'ImageButton1.y':'8',
	'TextBox2':'',
	'TextBox3':''
	}
	i=0
	values_3['programId'] = programId
	values_3['txtyq'] = txtyq
	values_3['Txtroom'] = Txtroom
	values_3['txtld'] = Txtroom[0]+'层'

	values_3['__VIEWSTATE'] =  ppd.pairs[programId][txtyq]['viewstate']
	values_3['__EVENTVALIDATION'] = ppd.pairs[programId][txtyq]['eventvalidation']
	
	try:
		resp = requests.post(url,headers=headers,data=values_3)
		content = BS(resp.content)
		#gou_dian_ming_xi
		try:
			gou_dian_ming_xi_tds = content.find('table',{'id':'GridView1'}).find_all('td')
			gou_dian_ming_xi['chong_zhi'] = gou_dian_ming_xi_tds[0].string
			gou_dian_ming_xi['dian_fei'] = gou_dian_ming_xi_tds[1].string
			gou_dian_ming_xi['shi_jian'] = gou_dian_ming_xi_tds[2].string
			res_data['gou_dian_ming_xi'] = gou_dian_ming_xi
		except:
			res_data['gou_dian_ming_xi'] = None
		#chao_biao_ming_xi
		try:
			chao_biao_ming_xi_tds = content.find('table',{'id':'GridView2'}).find_all('td')
			#print chao_biao_ming_xi_tds
			for j in range(0,14,2):
				chao_biao = {}
				chao_biao['shu_ju'] = chao_biao_ming_xi_tds[j].string
				chao_biao['shi_jian'] = chao_biao_ming_xi_tds[j+1].string
				chao_biao_ming_xi.append(chao_biao)
			res_data['chao_biao_ming_xi'] = chao_biao_ming_xi
		except:
			res_data['chao_biao_ming_xi'] = None
		#print res_data
		#pattern = re.compile(r'name=\"TextBox2\"?.*value=\"(.*)\" readonly=',re.I)
	except Exception,e:
		print e

	return res_data

#print crawler_once('东区','沁苑东十舍','521')
