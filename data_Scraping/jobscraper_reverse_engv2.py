import requests
import json
import time
import re # Nécessaire pour le nettoyage NLP/HTML

# --- Configuration ---
API_URL = "https://hiring.cafe/api/search-jobs"
MAX_PAGES_TO_SCRAPE = 100  # Limite pour le respect des ressources serveur.
REQUEST_DELAY_SECONDS = 1.5  # Délai crucial pour l'éthique de scraping.
OUTPUT_FILENAME = "hiring_cafe_jobs_data_structuredv3.json" # Nom du fichier pour les données structurées et nettoyées

# Le payload de base avec des filtres pour cibler les offres riches en détails.
BASE_PAYLOAD = {
    "size": 40,  
    "page": 0,   
    "searchState": {
        "locations": [],
        "workplaceTypes": ["Remote", "Hybrid", "Onsite"],
        "commitmentTypes": ["Full Time", "Part Time", "Contract", "Internship", "Temporary", "Seasonal", "Volunteer"],
        "seniorityLevel": ["No Prior Experience Required", "Entry Level", "Mid Level", "Senior Level"],
        # CIBLAGE : Requête de titre de poste pour trouver des offres bien détaillées.
        "jobTitleQuery": "", 
        "dateFetchedPastNDays": 121,
        "searchQuery": "", 
        "sortBy": "default",
        # Reste des filtres par défaut (conservés pour la compatibilité)
        "defaultToUserLocation": False, "userLocation": None, "physicalEnvironments": ["Office", "Outdoor", "Vehicle", "Industrial", "Customer-Facing"], "physicalLaborIntensity": ["Low", "Medium", "High"], "physicalPositions": ["Sitting", "Standing"], "oralCommunicationLevels": ["Low", "Medium", "High"], "computerUsageLevels": ["Low", "Medium", "High"], "cognitiveDemandLevels": ["Low", "Medium", "High"], "currency": {"label": "Any", "value": None}, "frequency": {"label": "Any", "value": None}, "minCompensationLowEnd": None, "minCompensationHighEnd": None, "maxCompensationLowEnd": None, "maxCompensationHighEnd": None, "restrictJobsToTransparentSalaries": False, "calcFrequency": "Yearly", "associatesDegreeFieldsOfStudy": [], "excludedAssociatesDegreeFieldsOfStudy": [], "bachelorsDegreeFieldsOfStudy": [], "excludedBachelorsDegreeFieldsOfStudy": [], "mastersDegreeFieldsOfStudy": [], "excludedMastersDegreeFieldsOfStudy": [], "doctorateDegreeFieldsOfStudy": [], "excludedDoctorateDegreeFieldsOfStudy": [], "associatesDegreeRequirements": [], "bachelorsDegreeRequirements": [], "mastersDegreeRequirements": [], "doctorateDegreeRequirements": [], "licensesAndCertifications": [], "excludedLicensesAndCertifications": [], "excludeAllLicensesAndCertifications": False, "roleTypes": ["Individual Contributor", "People Manager"], "roleYoeRange": [0, 20], "excludeIfRoleYoeIsNotSpecified": False, "managementYoeRange": [0, 20], "excludeIfManagementYoeIsNotSpecified": False, "securityClearances": ["None", "Confidential", "Secret", "Top Secret", "Top Secret/SCI", "Public Trust", "Interim Clearances", "Other"], "languageRequirements": [], "excludedLanguageRequirements": [], "languageRequirementsOperator": "OR", "excludeJobsWithAdditionalLanguageRequirements": False, "airTravelRequirement": ["None", "Minimal", "Moderate", "Extensive"], "landTravelRequirement": ["None", "Minimal", "Moderate", "Extensive"], "morningShiftWork": [], "eveningShiftWork": [], "overnightShiftWork": [], "weekendAvailabilityRequired": "Doesn't Matter", "holidayAvailabilityRequired": "Doesn't Matter", "overtimeRequired": "Doesn't Matter", "onCallRequirements": ["None", "Occasional (once a month or less)", "Regular (once a week or more)"], "benefitsAndPerks": [], "applicationFormEase": [], "companyNames": [], "excludedCompanyNames": [], "usaGovPref": None, "industries": [], "excludedIndustries": [], "companyKeywords": [], "companyKeywordsBooleanOperator": "OR", "excludedCompanyKeywords": [], "hideJobTypes": [], "encouragedToApply": [], "hiddenCompanies": [], "user": None, "searchModeSelectedCompany": None, "departments": [], "restrictedSearchAttributes": [], "technologyKeywordsQuery": "", "requirementsKeywordsQuery": "", "companyPublicOrPrivate": "all", "latestInvestmentYearRange": [None, None], "latestInvestmentSeries": [], "latestInvestmentAmount": None, "latestInvestmentCurrency": [], "investors": [], "excludedInvestors": [], "isNonProfit": "all", "companySizeRanges": [], "minYearFounded": None, "maxYearFounded": None, "excludedLatestInvestmentSeries": []
    }
}

def _extract_field(data, keys, default="N/A"):
    """
    Fonction utilitaire pour extraire en toute sécurité des données d'un dictionnaire potentiellement imbriqué.
    Gère les valeurs manquantes, nulles ou les types de données listes.
    """
    # Si 'keys' est une chaîne, le convertir en liste pour l'itération
    if isinstance(keys, str):
        keys = [keys]
    
    value = data
    for key in keys:
        # Tente l'accès par clé de dictionnaire
        if isinstance(value, dict) and key in value:
            value = value[key]
        # Tente l'accès par index de liste (si la clé est un nombre)
        elif isinstance(value, list) and key.isdigit():
             try:
                 value = value[int(key)]
             except IndexError:
                 return default
        else:
            return default
            
    if isinstance(value, list):
        # Convertit les listes en une seule chaîne, séparée par des virgules
        return ", ".join(filter(None, map(str, value))) if value else default
    elif value is None or (isinstance(value, str) and value.strip() == ""):
        return default
    
    return str(value).strip()

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

def _get_value_from_paths(job, paths, default="N/A"):
    """
    Tente d'extraire une valeur en utilisant une liste ordonnée de chemins (listes de clés) 
    et retourne la première valeur non-"N/A" trouvée. Ceci gère l'inconsistence de l'API.
    """
    for path_keys in paths:
        # path_keys est une liste de clés, e.g., ["v5_processed_job_data", "workplace_type"]
        value = _extract_field(job, path_keys)
        if value != "N/A":
            return value
    return default


def clean_and_structure_jobs(raw_jobs):
    """
    Nettoie, applique le NLP et structure la liste des offres d'emploi brutes en un format JSON lisible.
    Mise à jour pour gérer les incohérences de l'API en vérifiant plusieurs chemins (fallback extraction).
    """
    print(f"\nNettoyage et structuration de {len(raw_jobs)} offres d'emploi...")
    structured_jobs = []
    
    for job in raw_jobs:
        
        # --- 1. Extraction des Champs Simples (avec robustesse) ---
        
        # Titre (vérifie la racine, puis l'objet d'information, puis le titre normalisé v5)
        title = _get_value_from_paths(job, [
            ["title"], 
            ["job_information", "title"], 
            ["v5_processed_job_data", "core_job_title"], 
        ])
        
        # Type de Lieu de Travail (Workplace Type)
        workplace_type = _get_value_from_paths(job, [
            ["workplaceType"],
            ["v5_processed_job_data", "workplace_type"]
        ])
        
        # Type de Contrat (Commitment Type)
        commitment_type = _get_value_from_paths(job, [
            ["commitmentType"],
            ["job_information", "Job Type"], # Ex: 'Part Time ' dans l'objet d'information
            ["v5_processed_job_data", "commitment"], # Array Ex: ['Part Time']
        ])
        
        # Niveau d'Ancienneté (Seniority Level)
        seniority_level = _get_value_from_paths(job, [
            ["seniorityLevel"],
            ["v5_processed_job_data", "seniority_level"]
        ])
        
        # Catégorie d'Emploi (Job Category)
        job_category = _get_value_from_paths(job, [
            ["industries"], 
            ["v5_processed_job_data", "job_category"]
        ])
        
        # Activité/Département (Role Activity)
        role_activity = _get_value_from_paths(job, [
            ["departments"], 
            ["v5_processed_job_data", "role_activities"] # Array
        ])
        
        # Lieu (Location)
        location_detailed = _get_value_from_paths(job, [
            ["location"],
            ["job_information", "City"], # Ex: Anaheim (besoin de plus de contexte)
            ["v5_processed_job_data", "formatted_workplace_location"]
        ])

        # Company Name
        company_name = _get_value_from_paths(job, [
            ["companyName"],
            ["v5_processed_company_data", "name"]
        ])

        # Job ID
        job_id = _get_value_from_paths(job, [
            ["id"],
            ["jobId"]
        ])

        # Job Link
        job_link = _get_value_from_paths(job, [
            ["apply_url"], # Lien d'application (plus pertinent)
            ["link"]
        ])

        # Date Posted
        date_posted = _extract_field(job, "postedAt")


        # --- 2. Extraction du Salaire (Compensation) ---
        
        # Tente l'extraction structurée standard
        compensation_low = _extract_field(job, ["compensation", "lowEnd", "amount"])
        compensation_high = _extract_field(job, ["compensation", "highEnd", "amount"])
        currency = _extract_field(job, ["compensation", "currency", "label"])
        frequency = _extract_field(job, ["compensation", "frequency", "label"])
        
        salary_string = "N/A"
        
        if compensation_low != "N/A" and compensation_high != "N/A":
            salary_string = f"{currency} {compensation_low} - {compensation_high} ({frequency})"
        elif compensation_low != "N/A":
             salary_string = f"{currency} {compensation_low} minimum ({frequency})"
             
        # Si le salaire structuré est N/A, tente d'extraire les détails du bloc de texte Compensation Details
        if salary_string == "N/A":
            compensation_details_text = _extract_field(job, ["job_information", "Compensation Details"])
            if compensation_details_text != "N/A":
                 # Nettoyage et utilisation du texte brut (le modèle d'embedding peut le gérer)
                 salary_string = _clean_text(compensation_details_text)
                 
        # --- 3. Construction du champ de description composite riche: job_description_full ---
        details_blocks = []

        # Fonction utilitaire pour créer un bloc de contenu si les données existent (applique le nettoyage NLP)
        def create_content_block_for_desc(header, paths):
            # Tente plusieurs chemins pour la robustesse des données (si elles sont fractionnées)
            content = _get_value_from_paths(job, paths)
            
            # Application du nettoyage NLP/HTML
            cleaned_content = _clean_text(content)
            
            if cleaned_content != "N/A":
                return f"{header}: {cleaned_content}"
            return None

        # A. Bloc Description & Mission (Description de l'entreprise, Mission, Description du poste)
        desc_content_list = [
            create_content_block_for_desc("COMPANY DESCRIPTION", [["companyDescription"], ["v5_processed_company_data", "tagline"]]),
            create_content_block_for_desc("MISSION", [["mission"]]),
            create_content_block_for_desc("JOB DESCRIPTION", [["description"], ["job_information", "description"]]),
        ]
        desc_content = "\n".join(filter(None, desc_content_list))
        if desc_content:
            details_blocks.append(("COMPANY & JOB DETAILS (Description, Mission)", desc_content))

        # B. Bloc Exigences et Profil (Compétences, Profil Recherché, Qualifications)
        req_content_list = [
            create_content_block_for_desc("SKILLS NEEDED", [["skills"], ["v5_processed_job_data", "requirements_summary"]]),
            create_content_block_for_desc("PROFILE & GENERAL REQUIREMENTS", [["requirements"], ["job_information", "Basic Qualifications"], ["job_information", "Preferred Qualifications"]]),
            create_content_block_for_desc("BACHELOR'S QUALIFICATIONS", [["bachelorsDegreeRequirements"], ["v5_processed_job_data", "bachelors_degree_requirement"]]),
            create_content_block_for_desc("MASTER'S QUALIFICATIONS", [["mastersDegreeRequirements"], ["v5_processed_job_data", "masters_degree_requirement"]]),
        ]
        req_content = "\n".join(filter(None, req_content_list))
        if req_content:
            details_blocks.append(("PROFILE, SKILLS, & QUALIFICATIONS", req_content))

        # C. Bloc Exigences Physiques (Physical Requirements)
        physical_reqs_list = [
            create_content_block_for_desc("Environments", [["physicalEnvironments"], ["v5_processed_job_data", "workplace_physical_environment"]]),
            create_content_block_for_desc("Labor Intensity", [["physicalLaborIntensity"], ["v5_processed_job_data", "physical_labor_intensity"]]),
            create_content_block_for_desc("Positions", [["physicalPositions"], ["v5_processed_job_data", "physical_position"]]),
        ]
        
        # Garde seulement le contenu nettoyé du bloc
        physical_reqs_text = "\n".join(filter(None, [req.split(': ', 1)[1] for req in physical_reqs_list if req]))
        if physical_reqs_text:
            details_blocks.append(("PHYSICAL REQUIREMENTS", physical_reqs_text))


        # D. Bloc Info Supplémentaire et Avantages (Additional Information, Benefits)
        benefit_content_list = [
            create_content_block_for_desc("BENEFITS & PERKS (Additional Information)", [["benefitsAndPerks"], ["job_information", "Additional Information"]]),
            create_content_block_for_desc("EQUAL OPPORTUNITY COMMITMENT", [["commitmentToEqualOpportunity"]]),
        ]
        benefit_content = "\n".join(filter(None, benefit_content_list))
        if benefit_content:
            details_blocks.append(("BENEFITS & EEO", benefit_content))

        
        # Concaténation finale pour le champ de description complet
        full_description_parts = []
        for header, content in details_blocks:
            full_description_parts.append(f"--- {header} ---\n\n{content}")

        full_description_text = "\n\n".join(full_description_parts).strip()
        if not full_description_text:
            full_description_text = "N/A - No detailed description available."


        # 4. Construction de l'objet structuré final
        structured_job = {
            # Champs principaux (demandés explicitement)
            "title": title,
            "job_link": job_link, 
            "job_description_full": full_description_text, # Le champ riche et NETTOYÉ (NLP) pour l'embedding
            "salary_detailed": salary_string, # Format: "USD 50000 - 80000 (Yearly)" ou extrait de 'Compensation Details'
            "location_detailed": location_detailed,
            "workplace_type": workplace_type, # Remote, Hybrid, Onsite
            "commitment_type": commitment_type, # Full Time, Part Time, Contract, etc.
            "role_activity": role_activity, # Rôle activité / Département
            "job_category": job_category, # Catégorie d'emploi / Industrie
            "seniority_level": seniority_level,
            
            # Champs de métadonnées
            "job_id": job_id,
            "company_name": company_name,
            "date_posted": date_posted,
        }
        
        structured_jobs.append(structured_job)
        
    print("Structuration terminée. Les données sont prêtes pour l'entraînement de votre agent RH et modèle d'embedding.")
    return structured_jobs


def fetch_jobs():
    """
    Paginates through the /api/search-jobs endpoint to collect all job listings.
    """
    raw_jobs = []
    page = 0
    
    # Clonage du payload pour modifier le numéro de page en toute sécurité
    payload = BASE_PAYLOAD.copy()

    print(f"Démarrage du scraping des offres d'emploi depuis {API_URL}")
    print(f"Ciblage d'un maximum de {MAX_PAGES_TO_SCRAPE} pages.")

    while page < MAX_PAGES_TO_SCRAPE:
        payload["page"] = page
        
        try:
            # 1. Codage Défensif: Définition de l'User-Agent pour simuler une requête de navigateur.
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Content-Type": "application/json"
            }
            
            print(f"Récupération de la page {page}...")
            
            # L'API nécessite une requête POST avec le payload de recherche complexe
            response = requests.post(
                API_URL, 
                json=payload, 
                headers=headers, 
                timeout=15 # Augmentation du timeout pour plus de robustesse
            )
            
            # 2. Vérification de la Robustesse: Assurer le succès de la requête HTTP
            response.raise_for_status() 
            
            data = response.json()
            
            # Les résultats de l'API se trouvent sous la clé 'results'
            jobs_on_page = data.get("results", [])
            total_hits = data.get("totalHits", 0)

            if not jobs_on_page:
                print(f"La page {page} n'a retourné aucune offre. Fin des résultats supposée.")
                break
                
            raw_jobs.extend(jobs_on_page)
            print(f"Ajout réussi de {len(jobs_on_page)} offres. Total collecté: {len(raw_jobs)} / Total sur le serveur: {total_hits}")

            # --- DÉBOGAGE: Affichage de la structure de données brute (utile pour vérifier les clés manquantes) ---
            if page == 0 and jobs_on_page:
                print("\n--- ÉCHANTILLON DE DONNÉES BRUTES (JOB 0) ---")
                # Afficher le JSON brut du premier job (limité à 1500 caractères pour la console)
                print(json.dumps(jobs_on_page[0], indent=2)[:1500] + "...") 
                print("----------------------------------------------------------\n")
            # -----------------------------------------------------------

            # Préparation de l'itération suivante
            page += 1
            
            # 3. Pratique Éthique: Introduction d'un délai pour respecter les limites de débit
            if page < MAX_PAGES_TO_SCRAPE:
                 print(f"Pause de {REQUEST_DELAY_SECONDS} secondes...")
                 time.sleep(REQUEST_DELAY_SECONDS)

        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP à la page {page}: {e}")
            if response.status_code == 429:
                print("Reçu 429 (Trop de Requêtes). Veuillez augmenter REQUEST_DELAY_SECONDS.")
            break
        except requests.exceptions.RequestException as e:
            print(f"Erreur Réseau à la page {page}: {e}")
            break
        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON de la réponse de la page {page}.")
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
