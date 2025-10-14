#!/usr/bin/env python3
"""
Future-Agent Multi-Agent Integration
Integrates formul8-multiagent with Future4200 thread querying for enhanced cannabis knowledge processing
"""

import json
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of agents in the multi-agent system"""
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    TECHNICAL_EXPERT = "technical_expert"
    BUSINESS_CONSULTANT = "business_consultant"
    SAFETY_SPECIALIST = "safety_specialist"
    SYNTHESIZER = "synthesizer"

@dataclass
class ThreadResult:
    """Result from Future4200 thread query"""
    thread_id: str
    title: str
    content: str
    author: str
    url: str
    category: str
    relevance_score: float
    post_count: int
    view_count: int
    last_activity: str

@dataclass
class AgentResponse:
    """Response from a specific agent"""
    agent_type: AgentType
    response: str
    confidence: float
    sources: List[str]
    processing_time: float
    reasoning: str

@dataclass
class MultiAgentResult:
    """Final result from multi-agent processing"""
    question: str
    thread_results: List[ThreadResult]
    agent_responses: List[AgentResponse]
    synthesized_response: str
    overall_confidence: float
    total_processing_time: float
    pipeline_steps: List[str]

class Future4200ThreadQuery:
    """Handles querying Future4200 threads for relevant discussions"""
    
    def __init__(self, data_file: str = "data/comprehensive_scraping_results.json"):
        self.data_file = Path(data_file)
        self.threads_data = None
        self._load_threads_data()
    
    def _load_threads_data(self):
        """Load the comprehensive scraping results"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.threads_data = data.get("results", [])
            logger.info(f"Loaded {len(self.threads_data)} threads from Future4200 data")
        except Exception as e:
            logger.error(f"Failed to load threads data: {e}")
            self.threads_data = []
    
    async def search_threads(self, query: str, max_results: int = 10) -> List[ThreadResult]:
        """Search for relevant threads based on query"""
        if not self.threads_data:
            return []
        
        # Simple keyword matching for now - could be enhanced with semantic search
        query_lower = query.lower()
        relevant_threads = []
        
        for thread in self.threads_data:
            if not thread.get("success", False):
                continue
                
            data = thread.get("data", {})
            content = data.get("content", "").lower()
            title = data.get("title", "").lower()
            
            # Calculate relevance score based on keyword matches
            relevance_score = 0
            query_words = query_lower.split()
            
            for word in query_words:
                if word in content:
                    relevance_score += content.count(word) * 0.1
                if word in title:
                    relevance_score += title.count(word) * 0.5
            
            if relevance_score > 0:
                thread_result = ThreadResult(
                    thread_id=data.get("thread_id", ""),
                    title=data.get("title", ""),
                    content=data.get("content", "")[:1000],  # Truncate for processing
                    author=data.get("author", ""),
                    url=data.get("url", ""),
                    category=self._categorize_thread(content),
                    relevance_score=relevance_score,
                    post_count=data.get("post_count", 0),
                    view_count=data.get("view_count", 0),
                    last_activity=data.get("last_activity", "")
                )
                relevant_threads.append(thread_result)
        
        # Sort by relevance score and return top results
        relevant_threads.sort(key=lambda x: x.relevance_score, reverse=True)
        return relevant_threads[:max_results]
    
    def _categorize_thread(self, content: str) -> str:
        """Categorize thread based on content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["extract", "extraction", "distill", "distillation"]):
            return "extraction"
        elif any(word in content_lower for word in ["grow", "cultivate", "plant", "seed"]):
            return "cultivation"
        elif any(word in content_lower for word in ["business", "legal", "regulation", "license"]):
            return "business"
        elif any(word in content_lower for word in ["equipment", "machine", "tool", "device"]):
            return "equipment"
        elif any(word in content_lower for word in ["genetic", "strain", "breed", "hybrid"]):
            return "genetics"
        else:
            return "general"

class Formul8MultiAgent:
    """Integrates with formul8-multiagent for LangChain processing"""
    
    def __init__(self, api_url: str = "https://api.formul8.com/multiagent/v1"):
        self.api_url = api_url
        self.api_key = "your_formul8_api_key_here"  # Replace with actual API key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def process_with_agents(self, question: str, thread_results: List[ThreadResult]) -> List[AgentResponse]:
        """Process question and thread data through multiple specialized agents"""
        agent_responses = []
        
        # Prepare context from thread results
        context = self._prepare_context(thread_results)
        
        # Process through different agent types
        agent_tasks = [
            self._call_researcher_agent(question, context),
            self._call_analyst_agent(question, context),
            self._call_technical_expert_agent(question, context),
            self._call_business_consultant_agent(question, context),
            self._call_safety_specialist_agent(question, context)
        ]
        
        # Execute all agents in parallel
        results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {i} failed: {result}")
                continue
            if result:
                agent_responses.append(result)
        
        return agent_responses
    
    def _prepare_context(self, thread_results: List[ThreadResult]) -> str:
        """Prepare context from thread results for agent processing"""
        context_parts = []
        
        for thread in thread_results[:5]:  # Use top 5 most relevant threads
            context_parts.append(f"""
Thread: {thread.title}
Author: {thread.author}
Category: {thread.category}
Content: {thread.content[:500]}...
Relevance Score: {thread.relevance_score}
URL: {thread.url}
""")
        
        return "\n".join(context_parts)
    
    async def _call_researcher_agent(self, question: str, context: str) -> Optional[AgentResponse]:
        """Call the researcher agent for comprehensive information gathering"""
        return await self._call_agent(
            AgentType.RESEARCHER,
            question,
            context,
            "You are a cannabis research specialist. Analyze the provided forum discussions and provide comprehensive research-based insights."
        )
    
    async def _call_analyst_agent(self, question: str, context: str) -> Optional[AgentResponse]:
        """Call the analyst agent for data analysis and insights"""
        return await self._call_agent(
            AgentType.ANALYST,
            question,
            context,
            "You are a cannabis industry analyst. Analyze trends, patterns, and insights from the community discussions."
        )
    
    async def _call_technical_expert_agent(self, question: str, context: str) -> Optional[AgentResponse]:
        """Call the technical expert agent for technical guidance"""
        return await self._call_agent(
            AgentType.TECHNICAL_EXPERT,
            question,
            context,
            "You are a cannabis technical expert. Provide detailed technical guidance based on the forum discussions and industry best practices."
        )
    
    async def _call_business_consultant_agent(self, question: str, context: str) -> Optional[AgentResponse]:
        """Call the business consultant agent for business insights"""
        return await self._call_agent(
            AgentType.BUSINESS_CONSULTANT,
            question,
            context,
            "You are a cannabis business consultant. Provide business insights, market analysis, and regulatory guidance based on the community discussions."
        )
    
    async def _call_safety_specialist_agent(self, question: str, context: str) -> Optional[AgentResponse]:
        """Call the safety specialist agent for safety guidance"""
        return await self._call_agent(
            AgentType.SAFETY_SPECIALIST,
            question,
            context,
            "You are a cannabis safety specialist. Focus on safety protocols, risk assessment, and best practices from the community discussions."
        )
    
    async def _call_agent(self, agent_type: AgentType, question: str, context: str, system_prompt: str) -> Optional[AgentResponse]:
        """Generic method to call any agent"""
        try:
            payload = {
                "agent_type": agent_type.value,
                "question": question,
                "context": context,
                "system_prompt": system_prompt,
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            start_time = time.time()
            
            async with self.session.post(
                f"{self.api_url}/agents/process",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    processing_time = time.time() - start_time
                    
                    return AgentResponse(
                        agent_type=agent_type,
                        response=data.get("response", ""),
                        confidence=data.get("confidence", 0.0),
                        sources=data.get("sources", []),
                        processing_time=processing_time,
                        reasoning=data.get("reasoning", "")
                    )
                else:
                    logger.error(f"Agent {agent_type.value} failed with status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling agent {agent_type.value}: {e}")
            return None
    
    async def synthesize_responses(self, question: str, agent_responses: List[AgentResponse]) -> str:
        """Synthesize responses from all agents into a final answer"""
        try:
            # Prepare agent responses for synthesis
            agent_data = []
            for response in agent_responses:
                agent_data.append({
                    "agent_type": response.agent_type.value,
                    "response": response.response,
                    "confidence": response.confidence,
                    "reasoning": response.reasoning
                })
            
            payload = {
                "question": question,
                "agent_responses": agent_data,
                "synthesis_instructions": "Synthesize the responses from all agents into a comprehensive, well-structured answer that incorporates the best insights from each specialist."
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with self.session.post(
                f"{self.api_url}/synthesize",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("synthesized_response", "")
                else:
                    logger.error(f"Synthesis failed with status {response.status}")
                    return self._fallback_synthesis(agent_responses)
                    
        except Exception as e:
            logger.error(f"Error in synthesis: {e}")
            return self._fallback_synthesis(agent_responses)
    
    def _fallback_synthesis(self, agent_responses: List[AgentResponse]) -> str:
        """Fallback synthesis when API is unavailable"""
        if not agent_responses:
            return "No agent responses available for synthesis."
        
        synthesis_parts = ["# Multi-Agent Analysis\n"]
        
        for response in agent_responses:
            synthesis_parts.append(f"## {response.agent_type.value.title()} Perspective")
            synthesis_parts.append(f"**Confidence:** {response.confidence:.2f}")
            synthesis_parts.append(f"**Response:** {response.response}")
            if response.reasoning:
                synthesis_parts.append(f"**Reasoning:** {response.reasoning}")
            synthesis_parts.append("")
        
        return "\n".join(synthesis_parts)

class FutureAgentMultiAgentPipeline:
    """Main pipeline that orchestrates the multi-agent processing"""
    
    def __init__(self):
        self.thread_query = Future4200ThreadQuery()
        self.multiagent = None
    
    async def process_question(self, question: str) -> MultiAgentResult:
        """Process a question through the complete multi-agent pipeline"""
        pipeline_steps = []
        start_time = time.time()
        
        try:
            # Step 1: Query Future4200 threads
            pipeline_steps.append("Querying Future4200 threads...")
            thread_results = await self.thread_query.search_threads(question, max_results=10)
            pipeline_steps.append(f"Found {len(thread_results)} relevant threads")
            
            # Step 2: Initialize multi-agent system
            pipeline_steps.append("Initializing multi-agent system...")
            async with Formul8MultiAgent() as multiagent:
                self.multiagent = multiagent
                
                # Step 3: Process through multiple agents
                pipeline_steps.append("Processing through specialized agents...")
                agent_responses = await multiagent.process_with_agents(question, thread_results)
                pipeline_steps.append(f"Completed processing with {len(agent_responses)} agents")
                
                # Step 4: Synthesize responses
                pipeline_steps.append("Synthesizing agent responses...")
                synthesized_response = await multiagent.synthesize_responses(question, agent_responses)
                pipeline_steps.append("Synthesis completed")
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(agent_responses)
            
            total_processing_time = time.time() - start_time
            
            return MultiAgentResult(
                question=question,
                thread_results=thread_results,
                agent_responses=agent_responses,
                synthesized_response=synthesized_response,
                overall_confidence=overall_confidence,
                total_processing_time=total_processing_time,
                pipeline_steps=pipeline_steps
            )
            
        except Exception as e:
            logger.error(f"Error in multi-agent pipeline: {e}")
            pipeline_steps.append(f"Error: {str(e)}")
            
            return MultiAgentResult(
                question=question,
                thread_results=[],
                agent_responses=[],
                synthesized_response=f"Error processing question: {str(e)}",
                overall_confidence=0.0,
                total_processing_time=time.time() - start_time,
                pipeline_steps=pipeline_steps
            )
    
    def _calculate_overall_confidence(self, agent_responses: List[AgentResponse]) -> float:
        """Calculate overall confidence from agent responses"""
        if not agent_responses:
            return 0.0
        
        # Weighted average based on agent type importance
        weights = {
            AgentType.RESEARCHER: 0.25,
            AgentType.ANALYST: 0.20,
            AgentType.TECHNICAL_EXPERT: 0.25,
            AgentType.BUSINESS_CONSULTANT: 0.15,
            AgentType.SAFETY_SPECIALIST: 0.15
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for response in agent_responses:
            weight = weights.get(response.agent_type, 0.1)
            weighted_sum += response.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

async def main():
    """Demo the multi-agent integration"""
    pipeline = FutureAgentMultiAgentPipeline()
    
    # Test questions
    test_questions = [
        "How do I extract CBD from hemp safely?",
        "What are the best LED lights for growing cannabis?",
        "How do I start a cannabis business in California?",
        "What equipment do I need for distillation?",
        "How do I choose the right cannabis strain for extraction?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*80}")
        print(f"Processing: {question}")
        print('='*80)
        
        result = await pipeline.process_question(question)
        
        print(f"\nPipeline Steps:")
        for i, step in enumerate(result.pipeline_steps, 1):
            print(f"{i}. {step}")
        
        print(f"\nThread Results: {len(result.thread_results)}")
        for thread in result.thread_results[:3]:  # Show top 3
            print(f"  - {thread.title} (Score: {thread.relevance_score:.2f})")
        
        print(f"\nAgent Responses: {len(result.agent_responses)}")
        for response in result.agent_responses:
            print(f"  - {response.agent_type.value}: {response.confidence:.2f} confidence")
        
        print(f"\nSynthesized Response:")
        print(result.synthesized_response[:500] + "..." if len(result.synthesized_response) > 500 else result.synthesized_response)
        
        print(f"\nOverall Confidence: {result.overall_confidence:.2f}")
        print(f"Total Processing Time: {result.total_processing_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())