# originally intended to scrape for counts by boat and day in history.
# Currently can scrape a single page, but it is a summary and not by boat.
# Found a new url to work with and working on it in scrape_02.py

import requests
import bs4
import lxml
import re
url = 'http://sandiego.fishreports.com/landings/landing_details.php?' + \
                    'landing_id=23&month={}&year={}#historicals'.format(10,2016)

r = requests.get(url)
soup = bs4.BeautifulSoup(r.text, 'lxml')

countsTable = soup.html.body.find_all('table',{'class':'scale-table'})
soup = bs4.BeautifulSoup(str(countsTable[0]),'lxml')
tableRecords = soup.table.tbody.find_all('tr')

for record in tableRecords:
    soup = bs4.BeautifulSoup(str(record),'lxml')
    soup = bs4.BeautifulSoup(str(soup.html.body.tr),'lxml')
    dataList = soup.find_all('td')
    if len(dataList) == 4:
        fishDate = re.search('(?:>)(.*)(?:<)',str(dataList[0])).group(1)
        numBoats =  re.search('(?:>)([0-9]*)(?:<)',str(dataList[1])).group(1)
        anglers = re.search('(?:>)([0-9]*)(?:<)',str(dataList[2])).group(1)
        allFish = re.search('(?:>)(.*)(?:<)',str(dataList[3])).group(1)
        
        # print(str(item4))
        print('----')
        print('*****')

    

f = open('sample.txt','w')
f.write(str(soup))
f.close()