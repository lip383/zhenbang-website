import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取员工数据
with open('employees.json', encoding='utf-8') as f:
    employees = json.load(f)

# 生成内嵌JS数组字符串
lines = []
for e in employees:
    gender_emoji = '\\u{1F469}' if e['gender'] == '女' else '\\u{1F468}'
    job = e.get('job') or '员工'
    name = e['name']
    # 用unicode转义避免编码问题
    lines.append(f'  {{name:"{name}",role:"{job}",gender:"{e["gender"]}"}}\n')

# 生成不含emoji的数组，emoji在JS里动态处理
simple_lines = []
for e in employees:
    job = e.get('job') or '员工'
    name = e['name']
    gender = e['gender']
    simple_lines.append(f'  {{name:"{name}",role:"{job}",gender:"{gender}"}}')

js_array = 'const ALL_EMPLOYEES = [\n' + ',\n'.join(simple_lines) + '\n];'

with open('employees_embedded.js', 'w', encoding='utf-8') as f:
    f.write(js_array)

print(f"OK: {len(employees)} employees", file=sys.stdout)
print(simple_lines[0], file=sys.stdout)
print(simple_lines[1], file=sys.stdout)
