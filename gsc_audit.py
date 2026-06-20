import json, csv, os
from datetime import date, timedelta
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests

KEY  = '/home/chubert/omni-builder/sites/site_MHC/key.json'
SITE = 'https://mikes-house-clearance.co.uk/'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
OUT  = '/home/chubert/omni-builder/sites/site_MHC/gsc_audit'
os.makedirs(OUT, exist_ok=True)

creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
creds.refresh(Request())
HEADERS = {'Authorization': f'Bearer {creds.token}'}
BASE = 'https://www.googleapis.com/webmasters/v3'

END   = date.today()
START = END - timedelta(days=90)

def search(payload):
    r = requests.post(f'{BASE}/sites/{requests.utils.quote(SITE, safe="")}/searchAnalytics/query',
                      headers=HEADERS, json=payload)
    return r.json().get('rows', [])

def save_csv(filename, rows, fieldnames):
    path = f'{OUT}/{filename}'
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f'  Saved: {path} ({len(rows)} rows)')

print('\n=== GSC FULL AUDIT: mikes-house-clearance.co.uk ===')
print(f'Period: {START} to {END}\n')

# ── 1. TOP QUERIES ──────────────────────────────────────────────────────────
print('[1/7] Top queries by impressions...')
rows = search({'startDate': str(START), 'endDate': str(END),
               'dimensions': ['query'], 'rowLimit': 1000})
queries = [{'query': r['keys'][0], 'clicks': r['clicks'],
            'impressions': r['impressions'],
            'ctr': round(r['ctr']*100, 2),
            'position': round(r['position'], 1)} for r in rows]
queries.sort(key=lambda x: x['impressions'], reverse=True)
save_csv('1_top_queries.csv', queries, ['query','clicks','impressions','ctr','position'])

# ── 2. TOP PAGES ─────────────────────────────────────────────────────────────
print('[2/7] Top pages by clicks...')
rows = search({'startDate': str(START), 'endDate': str(END),
               'dimensions': ['page'], 'rowLimit': 1000})
pages = [{'page': r['keys'][0], 'clicks': r['clicks'],
          'impressions': r['impressions'],
          'ctr': round(r['ctr']*100, 2),
          'position': round(r['position'], 1)} for r in rows]
pages.sort(key=lambda x: x['clicks'], reverse=True)
save_csv('2_top_pages.csv', pages, ['page','clicks','impressions','ctr','position'])

# ── 3. ZERO-CLICK OPPORTUNITIES (high impressions, low ctr) ─────────────────
print('[3/7] Zero-click opportunities...')
opps = [q for q in queries if q['impressions'] >= 100 and q['ctr'] < 2.0]
opps.sort(key=lambda x: x['impressions'], reverse=True)
save_csv('3_zero_click_opportunities.csv', opps, ['query','clicks','impressions','ctr','position'])

# ── 4. QUICK WINS (position 5-20, decent impressions) ────────────────────────
print('[4/7] Quick win keywords (pos 5-20)...')
wins = [q for q in queries if 5 <= q['position'] <= 20 and q['impressions'] >= 50]
wins.sort(key=lambda x: x['impressions'], reverse=True)
save_csv('4_quick_wins.csv', wins, ['query','clicks','impressions','ctr','position'])

# ── 5. QUERIES BY DEVICE ─────────────────────────────────────────────────────
print('[5/7] Performance by device...')
rows = search({'startDate': str(START), 'endDate': str(END),
               'dimensions': ['device'], 'rowLimit': 10})
devices = [{'device': r['keys'][0], 'clicks': r['clicks'],
            'impressions': r['impressions'],
            'ctr': round(r['ctr']*100, 2),
            'position': round(r['position'], 1)} for r in rows]
save_csv('5_by_device.csv', devices, ['device','clicks','impressions','ctr','position'])

# ── 6. QUERIES BY COUNTRY ────────────────────────────────────────────────────
print('[6/7] Performance by country...')
rows = search({'startDate': str(START), 'endDate': str(END),
               'dimensions': ['country'], 'rowLimit': 50})
countries = [{'country': r['keys'][0], 'clicks': r['clicks'],
              'impressions': r['impressions'],
              'ctr': round(r['ctr']*100, 2),
              'position': round(r['position'], 1)} for r in rows]
countries.sort(key=lambda x: x['clicks'], reverse=True)
save_csv('6_by_country.csv', countries, ['country','clicks','impressions','ctr','position'])

# ── 7. PAGE + QUERY MATRIX (top 500) ─────────────────────────────────────────
print('[7/7] Page + query matrix...')
rows = search({'startDate': str(START), 'endDate': str(END),
               'dimensions': ['page','query'], 'rowLimit': 500})
matrix = [{'page': r['keys'][0], 'query': r['keys'][1],
           'clicks': r['clicks'], 'impressions': r['impressions'],
           'ctr': round(r['ctr']*100, 2),
           'position': round(r['position'], 1)} for r in rows]
matrix.sort(key=lambda x: x['clicks'], reverse=True)
save_csv('7_page_query_matrix.csv', matrix, ['page','query','clicks','impressions','ctr','position'])

# ── SUMMARY REPORT ────────────────────────────────────────────────────────────
total_clicks      = sum(q['clicks'] for q in queries)
total_impressions = sum(q['impressions'] for q in queries)
avg_ctr           = round(total_clicks / total_impressions * 100, 2) if total_impressions else 0
avg_pos           = round(sum(q['position'] for q in queries) / len(queries), 1) if queries else 0

summary = f"""
=== GSC AUDIT SUMMARY ===
Site      : {SITE}
Period    : {START} to {END}

OVERALL (last 90 days)
  Total clicks      : {total_clicks:,}
  Total impressions : {total_impressions:,}
  Avg CTR           : {avg_ctr}%
  Avg position      : {avg_pos}

OPPORTUNITIES
  Zero-click queries (imp>=100, ctr<2%) : {len(opps)}
  Quick-win keywords (pos 5-20)         : {len(wins)}

FILES SAVED TO: {OUT}/
  1_top_queries.csv
  2_top_pages.csv
  3_zero_click_opportunities.csv
  4_quick_wins.csv
  5_by_device.csv
  6_by_country.csv
  7_page_query_matrix.csv
"""
print(summary)
with open(f'{OUT}/SUMMARY.txt', 'w') as f:
    f.write(summary)
print(f'  Saved: {OUT}/SUMMARY.txt')
