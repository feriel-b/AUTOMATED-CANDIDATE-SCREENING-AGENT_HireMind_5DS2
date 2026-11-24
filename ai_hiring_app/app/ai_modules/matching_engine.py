from typing import List

def calculate_match_score(candidate_skills: List[str], job_skills: List[str]) -> int:
    """
    Calculates a simple match score based on the percentage of job skills
    found in the candidate's skills.
    """
    # Ensure inputs are sets for efficient intersection
    candidate_skills_set = set(skill.lower() for skill in candidate_skills)
    job_skills_set = set(skill.lower() for skill in job_skills)

    if not job_skills_set:
        return 0
    
    common_skills = candidate_skills_set.intersection(job_skills_set)
    
    score = (len(common_skills) / len(job_skills_set)) * 100
    
    return int(score)