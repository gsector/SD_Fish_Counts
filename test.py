import tqdm

numDays = 888
chunkSize = 888


x = 0
chunks = []
for x in tqdm(range(numDays)):
    chunkers = []
    for i in range(x, x + chunkSize):
        if i > numDays:
            continue
        chunkers.append(i)
    chunks.append(chunkers)
    x = x + chunkSize

print(len(chunks))
print(chunks[0])
