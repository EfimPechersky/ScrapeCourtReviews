import json
count=0
with open("yandex_aspects.json", 'r') as file:
    data=json.load(file)
    for court in data:
        for rev in data[court]:
            count+=len(rev)
with open("google_aspects.json", 'r') as file:
    data=json.load(file)
    for court in data:
        for rev in data[court]:
            count+=len(rev)
print(count)
