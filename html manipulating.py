# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 16:33:29 2018

@author: hkoo_RA
"""
import re
import numpy as np
import os
import pdfkit
import csv
import numpy as np
import wkhtmltopdf
from urllib2 import urlopen
import requests
from bs4 import BeautifulSoup

'''
#matching 中文
a = re.match(u"[\u4e00-\u9fa5 ⼿□●]*共參紙[\u4e00-\u9fa5 ⼿□●]*",u"⼿契字式紙共參紙各□執存●，我我五我我有⾃置 份園⼀段")
print a

#operation of set object
s = set()
s.add('254')
s.add('this is a number')
if 'this is a number' not in s:
    s.add(2)
print s
'''



headers = {'User-Agent': 'Mozilla/5.0'}
payload = {'username': 'pohan1@ntu.edu.tw','password': 'sp50315A'}

session = requests.Session()
session.post('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php',headers=headers,data=payload)

#create paths for pdf files
keywords = [ '找','洗','贈','增','添']


path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' #load wkhtml
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

printoptions = {
    'encoding': "UTF-8",
    'quiet': '',
    'DPI':'96',
    'zoom':'1.4'
}

os.chdir('D:\\')

def makedirs_keyword(keyword):
    emperor_year_list = []
    search_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=title:'+keyword)
    search_result = BeautifulSoup(search_session.text,"html.parser")
    for emperor_year in search_result.findAll("a",href = re.compile("^(RetrieveDocs\.php\?text\_query\=\{TM\:)")):
        emperor_year_list.append(emperor_year.attrs["href"])
    for emperor_year in emperor_year_list:
        firstpage_url = emperor_year.encode('utf-8').replace("&in_corpus=OldDeeds&viewing_option=Extract&is_refined_query=1","&paging_option=&cur_page=1")
        firstpage_session = session.get('http://thdl.ntu.edu.tw/THDL/'+firstpage_url)
        firstpage_page = BeautifulSoup(firstpage_session.text,"html.parser")
        emperor = firstpage_page.find("a",{"title":re.compile("^[0-9]")}).get_text()[0:3] #清乾隆
        emperoryear = firstpage_page.find("a",{"title":re.compile("^[0-9]")}).get_text()#清乾隆二十九年(1999)
        if emperoryear[-3:] == '**)'or'14)':
            emperoryear = emperoryear.replace("*","")
            emperoryear = emperoryear.replace(":","")
        os.makedirs('/'+keyword.decode('utf-8')+'/'+emperor+'/'+emperoryear)



tmpsession = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=cca100003-od-383510500e_0006025_01-0001-u.txt')
page = BeautifulSoup(tmpsession.text,"html.parser").find(id='doc1_x_1')
print type(tmpsession)
print type(tmpsession.text)
print type(tmpsession.text.encode('utf-8'))
print type(page)
print type(str(page).decode('utf-8'))
page.findAll('span')[-1].extract()
pdfkit.from_string(str(page).decode('utf-8'),"demo.pdf",configuration=config,options=printoptions)




testsession = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=cca100003-od-383510500e_0006029_02-0001-u.txt')
test = BeautifulSoup(testsession.text,"html.parser")
string = test.find("a",href = re.compile(".*(prepost_cluster)")).attrs["href"]
testsession = session.get('http://thdl.ntu.edu.tw/THDL/'+string)
test = BeautifulSoup(testsession.text,"html.parser")
print test

#os.makedirs('/'+keywords[0].decode('utf-8'))
testsession = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query={TM:清咸豐十一年}+title:贈&paging_option=&cur_page=1')
test = BeautifulSoup(testsession.text,"html.parser")
e = test.find("a",{"title":re.compile("^[0-9]")}).get_text()[-5:-1]
y = test.find("a",{"title":re.compile("^[0-9]")}).get_text()
print e
os.chdir('/'+keywords[0].decode('utf-8')+'/'+e+'/'+y)

os.chdir('D:\\')
#for emperor_year in emperor_year_list:
    #print emperor_year.encode('utf-8')
for keyword in range(len(keywords)):
    emperor_year_list = []
    search_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=title:'+keywords[keyword])
    search_result = BeautifulSoup(search_session.text,"html.parser")
    for emperor_year in search_result.findAll("a",href = re.compile("^(RetrieveDocs\.php\?text\_query\=\{TM\:)")):
        emperor_year_list.append(emperor_year.attrs["href"])
    for emperor_year in emperor_year_list:
        ey = emperor_year.encode('utf-8').replace("&in_corpus=OldDeeds&viewing_option=Extract&is_refined_query=1","&paging_option=&cur_page=1")
        eysession = session.get('http://thdl.ntu.edu.tw/THDL/'+ey)
        eypage = BeautifulSoup(eysession.text,"html.parser")
        e = eypage.find("a",{"title":re.compile("^[0-9]")}).get_text()[0:3] #清乾隆
        y = eypage.find("a",{"title":re.compile("^[0-9]")}).get_text()#清乾隆二十九年(1999)
        if y[-3:] == '**)':
            y = y.replace("*","")
            y = y.replace(":","")
        os.makedirs('/'+keywords[keyword].decode('utf-8')+'/'+e+'/'+y)

ey = emperor_year_list[0].encode('utf-8').replace("&in_corpus=OldDeeds&viewing_option=Extract&is_refined_query=1","&paging_option=&cur_page=1")
testsession = session.get('http://thdl.ntu.edu.tw/THDL/'+ey)
test = BeautifulSoup(testsession.text,"html.parser")
#print test

#
testsession = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=title:'+keywords[0])
test = BeautifulSoup(testsession.text,"html.parser")
#print test
 


testsession = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query={TM:清乾隆二十九年}+title:找&paging_option=&cur_page=1')
test = BeautifulSoup(testsession.text,"html.parser")
print type(test.find("a",{"title":re.compile("^[0-9]")}).get_text()[0:3]) #清乾隆
print type(test.find("font",{"class":"BgYellow"}).get_text())#清乾隆二十九年
print type(keywords[0].decode('utf-8'))
newstr = test.find("table", {"class":"PagingSelection"}).get_text().split(" ")[1].replace("\n","")
#print int(newstr)%10
'''
#add a tag into soup object
tmp = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveSVG.php?filename=cca100003-od-383510500e_0006025_01-0001-u.txt')
svg =  BeautifulSoup(tmp.text.encode('utf-8'),"html.parser")
new_tag = svg.new_tag("table")
new_tag.append("some text")
svg.svg.g.insert_after(new_tag) #加一個新的tag:table

new_tag = svg.new_tag("tr")
new_tag.append("month")
svg.svg.table.insert_after(new_tag)#table後面加一個<tr>month</tr> 

new_tag = svg.new_tag("tr")
new_tag.append('month')
svg.svg.table.append(new_tag)#table裡面加一個<tr>month</tr>

svg.svg.table.insert("tr","month")#table裡面加文字month

print svg

svg.svg.table.clear() #刪除<table>...</table>中的內容...

print svg

svg.svg.table.extract() #刪除整個<table>...</table>

print svg
'''


