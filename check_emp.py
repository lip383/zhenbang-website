import json
with open('employees.json', encoding='utf-8') as f:
    data = json.load(f)
print('员工总数:', len(data))
for e in data[:5]:
    print(e)
