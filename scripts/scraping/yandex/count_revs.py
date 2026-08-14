import os
import json
target_name="yandex"
all_files=[]
for root, dirs, files in os.walk("./"):
    for i in files:
      if target_name in i and "json" in i:
        all_files+=[i]
all_data={}
count=0
for f in all_files:
  with open(f, 'r') as file:
    data=json.load(file)
    all_data.update(data)
for court in all_data:
    count+=len(all_data[court])
print(count)
