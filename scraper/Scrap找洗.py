# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 23:58:27 2018

@author: Po-Han Chen
"""

# coding=UTF-8
import requests
from bs4 import BeautifulSoup
import os
import csv
import pdfkit
import time
import datetime
from urllib2 import urlopen
import re


keyword_dic = { '找':'zhao','洗':'shi','贈':'zheng','增':'tseng','添':'tian'}
empieror = [ '康熙','雍正','乾隆','嘉慶','道光','咸豐','同治','光緒','明治','大正']

headers = {'User-Agent': 'Mozilla/5.0'}
payload = {'username': 'enterusername','password': 'enterpassword'}

session = requests.Session()
session.post('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php',headers=headers,data=payload) #login

path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' #load wkhtml
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

printoptions = {
    'encoding': "UTF-8",
    'quiet': '',
    'DPI':'96',
    'zoom':'1.4'
}

os.chdir('D:\\')
#define the scraper
def scrap_zhao(keyword):
    session = requests.Session()
    session.post('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php',headers=headers,data=payload)
    #get the result of searching title:keyword
    search_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=title:'+keyword)
    search_page = BeautifulSoup(search_session.text,"html.parser")
    #find emperor-year
    #<a href="RetrieveDocs.php?text_query={TM:..."
    emperor_year_list = []
    for emperor_year in search_page.findAll( "a" , href = re.compile("^(RetrieveDocs\.php\?text\_query\=\{TM\:)")):
        emperor_year_list.append(emperor_year.attrs["href"])
    
    #starts scraping
    for emperor_year in emperor_year_list:
        beginning_session = session.get('http://thdl.ntu.edu.tw/THDL/'+emperor_year)
        beginning_page = BeautifulSoup(beginning_session.text,"html.parser")
        found = int(beginning_page.find("table", {"class":"PagingSelection"}).get_text().split(" ")[1].replace("\n",""))
        #no tree
        if found <= 10:
            serial_number = 1
            onlypage_url = emperor_year.encode('utf-8').replace("&in_corpus=OldDeeds&viewing_option=Extract&is_refined_query=1","&paging_option=&cur_page=1")
            onlypage_session = session.get('http://thdl.ntu.edu.tw/THDL/'+onlypage_url)
            onlypage_page = BeautifulSoup(onlypage_session.text,"html.parser")
            emperor = onlypage_page.find("a",{"title":re.compile("^[0-9]")}).get_text()[0:3] #清乾隆
            year = onlypage_page.find("a",{"title":re.compile("^[0-9]")}).get_text()[-5:-1] #1999
            emperoryear = onlypage_page.find("a",{"title":re.compile("^[0-9]")}).get_text()#清乾隆二十九年(1999)
            if emperoryear[-3:] == '**)'or'14)':
                emperoryear = emperoryear.replace("*","")
                emperoryear = emperoryear.replace(":","")
            if year[-2:] == '**':
                    year = year.replace("*","u")
                    year = year.replace(":","")
            os.chdir('/'+keyword.decode('utf-8')+'/'+emperor+'/'+emperoryear)
            contract_list = []
            for contract in onlypage_page.findAll("input",{"id":re.compile("^(g1)")}):
                contract_list.append(contract.attrs["value"])
            
            for contract in contract_list:
                              
                contract_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query={'+contract+'}')
                contract_page = BeautifulSoup(contract_session.text,"html.parser")
                #看是否有tree
                if contract_page.find("a",{"href":re.compile(".*(prepost_docs)")}) == None:
                    content = contract_page.findAll(id='doc1_x_1')[0]
                    content.findAll('span')[-1].extract()
                    pdfkit.from_string(str(content).decode('utf-8'),keyword_dic[keyword]+"."+year+"."+str(serial_number)+".pdf",configuration=config,options=printoptions)
                    serial_number += 1
                #http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=?prepost_cluster:{contract code} 
                else:
                    
                    tree_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=?prepost_cluster:{'+contract+'}')
                    tree_page = BeautifulSoup(tree_session.text,"html.parser")
                    tree_svg_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveSVG.php?filename='+contract)
                    tree_svg = BeautifulSoup(tree_svg_session.text,"html.parser")
                    pdfkit.from_string(str(tree_svg).decode('utf-8'),keyword_dic[keyword]+"."+year+"."+str(serial_number)+".pdf",configuration=config,options=printoptions)
                    tree_contract_list = []
                    for tree_contract in tree_page.findAll("input",{"id":re.compile("^(g1)")}):
                        tree_contract_list.append(tree_contract.attrs["value"])
                    tree_number = 1
                    for tree_contract in tree_contract_list:    
                        
                        tree_contract_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query={'+tree_contract+'}')
                        tree_contract_page = BeautifulSoup(tree_contract_session.text.encode('utf-8'),"html.parser")
                        tree_year = tree_contract_page.find("a",{"title":re.compile("^[0-9]")}).get_text()[-5:-1]
                        if tree_year[-2:] == '**':
                            tree_year = year.replace("*","u")
                            tree_year = year.replace(":","")
                        tree_contract_content = tree_contract_page.find(id='doc1_x_1')
                        tree_contract_content.findAll('span')[-1].extract()
                        pdfkit.from_string(str(tree_contract_content).decode('utf-8'),keyword_dic[keyword]+"."+year+"."+str(serial_number)+"."+tree_year+"."+str(tree_number)+".pdf",configuration=config,options=printoptions)
                        tree_number += 1
                    serial_number += 1
        else:
            if found % 10 == 0:
                pages = found / 10
            else:
                pages = found / 10 + 1 
            serial_number = 1
            for page in range(pages):
                page_url = emperor_year.encode('utf-8').replace("&in_corpus=OldDeeds&viewing_option=Extract&is_refined_query=1","&paging_option=&cur_page="+str(page+1))
                page_session = session.get('http://thdl.ntu.edu.tw/THDL/'+page_url)
                page_page = BeautifulSoup(page_session.text,"html.parser")
                emperor = page_page.find("a",{"title":re.compile("^[0-9]")}).get_text()[0:3] #清乾隆
                year = page_page.find("a",{"title":re.compile("^[0-9]")}).get_text()[-5:-1] #1999
                emperoryear = page_page.find("a",{"title":re.compile("^[0-9]")}).get_text()#清乾隆二十九年(1999)
                if emperoryear[-3:] == '**)'or'14)':
                    emperoryear = emperoryear.replace("*","")
                    emperoryear = emperoryear.replace(":","")
                if year[-2:] == '**':
                    year = year.replace("*","u")
                    year = year.replace(":","")
                os.chdir('/'+keyword.decode('utf-8')+'/'+emperor+'/'+emperoryear)
                contract_list = []
                for contract in page_page.findAll("input",{"id":re.compile("^(g1)")}):
                    contract_list.append(contract.attrs["value"])
                
                for contract in contract_list:
                          
                    contract_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query={'+contract+'}')
                    contract_page = BeautifulSoup(contract_session.text.encode('utf-8'),"html.parser")
                    #看是否有tree
                    if contract_page.find("a",{"href":re.compile(".*(prepost_docs)")}) == None:
                        content = contract_page.find(id='doc1_x_1')
                        content.findAll('span')[-1].extract()
                        pdfkit.from_string(str(content).decode('utf-8'),keyword_dic[keyword]+"."+year+"."+str(serial_number)+".pdf",configuration=config,options=printoptions)
                        serial_number += 1
                    #http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=?prepost_cluster:{contract code} 
                    else:
                        
                        tree_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query=?prepost_cluster:{'+contract+'}')
                        tree_page = BeautifulSoup(tree_session.text,"html.parser")
                        tree_svg_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveSVG.php?filename='+contract)
                        tree_svg = BeautifulSoup(tree_svg_session.text.encode('utf-8'),"html.parser")
                        pdfkit.from_string(str(tree_svg).decode('utf-8'),keyword_dic[keyword]+"."+year+"."+str(serial_number)+".pdf",configuration=config,options=printoptions)
                        tree_contract_list = []
                        for tree_contract in tree_page.findAll("input",{"id":re.compile("^(g1)")}):
                            tree_contract_list.append(tree_contract.attrs["value"])
                        tree_number = 1
                        for tree_contract in tree_contract_list:    
                            
                            tree_contract_session = session.get('http://thdl.ntu.edu.tw/THDL/RetrieveDocs.php?text_query={'+tree_contract+'}')
                            tree_contract_page = BeautifulSoup(tree_contract_session.text.encode('utf-8'),"html.parser")
                            tree_year = tree_contract_page.find("a",{"title":re.compile("^[0-9]")}).get_text()[-5:-1]
                            if tree_year[-2:] == '**':
                                tree_year = year.replace("*","u")
                                tree_year = year.replace(":","")
                            tree_contract_content = tree_contract_page.find(id='doc1_x_1')
                            tree_contract_content.findAll('span')[-1].extract()
                            pdfkit.from_string(str(tree_contract_content).decode('utf-8'),keyword_dic[keyword]+"."+year+"."+str(serial_number)+"."+tree_year+"."+str(tree_number)+".pdf",configuration=config,options=printoptions)
                            tree_number += 1
                        serial_number += 1

#scraping
if __name__ == "__main__":
    for keyword in keyword_dic.keys():
        scrap_zhao(keyword)
    
