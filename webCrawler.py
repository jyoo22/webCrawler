#!/usr/bin/python3
import ssl
import os
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from queue import *

#make urls check against the  keywords

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl.create_default_https_context = _create_unverified_https_context

def get_page_content(url):
    try:
        html_response_text = urlopen(url).read()
        page_content = html_response_text.decode('utf-8')
        return page_content
    except Exception as e:
        return None


def clean_title(title):
    invalid = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for c in invalid:
        title=title.replace(c, '')
    return title

def get_urls(soup):
    links = soup.find_all('a')
    urls=[]
    for link in links:
        urls.append(link.get('href'))
    return urls

def is_url_valid(url):
    if url is None:
        return False
    if re.search('#', url):
        return False
    match = re.search('^/wiki/', url)
    if match:
        return True
    else:
        return False

def reformat_url(url):
    match=re.search('^/wiki/', url)
    if match:
        return "https://en.wikipedia.org" + url
    else:
        return url

def save(text, path):
    f=open(path, 'w', encoding = 'utf-8', errors = 'ignore')
    f.write(text)
    f.close()

#Initialization
seedURL = []
q = Queue()
visitedURL = []
pageCounter = 0
savedURL = []
keywords = []

#for keyword count
count=1

topic = input('Please Enter Topic:')

while(True):
    word = input('Please enter keyword Or 123 to stop entering keywords: ' )
    if (word != "123"):
        keywords.append(word)
        print('Current Length: ' + str(count))
        count += 1
    else:
        break;

s1 = input('Enter first seed URL: ')
s2 = input('Enter second seed URL: ')

seedURL.append(s1)
seedURL.append(s2)

for url in seedURL:
    q.put(url)

###############################
while q.empty() == False:
    url = q.get()
    #print(url)
    pageContent = get_page_content(url)
    #print(pageContent)
    
    ##Gucci
    if not pageContent:
        continue

    termCount = 0 
    soup = BeautifulSoup(pageContent, 'html.parser')
    page_text = soup.get_text()

    #print(page_text)

    tCount=0
    for word in keywords:
        #c = page_text.count(" " + word + " ")
        #print(word + ": " + str(c))

        #only checks of it is included NOT how many times
        print(url)
        print("word: " + word + ": " + str(re.search(word, page_text, re.I)))
        if re.search(word, page_text, re.I):
            tCount += 1

            #print(str(word) + ": " + str(tCount))
            #print("tCount: " + str(tCount) + " Word: " + word)
            if tCount >= 2:
                title = soup.title.string
                title = clean_title(title)
                    
                
                myPath = os.path.join("/home/jeff/Documents/NJIT/is392/Crawler/creepyCrawlingPages", title + '.html')
                #myPath = os.path.join("/home/jeff/Documents/NJIT/is392/Crawler/creepyCrawlingPages", title + '.html')
                save(pageContent, myPath)
                
                
                savedURL.append(url)
                pageCounter += 1

                print('Page # {}: {}'.format(pageCounter, url))
                break
    if pageCounter >= 10:
        break
#########################################
    #here we go#
    inner_urls = get_urls(soup)
    for inner_url in inner_urls:
        if is_url_valid(inner_url):
            inner_url = reformat_url(inner_url)
            if inner_url not in savedURL:
                q.put(inner_url)
                savedURL.append(inner_url)
                
f = open("crawled_urls.txt", "w")
i = 1
for url in savedURL:
    f.write(str(i) + ': ' + url + '\n')
    i += 1
f.close()

