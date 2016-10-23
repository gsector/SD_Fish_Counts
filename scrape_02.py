import requests
import bs4
import re
import datetime
import tqdm

def csvPrep(t):
    t = t.strip()
    t = t.replace('"','""')
    return '"' + t + '"'

# Variables/Parameters
url = 'http://sandiego.fishreports.com/dock_totals/boats.php?date='
currentDate = datetime.date.today()
numDays = 100

# Open File to write to
f = open('output.csv','a')

for dayz in tqdm(range(numDays)):    # Get Request Results
    queryDate = str(currentDate - datetime.timedelta(days=dayz))
    queryUrl = 'http://sandiego.fishreports.com/dock_totals/boats.php?date=' + queryDate
    r = requests.get(queryUrl)
    soup = bs4.BeautifulSoup(r.text,'html.parser')

    # Split by Trip Type
    for aTable in soup.find_all('div',{'class':'panel'}):
        soup2 = bs4.BeautifulSoup(str(aTable),'html.parser')

        # Check to see if parsed piece is a table with fishcounts
        try:
            countType = soup2.h2.string
        except:
            countType = ''
            continue
        
        # Split tables by boat
        for bTable in soup2.find_all('tr'):
            soup3 = bs4.BeautifulSoup(str(bTable),'html.parser')

            # Split boat's table by row + Initialize stuff
            soup3List = soup3.find_all('td')
            tripData = dict()
            tripData['date'] = queryDate

            for cTable in soup3List:
                # Get Boat and Landing
                if soup3List.index(cTable) == 0:
                    # Get Boat
                    rexp = '(?:boats)(?:.*>)(.*)(?:<\/b)'
                    tripData['boat'] = re.search(rexp,str(cTable)).group(1)
                    # Get Landing
                    rexp = '(?:landings)(?:.*>)(.*)(?:<\/a)'
                    tripData['landing'] = re.search(rexp,str(cTable)).group(1)
                
                # Get # of Anglers & Trip Type
                if soup3List.index(cTable) == 1:
                    # Anglers
                    rexp = '(?:<td>)(\d+\s+[a-zA-Z]*)(?:<br>)'
                    anglers = re.search(rexp,str(cTable)).group(1)
                    rexp = '(\d*)'
                    tripData['anglers'] = re.search(rexp,anglers).group(1).strip()

                    # Trip Type
                    rexp = '(?:<br>)(.*)(?:<\/br>|<br>)'
                    tripData['tripType'] = re.search(rexp,str(cTable)).group(1)

                # Get List of all the Fish
                if soup3List.index(cTable) == 2:
                    rexp = '<[^>]*>'
                    tripData['rawFishes'] = re.sub(rexp,'',str(cTable))

        # Get Counts by Fish
        for fish in tripData['rawFishes'].split(','):
            fish = fish.strip()
            rexp = '(\d*)'
            tripData['numFish'] =  re.search(rexp,fish).group(1).strip()
            rexp = '(\D*)'
            tripData['species'] = fish.replace(tripData['numFish'],'').strip()
            
            csvString = csvPrep(tripData['date']) \
                        + ',' + csvPrep(tripData['landing']) \
                        + ',' + csvPrep(tripData['boat']) \
                        + ',' + csvPrep(tripData['tripType']) \
                        + ',' + csvPrep(tripData['anglers']) \
                        + ',' + csvPrep(tripData['numFish']) \
                        + ',' + csvPrep(tripData['species']) \
                        + '\n'
            f.write(csvString)

f.close()