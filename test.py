fish = ' 23 walruses '

fish = fish.strip()

aFish = dict()

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