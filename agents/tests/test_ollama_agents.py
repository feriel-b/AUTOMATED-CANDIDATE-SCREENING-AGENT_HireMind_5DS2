"""
Test Ollama-powered agents.
"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from interview_agents.interviewer_agent import InterviewerAgent
from core.ollama_config import OllamaConfig

async def test_interviewer():
    """Test interviewer agent with Phi4-Mini."""
    
    # Check Ollama
    if not OllamaConfig.check_availability():
        print("❌ Ollama not available!")
        print("💡 Run: ollama serve")
        print("💡 Run: ollama pull phi4-mini")
        return
    
    print("🤖 Testing Interviewer Agent with Phi4-Mini...\n")
    
    agent = InterviewerAgent()
    
    # Test: Select a question
    result = await agent.execute(
        task="Select a medium difficulty Python question for a backend developer who is performing well"
    )
    
    print("="*50)
    print("RESULT:")
    print("="*50)
    print(f"Success: {result['success']}")
    print(f"Agent: {result['agent']}")
    print(f"Output: {result['result']}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(test_interviewer())