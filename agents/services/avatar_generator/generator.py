"""
Avatar Generator using Stable Diffusion.

Creates professional avatar images based on CV data.

Styles:
- tech-professional: Modern tech industry professional
- business-formal: Business executive style
- creative-artistic: Creative industry professional
- academic-researcher: Academic/research style
"""

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from typing import Dict, Optional
import logging
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64

logger = logging.getLogger(__name__)

class AvatarGenerator:
    """
    Generate professional avatars from CV data.
    
    Features:
    - Style-based generation (tech, business, creative, academic)
    - Seniority-appropriate appearance
    - Domain-specific elements
    - Skill badges overlay
    """
    
    def __init__(self, model_name: str = "runwayml/stable-diffusion-v1-5"):
        """
        Initialize avatar generator.
        
        Args:
            model_name: Hugging Face model identifier
        """
        logger.info(f"Initializing Avatar Generator with model: {model_name}")
        
        self.model_name = model_name
        self.pipeline = None
        
        # Style templates
        self.STYLE_PROMPTS = {
            'tech-professional': "professional headshot, software engineer, modern tech startup, "
                                "confident, friendly, smart casual, office background, "
                                "natural lighting, high quality, detailed face",
            
            'business-formal': "professional business portrait, executive, formal suit, "
                              "confident, corporate office, professional lighting, "
                              "high quality, detailed face, leadership presence",
            
            'creative-artistic': "creative professional portrait, designer, artistic, "
                                "modern creative space, stylish, innovative, "
                                "natural lighting, high quality, detailed face",
            
            'academic-researcher': "academic professional portrait, researcher, intelligent, "
                                  "university office, scholarly, professional attire, "
                                  "natural lighting, high quality, detailed face"
        }
        
        # Seniority modifiers
        self.SENIORITY_MODIFIERS = {
            'junior': "young, early 20s, enthusiastic, fresh graduate",
            'mid': "30s, experienced, confident, professional",
            'senior': "40s, highly experienced, authoritative, seasoned professional",
            'executive': "50s, leadership, executive presence, distinguished, authoritative"
        }
        
        # Negative prompt
        self.NEGATIVE_PROMPT = (
            "ugly, deformed, distorted, cartoon, anime, low quality, blurry, "
            "multiple faces, duplicate, extra limbs, disfigured, bad anatomy"
        )
        
        logger.info("✅ Avatar Generator initialized (model will load on first use)")
    
    def _load_model(self):
        """Lazy load Stable Diffusion model."""
        if self.pipeline is not None:
            return
        
        logger.info("Loading Stable Diffusion model...")
        
        try:
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                safety_checker=None  # Disable for speed
            )
            
            # Use DPM solver for faster generation
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.pipeline = self.pipeline.to("cuda")
                logger.info("✅ Model loaded on GPU")
            else:
                logger.info("✅ Model loaded on CPU (slower)")
            
        except Exception as e:
            logger.error(f"Failed to load Stable Diffusion model: {e}")
            raise
    
    def generate_avatar(
        self,
        cv_data: Dict,
        style: str = 'tech-professional',
        size: tuple = (512, 512),
        seed: Optional[int] = None
    ) -> Dict:
        """
        Generate avatar image from CV data.
        
        Args:
            cv_data: Parsed CV data
            style: Visual style (tech-professional, business-formal, etc.)
            size: Image size (width, height)
            seed: Random seed for reproducibility
            
        Returns:
            Dict with image path, metadata, prompt used
        """
        logger.info(f"Generating avatar for {cv_data['name']} with style: {style}")
        
        try:
            # Load model if needed
            self._load_model()
            
            # Build prompt
            prompt = self._build_prompt(cv_data, style)
            
            logger.info(f"Using prompt: {prompt}")
            
            # Set random seed
            if seed is not None:
                torch.manual_seed(seed)
            
            # Generate image
            with torch.inference_mode():
                result = self.pipeline(
                    prompt=prompt,
                    negative_prompt=self.NEGATIVE_PROMPT,
                    num_inference_steps=30,  # Balance between quality and speed
                    guidance_scale=7.5,
                    height=size[1],
                    width=size[0]
                )
            
            avatar_image = result.images[0]
            
            # Add visual elements (skill badges, etc.)
            avatar_with_elements = self._add_visual_elements(avatar_image, cv_data)
            
            # Save image
            output_path = self._save_image(avatar_with_elements, cv_data['name'])
            
            logger.info(f"✅ Avatar generated: {output_path}")
            
            return {
                'image_path': output_path,
                'image_base64': self._image_to_base64(avatar_with_elements),
                'prompt': prompt,
                'style': style,
                'cv_data': cv_data,
                'metadata': {
                    'name': cv_data['name'],
                    'role': cv_data['role'],
                    'domain': cv_data['domain'],
                    'seniority': cv_data['seniority']
                }
            }
            
        except Exception as e:
            logger.error(f"Avatar generation failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Return placeholder
            return self._get_placeholder_avatar(cv_data)
    
    def _build_prompt(self, cv_data: Dict, style: str) -> str:
        """
        Build Stable Diffusion prompt from CV data.
        
        Args:
            cv_data: Parsed CV data
            style: Visual style
            
        Returns:
            Complete prompt string
        """
        # Base style prompt
        base_prompt = self.STYLE_PROMPTS.get(style, self.STYLE_PROMPTS['tech-professional'])
        
        # Add seniority modifier
        seniority = cv_data.get('seniority', 'mid')
        seniority_modifier = self.SENIORITY_MODIFIERS.get(seniority, self.SENIORITY_MODIFIERS['mid'])
        
        # Add domain-specific elements
        domain = cv_data.get('domain', 'tech')
        domain_elements = {
            'tech': "computer, modern office, technology",
            'business': "professional office, corporate environment",
            'creative': "creative studio, artistic workspace",
            'academic': "university office, books, research papers",
            'healthcare': "medical office, professional healthcare setting",
            'finance': "financial office, professional business setting"
        }
        domain_context = domain_elements.get(domain, domain_elements['tech'])
        
        # Combine
        full_prompt = f"{base_prompt}, {seniority_modifier}, {domain_context}"
        
        return full_prompt
    
    def _add_visual_elements(self, image: Image.Image, cv_data: Dict) -> Image.Image:
        """
        Add visual elements to avatar (skill badges, domain indicators).
        
        Args:
            image: Base avatar image
            cv_data: CV data
            
        Returns:
            Enhanced image with overlays
        """
        # Create copy
        enhanced = image.copy()
        draw = ImageDraw.Draw(enhanced)
        
        # Add subtle badge in corner
        domain = cv_data.get('domain', 'tech')
        seniority = cv_data.get('seniority', 'mid')
        
        # Domain color scheme
        domain_colors = {
            'tech': '#3498db',      # Blue
            'business': '#2c3e50',  # Dark gray
            'creative': '#e74c3c',  # Red
            'academic': '#27ae60',  # Green
            'healthcare': '#1abc9c',# Teal
            'finance': '#f39c12'    # Orange
        }
        
        color = domain_colors.get(domain, '#3498db')
        
        # Draw corner badge
        badge_size = 60
        badge_pos = (enhanced.width - badge_size - 10, 10)
        
        draw.rectangle(
            [badge_pos, (badge_pos[0] + badge_size, badge_pos[1] + badge_size)],
            fill=color,
            outline='white',
            width=2
        )
        
        # Add text (first letter of domain + seniority level indicator)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        badge_text = domain[0].upper()
        text_bbox = draw.textbbox((0, 0), badge_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_pos = (
            badge_pos[0] + (badge_size - text_width) // 2,
            badge_pos[1] + (badge_size - text_height) // 2
        )
        
        draw.text(text_pos, badge_text, fill='white', font=font)
        
        return enhanced
    
    def _save_image(self, image: Image.Image, name: str) -> str:
        """
        Save avatar image to disk.
        
        Args:
            image: PIL Image
            name: Candidate name
            
        Returns:
            Path to saved image
        """
        # Create avatars directory
        output_dir = Path('data/avatars')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        
        output_path = output_dir / f"{safe_name}_avatar.png"
        
        # Save
        image.save(output_path, 'PNG')
        
        return str(output_path)
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def _get_placeholder_avatar(self, cv_data: Dict) -> Dict:
        """Return placeholder avatar when generation fails."""
        # Create simple colored square with initials
        size = (512, 512)
        image = Image.new('RGB', size, color='#3498db')
        draw = ImageDraw.Draw(image)
        
        # Get initials
        name = cv_data.get('name', 'C')
        initials = ''.join([word[0].upper() for word in name.split()[:2]])
        
        try:
            font = ImageFont.truetype("arial.ttf", 120)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_pos = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        draw.text(text_pos, initials, fill='white', font=font)
        
        output_path = self._save_image(image, cv_data['name'])
        
        return {
            'image_path': output_path,
            'image_base64': self._image_to_base64(image),
            'prompt': 'placeholder',
            'style': 'placeholder',
            'cv_data': cv_data,
            'metadata': {
                'name': cv_data['name'],
                'role': cv_data.get('role', 'Professional'),
                'domain': cv_data.get('domain', 'tech'),
                'seniority': cv_data.get('seniority', 'mid')
            }
        }

# Global instance
avatar_generator = AvatarGenerator()