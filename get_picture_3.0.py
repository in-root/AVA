import time
import os
import urllib2
import random
import sys
import requests
from bs4 import BeautifulSoup
from  lxml import etree
from HTMLParser import HTMLParser


import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

txt_file = "old0.txt"

savePath = r'/home/ndn/yjw/new_way_for_lyf/image'
URLprefix = r'http://www.dpchallenge.com/image.php?IMAGE_ID='
AVAtxt = '/home/ndn/yjw/file_txt/'+txt_file
HEADERS = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3','Connection': 'keep-alive','DNT': '1','Host': 'www.dpchallenge.com','Upgrade-Insecure-Requests': '1'}
fp_source = open(AVAtxt)
count = 0   #the frequent to renew proxy


#parse true url from html
class dpchallengeImageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.name = None

    # fetch url and loop out when both image's width and height exceed 200 pix.
    def handle_starttag(self, tag, attrs):
        if self.name is not None:
            return
        if tag == 'img':
            tmpWidth = 0
            tmpHeight = 0
            for key,value in attrs:
                if key == 'src':
                    tmpName = value
                    tmpWidth = 0
                    tmpHeight = 0
                elif key == 'width':
                    tmpWidth = float(value)
                elif key == 'height':
                    tmpHeight = float(value)
                if (tmpWidth > 150) and (tmpHeight > 150):
                    self.name = tmpName
                    break

#get proxy
def get_proxy():
    for i in range(10):
        try:
            url_proxy = 'http://www.xicidaili.com/wn/'
            headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }
            proxy_data = requests.get(url_proxy, headers=headers)
            soup = BeautifulSoup(proxy_data.text, 'lxml')
            ips = soup.find_all('tr')
            temp_ip_list = []
            for temp_i in range(1, len(ips)):
                ip_info = ips[temp_i]
                tds = ip_info.find_all('td')
                temp_ip_list.append(tds[1].text + ':' + tds[2].text)
                temp_ip_list_length = len(temp_ip_list)
            print "The total proxy wo get is: "+str(temp_ip_list_length)
        except Exception,e:
            continue
        break
    return temp_ip_list




# get  an random  proxy, not use
def get_random_proxy():
    ip_list_length = len(ip_list)
    index = random.randint(0,ip_list_length)
    return index


def get_per_url(imageIndex,imageID):
    print "begin to parse"+ imageIndex
    for cishu in range(20):
        print "the "+str(cishu+1)+"tries for "+imageIndex
        try:
            index = random.randint(0,len(ip_list))
            ip = ip_list[index]
            print "get a proxy: "+ip
            URL = URLprefix + imageID
            html_data = requests.get(URL, headers=HEADERS, proxies={'http': 'http://'+str(ip)},timeout=60)
            html_data = html_data.text
            print "we have get the html "
            urlParser = dpchallengeImageParser()
            urlParser.feed(html_data)
        except Exception,e:
            print "error in get_pre_url"
            continue

        if urlParser.name is not None:
            #print urlParser.name
			#print str(urlParser.name[:-10])
            temp_index = len(imageID+".jpg")
            return str(urlParser.name[:-temp_index])
        print "this proxy parse html_data for per_url is  not usrful, try again!!!"
        continue


for line in fp_source:
    line_first = line.strip().split(' ')
    imageIndex_temp = line_first[0]
    imageID_temp = line_first[1]
    per_url = get_per_url(imageIndex_temp,imageID_temp)	
    if int(imageIndex_temp)>1:
        break
ip_list = get_proxy()
for line in fp_source:
    line = line.strip().split(' ')
    imageIndex = line[0]

    #print line
    # if int(imageIndex) < beginIndex:
    # 	continue
    # elif int(imageIndex) >= stopIndex:
    # 	break
    print "the request for "+imageIndex
    if os.path.isfile(os.path.join(savePath,imageIndex+'.jpg')) == True:
        print "get"+imageIndex+"success"
        continue

    #if the request times is equal 5  ,we should change our proxy!!!
	count = count +1
    if count ==5:
        print "**we need to get new proxy!!!!**"
        ip_list = []
        ip_list = get_proxy()
        count = 0

    # product an URL
    imageID = line[1]
    

    # get per_url , it can be help us find an image_url
    # per_url = "http://images.dpchallenge.com/images_challenge/1000-1999/1396/1200/Copyrighted_Image_Reuse_Prohibited_"


    #download the picture
    #url = http://images.dpchallenge.com/images_challenge/1000-1999/1396/1200/Copyrighted_Image_Reuse_Prohibited_954179.jpg

	#for each picture we will requst 10 times
    for i in range(11):
        try:
            url = per_url+imageID+".jpg"

            req = urllib2.Request(url, headers=HEADERS)
            response = urllib2.urlopen(req,timeout=30)
            page_data = response.read()
            print "DownLoad the picture "+ imageIndex+"seccess"
            fout = open(os.path.join(savePath, imageIndex + '.jpg'), 'w+b')
            fout.write(page_data)
            print "picture "+imageIndex+"has been written into file!..............."
            fout.close()
        except Exception,e:
            print "##################error in download image"
            print "The image_url is older!"
            per_url = get_per_url(imageIndex,imageID)
            print "we get useful image_url"
            print "try "+str(i+1)+" to get "+imageIndex
            continue
        break



