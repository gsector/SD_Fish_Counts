
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

# Request Web Page Data
def requestPage(url):
    import requests
    try:
        r = requests.get(url)
        return r.text
    except:
        return ''

def pageParser(r,queryDate):
    import bs4
    import re

    trips = list() # Initialize list of trips
    soup = bs4.BeautifulSoup(r,'html.parser') # Initialize request data into a BeautifulSoup thing
    # Split by Trip Type
    for aTable in soup.find_all('div',{'class':'panel'}):
        soup2 = bs4.BeautifulSoup(str(aTable),'html.parser')
        
        # Check to see if parsed piece is a table with fish counts
        try:
            countType = soup2.h2.string
        except:
            continue

        # Split tables by boat
        for bTable in soup2.find_all('tr'):
            soup3 = bs4.BeautifulSoup(str(bTable),'html.parser')

            # Split boat's table by row + Initialize stuff
            soup3List = soup3.find_all('td')
            tripData = dict()
            tripData['date'] = queryDate

            # Get individual trip data
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
                    
                    # Break up fish list into individual dictionaries in a list
                    if tripData['rawFishes']:
                        # Split on comma's
                        tripData['fishes'] = list()
                        for fish in tripData['rawFishes'].split(','):
                            fish = fish.strip()
                            fishes = dict()
                            # Get # of fish
                            try:
                                rexp = '(\d*)'
                                fishes['numFish'] =  re.search(rexp,fish).group(1).strip()
                            except:
                                fishes['numFish']= '?'
                            # Get type/species of fish
                            try:
                                fishes['species'] = fish.replace(fishes['numFish'],'').strip()
                            except:
                                fishes['species'] = '?'

                            # Add parsed fish data to dictionary    
                            tripData['fishes'].append(fishes)
                    # Append each trips' data to a list of trips
                    trips.append(tripData)
            
            # Return list of dictionaries that contain each individual trips' data
        print('----------')
        return trips