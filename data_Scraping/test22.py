"""

HiringCafe Job Scraper

Advanced scraper with full job data extraction including descriptions and skills.
Features:
- Multiple pages scraping with smart pagination
- Full job descriptions and skills extraction  
- Advanced error handling and retries
- Progress tracking and logging
- Flexible search parameters
- Data cleaning and validation
- Export to multiple formats (CSV, JSON, Excel)
- Rate limiting and respectful scraping
"""

import requests
import pandas as pd
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import re
from dataclasses import dataclass, asdict
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'hiring_scraper_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    """Enhanced job listing structure"""
    url: str
    job_title: str
    company: str
    salary_min: Optional[Union[int, float]]
    salary_max: Optional[Union[int, float]]
    salary_currency: str
    compensation_transparent: bool
    remote: str
    workplace_type: str
    location: str
    seniority_level: str
    commitment: str
    apply_source: str
    description: str
    requirements_summary: str
    skills: List[str]
    job_category: str
    company_size: str
    industry: str
    posted_date: str
    scraped_at: str

class EnhancedHiringCafeScraper:
    """Enhanced scraper with advanced features"""
    
    def __init__(self, delay_between_requests: float = 2.0, max_retries: int = 3):
        self.base_url = "https://hiring.cafe/api/search-jobs"
        self.delay = delay_between_requests
        self.max_retries = max_retries
        self.session = self._create_session()
        self.jobs_collected = []
        
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Enhanced headers
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://hiring.cafe",
            "Referer": "https://hiring.cafe/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        })
        
        return session
    
    def create_search_payload(self, 
                            search_query: str = "marketing director",
                            location: str = "New York",
                            workplace_types: List[str] = ["Remote", "Hybrid", "Onsite"],
                            days_back: int = 14,
                            page: int = 0,
                            size: int = 40) -> Dict[str, Any]:
        """Create flexible search payload with European and North African locations"""
        
        # Extended location mapping including EU and North Africa
        location_configs = {
            # United States
            "New York": {
                "id": "ZhY1yZQBoEtHp_8UErzY",
                "formatted_address": "New York, United States",
                "population": 19274244,
                "address_components": [
                    {"long_name": "New York", "short_name": "NY", "types": ["administrative_area_level_1"]},
                    {"long_name": "United States", "short_name": "US", "types": ["country"]}
                ]
            },
            "California": {
                "id": "ChIJPV4oX_65j4ARFV0POl7DMCQ",
                "formatted_address": "California, United States", 
                "population": 39538223,
                "address_components": [
                    {"long_name": "California", "short_name": "CA", "types": ["administrative_area_level_1"]},
                    {"long_name": "United States", "short_name": "US", "types": ["country"]}
                ]
            },
            "Texas": {
                "id": "ChIJSTKCCzZwQIYRPN4IGI8c6xY",
                "formatted_address": "Texas, United States",
                "population": 29145505,
                "address_components": [
                    {"long_name": "Texas", "short_name": "TX", "types": ["administrative_area_level_1"]},
                    {"long_name": "United States", "short_name": "US", "types": ["country"]}
                ]
            },
            
            # European Union Countries
            "France": {
                "id": "ChIJMVd4MymgVA0R99lHx5Y__Ws",
                "formatted_address": "France",
                "population": 67413000,
                "address_components": [
                    {"long_name": "France", "short_name": "FR", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Germany": {
                "id": "ChIJa76xwh5ymkcRW-WRjmtd6HU",
                "formatted_address": "Germany", 
                "population": 83240000,
                "address_components": [
                    {"long_name": "Germany", "short_name": "DE", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Netherlands": {
                "id": "ChIJu-SH28MJxkcRnwq9_851obM",
                "formatted_address": "Netherlands",
                "population": 17441000,
                "address_components": [
                    {"long_name": "Netherlands", "short_name": "NL", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Switzerland": {
                "id": "ChIJYUHLgFq4jkcRBCGaSmw4-QA",
                "formatted_address": "Switzerland",
                "population": 8703000,
                "address_components": [
                    {"long_name": "Switzerland", "short_name": "CH", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Denmark": {
                "id": "ChIJ-1-U7rYSUkYR6osv42C_dQ8",
                "formatted_address": "Denmark",
                "population": 5831000,
                "address_components": [
                    {"long_name": "Denmark", "short_name": "DK", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Italy": {
                "id": "ChIJA9KNRIL-1BIRb15jJFz1LOI",
                "formatted_address": "Italy",
                "population": 59550000,
                "address_components": [
                    {"long_name": "Italy", "short_name": "IT", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Spain": {
                "id": "ChIJi7xhMnjjQgwR7KNoB5Qs7KY",
                "formatted_address": "Spain",
                "population": 47350000,
                "address_components": [
                    {"long_name": "Spain", "short_name": "ES", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "United Kingdom": {
                "id": "ChIJqZHHQhE7WgIReiWIMkOg-MQ",
                "formatted_address": "United Kingdom",
                "population": 67220000,
                "address_components": [
                    {"long_name": "United Kingdom", "short_name": "UK", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Belgium": {
                "id": "ChIJl5fz7WSkwUcR8bCgJb-vAQo",
                "formatted_address": "Belgium",
                "population": 11590000,
                "address_components": [
                    {"long_name": "Belgium", "short_name": "BE", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Sweden": {
                "id": "ChIJ8fA1bTmyXEYRYm-tjaLruEI",
                "formatted_address": "Sweden",
                "population": 10420000,
                "address_components": [
                    {"long_name": "Sweden", "short_name": "SE", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Norway": {
                "id": "ChIJv-VLrwMDD0YR3HxGaMs-7RI",
                "formatted_address": "Norway",
                "population": 5421000,
                "address_components": [
                    {"long_name": "Norway", "short_name": "NO", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Austria": {
                "id": "ChIJfyqdJZsHbUcRr8Hk3XvUEhA",
                "formatted_address": "Austria",
                "population": 8955000,
                "address_components": [
                    {"long_name": "Austria", "short_name": "AT", "types": ["country"]},
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            
            # North Africa
            "Morocco": {
                "id": "ChIJjbMzjGkQqw0RFetWtGCUEQ",
                "formatted_address": "Morocco",
                "population": 37458000,
                "address_components": [
                    {"long_name": "Morocco", "short_name": "MA", "types": ["country"]},
                    {"long_name": "Africa", "short_name": "AF", "types": ["continent"]}
                ]
            },
            "Tunisia": {
                "id": "ChIJ4SbrAQoMZBIR-3WBg7ND7YM",
                "formatted_address": "Tunisia",
                "population": 11818000,
                "address_components": [
                    {"long_name": "Tunisia", "short_name": "TN", "types": ["country"]},
                    {"long_name": "Africa", "short_name": "AF", "types": ["continent"]}
                ]
            },
            "Algeria": {
                "id": "ChIJ0RtumjD7dxIRFJOJzUd_CRY",
                "formatted_address": "Algeria",
                "population": 44903000,
                "address_components": [
                    {"long_name": "Algeria", "short_name": "DZ", "types": ["country"]},
                    {"long_name": "Africa", "short_name": "AF", "types": ["continent"]}
                ]
            },
            "Egypt": {
                "id": "ChIJ4drC5Sh-xhMRl7HH0cEXBkI",
                "formatted_address": "Egypt",
                "population": 104258000,
                "address_components": [
                    {"long_name": "Egypt", "short_name": "EG", "types": ["country"]},
                    {"long_name": "Africa", "short_name": "AF", "types": ["continent"]}
                ]
            },
            
            # Special regions
            "Europe": {
                "id": "ChIJ8a_c-JZYwokRYYsigX9z8p0",
                "formatted_address": "Europe",
                "population": 746400000,
                "address_components": [
                    {"long_name": "Europe", "short_name": "EU", "types": ["continent"]}
                ]
            },
            "Remote Worldwide": {
                "id": "ChIJ_9Zr9wnwxUcRTc1nf8VjR2M",
                "formatted_address": "Remote Worldwide",
                "population": 8000000000,
                "address_components": [
                    {"long_name": "World", "short_name": "WW", "types": ["global"]}
                ]
            }
        }
        
        location_config = location_configs.get(location, location_configs["New York"])
        
        payload = {
            "size": min(size, 40),  # Max 40 per API limits
            "page": page,
            "searchState": {
                "locations": [
                    {
                        "id": location_config["id"],
                        "types": ["administrative_area_level_1"],
                        "address_components": location_config["address_components"],
                        "formatted_address": location_config["formatted_address"],
                        "population": location_config["population"],
                        "workplace_types": [],
                        "options": {
                            "flexible_regions": [
                                "anywhere_in_country",
                                "anywhere_in_continent", 
                                "anywhere_in_world"
                            ]
                        }
                    }
                ],
                "workplaceTypes": workplace_types,
                "defaultToUserLocation": True,
                "userLocation": None,
                "searchQuery": search_query,
                "dateFetchedPastNDays": days_back,
                "sortBy": "default"
            }
        }
        
        return payload
    
    def scrape_jobs(self, 
                   search_query: str = "marketing director",
                   location: str = "New York", 
                   workplace_types: List[str] = ["Remote", "Hybrid", "Onsite"],
                   days_back: int = 14,
                   max_pages: Optional[int] = None,
                   max_jobs: Optional[int] = None) -> List[JobListing]:
        """
        Enhanced scraping with multiple pages and comprehensive data extraction
        
        Args:
            search_query: Job search terms
            location: Location to search in
            workplace_types: Types of workplace (Remote, Hybrid, Onsite)
            days_back: How many days back to search
            max_pages: Maximum pages to scrape (None for all)
            max_jobs: Maximum jobs to collect (None for all)
        """
        
        logger.info(f"🚀 Starting enhanced scraping for '{search_query}' in {location}")
        logger.info(f"📊 Parameters: {days_back} days back, workplace types: {workplace_types}")
        
        page = 0
        total_collected = 0
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while True:
            # Check stopping conditions
            if max_pages and page >= max_pages:
                logger.info(f"✋ Reached max pages limit: {max_pages}")
                break
                
            if max_jobs and total_collected >= max_jobs:
                logger.info(f"✋ Reached max jobs limit: {max_jobs}")
                break
            
            # Create payload for current page
            payload = self.create_search_payload(
                search_query=search_query,
                location=location,
                workplace_types=workplace_types,
                days_back=days_back,
                page=page,
                size=40
            )
            
            try:
                logger.info(f"📄 Scraping page {page + 1}...")
                
                # Make request with retry logic
                response = self.session.post(
                    self.base_url, 
                    data=json.dumps(payload),
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Error {response.status_code} on page {page}")
                    consecutive_failures += 1
                    
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(f"💥 Too many consecutive failures ({consecutive_failures}), stopping")
                        break
                    
                    # Wait longer on errors
                    time.sleep(self.delay * 2)
                    page += 1
                    continue
                
                # Parse response
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    logger.info("✅ No more jobs found, scraping complete")
                    break
                
                # Process jobs from this page
                page_jobs = []
                for job_data in results:
                    job = self._extract_job_data(job_data)
                    if job:
                        page_jobs.append(job)
                        total_collected += 1
                        
                        # Check max jobs limit
                        if max_jobs and total_collected >= max_jobs:
                            break
                
                self.jobs_collected.extend(page_jobs)
                logger.info(f"✅ Page {page + 1}: Collected {len(page_jobs)} jobs (Total: {total_collected})")
                
                # Reset failure counter on success
                consecutive_failures = 0
                
                # Respectful delay
                time.sleep(self.delay)
                page += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"🌐 Network error on page {page}: {e}")
                consecutive_failures += 1
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.error("💥 Too many network failures, stopping")
                    break
                
                time.sleep(self.delay * 3)  # Longer wait on network errors
                
            except Exception as e:
                logger.error(f"💥 Unexpected error on page {page}: {e}")
                consecutive_failures += 1
                
                if consecutive_failures >= max_consecutive_failures:
                    break
                
                time.sleep(self.delay * 2)
        
        logger.info(f"🎉 Scraping complete! Collected {len(self.jobs_collected)} total jobs")
        return self.jobs_collected
    
    def _extract_job_data(self, job_raw: Dict[str, Any]) -> Optional[JobListing]:
        """Extract and clean job data with enhanced fields"""
        
        try:
            # Main data sources
            job_data = job_raw.get("v5_processed_job_data", {})
            company_data = job_raw.get("v5_processed_company_data", {})
            job_info = job_raw.get("job_information", {})
            
            # Extract skills from various sources
            skills = self._extract_skills(job_data, job_info)
            
            # Clean and format data
            job = JobListing(
                url=job_raw.get("apply_url", ""),
                job_title=self._clean_text(job_info.get("title", "")),
                company=self._clean_text(
                    job_data.get("company_name") or 
                    company_data.get("name") or 
                    ""
                ),
                
                # Enhanced salary handling
                salary_min=self._parse_salary(job_data.get("yearly_min_compensation")),
                salary_max=self._parse_salary(job_data.get("yearly_max_compensation")),
                salary_currency=job_data.get("salary_currency", "USD"),
                compensation_transparent=job_data.get("is_compensation_transparent", False),
                
                # Workplace info
                remote="yes" if str(job_data.get("workplace_type", "")).lower() == "remote" else "no",
                workplace_type=job_data.get("workplace_type", ""),
                location=self._clean_text(job_data.get("formatted_workplace_location", "")),
                
                # Job details
                seniority_level=job_data.get("seniority_level", ""),
                commitment=", ".join(job_data.get("commitment", [])),
                apply_source=job_raw.get("source", ""),
                
                # Enhanced content
                description=self._clean_description(job_info.get("description", "")),
                requirements_summary=self._clean_text(job_data.get("requirements_summary", "")),
                skills=skills,
                job_category=job_data.get("job_category", ""),
                
                # Company info
                company_size=company_data.get("size_range", ""),
                industry=company_data.get("industry", ""),
                
                # Dates
                posted_date=self._format_date(job_data.get("estimated_publish_date_millis")),
                scraped_at=datetime.now().isoformat()
            )
            
            return job
            
        except Exception as e:
            logger.error(f"❌ Error extracting job data: {e}")
            return None
    
    def _extract_skills(self, job_data: Dict, job_info: Dict) -> List[str]:
        """Extract skills from multiple sources"""
        skills = set()
        
        # From role activities
        role_activities = job_data.get("role_activities", [])
        if isinstance(role_activities, list):
            skills.update(role_activities)
        
        # From description and requirements using keyword matching
        text_content = (
            job_info.get("description", "") + " " + 
            job_data.get("requirements_summary", "")
        ).lower()
        
        # Common tech skills to extract
        tech_skills = [
            # Programming languages
            "python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust", "swift",
            "typescript", "kotlin", "scala", "r", "matlab", "sql",
            
            # Frameworks & Libraries
            "react", "angular", "vue.js", "node.js", "django", "flask", "spring", "laravel",
            "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
            
            # Tools & Platforms
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github",
            "jira", "confluence", "slack", "figma", "adobe", "salesforce", "hubspot",
            
            # Marketing specific
            "google analytics", "google ads", "facebook ads", "linkedin ads", "seo", "sem",
            "content marketing", "email marketing", "social media", "crm", "marketing automation",
            "a/b testing", "conversion optimization", "brand management", "digital marketing",
            "performance marketing", "growth hacking", "influencer marketing"
        ]
        
        for skill in tech_skills:
            if skill in text_content:
                skills.add(skill.title())
        
        return sorted(list(skills))[:20]  # Limit to top 20 skills
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and clean up
        cleaned = re.sub(r'\s+', ' ', str(text)).strip()
        return cleaned
    
    def _clean_description(self, description: str) -> str:
        """Clean job description"""
        if not description:
            return ""
        
        # Remove HTML tags if present
        cleaned = re.sub(r'<[^>]+>', '', str(description))
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Truncate if too long (for CSV compatibility)
        if len(cleaned) > 2000:
            cleaned = cleaned[:1997] + "..."
        
        return cleaned
    
    def _parse_salary(self, salary: Any) -> Optional[Union[int, float]]:
        """Parse salary value"""
        if not salary:
            return None
        
        try:
            return float(salary)
        except (ValueError, TypeError):
            return None
    
    def _format_date(self, timestamp_ms: Any) -> str:
        """Format timestamp to readable date"""
        if not timestamp_ms:
            return ""
        
        try:
            timestamp_sec = int(timestamp_ms) / 1000
            date_obj = datetime.fromtimestamp(timestamp_sec)
            return date_obj.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return ""
    
    def save_results(self, 
                    filename_prefix: str = "hiringcafe_jobs",
                    formats: List[str] = ["csv", "json", "excel"]) -> Dict[str, str]:
        """Save results in multiple formats"""
        
        if not self.jobs_collected:
            logger.warning("⚠️ No jobs to save")
            return {}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}
        
        # Convert to DataFrame
        df = pd.DataFrame([asdict(job) for job in self.jobs_collected])
        
        # Clean skills column for CSV (convert list to string)
        df['skills'] = df['skills'].apply(lambda x: '; '.join(x) if x else '')
        
        try:
            # Save CSV
            if "csv" in formats:
                csv_filename = f"{filename_prefix}_{timestamp}.csv"
                df.to_csv(csv_filename, index=False, encoding="utf-8")
                saved_files["csv"] = csv_filename
                logger.info(f"💾 Saved CSV: {csv_filename}")
            
            # Save JSON (with original list format for skills)
            if "json" in formats:
                json_filename = f"{filename_prefix}_{timestamp}.json"
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump([asdict(job) for job in self.jobs_collected], 
                            f, ensure_ascii=False, indent=2)
                saved_files["json"] = json_filename
                logger.info(f"💾 Saved JSON: {json_filename}")
            
            # Save Excel
            if "excel" in formats:
                excel_filename = f"{filename_prefix}_{timestamp}.xlsx"
                with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Jobs', index=False)
                    
                    # Add summary sheet
                    summary_df = self._create_summary_df(df)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                saved_files["excel"] = excel_filename
                logger.info(f"💾 Saved Excel: {excel_filename}")
            
        except Exception as e:
            logger.error(f"❌ Error saving files: {e}")
        
        return saved_files
    
    def _create_summary_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create summary statistics"""
        summary_data = []
        
        summary_data.append(["Total Jobs", len(df)])
        summary_data.append(["Unique Companies", df['company'].nunique()])
        summary_data.append(["Unique Locations", df['location'].nunique()])
        summary_data.append(["Remote Jobs", len(df[df['remote'] == 'yes'])])
        summary_data.append(["Jobs with Salary Info", len(df[df['salary_min'].notna()])])
        
        # Top companies
        top_companies = df['company'].value_counts().head(5)
        summary_data.append(["", ""])
        summary_data.append(["Top Companies", "Count"])
        for company, count in top_companies.items():
            summary_data.append([company, count])
        
        # Top locations
        top_locations = df['location'].value_counts().head(5)
        summary_data.append(["", ""])
        summary_data.append(["Top Locations", "Count"])
        for location, count in top_locations.items():
            summary_data.append([location, count])
        
        return pd.DataFrame(summary_data, columns=["Metric", "Value"])
    
    def scrape_multiple_regions(self,
                               search_query: str = "IT",
                               regions: List[str] = None,
                               days_back: int = 30,
                               max_pages_per_region: int = 20,
                               workplace_types: List[str] = ["Remote", "Hybrid", "Onsite"]) -> Dict[str, List[JobListing]]:
        """
        Scrape jobs from multiple European and North African regions automatically
        
        Args:
            search_query: Job search terms
            regions: List of regions to scrape (None for all supported regions)
            days_back: How many days back to search
            max_pages_per_region: Max pages per region
            workplace_types: Types of workplace
        
        Returns:
            Dictionary with region as key and jobs list as value
        """
        
        # Default regions if none specified
        if regions is None:
            regions = [
                # European Union
                "France", "Germany", "Netherlands", "Switzerland", "Denmark",
                "Italy", "Spain", "United Kingdom", "Belgium", "Sweden", 
                "Norway", "Austria",
                
                # North Africa
                "Morocco", "Tunisia", "Algeria", "Egypt",
                
                # Global
                "Europe", "Remote Worldwide"
            ]
        
        logger.info(f"🌍 Starting multi-region scraping for '{search_query}'")
        logger.info(f"📍 Regions to scrape: {', '.join(regions)}")
        
        all_results = {}
        total_jobs_collected = 0
        
        for i, region in enumerate(regions):
            logger.info(f"🎯 [{i+1}/{len(regions)}] Scraping {region}...")
            
            try:
                # Clear previous jobs for this region
                region_jobs = []
                
                # Scrape this region
                jobs = self.scrape_jobs(
                    search_query=search_query,
                    location=region,
                    workplace_types=workplace_types,
                    days_back=days_back,
                    max_pages=max_pages_per_region
                )
                
                # Store results for this region
                region_jobs = jobs.copy()
                all_results[region] = region_jobs
                total_jobs_collected += len(region_jobs)
                
                logger.info(f"✅ {region}: {len(region_jobs)} jobs collected")
                
                # Reset jobs_collected for next region
                self.jobs_collected = []
                
                # Respectful delay between regions
                if i < len(regions) - 1:  # Don't wait after last region
                    logger.info(f"⏳ Waiting 5 seconds before next region...")
                    time.sleep(5)
                    
            except Exception as e:
                logger.error(f"❌ Error scraping {region}: {e}")
                all_results[region] = []
                continue
        
        # Combine all jobs into main collection
        combined_jobs = []
        for region, jobs in all_results.items():
            # Add region info to each job
            for job in jobs:
                job.location = f"{job.location} ({region})" if job.location else region
                combined_jobs.append(job)
        
        self.jobs_collected = combined_jobs
        
        logger.info(f"🎉 Multi-region scraping complete!")
        logger.info(f"📊 Total jobs collected: {total_jobs_collected} across {len(regions)} regions")
        
        return all_results
        """Get scraping statistics"""
        if not self.jobs_collected:
            return {}
        
        df = pd.DataFrame([asdict(job) for job in self.jobs_collected])
        
        return {
            "total_jobs": len(df),
            "unique_companies": df['company'].nunique(),
            "unique_locations": df['location'].nunique(),
            "remote_jobs": len(df[df['remote'] == 'yes']),
            "jobs_with_salary": len(df[df['salary_min'].notna()]),
            "top_companies": df['company'].value_counts().head(10).to_dict(),
            "top_locations": df['location'].value_counts().head(10).to_dict(),
            "workplace_types": df['workplace_type'].value_counts().to_dict(),
            "seniority_levels": df['seniority_level'].value_counts().to_dict(),
            "scraped_at": datetime.now().isoformat()
        }

def main():
    """Enhanced main function with multi-region scraping"""
    
    print("🌍 Enhanced HiringCafe Job Scraper - Multi-Region Edition")
    print("=" * 60)
    
    # Choose scraping mode
    print("\nSelect scraping mode:")
    print("1. Single region (interactive)")
    print("2. Multiple regions (EU + North Africa) - Auto")
    print("3. Custom regions")
    
    mode = input("Enter choice (1/2/3, default: 2): ").strip()
    if not mode:
        mode = "2"
    
    # Initialize scraper
    scraper = EnhancedHiringCafeScraper(delay_between_requests=2.0)
    
    try:
        start_time = datetime.now()
        
        if mode == "1":
            # Single region mode (original)
            search_query = input("Enter job search query (default: 'IT'): ").strip()
            if not search_query:
                search_query = "IT"
            
            location = input("Enter location (default: 'Europe'): ").strip()
            if not location:
                location = "Europe"
            
            days_back = input("Days back to search (default: 30): ").strip()
            days_back = int(days_back) if days_back.isdigit() else 30
            
            max_pages = input("Max pages to scrape (default: 20): ").strip()
            max_pages = int(max_pages) if max_pages.isdigit() else 20
            
            jobs = scraper.scrape_jobs(
                search_query=search_query,
                location=location,
                days_back=days_back,
                max_pages=max_pages,
                workplace_types=["Remote", "Hybrid", "Onsite"]
            )
            
        elif mode == "2":
            # Auto multi-region mode
            search_query = input("Enter job search query (default: 'IT'): ").strip()
            if not search_query:
                search_query = "IT"
            
            print(f"\n🚀 Starting automatic multi-region scraping for '{search_query}'")
            print("📍 Regions: EU countries + North Africa + Remote opportunities")
            
            # Auto scrape all regions
            regional_results = scraper.scrape_multiple_regions(
                search_query=search_query,
                days_back=30,
                max_pages_per_region=10  # Reasonable limit per region
            )
            
        elif mode == "3":
            # Custom regions mode
            search_query = input("Enter job search query (default: 'IT'): ").strip()
            if not search_query:
                search_query = "IT"
            
            print("\nAvailable regions:")
            available_regions = [
                "France", "Germany", "Netherlands", "Switzerland", "Denmark",
                "Italy", "Spain", "United Kingdom", "Belgium", "Sweden",
                "Norway", "Austria", "Morocco", "Tunisia", "Algeria", "Egypt",
                "Europe", "Remote Worldwide"
            ]
            
            for i, region in enumerate(available_regions, 1):
                print(f"{i:2d}. {region}")
            
            selected = input("\nEnter region numbers (comma-separated, e.g., 1,2,3): ").strip()
            
            if selected:
                try:
                    indices = [int(x.strip()) - 1 for x in selected.split(',')]
                    custom_regions = [available_regions[i] for i in indices if 0 <= i < len(available_regions)]
                except:
                    custom_regions = ["Europe"]  # Fallback
            else:
                custom_regions = ["Europe"]
            
            regional_results = scraper.scrape_multiple_regions(
                search_query=search_query,
                regions=custom_regions,
                days_back=30,
                max_pages_per_region=15
            )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if scraper.jobs_collected:
            # Save results with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save in all formats
            saved_files = scraper.save_results(
                filename_prefix=f"hiringcafe_global_{search_query.replace(' ', '_')}",
                formats=["csv", "json", "excel"]
            )
            
            # Display comprehensive statistics
            stats = scraper.get_stats()
            
            print("\n" + "=" * 60)
            print("🌍 GLOBAL SCRAPING RESULTS")
            print("=" * 60)
            print(f"🎯 Total Jobs Collected: {stats['total_jobs']}")
            print(f"🏢 Unique Companies: {stats['unique_companies']}")
            print(f"📍 Unique Locations: {stats['unique_locations']}")
            print(f"🏠 Remote Jobs: {stats['remote_jobs']}")
            print(f"💰 Jobs with Salary Info: {stats['jobs_with_salary']}")
            print(f"⏱️  Total Scraping Duration: {duration}")
            
            print(f"\n📁 Files Saved:")
            for format_type, filename in saved_files.items():
                print(f"   📄 {format_type.upper()}: {filename}")
            
            print(f"\n🏆 Top 5 Companies:")
            for company, count in list(stats['top_companies'].items())[:5]:
                print(f"   • {company}: {count} jobs")
            
            print(f"\n🌍 Top 5 Regions/Locations:")
            for location, count in list(stats['top_locations'].items())[:5]:
                print(f"   • {location}: {count} jobs")
            
            print(f"\n💼 Workplace Types:")
            for wtype, count in stats['workplace_types'].items():
                print(f"   • {wtype}: {count} jobs")
            
            # Regional breakdown if multi-region scraping
            if mode in ["2", "3"] and 'regional_results' in locals():
                print(f"\n📊 Regional Breakdown:")
                for region, jobs in regional_results.items():
                    print(f"   🌍 {region}: {len(jobs)} jobs")
            
            print(f"\n🎉 Success! All data saved and ready for analysis.")
            
        else:
            print("❌ No jobs found. The search might be too specific or the regions might not have matching jobs.")
            print("💡 Try:")
            print("   - Broader search terms (e.g., 'developer' instead of 'senior python developer')")
            print("   - Different regions") 
            print("   - Longer time period (more days back)")
    
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
        if scraper.jobs_collected:
            print(f"💾 Saving {len(scraper.jobs_collected)} jobs collected so far...")
            scraper.save_results(filename_prefix="interrupted_scrape")
    except Exception as e:
        logger.error(f"💥 Scraping failed: {e}")
        print(f"❌ Error: {e}")
        print("💡 Check the log file for detailed error information.")

if __name__ == "__main__":
    main()