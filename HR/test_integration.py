import sys
sys.path.insert(0, 'C:\\NEWTEST\\HR')
from parse_company_portals import parse_alfa_bank, parse_severstal

a = parse_alfa_bank(max_items=30)
print(f'Alfa-Bank: {len(a)}')
for v in a[:3]:
    print(f'  {v["Title"]} | {v["Salary"]} | {v["Location"]} | {v["Url"][:60]}')

s = parse_severstal()
print(f'\nSeverstal: {len(s)}')
for v in s[:3]:
    print(f'  {v["Title"]} | {v["Location"]} | {v["Url"][:60]}')
