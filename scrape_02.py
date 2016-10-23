# import requests
# import bs4
# import re
import datetime
import tqdm
import sqlite3
import scrape_02_Modules as modz
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

# Function to prep string for CSV output
def csvPrep(t):
    t = t.strip()
    t = t.replace('"','""')
    return '"' + t + '"'

# Variables/Parameters
url = 'http://sandiego.fishreports.com/dock_totals/boats.php?date='
currentDate = datetime.date.today()
currentDate = datetime.date(2016,10,22) # Entry for testing only
lastDate = datetime.date(2000,1,1)
lastDate = datetime.date(2016,10,21) # Entry for testing only
numDays = int((currentDate - lastDate).days)

#conn = sqlite3.connect('Fish_Counts.db')
#c = conn.cursor()
#c.execute('BEGIN TRANSACTION;')

def scraper(currentDate,dayz):
    queryDate = str(currentDate - datetime.timedelta(days=dayz))
    r = modz.requestPage('http://sandiego.fishreports.com/dock_totals/boats.php?date=' + queryDate)
    if r == '':
        return None
    trips = modz.pageParser(r,str(queryDate))
    return trips

# Loop through every day
# for dayz in tqdm.tqdm(range(numDays),ncols=10):    # Get Request Results
for dayz in range(0,numDays):
    scrapeResult = scraper(currentDate,dayz)
    print(scrapeResult)
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
            # dbQuery = modz.insertQuery(tripData)
            # c.execute(str(dbQuery))

# Close connections
# f.close() # Close CSV File
#conn.commit()
#conn.close()