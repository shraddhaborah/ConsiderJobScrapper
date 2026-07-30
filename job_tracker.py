import json
import os
import time
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Local tracking file
JOBS_FILE = "seen_jobs.json"

# Google Services Configurations
SERVICE_ACCOUNT_FILE = 'service_account.json'

# Extracted Spreadsheet ID from your open "Consider Jobs Live Tracker" Google Sheet
SPREADSHEET_ID = '1O2dNSopcGMW1X0HpoY196cmLFC4HJJVEite6k8uUfaw'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def get_or_create_worksheet(spreadsheet, title, rows=1000, cols=20):
    """
    Retrieves a worksheet by name, or creates it if it doesn't exist.
    """
    try:
        return spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        print(f"[+] Worksheet '{title}' not found. Creating it...")
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def update_google_sheet(jobs_batch, seen_jobs_dict):
    """
    Updates the Google Sheet tabs:
    1. 'Latest Scrape': Replaced with current run batch.
    2. 'Master Database': Full historical record of all scraped jobs.
    """
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[!] {SERVICE_ACCOUNT_FILE} missing. Skipping Google Sheets update.")
        return

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)

        headers = ["Job ID", "Status", "Title", "Company", "Location", "Posted At", "URL", "Scraped At"]

        # --- Tab 1: Latest Scrape ---
        latest_ws = get_or_create_worksheet(spreadsheet, "Latest Scrape")
        latest_ws.clear()
        
        latest_rows = [headers]
        for job in jobs_batch:
            latest_rows.append([
                job["job_id"], job["status"], job["title"], 
                job["company"], job["location"], job["posted_at"], 
                job["url"], job["scraped_at"]
            ])
        latest_ws.update('A1', latest_rows)

        # --- Tab 2: Master Database ---
        master_ws = get_or_create_worksheet(spreadsheet, "Master Database")
        master_ws.clear()

        master_rows = [headers]
        for job_id, job in seen_jobs_dict.items():
            master_rows.append([
                job.get("job_id", job_id),
                job.get("status", "EXISTING"),
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("posted_at", ""),
                job.get("url", ""),
                job.get("scraped_at", "")
            ])
        master_ws.update('A1', master_rows)

        print(f"[✓] Google Sheet successfully updated live!")

    except Exception as e:
        print(f"[!] Google Sheets sync failed: {e}")


def fetch_jobs_from_endpoint():
    """
    Fetches job listings directly using your active Consider session details.
    """
    cookies = {
        '_ga': 'GA1.1.1547770298.1775849110',
        'AWSALBAPP-1': '_remove_',
        'AWSALBAPP-2': '_remove_',
        'AWSALBAPP-3': '_remove_',
        '__zlcmid': '1XpoYMtZOnGHeON',
        '_ga_JB478S76GL': 'GS2.1.s1784212708$o3$g0$t1784212708$j60$l0$h0',
        'session': 'eyJmbGFzaCI6e30sImNzcmZTZWNyZXQiOiI0Ql9Pb19BSnRPYXVRTWpaZ3hVeXJnVW8iLCJ3b3Jrc3BhY2VJZCI6ImMwMTBlYTMzLWI2YmEtNGI5MC04ZjZkLTZjOGVkZWE4ZTE3NSIsInBhc3N3b3JkbGVzcyI6IjlhMjY5NTI2LWZhNzAtNDU1OS1iMGU2LWU2YTY4M2MxMWNhMyIsInN0YXJ0ZWQiOjE3ODQ4MjU2MDUyMjl9',
        'session.sig': 'QrNpGCXbed7oyyvbqm7kq2gB1Sk',
        'AWSALBAPP-0': '_remove_',
        '_ga_KKGEK8HDTN': 'GS2.1.s1785353494$o34$g1$t1785353745$j60$l0$h0',
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://consider.com',
        'priority': 'u=1, i',
        'referer': 'https://consider.com/jobs/search/all?order=time',
        'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
        'x-csrf-token': 'dUcVSS4s-AqxGlCBOmiYQVB9cMV3SOD7nbNA',
    }

    json_data = {
        'meta': {
            'size': 50,  # Number of jobs to return per pull
        },
        'board': {
            'id': 'initialized',
            'isParent': True,
        },
        'query': {
            'order': 'time',
        },
    }

    try:
        response = requests.post(
            'https://consider.com/api/search-boards-jobs',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return data.get("jobs") or data.get("results") or data.get("items") or []
            elif isinstance(data, list):
                return data
        else:
            print(f"[!] Server returned HTTP Status {response.status_code}")
    except Exception as e:
        print(f"[!] Error making request: {e}")
    return []


def load_seen_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_seen_jobs(jobs_dict):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs_dict, f, indent=4)


def scrape_and_classify_jobs():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraping all jobs...")
    
    seen_jobs = load_seen_jobs()
    current_jobs = fetch_jobs_from_endpoint()
    
    if not current_jobs:
        print("[-] No jobs retrieved from endpoint.")
        return

    all_scraped_batch = []
    new_count = 0
    existing_count = 0

    for job in current_jobs:
        job_id = str(job.get("id") or job.get("url") or job.get("title"))
        
        is_new = job_id not in seen_jobs
        status = "NEW" if is_new else "EXISTING"

        job_data = {
            "job_id": job_id,
            "status": status,
            "title": job.get("title") or job.get("name"),
            "company": job.get("company") or job.get("companyName"),
            "location": job.get("location"),
            "posted_at": job.get("posted_at") or job.get("createdAt"),
            "url": job.get("url"),
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        all_scraped_batch.append(job_data)

        if is_new:
            new_count += 1
            seen_jobs[job_id] = job_data
        else:
            existing_count += 1

    save_seen_jobs(seen_jobs)

    print(f"[✓] Scraped {len(all_scraped_batch)} total job(s) -> ({new_count} NEW, {existing_count} EXISTING)")

    # Directly updates your live Google Sheet dashboard tabs
    update_google_sheet(all_scraped_batch, seen_jobs)


if __name__ == "__main__":
    scrape_and_classify_jobs()