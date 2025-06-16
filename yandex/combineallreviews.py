import json
all_reviews={}
s=0
with open("alldata.json",'r') as file:
    d=json.load(file)
    k=d.keys()
    for i in k:
        all_reviews[i]={"type":"ordinary", "reviews":[]}
        for j in d[i]:
            all_reviews[i]["reviews"]+=[j]
            s+=1
with open("ms_all_data.json",'r') as file:
    d=json.load(file)
    k=d.keys()
    for i in k:
        all_reviews[i]={"type":"world", "reviews":[]}
        for j in d[i]:
            all_reviews[i]["reviews"]+=[j]
            s+=1
with open("as_data0120.json",'r') as file:
    d=json.load(file)
    k=d.keys()
    for i in k:
        all_reviews[i]={"type":"arbitrage", "reviews":[]}
        for j in d[i]:
            all_reviews[i]["reviews"]+=[j]
            s+=1
print(s)
for i in all_reviews.keys():
    for j in all_reviews.keys():
        if len(all_reviews[i]["reviews"])==0:
            break
        if len(all_reviews[j]["reviews"])==0:
            continue
        if all_reviews[i]["reviews"]==all_reviews[j]["reviews"] and i!=j:
            all_reviews[j]["reviews"]=[]
count=0
for i in all_reviews.keys():
    for j in all_reviews[i]["reviews"]:
        count+=1
with open("all_court_reviews.json", "w") as finalfile:
    json.dump(all_reviews,finalfile)
