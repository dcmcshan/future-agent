#!/usr/bin/env python3
"""
Ask F8 All Questions Script
Processes all 16,337 extracted questions through F8 LangChain and saves responses
"""

import json
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class F8QuestionProcessor:
    def __init__(self, f8_api_url: str = "https://api.formul8.com/f8-langchain/v1/chat"):
        self.f8_api_url = f8_api_url
        self.api_key = "your_f8_api_key_here"  # Replace with actual API key
        self.session = None
        self.results = []
        self.processed_count = 0
        self.failed_count = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def ask_f8_question(self, question: str, question_id: str, category: str) -> Dict[str, Any]:
        """Ask a single question to F8 LangChain"""
        try:
            payload = {
                "query": question,
                "max_tokens": 500,
                "temperature": 0.7,
                "include_sources": True
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with self.session.post(
                self.f8_api_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "question_id": question_id,
                        "question": question,
                        "category": category,
                        "f8_response": data.get("response", ""),
                        "f8_sources": data.get("sources", []),
                        "f8_confidence": data.get("confidence", 0.0),
                        "f8_processing_time": data.get("processing_time", 0.0),
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"F8 API error for question {question_id}: {response.status} - {error_text}")
                    return {
                        "question_id": question_id,
                        "question": question,
                        "category": category,
                        "f8_response": "",
                        "f8_sources": [],
                        "f8_confidence": 0.0,
                        "f8_processing_time": 0.0,
                        "status": "error",
                        "error": f"HTTP {response.status}: {error_text}",
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout for question {question_id}")
            return {
                "question_id": question_id,
                "question": question,
                "category": category,
                "f8_response": "",
                "f8_sources": [],
                "f8_confidence": 0.0,
                "f8_processing_time": 0.0,
                "status": "timeout",
                "error": "Request timeout",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Exception for question {question_id}: {str(e)}")
            return {
                "question_id": question_id,
                "question": question,
                "category": category,
                "f8_response": "",
                "f8_sources": [],
                "f8_confidence": 0.0,
                "f8_processing_time": 0.0,
                "status": "exception",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def process_questions_batch(self, questions: List[Dict[str, Any]], batch_size: int = 10) -> List[Dict[str, Any]]:
        """Process questions in batches to avoid overwhelming the API"""
        results = []
        
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(questions) + batch_size - 1)//batch_size}")
            
            # Process batch concurrently
            tasks = []
            for q in batch:
                task = self.ask_f8_question(
                    q["question"],
                    q.get("id", f"q_{i}"),
                    q.get("category", "general")
                )
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Exception in batch processing: {result}")
                    results.append({
                        "question_id": batch[j].get("id", f"q_{i+j}"),
                        "question": batch[j]["question"],
                        "category": batch[j].get("category", "general"),
                        "f8_response": "",
                        "f8_sources": [],
                        "f8_confidence": 0.0,
                        "f8_processing_time": 0.0,
                        "status": "exception",
                        "error": str(result),
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    results.append(result)
            
            # Update counters
            successful = sum(1 for r in results[-len(batch):] if r["status"] == "success")
            self.processed_count += successful
            self.failed_count += len(batch) - successful
            
            logger.info(f"Batch completed: {successful}/{len(batch)} successful")
            
            # Save intermediate results
            if i % (batch_size * 10) == 0:  # Save every 100 questions
                await self.save_intermediate_results(results)
            
            # Rate limiting - wait between batches
            await asyncio.sleep(1)
        
        return results
    
    async def save_intermediate_results(self, results: List[Dict[str, Any]]):
        """Save intermediate results to avoid data loss"""
        output_file = Path("data/f8_responses_intermediate.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_processed": len(results),
                "successful": self.processed_count,
                "failed": self.failed_count,
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Intermediate results saved: {len(results)} total, {self.processed_count} successful, {self.failed_count} failed")

async def main():
    """Main function to process all questions through F8"""
    # Load extracted questions
    questions_file = Path("data/extracted_questions.json")
    if not questions_file.exists():
        logger.error(f"Questions file not found: {questions_file}")
        return
    
    logger.info("Loading extracted questions...")
    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    logger.info(f"Loaded {len(questions)} questions")
    
    # Process questions through F8
    async with F8QuestionProcessor() as processor:
        logger.info("Starting F8 processing...")
        start_time = time.time()
        
        results = await processor.process_questions_batch(questions, batch_size=5)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        logger.info(f"Total processed: {len(results)}")
        logger.info(f"Successful: {processor.processed_count}")
        logger.info(f"Failed: {processor.failed_count}")
        
        # Save final results
        output_file = Path("data/f8_responses_complete.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "processing_timestamp": datetime.now().isoformat(),
                "total_questions": len(questions),
                "total_processed": len(results),
                "successful_responses": processor.processed_count,
                "failed_responses": processor.failed_count,
                "processing_time_seconds": processing_time,
                "average_time_per_question": processing_time / len(questions) if questions else 0,
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Final results saved to {output_file}")
        
        # Generate summary statistics
        await generate_summary_stats(results)

async def generate_summary_stats(results: List[Dict[str, Any]]):
    """Generate summary statistics for the F8 responses"""
    stats = {
        "total_questions": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] != "success"),
        "by_category": {},
        "by_status": {},
        "average_confidence": 0.0,
        "average_processing_time": 0.0
    }
    
    # Calculate statistics
    successful_results = [r for r in results if r["status"] == "success"]
    
    if successful_results:
        stats["average_confidence"] = sum(r["f8_confidence"] for r in successful_results) / len(successful_results)
        stats["average_processing_time"] = sum(r["f8_processing_time"] for r in successful_results) / len(successful_results)
    
    # Count by category
    for result in results:
        category = result.get("category", "unknown")
        status = result.get("status", "unknown")
        
        if category not in stats["by_category"]:
            stats["by_category"][category] = {"total": 0, "successful": 0, "failed": 0}
        
        if status not in stats["by_status"]:
            stats["by_status"][status] = 0
        
        stats["by_category"][category]["total"] += 1
        if status == "success":
            stats["by_category"][category]["successful"] += 1
        else:
            stats["by_category"][category]["failed"] += 1
        
        stats["by_status"][status] += 1
    
    # Save statistics
    stats_file = Path("data/f8_processing_stats.json")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    logger.info("Summary statistics:")
    logger.info(f"  Total questions: {stats['total_questions']}")
    logger.info(f"  Successful: {stats['successful']}")
    logger.info(f"  Failed: {stats['failed']}")
    logger.info(f"  Average confidence: {stats['average_confidence']:.3f}")
    logger.info(f"  Average processing time: {stats['average_processing_time']:.3f}s")
    
    for category, cat_stats in stats["by_category"].items():
        logger.info(f"  {category}: {cat_stats['successful']}/{cat_stats['total']} successful")

if __name__ == "__main__":
    asyncio.run(main())