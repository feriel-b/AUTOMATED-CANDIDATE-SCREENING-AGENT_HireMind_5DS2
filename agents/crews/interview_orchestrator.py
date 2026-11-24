"""
Interview Orchestrator - Coordinates all interview agents.
"""

from typing import Dict, Any, List, Optional
import logging
import asyncio
import json
import re


from interview_agents.interviewer_agent import InterviewerAgent
from interview_agents.stt_agent import STTAgent
from interview_agents.prosody_agent import ProsodyAgent
from interview_agents.emotion_agent import EmotionAgent
from interview_agents.evaluator_agent import evaluator_agent
from interview_agents.summarizer_agent import SummarizerAgent
from interview_agents.cheating_detector_agent import CheatingDetectorAgent
from interview_agents.avatar_agent import avatar_agent

logger = logging.getLogger(__name__)

class InterviewOrchestrator:
    """Orchestrates complete interview workflow with security analysis."""
    
    def __init__(self):
        logger.info("Initializing Interview Orchestrator...")
        
        # Initialize all agents
        self.interviewer = InterviewerAgent()
        self.stt = STTAgent()
        self.prosody = ProsodyAgent()
        self.emotion = EmotionAgent()
        self.evaluator = evaluator_agent
        self.summarizer = SummarizerAgent()

        # New agents
        self.cheating_detector = CheatingDetectorAgent()
        self.avatar_generator = avatar_agent
        
        # State
        self.interview_data = {
            'questions': [],
            'answers': [],
            'evaluations': [],
            'security_flags': []
        }
        
        logger.info("✅ Interview Orchestrator initialized")
    def get_status(self) -> Dict[str, Any]:
        """
        Get system status.
        
        Returns:
            Dict with system information
        """
        return {
            'framework': 'LangChain + Ollama',
            'model': 'phi4-mini (or configured model)',
            'agents': [
                'Interviewer',
                'STT_Specialist',
                'Prosody_Analyst',
                'Emotion_Detector',
                'Answer_Evaluator',
                'Session_Summarizer',
                'Cheating_Detector',
                'Avatar_Generator'
            ],
            'tools': {
                'stt': 'Whisper (openai-whisper)',
                'prosody': 'Librosa',
                'emotion': 'DeepFace',
                'cheating': 'Multi-modal detection',
                'avatar': 'Stable Diffusion (optional)'
            },
            'capabilities': [
                'Question Generation',
                'Audio Transcription',
                'Voice Prosody Analysis',
                'Emotion Detection',
                'Answer Evaluation',
                'Session Summarization',
                'Cheating Detection (AI text, gaze, multi-speaker)',
                'Avatar Generation'
            ],
            'status': 'ready',
            'interview_stats': {
                'questions_generated': len(self.interview_data['questions']),
                'answers_processed': len(self.interview_data['answers']),
                'security_flags': len(self.interview_data['security_flags'])
            }
        }
    
    async def select_questions(
        self,
        categories: List[str],
        difficulty: str = 'medium',
        num_questions: int = 5,
        candidate_performance: str = 'average'
    ) -> Dict[str, Any]:
        """
        Select interview questions based on criteria.
        
        Args:
            categories: List of question categories
            difficulty: easy, medium, or hard
            num_questions: Number of questions to select
            candidate_performance: Candidate's performance level
            
        Returns:
            Dict with selected questions
        """
        logger.info(f"Selecting {num_questions} questions from categories: {categories}")
        
        # Build task for interviewer agent
        task = f"""Select {num_questions} interview questions with these criteria:

CATEGORIES: {', '.join(categories)}
DIFFICULTY: {difficulty}
CANDIDATE PERFORMANCE: {candidate_performance}

Requirements:
1. Select diverse questions covering different aspects
2. Match the specified difficulty level
3. Consider candidate performance (easier if struggling, harder if excelling)
4. Include both theoretical and practical questions
5. Ensure questions test problem-solving ability

Return a structured list with:
- Question ID
- Question text
- Category
- Difficulty level
- Expected answer elements
- Evaluation criteria

Format as JSON array."""

        try:
            result = await self.interviewer.execute(
                task=task,
                context={
                    'categories': categories,
                    'difficulty': difficulty,
                    'num_questions': num_questions,
                    'candidate_performance': candidate_performance
                }
            )
            
            if result.get('success'):
                result_text = result.get('result', '')
                
                # Try to parse JSON
                try:
                    json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                    if json_match:
                        questions = json.loads(json_match.group(0))
                    else:
                        questions = self._parse_questions_from_text(result_text, num_questions)
                except:
                    questions = self._parse_questions_from_text(result_text, num_questions)
                
                return {
                    'success': True,
                    'questions': questions,
                    'count': len(questions)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'questions': []
                }
                
        except Exception as e:
            logger.error(f"Question selection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'questions': []
            }
    
    async def generate_questions(
        self,
        job_description: str,
        difficulty: str = 'medium',
        num_questions: int = 5
    ) -> List[Dict]:
        """Generate interview questions."""
        logger.info(f"Generating {num_questions} questions...")
        
        # BUILD THE TASK STRING (FIX HERE!)
        task = f"""Generate {num_questions} interview questions for this role:

JOB DESCRIPTION:
{job_description}

DIFFICULTY: {difficulty}

Requirements:
- Questions should test technical knowledge and problem-solving
- Include both theoretical and practical questions
- Vary difficulty levels appropriately
- Each question should have clear evaluation criteria

Return a structured list of questions with:
1. Question text
2. Expected answer elements/keywords
3. Difficulty level
4. Topic/category

Format your response as a JSON list of question objects."""

        try:
            # FIXED: Pass task as string, not dict
            result = await self.interviewer.execute(task=task, context={
                'job_description': job_description,
                'difficulty': difficulty,
                'num_questions': num_questions
            })
            
            # Parse result
            if result.get('success'):
                result_text = result.get('result', '')
                
                # Try to parse JSON from result
                try:
                    # Look for JSON in the response
                    import re
                    json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                    if json_match:
                        questions = json.loads(json_match.group(0))
                    else:
                        # Fallback: parse text manually
                        questions = self._parse_questions_from_text(result_text, num_questions)
                except:
                    # Fallback parsing
                    questions = self._parse_questions_from_text(result_text, num_questions)
                
                self.interview_data['questions'] = questions
                logger.info(f"✅ Generated {len(questions)} questions")
                
                return questions
            else:
                logger.error(f"Question generation failed: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_questions_from_text(self, text: str, num_questions: int) -> List[Dict]:
        """Fallback: Parse questions from text response."""
        questions = []
        
        # Split by common question patterns
        lines = text.split('\n')
        current_question = None
        
        for line in lines:
            line = line.strip()
            
            # Look for numbered questions
            if re.match(r'^\d+[\.\)]\s+', line):
                if current_question:
                    questions.append(current_question)
                
                question_text = re.sub(r'^\d+[\.\)]\s+', '', line)
                current_question = {
                    'id': len(questions) + 1,
                    'text': question_text,
                    'keywords': '',
                    'difficulty': 'medium',
                    'category': 'general'
                }
            elif current_question and line:
                # Append to current question
                current_question['text'] += ' ' + line
        
        if current_question:
            questions.append(current_question)
        
        # Ensure we have at least some questions
        if len(questions) == 0:
            # Generate default questions
            for i in range(num_questions):
                questions.append({
                    'id': i + 1,
                    'text': f'Question {i+1}: Please describe your experience with the relevant technologies.',
                    'keywords': 'experience, technology, skills',
                    'difficulty': 'medium',
                    'category': 'general'
                })
        
        return questions[:num_questions]
    
    async def process_answer_with_security(
        self,
        question: Dict,
        audio_path: str,
        video_path: Optional[str] = None,
        candidate_baseline: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process answer with comprehensive analysis including security check."""
        logger.info("🎯 Processing answer with security analysis...")
        
        try:
            # STEP 1: TRANSCRIPTION 
            logger.info("📝 Step 1: Transcribing audio...")
            
            task = f"""Transcribe the audio file at: {audio_path}

Return the complete transcript of what was said."""
            
            stt_result = await self.stt.execute(task=task, context={'audio_path': audio_path})
            transcript = stt_result.get('result', '')
            
            # STEP 2: PROSODY ANALYSIS 
            logger.info("🎵 Step 2: Analyzing voice prosody...")
            
            task = f"""Analyze the voice prosody and quality of the audio at: {audio_path}

Evaluate:
- Speech rate and fluency
- Tone and pitch variation
- Confidence indicators
- Stress/nervousness markers

Provide a structured analysis."""
            
            prosody_result = await self.prosody.execute(task=task, context={'audio_path': audio_path})
            
            # STEP 3: EMOTION + GAZE ANALYSIS (FIXED)
            emotion_result = {}
            if video_path:
                logger.info("😊 Step 3: Analyzing emotions and gaze...")
                
                task = f"""Analyze the video at: {video_path}

Evaluate:
- Facial emotions throughout the video
- Eye gaze patterns (looking at camera vs. elsewhere)
- Body language and confidence
- Signs of reading or distraction

Provide detailed behavioral analysis."""
                
                emotion_result = await self.emotion.execute(task=task, context={'video_path': video_path})
            
            # STEP 4: CHEATING DETECTION (FIXED)
            logger.info("🔒 Step 4: Running security analysis...")
            security_result = await self.cheating_detector.analyze_interview_security(
                transcript=transcript,
                video_path=video_path,
                audio_path=audio_path,
                candidate_baseline=candidate_baseline
            )
            
            # STEP 5: EVALUATION (FIXED)
            logger.info("📊 Step 5: Evaluating answer...")
            
            task = f"""Evaluate this interview answer:

QUESTION: {question.get('text', '')}
ANSWER: {transcript}
EXPECTED KEYWORDS: {question.get('keywords', '')}

Prosody Analysis: {prosody_result.get('result', 'N/A')}
Emotion Analysis: {emotion_result.get('result', 'N/A')}

Provide a comprehensive evaluation including:
1. Overall score (0-100)
2. Technical accuracy
3. Completeness
4. Communication quality
5. Strengths (2-3 points)
6. Areas for improvement (2-3 points)
7. Final recommendation

Structure your response clearly."""
            
            evaluation_result = await self.evaluator.execute(task=task, context={
                'question': question,
                'transcript': transcript,
                'prosody': prosody_result,
                'emotion': emotion_result
            })
            
            # AGGREGATE RESULTS
            complete_result = {
                'question': question,
                'transcript': transcript,
                'prosody_analysis': prosody_result,
                'emotion_analysis': emotion_result,
                'security_analysis': security_result,
                'evaluation': evaluation_result,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            # Store
            self.interview_data['answers'].append(complete_result)
            
            if security_result.get('risk_level') in ['MODERATE', 'HIGH']:
                self.interview_data['security_flags'].append({
                    'question_id': question.get('id'),
                    'risk_level': security_result['risk_level'],
                    'cheating_score': security_result['cheating_score']
                })
            
            logger.info("✅ Answer processing complete")
            
            return complete_result
            
        except Exception as e:
            logger.error(f"Answer processing failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'error': str(e),
                'question': question,
                'transcript': '',
                'security_analysis': {'risk_level': 'UNKNOWN', 'cheating_score': 0},
                'evaluation': {'overall_score': 0}
            }
    
    async def generate_interview_summary(self) -> Dict[str, Any]:
        """Generate final interview summary."""
        logger.info("📋 Generating interview summary...")
        
        try:
            task = f"""Generate a comprehensive interview summary based on this data:

INTERVIEW STATISTICS:
- Total questions: {len(self.interview_data['questions'])}
- Answers processed: {len(self.interview_data['answers'])}
- Security flags: {len(self.interview_data['security_flags'])}

DETAILED RESULTS:
{json.dumps([
    {
        'question': a.get('question', {}).get('text', 'N/A'),
        'evaluation': a.get('evaluation', {}).get('result', 'N/A')[:200],
        'security_risk': a.get('security_analysis', {}).get('risk_level', 'N/A')
    }
    for a in self.interview_data['answers']
], indent=2)}

SECURITY CONCERNS:
{json.dumps(self.interview_data['security_flags'], indent=2)}

Provide:
1. Overall performance assessment (0-100 score)
2. Key strengths (3-5 points)
3. Areas for improvement (3-5 points)
4. Security/integrity concerns summary
5. Final hiring recommendation (Strong Pass / Pass / Borderline / Fail)
6. Detailed justification

Structure your response as a professional interview report."""
            
            result = await self.summarizer.execute(task=task, context={
                'interview_data': self.interview_data
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'result': 'Summary generation failed. Please review individual results.'
            }
    
    async def generate_candidate_avatar(
        self,
        cv_path: str,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate professional avatar from CV."""
        logger.info(f"🎨 Generating avatar from CV: {cv_path}")
        
        try:
            result = await self.avatar_generator.generate_from_cv(
                cv_path=cv_path,
                style_preference=style
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Avatar generation failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
orchestrator = InterviewOrchestrator()