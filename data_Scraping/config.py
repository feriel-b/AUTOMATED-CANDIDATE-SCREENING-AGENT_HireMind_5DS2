"""
Configuration du Job Scraper
Personnalisez ces paramètres selon vos besoins
"""

import os

# Configuration de base
BASE_CONFIG = {
    # URL de l'API hiring.cafe
    'HIRING_CAFE_BASE_URL': 'https://hiring.cafe',
    
    # Configuration du reverse proxy
    'PROXY_PORT': 5000,
    'PROXY_HOST': '0.0.0.0',
    
    # Paramètres de scraping
    'DEFAULT_DELAY_BETWEEN_REQUESTS': 1.0,  # secondes
    'MAX_CONCURRENT_REQUESTS': 5,
    'REQUEST_TIMEOUT': 30,  # secondes
    'MAX_RETRIES': 3,
    
    # Pagination
    'DEFAULT_JOBS_PER_PAGE': 100,
    'MAX_PAGES': None,  # None = illimité
    
    # Fichiers de sortie
    'OUTPUT_DIR': 'data',
    'JSON_FILENAME_TEMPLATE': 'jobs_hiring_cafe_{timestamp}.json',
    'CSV_FILENAME_TEMPLATE': 'jobs_hiring_cafe_{timestamp}.csv',
    'STATS_FILENAME': 'scraping_stats.json',
    'LOG_FILENAME': 'job_scraper.log',
}

# Headers HTTP personnalisés
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Filtres de recherche par défaut
DEFAULT_SEARCH_FILTERS = {
    # Exemples de filtres possibles (adaptez selon l'API)
    # 'location': 'remote',
    # 'type': 'full-time',
    # 'category': 'engineering',
    # 'experience_level': 'senior',
}

# Configuration CORS pour le reverse proxy
CORS_CONFIG = {
    'origins': '*',  # Pour développement uniquement
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
}

# Configuration du logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': ['file', 'console'],
    'log_file': 'job_scraper.log',
}

# Champs à extraire pour chaque job
JOB_FIELDS_MAPPING = {
    # Mappage des champs API vers notre structure
    'id': 'id',
    'title': 'title',
    'company': 'company.name',
    'location': 'location',
    'job_type': 'type',
    'remote': 'remote',
    'salary_min': 'salary.min',
    'salary_max': 'salary.max',
    'salary_currency': 'salary.currency',
    'description': 'description',
    'requirements': 'requirements',
    'skills': 'skills',
    'posted_date': 'posted_at',
    'application_url': 'apply_url',
    'experience_level': 'experience_level',
    'category': 'category',
}

# Variables d'environnement (optionnel)
def load_env_config():
    """Charge la configuration depuis les variables d'environnement"""
    return {
        'HIRING_CAFE_API_KEY': os.getenv('HIRING_CAFE_API_KEY'),
        'PROXY_PORT': int(os.getenv('PROXY_PORT', BASE_CONFIG['PROXY_PORT'])),
        'MAX_PAGES': int(os.getenv('MAX_PAGES')) if os.getenv('MAX_PAGES') else None,
        'OUTPUT_DIR': os.getenv('OUTPUT_DIR', BASE_CONFIG['OUTPUT_DIR']),
    }

# Configuration complète
def get_config():
    """Retourne la configuration complète"""
    config = BASE_CONFIG.copy()
    config.update(load_env_config())
    return config