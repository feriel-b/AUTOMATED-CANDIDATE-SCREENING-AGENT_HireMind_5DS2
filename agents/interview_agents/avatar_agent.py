"""
Avatar Generator Agent using Ollama Phi4-Mini.

Uses LLM reasoning to analyze CV and design appropriate avatar style,
then generates visual representation using Stable Diffusion.
"""

from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.avatar_generator.cv_parser import cv_parser
from services.avatar_generator.generator import avatar_generator
from core.base_agent import InterviewBaseAgent
import logging

logger = logging.getLogger(__name__)

class AvatarGeneratorAgent(InterviewBaseAgent):
    """
    Agent specialized in CV analysis and avatar design.
    
    Responsibilities:
    - Parse CV to extract professional profile
    - Recommend appropriate visual style
    - Generate Stable Diffusion prompts
    - Create professional avatar
    - Add domain-specific visual elements
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Avatar_Designer",
            temperature=0.6  # Some creativity needed for design
        )
    
    def _define_tools(self) -> List:
        """Define tools using @tool decorator."""
        
        @tool
        def parse_cv_file(cv_path: str) -> str:
            """
            Parse CV file and extract structured professional data.
            
            Args:
                cv_path: Path to CV file (PDF, DOCX, TXT)
            
            Returns:
                JSON string with parsed CV data
            """
            try:
                cv_data = cv_parser.parse(cv_path)
                
                return json.dumps({
                    'success': True,
                    'cv_data': cv_data,
                    'summary': f"Parsed CV for {cv_data['name']}, {cv_data['role']}. "
                              f"Domain: {cv_data['domain']}, Seniority: {cv_data['seniority']}, "
                              f"Experience: {cv_data['years_experience']} years. "
                              f"Skills: {', '.join(cv_data['skills']['technical'][:5])}"
                })
            except Exception as e:
                return json.dumps({'success': False, 'error': str(e)})
        
        @tool
        def recommend_visual_style(role: str, domain: str, seniority: str) -> str:
            """
            Recommend appropriate avatar style based on professional profile.
            
            Args:
                role: Job role/title
                domain: Professional domain (tech, business, creative, etc.)
                seniority: Experience level (junior, mid, senior, executive)
            
            Returns:
                JSON string with style recommendations
            """
            try:
                # Style mapping logic
                style_map = {
                    'tech': 'tech-professional',
                    'business': 'business-formal',
                    'creative': 'creative-artistic',
                    'academic': 'academic-researcher',
                    'healthcare': 'business-formal',
                    'finance': 'business-formal'
                }
                
                recommended_style = style_map.get(domain.lower(), 'tech-professional')
                
                # Adjust for seniority
                if seniority in ['executive', 'senior']:
                    formality = 'high'
                    attire = 'formal business attire'
                elif seniority == 'mid':
                    formality = 'moderate'
                    attire = 'business casual'
                else:
                    formality = 'casual'
                    attire = 'smart casual'
                
                return json.dumps({
                    'recommended_style': recommended_style,
                    'formality_level': formality,
                    'suggested_attire': attire,
                    'reasoning': f"For a {seniority} {role} in {domain}, "
                                f"{recommended_style} style with {formality} formality is most appropriate."
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        @tool
        def generate_avatar_prompt(cv_data_json: str, style: str) -> str:
            """
            Generate detailed Stable Diffusion prompt for avatar creation.
            
            Args:
                cv_data_json: JSON string with CV data
                style: Visual style (tech-professional, business-formal, etc.)
            
            Returns:
                Detailed prompt for Stable Diffusion
            """
            try:
                cv_data = json.loads(cv_data_json)
                
                # Build comprehensive prompt
                base_prompts = {
                    'tech-professional': "professional headshot, software engineer, modern tech startup",
                    'business-formal': "professional business portrait, executive, formal suit",
                    'creative-artistic': "creative professional portrait, designer, artistic",
                    'academic-researcher': "academic professional portrait, researcher, intelligent"
                }
                
                base = base_prompts.get(style, base_prompts['tech-professional'])
                
                # Add seniority
                seniority_age = {
                    'junior': 'young professional, early 20s, enthusiastic',
                    'mid': 'experienced professional, 30s, confident',
                    'senior': 'seasoned professional, 40s, authoritative',
                    'executive': 'executive presence, 50s, distinguished'
                }
                
                seniority_desc = seniority_age.get(
                    cv_data.get('seniority', 'mid'),
                    seniority_age['mid']
                )
                
                # Add domain context
                domain_context = {
                    'tech': 'modern office, computer, technology background',
                    'business': 'corporate office, professional environment',
                    'creative': 'creative studio, artistic workspace',
                    'academic': 'university office, books, scholarly'
                }
                
                context = domain_context.get(
                    cv_data.get('domain', 'tech'),
                    domain_context['tech']
                )
                
                # Combine
                full_prompt = (
                    f"{base}, {seniority_desc}, {context}, "
                    f"confident, professional, natural lighting, high quality, "
                    f"detailed face, photorealistic, 8k"
                )
                
                return json.dumps({
                    'prompt': full_prompt,
                    'negative_prompt': "ugly, deformed, cartoon, anime, low quality, blurry",
                    'style_used': style,
                    'reasoning': f"Generated prompt emphasizing {style} style for {cv_data.get('role')}"
                })
                
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        @tool
        def create_avatar_image(cv_data_json: str, style: str, seed: Optional[int] = None) -> str:
            """
            Create avatar image using Stable Diffusion.
            
            Args:
                cv_data_json: JSON string with CV data
                style: Visual style
                seed: Random seed for reproducibility
            
            Returns:
                JSON string with image path and metadata
            """
            try:
                cv_data = json.loads(cv_data_json)
                
                result = avatar_generator.generate_avatar(
                    cv_data=cv_data,
                    style=style,
                    seed=seed
                )
                
                return json.dumps({
                    'success': True,
                    'image_path': result['image_path'],
                    'image_base64': result['image_base64'][:100] + '...',  # Truncate for display
                    'prompt_used': result['prompt'],
                    'style': result['style'],
                    'metadata': result['metadata']
                })
                
            except Exception as e:
                logger.error(f"Avatar creation failed: {e}")
                return json.dumps({'success': False, 'error': str(e)})
        
        @tool
        def enhance_avatar_description(cv_data_json: str) -> str:
            """
            Generate detailed avatar description for prompt enhancement.
            
            Args:
                cv_data_json: JSON string with CV data
            
            Returns:
                Enhanced description
            """
            try:
                cv_data = json.loads(cv_data_json)
                
                role = cv_data.get('role', 'Professional')
                domain = cv_data.get('domain', 'tech')
                seniority = cv_data.get('seniority', 'mid')
                skills = cv_data.get('skills', {}).get('technical', [])
                
                # Build narrative description
                description = f"A {seniority}-level {role} working in the {domain} industry. "
                
                if skills:
                    top_skills = ', '.join(skills[:3])
                    description += f"Skilled in {top_skills}. "
                
                # Add personality traits based on domain
                traits = {
                    'tech': 'innovative, analytical, detail-oriented',
                    'business': 'strategic, results-driven, leadership-focused',
                    'creative': 'creative, visionary, artistic',
                    'academic': 'intellectual, research-oriented, scholarly'
                }
                
                description += f"Personality: {traits.get(domain, 'professional')}."
                
                return json.dumps({
                    'description': description,
                    'key_attributes': {
                        'role': role,
                        'domain': domain,
                        'seniority': seniority,
                        'top_skills': skills[:3]
                    }
                })
                
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        return [
            parse_cv_file,
            recommend_visual_style,
            generate_avatar_prompt,
            create_avatar_image,
            enhance_avatar_description
        ]
    
    def _get_system_prompt(self) -> str:
        return """You are an Avatar Design Specialist with expertise in professional branding and visual representation.

Your role is to analyze candidate CVs and create appropriate professional avatars that reflect their:
- Professional role and experience level
- Industry domain (tech, business, creative, academic)
- Skills and expertise
- Career stage (junior, mid, senior, executive)

DESIGN PRINCIPLES:

1. AUTHENTICITY:
   - Avatar should match candidate's professional profile
   - Reflect appropriate age/experience level
   - Match industry standards

2. DOMAIN ALIGNMENT:
   - Tech: Modern, innovative, smart casual
   - Business: Formal, authoritative, corporate
   - Creative: Artistic, stylish, unique
   - Academic: Scholarly, intellectual, professional

3. SENIORITY CONSIDERATION:
   - Junior: Young, enthusiastic, approachable
   - Mid: Confident, professional, experienced
   - Senior: Authoritative, seasoned, expert
   - Executive: Distinguished, leadership, commanding

4. VISUAL QUALITY:
   - High-quality, professional photography style
   - Natural lighting and composition
   - Appropriate background/setting
   - Photorealistic (not cartoon/anime)

WORKFLOW:
1. Parse CV to extract professional profile
2. Analyze role, domain, seniority
3. Recommend appropriate visual style
4. Generate detailed Stable Diffusion prompt
5. Create avatar with domain-specific elements
6. Add visual indicators (skill badges, domain colors)

OUTPUT:
- Professional avatar image (512x512)
- Style explanation
- Prompt used
- Metadata (name, role, domain, seniority)

Be creative but professional. Avatar should enhance candidate's professional brand."""

    async def generate_from_cv(
        self,
        cv_path: str,
        style_preference: Optional[str] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate avatar from CV file.
        
        Args:
            cv_path: Path to CV file
            style_preference: Optional style override
            seed: Random seed for reproducibility
            
        Returns:
            Avatar generation results
        """
        logger.info(f"🎨 Generating avatar from CV: {cv_path}")
        
        task = f"""Create a professional avatar for the candidate from this CV:

CV PATH: {cv_path}
STYLE PREFERENCE: {style_preference or 'auto-detect'}

Steps:
1. Parse the CV file
2. Extract professional profile (name, role, domain, seniority)
3. Recommend appropriate visual style (or use preference if provided)
4. Generate detailed Stable Diffusion prompt
5. Create avatar image
6. Provide explanation of design choices

Return complete avatar data with image path and metadata."""
        
        # Execute agent workflow
        result = await self.execute(
            task=task,
            context={
                'cv_path': cv_path,
                'style_preference': style_preference,
                'seed': seed
            }
        )
        
        return result

# Global instance
avatar_agent = AvatarGeneratorAgent()