#!/usr/bin/env python3
"""
Demo Multi-Agent Integration
Demonstrates the Future-Agent + formul8-multiagent integration
"""

import asyncio
import json
from pathlib import Path
from multiagent_integration import FutureAgentMultiAgentPipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demo_multiagent_processing():
    """Demonstrate the multi-agent processing pipeline"""
    
    print("🌿 Future-Agent Multi-Agent Integration Demo")
    print("=" * 60)
    
    # Initialize the pipeline
    pipeline = FutureAgentMultiAgentPipeline()
    
    # Demo questions covering different categories
    demo_questions = [
        {
            "question": "How do I safely extract CBD from hemp using CO2 extraction?",
            "category": "extraction",
            "expected_agents": ["technical_expert", "safety_specialist", "researcher"]
        },
        {
            "question": "What are the legal requirements for starting a cannabis business in California?",
            "category": "business",
            "expected_agents": ["business_consultant", "analyst", "researcher"]
        },
        {
            "question": "Which LED lights are best for growing cannabis indoors?",
            "category": "cultivation",
            "expected_agents": ["technical_expert", "researcher", "analyst"]
        },
        {
            "question": "How do I choose the right cannabis strain for making concentrates?",
            "category": "genetics",
            "expected_agents": ["researcher", "technical_expert", "analyst"]
        },
        {
            "question": "What safety equipment do I need for cannabis extraction?",
            "category": "safety",
            "expected_agents": ["safety_specialist", "technical_expert", "researcher"]
        }
    ]
    
    results = []
    
    for i, demo in enumerate(demo_questions, 1):
        print(f"\n{'='*80}")
        print(f"Demo {i}: {demo['question']}")
        print(f"Category: {demo['category']}")
        print(f"Expected Agents: {', '.join(demo['expected_agents'])}")
        print('='*80)
        
        # Process the question
        result = await pipeline.process_question(demo['question'])
        results.append({
            "demo": demo,
            "result": result
        })
        
        # Display results
        print(f"\n📊 Pipeline Execution:")
        for j, step in enumerate(result.pipeline_steps, 1):
            print(f"  {j}. {step}")
        
        print(f"\n🔍 Thread Discovery:")
        print(f"  Found {len(result.thread_results)} relevant threads")
        for thread in result.thread_results[:3]:  # Show top 3
            print(f"    • {thread.title[:60]}... (Score: {thread.relevance_score:.2f})")
        
        print(f"\n🤖 Agent Processing:")
        print(f"  {len(result.agent_responses)} agents responded")
        for response in result.agent_responses:
            print(f"    • {response.agent_type.value}: {response.confidence:.2f} confidence ({response.processing_time:.2f}s)")
        
        print(f"\n📝 Synthesized Response:")
        print(f"  {result.synthesized_response[:300]}...")
        
        print(f"\n📈 Performance Metrics:")
        print(f"  Overall Confidence: {result.overall_confidence:.2f}")
        print(f"  Total Processing Time: {result.total_processing_time:.2f}s")
        print(f"  Average Agent Time: {result.total_processing_time / max(len(result.agent_responses), 1):.2f}s")
    
    # Generate summary report
    await generate_summary_report(results)

async def generate_summary_report(results):
    """Generate a summary report of the demo results"""
    
    print(f"\n{'='*80}")
    print("📊 DEMO SUMMARY REPORT")
    print('='*80)
    
    total_questions = len(results)
    total_processing_time = sum(r['result'].total_processing_time for r in results)
    avg_processing_time = total_processing_time / total_questions
    
    total_threads = sum(len(r['result'].thread_results) for r in results)
    avg_threads_per_question = total_threads / total_questions
    
    total_agent_responses = sum(len(r['result'].agent_responses) for r in results)
    avg_agents_per_question = total_agent_responses / total_questions
    
    avg_confidence = sum(r['result'].overall_confidence for r in results) / total_questions
    
    print(f"Total Questions Processed: {total_questions}")
    print(f"Average Processing Time: {avg_processing_time:.2f}s")
    print(f"Total Threads Found: {total_threads}")
    print(f"Average Threads per Question: {avg_threads_per_question:.1f}")
    print(f"Total Agent Responses: {total_agent_responses}")
    print(f"Average Agents per Question: {avg_agents_per_question:.1f}")
    print(f"Average Confidence: {avg_confidence:.2f}")
    
    # Agent performance breakdown
    agent_performance = {}
    for result in results:
        for response in result['result'].agent_responses:
            agent_type = response.agent_type.value
            if agent_type not in agent_performance:
                agent_performance[agent_type] = {
                    'count': 0,
                    'total_confidence': 0,
                    'total_time': 0
                }
            agent_performance[agent_type]['count'] += 1
            agent_performance[agent_type]['total_confidence'] += response.confidence
            agent_performance[agent_type]['total_time'] += response.processing_time
    
    print(f"\n🤖 Agent Performance Breakdown:")
    for agent_type, perf in agent_performance.items():
        avg_conf = perf['total_confidence'] / perf['count']
        avg_time = perf['total_time'] / perf['count']
        print(f"  {agent_type}: {perf['count']} responses, {avg_conf:.2f} avg confidence, {avg_time:.2f}s avg time")
    
    # Category performance
    category_performance = {}
    for result in results:
        category = result['demo']['category']
        if category not in category_performance:
            category_performance[category] = {
                'count': 0,
                'total_confidence': 0,
                'total_time': 0
            }
        category_performance[category]['count'] += 1
        category_performance[category]['total_confidence'] += result['result'].overall_confidence
        category_performance[category]['total_time'] += result['result'].total_processing_time
    
    print(f"\n📂 Category Performance:")
    for category, perf in category_performance.items():
        avg_conf = perf['total_confidence'] / perf['count']
        avg_time = perf['total_time'] / perf['count']
        print(f"  {category}: {perf['count']} questions, {avg_conf:.2f} avg confidence, {avg_time:.2f}s avg time")
    
    # Save detailed results
    output_file = Path("data/multiagent_demo_results.json")
    output_file.parent.mkdir(exist_ok=True)
    
    # Convert results to serializable format
    serializable_results = []
    for result in results:
        serializable_result = {
            "question": result['demo']['question'],
            "category": result['demo']['category'],
            "expected_agents": result['demo']['expected_agents'],
            "thread_results": [
                {
                    "thread_id": t.thread_id,
                    "title": t.title,
                    "author": t.author,
                    "url": t.url,
                    "category": t.category,
                    "relevance_score": t.relevance_score,
                    "post_count": t.post_count,
                    "view_count": t.view_count
                } for t in result['result'].thread_results
            ],
            "agent_responses": [
                {
                    "agent_type": r.agent_type.value,
                    "response": r.response,
                    "confidence": r.confidence,
                    "sources": r.sources,
                    "processing_time": r.processing_time,
                    "reasoning": r.reasoning
                } for r in result['result'].agent_responses
            ],
            "synthesized_response": result['result'].synthesized_response,
            "overall_confidence": result['result'].overall_confidence,
            "total_processing_time": result['result'].total_processing_time,
            "pipeline_steps": result['result'].pipeline_steps
        }
        serializable_results.append(serializable_result)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "demo_timestamp": "2025-10-13T20:00:00Z",
            "total_questions": total_questions,
            "summary_metrics": {
                "avg_processing_time": avg_processing_time,
                "avg_threads_per_question": avg_threads_per_question,
                "avg_agents_per_question": avg_agents_per_question,
                "avg_confidence": avg_confidence
            },
            "agent_performance": agent_performance,
            "category_performance": category_performance,
            "results": serializable_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print(f"\n✅ Demo completed successfully!")

async def interactive_demo():
    """Interactive demo where user can ask questions"""
    
    print("🌿 Interactive Future-Agent Multi-Agent Demo")
    print("=" * 50)
    print("Ask questions about cannabis cultivation, extraction, business, etc.")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    pipeline = FutureAgentMultiAgentPipeline()
    
    while True:
        try:
            question = input("\n❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print(f"\n🔄 Processing: {question}")
            print("⏳ This may take a moment...")
            
            result = await pipeline.process_question(question)
            
            print(f"\n📊 Results:")
            print(f"  Threads found: {len(result.thread_results)}")
            print(f"  Agents responded: {len(result.agent_responses)}")
            print(f"  Confidence: {result.overall_confidence:.2f}")
            print(f"  Processing time: {result.total_processing_time:.2f}s")
            
            print(f"\n💬 Answer:")
            print(result.synthesized_response)
            
            if result.thread_results:
                print(f"\n🔗 Top relevant threads:")
                for thread in result.thread_results[:3]:
                    print(f"  • {thread.title} (Score: {thread.relevance_score:.2f})")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_demo())
    else:
        asyncio.run(demo_multiagent_processing())