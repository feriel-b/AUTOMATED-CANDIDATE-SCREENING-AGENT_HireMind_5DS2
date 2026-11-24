"""
Base agent class for all interview agents using LangChain 1.x.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging

from core.ollama_config import OllamaConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewBaseAgent(ABC):
    """
    Base class for all interview agents.
    Uses LangChain 1.x with Ollama Phi4-Mini.
    
    Simplified architecture without deprecated AgentExecutor.
    Uses direct LLM + Tools pattern with LCEL (LangChain Expression Language).
    """
    
    def __init__(self, agent_name: str, temperature: float = 0.7):
        self.agent_name = agent_name
        self.llm = OllamaConfig.get_llm(temperature=temperature)
        self.tools = self._define_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # Create prompt template
        self.prompt = self._create_prompt()
        
        logger.info(f"✅ {agent_name} initialized with {len(self.tools)} tools")
    
    @abstractmethod
    def _define_tools(self) -> List[BaseTool]:
        """Define agent-specific tools. Must return list of @tool decorated functions."""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Define agent-specific system prompt."""
        pass
    
    def _create_prompt(self) -> PromptTemplate:
        """Create prompt template for the agent."""
        
        # Build tool descriptions
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])
        
        tool_names = ", ".join([tool.name for tool in self.tools])
        
        template = f"""You are {{agent_name}}.

{{system_prompt}}

You have access to the following tools:

{tool_descriptions}

Available tool names: {tool_names}

Instructions:
1. Analyze the task carefully
2. If you need to use a tool, respond EXACTLY in this format:
   ACTION: tool_name
   INPUT: tool_input_value
3. If you have the final answer, respond with:
   FINAL ANSWER: your answer here

Task: {{task}}

Your response:"""
        
        return PromptTemplate.from_template(template).partial(
            agent_name=self.agent_name,
            system_prompt=self._get_system_prompt()
        )
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response to extract action or final answer.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Dict with 'type' (action/answer) and relevant data
        """
        response = response.strip()
        
        # Check for final answer
        if "FINAL ANSWER:" in response.upper():
            answer_start = response.upper().find("FINAL ANSWER:")
            answer = response[answer_start + len("FINAL ANSWER:"):].strip()
            return {
                "type": "answer",
                "content": answer
            }
        
        # Check for action
        if "ACTION:" in response.upper() and "INPUT:" in response.upper():
            lines = response.split("\n")
            action = None
            tool_input = None
            
            for line in lines:
                line_upper = line.upper().strip()
                if line_upper.startswith("ACTION:"):
                    action = line.split(":", 1)[1].strip()
                elif line_upper.startswith("INPUT:"):
                    tool_input = line.split(":", 1)[1].strip()
            
            if action and tool_input:
                return {
                    "type": "action",
                    "tool": action,
                    "input": tool_input
                }
        
        # Default: treat as final answer
        return {
            "type": "answer",
            "content": response
        }
    
    async def execute(self, task: str, context: Dict[str, Any] = None, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Execute agent task with iterative tool use.
        
        Args:
            task: Task description
            context: Additional context
            max_iterations: Maximum tool use iterations
            
        Returns:
            Dict with result and metadata
        """
        try:
            logger.info(f"🤖 {self.agent_name} executing task...")
            
            iteration = 0
            conversation_history = []
            
            while iteration < max_iterations:
                iteration += 1
                
                # Build prompt with history
                current_task = task
                if conversation_history:
                    history_text = "\n\n".join([
                        f"Previous action: {h['action']}\nResult: {h['result']}"
                        for h in conversation_history
                    ])
                    current_task = f"{task}\n\nPrevious steps:\n{history_text}\n\nContinue working on the task."
                
                # Get LLM response
                prompt_text = self.prompt.format(task=current_task)
                response = await self.llm.ainvoke(prompt_text)
                
                # Handle response content
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = str(response)
                
                logger.info(f"📝 Iteration {iteration} response: {response_text[:200]}...")
                
                # Parse response
                parsed = self._parse_response(response_text)
                
                if parsed["type"] == "answer":
                    # Final answer reached
                    logger.info(f"✅ {self.agent_name} completed task in {iteration} iterations")
                    return {
                        "success": True,
                        "result": parsed["content"],
                        "agent": self.agent_name,
                        "iterations": iteration,
                        "context": context
                    }
                
                elif parsed["type"] == "action":
                    # Execute tool
                    tool_name = parsed["tool"]
                    tool_input = parsed["input"]
                    
                    if tool_name in self.tool_map:
                        logger.info(f"🔧 Executing tool: {tool_name} with input: {tool_input[:100]}...")
                        
                        try:
                            tool = self.tool_map[tool_name]
                            tool_result = tool.invoke(tool_input)
                            
                            conversation_history.append({
                                "action": f"Used {tool_name}",
                                "result": str(tool_result)[:500]  # Limit result length
                            })
                            
                            logger.info(f"✅ Tool result: {str(tool_result)[:200]}...")
                            
                        except Exception as tool_error:
                            logger.error(f"❌ Tool execution failed: {tool_error}")
                            conversation_history.append({
                                "action": f"Tried {tool_name}",
                                "result": f"ERROR: {str(tool_error)}"
                            })
                    else:
                        logger.warning(f"⚠️ Unknown tool: {tool_name}")
                        conversation_history.append({
                            "action": f"Tried unknown tool {tool_name}",
                            "result": f"ERROR: Tool not found. Available: {', '.join(self.tool_map.keys())}"
                        })
                else:
                    # Unexpected response format
                    logger.warning(f"⚠️ Unexpected response format in iteration {iteration}")
                    return {
                        "success": True,
                        "result": response_text,
                        "agent": self.agent_name,
                        "iterations": iteration,
                        "context": context
                    }
            
            # Max iterations reached
            logger.warning(f"⚠️ {self.agent_name} reached max iterations ({max_iterations})")
            
            # Use last conversation as result
            if conversation_history:
                last_result = conversation_history[-1]["result"]
                return {
                    "success": True,
                    "result": last_result,
                    "agent": self.agent_name,
                    "iterations": iteration,
                    "warning": "Max iterations reached",
                    "context": context
                }
            
            return {
                "success": False,
                "error": "Max iterations reached without result",
                "agent": self.agent_name,
                "iterations": iteration,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "context": context
            }