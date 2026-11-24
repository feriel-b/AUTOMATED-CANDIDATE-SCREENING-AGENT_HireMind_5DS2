import requests
import json
import time
import re # Nécessaire pour le nettoyage NLP/HTML

# --- Configuration ---
# NOUVEL API: Jobicy Remote Jobs
API_URL = "https://jobicy.com/api/v2/remote-jobs"
# Nombre d'emplois à récupérer par requête (limite d'API inférée)
#JOBS_PER_PAGE = 200 
# Limite de sécurité pour éviter une boucle infinie (ou une charge excessive)
MAX_PAGES_TO_FETCH = 5 
REQUEST_DELAY_SECONDS = 0.5  # Délai entre les requêtes de pages
OUTPUT_FILENAME = "jobicy_remote_jobs_data_structuredv2.json" 

# NOTE: L'API Jobicy utilise une requête GET simple et ne nécessite pas de payload complexe.
# Nous allons utiliser les paramètres 'count' et 'offset' pour la pagination (hypothèse).

def _extract_field(data, key, default="N/A"):
    """
    Fonction utilitaire pour extraire en toute sécurité des données d'un dictionnaire.
    Gère les valeurs manquantes, nulles ou vides.
    """
    value = data.get(key)
            
    if isinstance(value, list):
        # Convertit les listes en une seule chaîne, séparée par des virgules
        return ", ".join(filter(None, map(str, value))) if value else default
    elif value is None or (isinstance(value, str) and value.strip() == ""):
        return default
    # Pour les IDs numériques ou autres valeurs non-chaîne
    return str(value).strip() if not isinstance(value, (int, float)) else str(value)

def _clean_text(text):
    """
    Applique le nettoyage de base (NLP) : suppression HTML et normalisation des espaces.
    """
    if not text or text == "N/A":
        return "N/A"
    
    # 1. Suppression des balises HTML (e.g., <div>, <br>, <li>)
    cleaned = re.sub(r'<[^>]+>', '', text)
    
    # 2. Remplacement des multiples sauts de ligne/espaces par un seul espace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # 3. Nettoyage des espaces de début/fin
    return cleaned.strip()


def clean_and_structure_jobs(raw_jobs):
    """
    Nettoie et structure la liste des offres d'emploi brutes de Jobicy en un format JSON lisible.
    """
    print(f"\nNettoyage et structuration de {len(raw_jobs)} offres d'emploi Jobicy...")
    structured_jobs = []
    
    for job in raw_jobs:
        
        # --- 1. Extraction des Champs Simples ---
        
        title = _extract_field(job, "jobTitle")
        job_link = _extract_field(job, "url")
        location_detailed = _extract_field(job, "jobGeo")
        company_name = _extract_field(job, "companyName")
        job_id = _extract_field(job, "id")
        date_posted = _extract_field(job, "pubDate")
        
        # --- 2. Champs de Classification ---
        
        # Ce sont des emplois à distance par nature de l'API
        workplace_type = "Remote" 
        commitment_type = _extract_field(job, "jobType") # full-time, part-time, etc.
        job_category = _extract_field(job, "jobIndustry") # Marketing & Sales, Tech, etc.
        seniority_level = _extract_field(job, "jobLevel") # Senior, Mid, etc.
        
        # Utilisation de 'jobExcerpt' comme activité du rôle la plus proche
        role_activity = _clean_text(_extract_field(job, "jobExcerpt")) 
        
        # --- 3. Description Complète (Nettoyage HTML requis) ---
        description_raw = _extract_field(job, "jobDescription")
        job_description_full = _clean_text(description_raw)
        
        if job_description_full == "N/A":
            job_description_full = "N/A - No detailed description available."
        
        # --- 4. Extraction et Formatage du Salaire ---
        
        salary_min = _extract_field(job, "salaryMin")
        salary_max = _extract_field(job, "salaryMax")
        salary_currency = _extract_field(job, "salaryCurrency")
        salary_period = _extract_field(job, "salaryPeriod")
        
        salary_detailed = "N/A"
        
        if salary_min != "N/A" and salary_max != "N/A":
            salary_detailed = f"{salary_currency} {salary_min} - {salary_max} ({salary_period})"
        elif salary_min != "N/A":
            salary_detailed = f"{salary_currency} {salary_min} minimum ({salary_period})"
        elif salary_max != "N/A":
             salary_detailed = f"{salary_currency} {salary_max} maximum ({salary_period})"
             
        # Nettoyage des formats qui peuvent être restés avec "N/A"
        salary_detailed = salary_detailed.replace('N/A - N/A', 'N/A').replace(' minimum (N/A)', '').replace(' maximum (N/A)', '')


        # 5. Construction de l'objet structuré final
        structured_job = {
            # Champs principaux
            "title": title,
            "job_link": job_link, 
            "job_description_full": job_description_full, 
            "salary_detailed": salary_detailed, 
            "location_detailed": location_detailed,
            "workplace_type": workplace_type, 
            "commitment_type": commitment_type, 
            "role_activity": role_activity, 
            "job_category": job_category, 
            "seniority_level": seniority_level,
            
            # Champs de métadonnées
            "job_id": job_id,
            "company_name": company_name,
            "date_posted": date_posted,
        }
        
        structured_jobs.append(structured_job)
        
    print("Structuration terminée.")
    return structured_jobs


def fetch_jobs():
    """
    Récupère les offres d'emploi de l'API Jobicy en itérant sur des pages à l'aide des paramètres 'count' et 'offset'.
    """
    raw_jobs = []
    offset = 0
    page = 1
    
    print(f"Démarrage du scraping des offres d'emploi remote.")# """Limite par page: {JOBS_PER_PAGE}"""

    while True:
        # Construire l'URL avec les paramètres 'count' (limite) et 'offset' (saut) pour la pagination
        url = API_URL
        
        print(f"\nRequête Page {page} (Offset: {offset})...")

        try:
            # 1. Codage Défensif: Définition de l'User-Agent
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }
            
            # Requête GET simple
            response = requests.get(
                url, 
                headers=headers, 
                timeout=15 
            )
            
            # 2. Vérification de la Robustesse: Assurer le succès de la requête HTTP
            response.raise_for_status() 
            
            data = response.json()
            
            # Les résultats de l'API Jobicy se trouvent sous la clé 'jobs'
            jobs_on_page = data.get("jobs", [])
            total_count = data.get("jobCount", "N/A")

            if not jobs_on_page:
                print("Fin de la pagination: Aucune nouvelle offre trouvée.")
                break
                
            raw_jobs.extend(jobs_on_page)
            print(f"Page {page} collectée ({len(jobs_on_page)} offres). Total actuel: {len(raw_jobs)} offres.")
            
            # Affichage d'un échantillon de données brutes pour la première page uniquement
            if page == 1:
                print("\n--- ÉCHANTILLON DE DONNÉES BRUTES (JOB 0) ---")
                print(json.dumps(jobs_on_page[0], indent=2)[:1500] + "...") 
                print("----------------------------------------------------------\n")
            
            # Préparation pour la page suivante
            #offset += JOBS_PER_PAGE
            page += 1
            
            # Arrêter si la limite maximale de pages est atteinte
            if page > MAX_PAGES_TO_FETCH:
                print(f"Limite maximale de {MAX_PAGES_TO_FETCH} pages atteinte. Arrêt.")
                break
                
            # Délai entre les requêtes pour respecter le taux d'appel de l'API
            time.sleep(REQUEST_DELAY_SECONDS)

        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Erreur Réseau: {e}")
            break
        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON de la réponse.")
            print("Texte de la réponse:", response.text[:200] + "...")
            break
        except Exception as e:
            print(f"Une erreur inattendue s'est produite: {e}")
            break

    print(f"\nScraping brut terminé. Collecté {len(raw_jobs)} offres d'emploi brutes.")
    
    # Appel de la fonction de nettoyage et de structuration
    return clean_and_structure_jobs(raw_jobs)


def save_data(data, filename):
    """
    Sauvegarde la liste collectée de données d'emploi dans un fichier JSON.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Utilisation de indent=4 pour un fichier de sortie lisible
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Données structurées sauvegardées avec succès dans {filename}")
    except IOError as e:
        print(f"Erreur lors de la sauvegarde du fichier: {e}")

if __name__ == "__main__":
    job_listings = fetch_jobs()
    if job_listings:
        save_data(job_listings, OUTPUT_FILENAME)
  