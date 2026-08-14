import json
with open("as_data010.json", 'r') as file:
    fr = json.load(file)
    count=0
    for i in fr:
        for j in fr[i]:
            count+=1
print(count)