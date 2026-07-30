# ConsiderJobScrapper
# Consider Job Scraper & Airtable Sync

An automated pipeline designed to scrape real-time job listings from Consider and push deduplicated records directly into the team's shared **Airtable Master Database**.

---

## 📋 Prerequisites

Before setting up the project, make sure you have the following installed on your machine:
* **Python 3.8+**
* **Git**

---

## 🚀 Quick Start Guide (Team Onboarding)

Follow these steps to set up and run the scraper on your local machine.

### 1. Clone the Repository

Open your terminal and clone the repository:

```bash
git clone [https://github.com/shraddhaborah/ConsiderJobScrapper.git](https://github.com/shraddhaborah/ConsiderJobScrapper.git)
cd ConsiderJobScrapper

##For security reasons, API keys are not committed to the GitHub repository. You need to create a local .env file containing the required Airtable Personal Access Token (PAT).

##Run this command in your terminal (or manually create a .env file in the project root):
echo 'AIRTABLE_PAT="YOUR_ACTUAL_AIRTABLE_PAT_HERE"' > .env

##Ensure the runner script has execution permissions:
chmod +x run_scraper.sh

##Execute the automated bash runner:
./run_scraper.sh

🛠️ What the Automation Script (run_scraper.sh) Does
When you execute ./run_scraper.sh, it handles everything end-to-end:

Virtual Environment Setup: Creates a local Python virtual environment (venv) if one doesn't exist yet.

Dependency Management: Automatically installs and updates all required packages listed in requirements.txt.

Execution: Launches job_tracker_Airtable.py to scrape open positions from Consider.

Deduplication: Cross-references listings with seen_jobs.json to categorize jobs as NEW or EXISTING.

Airtable Upsert: Syncs records directly into the shared Airtable base without creating duplicates.

📊 Database & Integration Specs
Target Base: appQRa3hTnAIpEE2R

Target Table: tblfhhTHshZCJWZnn (JobScrapper)

Primary Key: Job ID (Used to prevent duplicate records on batch upserts)

📁 Repository Structure

ConsiderJobScrapper/
├── job_tracker_Airtable.py  # Primary Python scraping & Airtable sync logic
├── run_scraper.sh           # One-click execution script for macOS / Linux
├── requirements.txt         # Python package dependencies
├── .gitignore               # Excludes secrets, caches, and local files
└── README.md                # Project documentation

⚠️ Troubleshooting & Support
Permission denied when running ./run_scraper.sh:

Run chmod +x run_scraper.sh to grant execution rights to your user.

Airtable Sync Errors:

Verify that your local .env file exists and contains a valid AIRTABLE_PAT.
