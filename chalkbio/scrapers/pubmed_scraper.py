import requests
import time
import logging
from ..core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
API_KEY = settings.PUBMED_API_KEY
# 3 req/sec without API key, 10 req/sec with.
RATE_LIMIT_DELAY_SECONDS = 0.1 if API_KEY else 0.34

def find_coauthors(investigator_name: str):
    """
    Finds publication IDs for a given author on PubMed.
    A full implementation would use these IDs to fetch publication details
    and build the collaboration network.
    """
    logger.info(f"Searching PubMed for author: {investigator_name}")
    params = {
        "db": "pubmed",
        "term": f"{investigator_name}[Author]",
        "retmax": 100,
        "retmode": "json",
        "api_key": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        logger.info(f"Found {len(id_list)} publications for {investigator_name}.")
        return id_list
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from PubMed for '{investigator_name}': {e}")
        return []
    finally:
        time.sleep(RATE_LIMIT_DELAY_SECONDS)

if __name__ == "__main__":
    publications = find_coauthors("Fauci AS")
    # print(publications)