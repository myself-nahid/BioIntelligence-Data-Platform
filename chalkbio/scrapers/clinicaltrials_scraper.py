import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "https://clinicaltrials.gov/api/query/study_fields"
# In production, use a more robust rate limiter.
# This simple sleep is for demonstration.
RATE_LIMIT_DELAY_SECONDS = 0.05  # 1 request per 50ms = 20 req/sec

def fetch_recent_trials(pages: int = 1):
    """
    Scrapes the latest trial data from ClinicalTrials.gov.

    In a real application, this would handle pagination, data cleaning,
    and upserting records into the 'investigators' and 'trials' tables.
    """
    logger.info("Starting scrape of ClinicalTrials.gov...")
    all_trials = []

    for page in range(1, pages + 1):
        params = {
            "expr": "AREA[LastUpdatePostDate]RANGE[01/01/2020, MAX]",
            "fields": "NCTId,LeadSponsorName,OverallStatus,CentralContactName,PrimaryCompletionDate",
            "min_rnk": (page - 1) * 1000 + 1,
            "max_rnk": page * 1000,
            "fmt": "json"
        }
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json().get("StudyFieldsResponse", {}).get("StudyFields", [])
            if not data:
                logger.info("No more data found. Ending scrape.")
                break

            all_trials.extend(data)
            logger.info(f"Successfully fetched page {page}, found {len(data)} trials.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from ClinicalTrials.gov on page {page}: {e}")
            break  # Stop on error
        finally:
            time.sleep(RATE_LIMIT_DELAY_SECONDS)

    logger.info(f"Scrape complete. Total trials fetched: {len(all_trials)}")
    return all_trials

if __name__ == "__main__":
    recent_trials = fetch_recent_trials(pages=2) # Fetch first 2000 results
    # print(recent_trials[:5])