import requests
import bs4
import re
import datetime
import xmltodict

# Variables/Parameters
queryDate = '2016-10-05'
url = 'http://sandiego.fishreports.com/dock_totals/boats.php?date=' + queryDate

# Get Request Results
r = requests.get(url)
soup = bs4.BeautifulSoup(r.text,'html.parser')

# Split by Trip Type
for aTable in soup.find_all('div',{'class':'panel'}):
    soup2 = bs4.BeautifulSoup(str(aTable),'html.parser')

    # Check to see if parsed piece is a table with fishcounts
    try:
        countType = soup2.h2.string
    except:
        print('Not a fish count table')
        countType = ''
        continue
    
    # Split tables by boat
    for bTable in soup2.find_all('tr'):
        soup3 = bs4.BeautifulSoup(str(bTable),'html.parser')

        # Split boat's table by row
        soup3List = soup3.find_all('td')
        for cTable in soup3List:
            # Get Boat and Landing
            if soup3List.index(cTable) == 0:
                # Get Boat
                rexp = '(?:boats)(?:.*>)(.*)(?:<\/b)'
                boat = re.search(rexp,str(cTable)).group(1)
                # Get Landing
                rexp = '(?:landings)(?:.*>)(.*)(?:<\/a)'
                landing = re.search(rexp,str(cTable)).group(1)
            # Get # of Anglers & Trip Type
            if soup3List.index(cTable) == 1:
                rexp = '(?:<td>)(\d+\s+[a-zA-Z]*)(?:<br>)'
                anglers = re.search(rexp,str(cTable)).group(1)
                rexp = '(?:<br>)(.*)(?:<\/br>|<br>)'
                tripType = re.search(rexp,str(cTable)).group(1)
            # Get Fishes
            if soup3List.index(cTable) == 2:
                rexp = '<[^>]*>'
                fishes = re.sub(rexp,'',str(cTable))
    # Print Output
    print('-----  BOAT TOTAL  -----')
    print('  Date: ' + queryDate)
    print('  Landing: ' + landing)
    print('  Boat: ' + boat)
    print('  Trip: ' + tripType)
    print('  Anglers: ' + anglers)
    # Print Fishes
    for fish in fishes.split(','):
        rexp = '(\d*)'
        fishInt = re.search(rexp,fishes).group(1)
        rexp = '(\D.*)'
        fishType = re.search(rexp,fishes).group(1)
        print('  Fish: ' + fish)
                
                