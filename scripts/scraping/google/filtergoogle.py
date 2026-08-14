import json
filterreviews={}
with open("all_google_reviews.json", 'r') as allfile:
    d=json.load(allfile)
    s=0
    k=d.keys()
    for i in k:
        for j in k:
            if d[i]["reviews"]==[]:
                break
            if d[j]["reviews"]==[]:
                continue
            if d[i]["reviews"][0]==d[j]["reviews"][0] and i!=j:
                d[j]["reviews"]=[]
    for i in k:
        for j in d[i]["reviews"]:
            s+=1
            if s%1000==0:
                print(j)
    print(s)
    filterreviews=d

with open("filtered_google_reviews.json", 'w') as file:
    json.dump(filterreviews, file)

    
            
    
