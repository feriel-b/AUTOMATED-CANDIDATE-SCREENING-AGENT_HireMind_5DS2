"""
HTML Scraper pour hiring.cafe
Alternative qui scrape directement le HTML au lieu d'utiliser l'API défaillante
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import re
from urllib.parse import urljoin, quote
import concurrent.futures

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    """Structure de données pour une offre d'emploi"""
    id: str
    title: str
    company: str
    location: str
    workplace_type: str
    salary: str
    description: str
    requirements: str
    skills: List[str]
    apply_url: str
    posted_date: str
    scraped_at: str

class HiringCafeHTMLScraper:
    """Scraper HTML pour hiring.cafe"""
    
    def __init__(self):
        self.session = self._create_session()
        self.base_url = "https://hiring.cafe"
        
    def _create_session(self) -> requests.Session:
        """Crée une session avec les bons headers"""
        session = requests.Session()
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
        
        return session
    
    def get_page_content(self, url: str, params: dict = None) -> str:
        """Récupère le contenu HTML d'une page"""
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de {url}: {e}")
            return ""
    
    def extract_jobs_from_search_page(self, keywords: str = "", workplace_type: str = "") -> List[Dict]:
        """Extrait les jobs depuis la page de recherche"""
        logger.info(f"Recherche avec keywords: '{keywords}', type: '{workplace_type}'")
        
        # Construction de l'URL de recherche
        params = {}
        if keywords:
            params['searchState'] = f'{{"technologyKeywords":["{keywords}"]}}'
        
        search_url = f"{self.base_url}/"
        
        html_content = self.get_page_content(search_url, params)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Recherche des scripts qui contiennent les données JSON
        jobs_data = []
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string and 'job' in script.string.lower():
                try:
                    # Recherche de patterns JSON dans le JavaScript
                    script_content = script.string
                    
                    # Pattern pour trouver des objets contenant des données de jobs
                    patterns = [
                        r'jobs["\']?\s*:\s*(\[.*?\])',
                        r'results["\']?\s*:\s*(\[.*?\])',
                        r'data["\']?\s*:\s*(\[.*?\])',
                        r'__NEXT_DATA__["\']?\s*=\s*(\{.*?\})',
                        r'window\.__STATE__\s*=\s*(\{.*?\})',
                    ]
                    
                    for pattern in patterns:
                        matches = re.search(pattern, script_content, re.DOTALL)
                        if matches:
                            try:
                                data = json.loads(matches.group(1))
                                jobs_data.extend(self._extract_jobs_from_data(data))
                            except json.JSONDecodeError:
                                continue
                                
                except Exception as e:
                    continue
        
        # Si pas de données trouvées dans les scripts, essayer le DOM
        if not jobs_data:
            jobs_data = self._extract_jobs_from_dom(soup)
        
        logger.info(f"Trouvé {len(jobs_data)} jobs dans la page")
        return jobs_data
    
    def _extract_jobs_from_data(self, data: Any) -> List[Dict]:
        """Extrait les jobs depuis une structure de données JSON"""
        jobs = []
        
        def find_jobs_recursive(obj, path=""):
            if isinstance(obj, dict):
                # Recherche de clés qui pourraient contenir des jobs
                for key, value in obj.items():
                    if key.lower() in ['jobs', 'results', 'data', 'items']:
                        if isinstance(value, list):
                            for item in value:
                                if self._is_job_object(item):
                                    jobs.append(item)
                    else:
                        find_jobs_recursive(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if self._is_job_object(item):
                        jobs.append(item)
                    else:
                        find_jobs_recursive(item, f"{path}[{i}]")
        
        find_jobs_recursive(data)
        return jobs
    
    def _is_job_object(self, obj: Any) -> bool:
        """Vérifie si un objet ressemble à une offre d'emploi"""
        if not isinstance(obj, dict):
            return False
        
        # Recherche de clés typiques d'un job
        job_keys = ['title', 'company', 'location', 'salary', 'apply_url', 'job_information']
        found_keys = sum(1 for key in job_keys if key in str(obj).lower())
        
        return found_keys >= 2
    
    def _extract_jobs_from_dom(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrait les jobs depuis le DOM HTML"""
        jobs = []
        
        # Recherche de différents sélecteurs possibles
        selectors = [
            '[data-testid*="job"]',
            '.job-listing',
            '.job-card',
            '.job-item',
            '[class*="job"]',
            '[id*="job"]'
        ]
        
        for selector in selectors:
            job_elements = soup.select(selector)
            if job_elements:
                logger.info(f"Trouvé {len(job_elements)} éléments avec sélecteur: {selector}")
                
                for element in job_elements:
                    job_data = self._parse_job_element(element)
                    if job_data:
                        jobs.append(job_data)
                break
        
        return jobs
    
    def _parse_job_element(self, element) -> Optional[Dict]:
        """Parse un élément HTML de job"""
        try:
            # Extraction des informations basiques
            title_elem = element.find(['h1', 'h2', 'h3', 'h4'], class_=lambda x: x and ('title' in x.lower() or 'job' in x.lower()))
            if not title_elem:
                title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
            
            company_elem = element.find(class_=lambda x: x and 'company' in x.lower())
            location_elem = element.find(class_=lambda x: x and ('location' in x.lower() or 'place' in x.lower()))
            salary_elem = element.find(class_=lambda x: x and ('salary' in x.lower() or 'pay' in x.lower()))
            
            # Recherche de liens
            link_elem = element.find('a', href=True)
            
            job_data = {
                'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                'location': location_elem.get_text(strip=True) if location_elem else 'N/A',
                'salary': salary_elem.get_text(strip=True) if salary_elem else 'N/A',
                'apply_url': link_elem['href'] if link_elem else '',
                'description': element.get_text(strip=True)[:500] + '...' if len(element.get_text(strip=True)) > 500 else element.get_text(strip=True),
                'scraped_from': 'DOM'
            }
            
            # Ne retourner que si on a au moins un titre
            if job_data['title'] != 'N/A':
                return job_data
                
        except Exception as e:
            logger.debug(f"Erreur lors du parsing d'un élément: {e}")
        
        return None
    
    def search_with_selenium(self, keywords: str = "", max_pages: int = 3):
        """Alternative avec Selenium (si nécessaire)"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            jobs = []
            
            try:
                # Navigation vers le site
                driver.get(self.base_url)
                
                # Attendre le chargement
                wait = WebDriverWait(driver, 10)
                
                # Si il y a un champ de recherche, l'utiliser
                if keywords:
                    try:
                        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[placeholder*="search"], input[placeholder*="keyword"]')))
                        search_input.clear()
                        search_input.send_keys(keywords)
                        
                        # Chercher et cliquer le bouton de recherche
                        search_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], button:contains("Search"), [role="button"]:contains("Search")')
                        search_button.click()
                        
                        # Attendre le chargement des résultats
                        time.sleep(3)
                    except:
                        logger.info("Pas de champ de recherche trouvé, scraping de la page principale")
                
                # Scraping des jobs visibles
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                jobs = self._extract_jobs_from_dom(soup)
                
            finally:
                driver.quit()
            
            return jobs
            
        except ImportError:
            logger.warning("Selenium non installé. Utilisez: pip install selenium")
            return []
        except Exception as e:
            logger.error(f"Erreur Selenium: {e}")
            return []

class JobProcessor:
    """Traite et nettoie les données des jobs"""
    
    @staticmethod
    def clean_job_data(job_data: Dict) -> JobListing:
        """Nettoie et structure les données d'un job"""
        try:
            # Génération d'un ID unique
            job_id = str(hash(f"{job_data.get('title', '')}{job_data.get('company', '')}"))[:10]
            
            # Nettoyage des données
            title = JobProcessor._clean_text(job_data.get('title', 'N/A'))
            company = JobProcessor._clean_text(job_data.get('company', 'N/A'))
            location = JobProcessor._clean_text(job_data.get('location', 'N/A'))
            
            # Détection du type de travail
            workplace_type = JobProcessor._detect_workplace_type(
                f"{title} {location} {job_data.get('description', '')}"
            )
            
            # URL d'application
            apply_url = job_data.get('apply_url', '')
            if apply_url and not apply_url.startswith('http'):
                apply_url = f"https://hiring.cafe{apply_url}"
            
            # Extraction des skills depuis la description
            skills = JobProcessor._extract_skills(job_data.get('description', ''))
            
            return JobListing(
                id=job_id,
                title=title,
                company=company,
                location=location,
                workplace_type=workplace_type,
                salary=JobProcessor._clean_text(job_data.get('salary', 'N/A')),
                description=job_data.get('description', '')[:1000],  # Limiter la taille
                requirements=job_data.get('requirements', 'N/A'),
                skills=skills,
                apply_url=apply_url,
                posted_date=job_data.get('posted_date', 'N/A'),
                scraped_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données: {e}")
            return None
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Nettoie un texte"""
        if not text:
            return 'N/A'
        
        # Supprime les caractères spéciaux et normalise les espaces
        cleaned = re.sub(r'\s+', ' ', text).strip()
        return cleaned if cleaned else 'N/A'
    
    @staticmethod
    def _detect_workplace_type(text: str) -> str:
        """Détecte le type de travail depuis le texte"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['remote', 'work from home', 'wfh', 'anywhere']):
            return 'remote'
        elif any(word in text_lower for word in ['hybrid', 'flexible', 'partial remote']):
            return 'hybrid'
        else:
            return 'onsite'
    
    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """Extrait les compétences techniques depuis le texte"""
        if not text:
            return []
        
        # Liste des compétences techniques communes
        tech_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'html', 'css', 'php', 'ruby', 'go', 'rust', 'c++',
            'c#', 'tensorflow', 'pytorch', 'mongodb', 'postgresql', 'redis', 'linux',
            'django', 'flask', 'spring', 'angular', 'vue.js', 'typescript', 'graphql'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in tech_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limiter à 10 compétences

def main():
    """Fonction principale"""
    print("=== HTML Scraper hiring.cafe ===")
    
    scraper = HiringCafeHTMLScraper()
    
    # Configuration
    keywords = input("Mots-clés de recherche (Enter pour tous): ").strip()
    use_selenium = input("Utiliser Selenium pour JavaScript? (y/n): ").lower() == 'y'
    
    try:
        print(f"\nDébut du scraping avec keywords: '{keywords}'")
        
        # Scraping
        if use_selenium:
            raw_jobs = scraper.search_with_selenium(keywords, max_pages=3)
        else:
            raw_jobs = scraper.extract_jobs_from_search_page(keywords)
        
        if not raw_jobs:
            print("Aucun job trouvé. Le site utilise peut-être du JavaScript complexe.")
            print("Essayez avec Selenium (y) ou vérifiez manuellement le site.")
            return
        
        # Traitement des données
        processor = JobProcessor()
        processed_jobs = []
        
        for raw_job in raw_jobs:
            job = processor.clean_job_data(raw_job)
            if job:
                processed_jobs.append(job)
        
        if processed_jobs:
            # Sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON
            json_filename = f"jobs_hiring_cafe_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump([asdict(job) for job in processed_jobs], f, ensure_ascii=False, indent=2)
            
            # CSV
            csv_filename = f"jobs_hiring_cafe_{timestamp}.csv"
            df = pd.DataFrame([asdict(job) for job in processed_jobs])
            df['skills'] = df['skills'].apply(lambda x: '; '.join(x) if x else '')
            df.to_csv(csv_filename, index=False, encoding='utf-8')
            
            # Statistiques
            stats = {
                'total_jobs': len(processed_jobs),
                'companies': len(set(job.company for job in processed_jobs)),
                'locations': len(set(job.location for job in processed_jobs)),
                'remote_jobs': len([job for job in processed_jobs if job.workplace_type == 'remote']),
                'hybrid_jobs': len([job for job in processed_jobs if job.workplace_type == 'hybrid']),
                'onsite_jobs': len([job for job in processed_jobs if job.workplace_type == 'onsite']),
            }
            
            print(f"\n=== Scraping terminé ===")
            print(f"Total jobs: {stats['total_jobs']}")
            print(f"Entreprises: {stats['companies']}")
            print(f"Localisations: {stats['locations']}")
            print(f"Remote: {stats['remote_jobs']}")
            print(f"Hybrid: {stats['hybrid_jobs']}")
            print(f"Onsite: {stats['onsite_jobs']}")
            print(f"\nFichiers créés:")
            print(f"- {json_filename}")
            print(f"- {csv_filename}")
            
        else:
            print("Aucune donnée exploitable trouvée.")
            
    except KeyboardInterrupt:
        print("\nScraping interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur durant le scraping: {e}")
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()