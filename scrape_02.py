import requests
import bs4
import re
import datetime
import tqdm
import sqlite3

# Function to prep string for CSV output
def csvPrep(t):
    t = t.strip()
    t = t.replace('"','""')
    return '"' + t + '"'

# Create Insert query
def insertQuery(d):
    dbFields = 'Date,Landing,Boat,Trip,Anglers,Fish,Species'
    tableName = 'Scraped_Data'
    q = ''
    q += '\'' + d["date"].replace('\'','') + '\'' + ','
    q += '\'' + d["landing"].replace('\'','') + '\'' + ','
    q += '\'' + d["boat"].replace('\'','') + '\'' + ','
    q += '\'' + d["tripType"].replace('\'','') + '\'' + ','
    q += '\'' + d["anglers"].replace('\'','') + '\'' + ','
    q += '\'' + d["numFish"].replace('\'','') + '\'' + ','
    q += '\'' + d["species"].replace('\'','') + '\''
    
    query = 'INSERT OR REPLACE INTO {table} ({fields}) VALUES ({values});'.format(table=tableName,fields=dbFields,values=q)
    return query


# Variables/Parameters
url = 'http://sandiego.fishreports.com/dock_totals/boats.php?date='
currentDate = datetime.date.today()
lastDate = datetime.date(2000,1,1)
# lastDate = datetime.date(2016,10,20) # Entry for testing only
numDays = int((currentDate - lastDate).days)
print(str(numDays))

# Open File/Database to write to
    # f = open('output.csv','a')
conn = sqlite3.connect('Fish_Counts.db')
c = conn.cursor()
c.execute('BEGIN TRANSACTION;')

# Loop through every day
for dayz in tqdm.tqdm(range(numDays)):    # Get Request Results
    queryDate = str(currentDate - datetime.timedelta(days=dayz))
    try:
        queryUrl = 'http://sandiego.fishreports.com/dock_totals/boats.php?date=' + queryDate
        r = requests.get(queryUrl)
        soup = bs4.BeautifulSoup(r.text,'html.parser')
    except:
        print('Could not get data for date: ' + str(queryDate))
        continue

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
                    try:
                        rexp = '(?:boats)(?:.*>)(.*)(?:<\/b)'
                        tripData['boat'] = re.search(rexp,str(cTable)).group(1)
                    except:
                        tripData['boat'] = ''
                    # Get Landing
                    try:
                        rexp = '(?:landings)(?:.*>)(.*)(?:<\/a)'
                        tripData['landing'] = re.search(rexp,str(cTable)).group(1)
                    except:
                        tripData['landing'] = ''    
                    
                # Get # of Anglers & Trip Type
                if soup3List.index(cTable) == 1:
                    # Anglers
                    try:
                        rexp = '(?:<td>)(\d+\s+[a-zA-Z]*)(?:<br>)'
                        anglers = re.search(rexp,str(cTable)).group(1)
                        rexp = '(\d*)'
                        tripData['anglers'] = re.search(rexp,anglers).group(1).strip()
                    except:
                        tripData['anglers'] = ''

                    # Trip Type
                    try:
                        rexp = '(?:<br>)(.*)(?:<\/br>|<br>)'
                        tripData['tripType'] = re.search(rexp,str(cTable)).group(1)
                        # if <br> exists, get rid of it and everything after
                        try:
                            j = tripData['tripType'].index('<br>')
                            tripData['tripType'] = tripData['tripType'][:j]
                        except:
                            pass
                    except:
                        tripData['tripType']=''

                # Get List of all the Fish
                if soup3List.index(cTable) == 2:
                    try:
                        rexp = '<[^>]*>'
                        tripData['rawFishes'] = re.sub(rexp,'',str(cTable))
                    except:
                        tripData['rawFishes'] = ''

        # Get Counts by Fish
        for fish in tripData['rawFishes'].split(','):
            fish = fish.strip()
            rexp = '(\d*)'
            tripData['numFish'] =  re.search(rexp,fish).group(1).strip()
            rexp = '(\D*)'
            tripData['species'] = fish.replace(tripData['numFish'],'').strip()
            

            # Write data to csv file
            # csvString = csvPrep(tripData['date']) \
                        #+ ',' + csvPrep(tripData['landing']) \
                        #+ ',' + csvPrep(tripData['boat']) \
                        #+ ',' + csvPrep(tripData['tripType']) \
                        #+ ',' + csvPrep(tripData['anglers']) \
                        #+ ',' + csvPrep(tripData['numFish']) \
                        #+ ',' + csvPrep(tripData['species']) \
                        #+ '\n'
            # f.write(csvString)

            # Write data to DB
            dbQuery = insertQuery(tripData)
            c.execute(str(dbQuery))

# Close connections
# f.close() # Close CSV File
conn.commit()
conn.close()