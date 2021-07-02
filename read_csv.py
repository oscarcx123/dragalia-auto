import csv

total_dragon = 40
each_type_cnt = total_dragon / 5

res = []
with open('龙玉.csv') as csvfile:
    rd = csv.reader(csvfile)
    for row in rd:
        res.append([row[0], row[1]])

res.pop(0)
temp = []
elements = ["flame_data", "water_data", "wind_data", "light_data", "shadow_data"]
edx = 0

for idx in range(len(res)):
    temp.append(res[idx])
    if idx % each_type_cnt == 7:
        print(f"self.{elements[edx]} = {temp}")
        edx += 1
        temp = []