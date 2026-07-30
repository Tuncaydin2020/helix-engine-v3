"""
HELIX PubMed Client
Search and retrieve biomedical literature from PubMed.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

class PubMedClient:
    """Client for interacting with the PubMed API."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def search(self, query: str, max_results: int = 20) -> List[str]:
        """Search PubMed and return PMIDs."""
        url = f"{self.BASE_URL}esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"⚠️  PubMed search failed: {e}")
            return []
    
    def fetch_details(self, pmid: str) -> Dict:
        """Fetch article details by PMID."""
        url = f"{self.BASE_URL}efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            
            # Extract title
            title_elem = root.find(".//ArticleTitle")
            title = title_elem.text if title_elem else "No title"
            
            # Extract abstract
            abstract_elem = root.find(".//AbstractText")
            abstract = abstract_elem.text if abstract_elem else ""
            
            # Extract authors
            authors = []
            for author in root.findall(".//Author"):
                last = author.find("LastName")
                first = author.find("ForeName")
                if last is not None:
                    name = last.text
                    if first is not None:
                        name = f"{first.text} {name}"
                    authors.append(name)
            
            # Extract journal
            journal_elem = root.find(".//Title")
            journal = journal_elem.text if journal_elem else "Unknown"
            
            # Extract date
            date_elem = root.find(".//PubDate")
            date = ""
            if date_elem:
                year = date_elem.find("Year")
                month = date_elem.find("Month")
                if year is not None:
                    date = year.text
                    if month is not None:
                        date = f"{date}-{month.text}"
            
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors[:10],
                "journal": journal,
                "date": date,
            }
            
        except Exception as e:
            print(f"⚠️  Failed to fetch PMID {pmid}: {e}")
            return {
                "pmid": pmid,
                "title": f"Failed to fetch: {pmid}",
                "abstract": "",
                "authors": [],
                "journal": "Unknown",
                "date": "",
            }
        