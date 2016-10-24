
def breakDict(tripz):
    dbFields = 'Date,Landing,Boat,Trip,Anglers,Fish,Species'
    tableName = 'Scraped_Data'
    allQueries = []
    # Break Dictionary
    for d in tripz:
        v = ''
        v += '\'' + d["date"].replace('\'','') + '\'' + ','
        v += '\'' + d["landing"].replace('\'','') + '\'' + ','
        v += '\'' + d["boat"].replace('\'','') + '\'' + ','
        v += '\'' + d["tripType"].replace('\'','') + '\'' + ','
        v += '\'' + d["anglers"].replace('\'','') + '\'' + ','
        for fish in d['fishes']:
            v2 = v + '\'' + fish["numFish"].replace('\'','') + '\'' + ','
            v2 += '\'' + fish["species"].replace('\'','') + '\''
            query = 'INSERT INTO {table} ({fields}) VALUES ({values});'.format(table=tableName,fields=dbFields,values=v2)
            allQueries.append(query)            
    return allQueries


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
            tripData['landing'] = ''
            tripData['boat'] = ''
            tripData['anglers'] = ''
            tripData['tripType'] = ''
            tripData['rawFishes'] = ''
            tripData['fishes'] = list()

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
                if soup3List.index(cTable) > 2:
                    continue
            
            try:
                if tripData['rawFishes'] != '':
                    pass
            except:
                tripData['rawFishes'] = ''
                    
            # Break up fish list into individual dictionaries in a list
            tripData['fishes'] = list()
            
            # if no fish were caught....
            if tripData['rawFishes'] == '':
                aFish = dict()
                aFish['numFish'] = ''
                aFish['species'] = ''
                tripData['fishes'].append(aFish.copy())
                continue
            
            # If Fish were caught....
            for fish in tripData['rawFishes'].split(','):
                fish = fish.strip()
                aFish = dict()
                # Get # of fish
                try:
                    rexp = '(\d*)'
                    aFish['numFish'] =  re.search(rexp,fish).group(1).strip()
                except:
                    aFish['numFish']= '?'
                # Get type/species of fish
                try:
                    aFish['species'] = fish.replace(aFish['numFish'],'').strip()
                except:
                    aFish['species'] = '?'
                # Add parsed fish data to dictionary    
                tripData['fishes'].append(aFish.copy())

            # Append each trips' data to a list of trips
            trips.append(tripData.copy())
            
        # Return list of dictionaries that contain each individual trips' data
    return trips.copy()



# Function to prep string for CSV output
def csvPrep(t):
    t = t.strip()
    t = t.replace('"','""')
    return '"' + t + '"'