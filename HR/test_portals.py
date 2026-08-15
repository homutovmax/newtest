#!/usr/bin/env python3
import parse_company_portals as pcp
import sys

print('=== Alfa-Bank ===', flush=True)
alfa = pcp.parse_alfa_bank(max_items=100)
print(f'Count: {len(alfa)}', flush=True)
for v in alfa[:3]:
    print(f'  {v["Title"]} | sal={v["Salary"]} | loc={v["Location"]} | date={v["PubDate"]}', flush=True)

print(file=sys.stderr)
print('=== NorNickel ===', flush=True)
nornickel = pcp.parse_nornickel(max_pages=3)
print(f'Count: {len(nornickel)}', flush=True)
for v in nornickel[:3]:
    print(f'  {v["Title"]} | sal={v["Salary"]} | loc={v["Location"]} | date={v["PubDate"]}', flush=True)

print(file=sys.stderr)
print('=== Severstal ===', flush=True)
severstal = pcp.parse_severstal()
print(f'Count: {len(severstal)}', flush=True)
for v in severstal[:3]:
    print(f'  {v["Title"]} | loc={v["Location"]} | date={v["PubDate"]}', flush=True)
