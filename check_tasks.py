import os, re
base = r'C:\_selabs\selabs\LPIC-3-Mixed-Environments'
files = [os.path.join(dp, f) for dp, _, fn in os.walk(base) for f in fn if f == 'task.md']
for f in files:
    with open(f, encoding='utf-8-sig') as fh:
        content = fh.read()
    count = len(re.findall(r'Практическая работа №', content))
    short = f.replace(base + '\\', '')
    print(f'{count} - {short}')