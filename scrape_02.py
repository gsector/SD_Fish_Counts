import datetime
import time
import tqdm
import sqlite3
import scrape_02_Modules as modz
from multiprocessing.dummy import Pool as ThreadPool 


# So much help!!! http://chriskiehl.com/article/parallelism-in-one-line/

# Variables/Parameters
currentDate = datetime.date.today()
lastDate = datetime.date(2000,1,1)
numDays = int((currentDate - lastDate).days)
# numDays = 200 # Used for testing
numDays = 0
threadz = 12
chunkSize = threadz * 4

def scraper(url):
    r = modz.requestPage(url)
    queryDate = url[len(url)-10:]
    if r == '':
        return None
    trips = modz.pageParser(r,str(queryDate))
    queryTxt = modz.breakDict(trips.copy())
    return queryTxt

tot = 0
x = 0
# Start Loop

while x <= numDays:
    chunk = []
    for i in range(x, x + chunkSize):
        if i > numDays:
            continue
        chunk.append(i)
    x += chunkSize

    # Get Every URL within the chunk
    urlz = []
    for dayz in chunk:
        queryDate = str(currentDate - datetime.timedelta(days=dayz))
        urlz.append('http://sandiego.fishreports.com/dock_totals/boats.php?date={}'.format(queryDate))
    
    # Run Multithreading
    pool = ThreadPool(threadz)
    results = pool.map(scraper, urlz)
    pool.close()
    pool.join()
    
    # Open DB connection
    conn = sqlite3.connect('Fish_Counts.db')
    c = conn.cursor()
    c.execute('BEGIN TRANSACTION;')

    # Write data to DB
    for dbQuery in results:
        try:
            for query in dbQuery:
                c.execute(query)
        except:
            pass

    # Close connections
    conn.commit()
    conn.close()
    results.clear()