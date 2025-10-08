#!/usr/bin/env python3
"""
Demo F8 Processing Script
Processes a sample of questions through F8 LangChain for demonstration
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

class F8DemoProcessor:
    def __init__(self):
        self.session = None
        self.results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def simulate_f8_response(self, question: str, category: str) -> Dict[str, Any]:
        """Simulate F8 LangChain response for demonstration"""
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Generate realistic responses based on category
        f8_responses = {
            "extraction": f"Based on current industry standards, here's a comprehensive answer to your question about {question.lower()}:\n\n**Key Methods:**\n- Short Path Distillation for high-purity concentrates\n- CO2 Extraction for commercial applications\n- Solvent-based methods with proper safety protocols\n- Rosin Press for solventless extraction\n\n**Best Practices:**\n- Always use proper safety equipment\n- Follow local regulations and guidelines\n- Consider your scale and target compounds\n- Maintain consistent quality control\n\n**Safety Considerations:**\n- Proper ventilation and equipment\n- Knowledge of solvent properties\n- Emergency procedures and protocols",
            
            "cultivation": f"Here's expert guidance on {question.lower()}:\n\n**Essential Requirements:**\n- Proper lighting (LED or HPS systems)\n- Climate control (70-80°F, 40-60% humidity)\n- Quality growing medium and nutrients\n- Adequate ventilation and air circulation\n\n**Growing Techniques:**\n- Training methods (LST, topping, pruning)\n- Nutrient management and pH balancing\n- Pest and disease prevention\n- Harvest timing and curing\n\n**Equipment Needed:**\n- Grow tent or dedicated space\n- Lighting system appropriate for your space\n- Ventilation and air circulation\n- Monitoring equipment for environmental conditions",
            
            "business": f"Regarding {question.lower()}, here are the key considerations:\n\n**Regulatory Compliance:**\n- State and federal licensing requirements\n- Testing and quality control standards\n- Tax obligations and reporting\n- Security and safety protocols\n\n**Market Considerations:**\n- Understanding local market dynamics\n- Competitive analysis and positioning\n- Supply chain management\n- Customer acquisition and retention\n\n**Legal Requirements:**\n- Business entity formation\n- Insurance and liability coverage\n- Employment law compliance\n- Intellectual property protection",
            
            "equipment": f"For {question.lower()}, here's what you need to know:\n\n**Essential Equipment:**\n- Quality tools and machinery\n- Safety equipment and protocols\n- Monitoring and control systems\n- Maintenance and calibration tools\n\n**Selection Criteria:**\n- Scale and capacity requirements\n- Quality and reliability standards\n- Budget and ROI considerations\n- Technical support and service\n\n**Best Practices:**\n- Regular maintenance schedules\n- Proper training and operation\n- Safety protocols and procedures\n- Documentation and record keeping",
            
            "genetics": f"About {question.lower()}, here's comprehensive information:\n\n**Genetic Considerations:**\n- Strain selection and characteristics\n- Breeding and propagation methods\n- Genetic stability and consistency\n- Phenotype expression and variation\n\n**Growing Factors:**\n- Environmental requirements\n- Nutrient and feeding schedules\n- Training and pruning techniques\n- Harvest timing and methods\n\n**Quality Factors:**\n- Cannabinoid and terpene profiles\n- Yield potential and characteristics\n- Disease resistance and hardiness\n- Market preferences and trends"
        }
        
        # Community responses from Future4200 forum
        community_responses = {
            "extraction": f"From the Future4200 community discussion:\n\n**Community Consensus:**\n- Most members prefer short path distillation for purity\n- CO2 extraction is popular for commercial scale\n- Safety is the #1 concern - proper ventilation is crucial\n- Start small and scale up gradually\n\n**Real User Experiences:**\n- 'I've been using a 2L short path for 3 years, works great for small batches'\n- 'CO2 is expensive but worth it for consistent results'\n- 'Make sure you have proper safety equipment before starting'\n- 'Join the extraction subforum for detailed guides'\n\n**Common Issues:**\n- Overheating during distillation\n- Inconsistent yields with different strains\n- Safety equipment costs\n- Learning curve for new methods",
            
            "cultivation": f"Future4200 community insights on {question.lower()}:\n\n**Community Tips:**\n- LED lights are more efficient than HPS for most growers\n- Keep humidity between 40-60% to prevent mold\n- LST (Low Stress Training) works better than topping for beginners\n- Start with good genetics - it makes everything easier\n\n**Real Grower Experiences:**\n- 'My first grow was a disaster, but I learned so much'\n- 'Spider mites are the worst - prevention is key'\n- 'Don't overwater! Let the soil dry between waterings'\n- 'The community here saved my grow multiple times'\n\n**Common Problems:**\n- Overwatering and root rot\n- Nutrient burn from too much fertilizer\n- Light burn from lights too close\n- pH issues causing nutrient lockout",
            
            "business": f"Future4200 business discussion insights:\n\n**Community Advice:**\n- Regulations vary wildly by state - check local laws first\n- Start with a solid business plan and legal structure\n- Network with other industry professionals\n- Be prepared for high startup costs\n\n**Real Business Experiences:**\n- 'Licensing took 18 months in my state'\n- 'Compliance costs are higher than expected'\n- 'Finding reliable suppliers is challenging'\n- 'Marketing restrictions are very limiting'\n\n**Key Challenges:**\n- Complex and changing regulations\n- High compliance and testing costs\n- Banking and payment processing issues\n- Competition from established players",
            
            "equipment": f"Community equipment recommendations:\n\n**Popular Choices:**\n- Most recommend starting with basic equipment\n- Quality matters more than brand names\n- Buy used equipment to save money initially\n- Research thoroughly before purchasing\n\n**User Reviews:**\n- 'This rosin press has been solid for 2 years'\n- 'Wish I had bought a bigger tent initially'\n- 'LED lights paid for themselves in electricity savings'\n- 'Cheap equipment breaks down faster'\n\n**Buying Tips:**\n- Check the classifieds section for deals\n- Ask for recommendations in specific forums\n- Consider your space and budget constraints\n- Read reviews from actual users",
            
            "genetics": f"Future4200 genetics discussion:\n\n**Community Favorites:**\n- Indica strains for beginners (easier to grow)\n- Autoflowering strains for quick harvests\n- Landrace strains for unique terpenes\n- Popular breeders have consistent quality\n\n**Grower Experiences:**\n- 'This strain is mold resistant and easy to grow'\n- 'Took 3 tries to get the right pheno'\n- 'Seed banks with good reputations are worth the extra cost'\n- 'Clones are easier than seeds for beginners'\n\n**Selection Criteria:**\n- Consider your growing environment\n- Look for mold and pest resistance\n- Check flowering times for your climate\n- Read grow journals for real experiences"
        }
        
        # Get responses based on category
        f8_response = f8_responses.get(category, f"Here's a comprehensive answer to your question about {question.lower()}:\n\nBased on industry best practices and community knowledge, this topic involves several key considerations that are important for success. The specific approach depends on your individual circumstances, goals, and constraints.\n\n**Key Points:**\n- Research and education are essential\n- Safety should always be the top priority\n- Local regulations must be followed\n- Quality control is crucial for success\n\n**Recommendations:**\n- Start with thorough research\n- Consult with experienced professionals\n- Begin with small-scale testing\n- Document everything for future reference")
        
        community_response = community_responses.get(category, f"Future4200 community discussion on {question.lower()}:\n\n**Community Insights:**\n- Multiple users have shared their experiences\n- Real-world advice from actual growers and extractors\n- Common problems and solutions discussed\n- Equipment recommendations from users\n\n**Key Points from Forum:**\n- Safety is always the top priority\n- Start small and learn from mistakes\n- Community support is invaluable\n- Documentation and sharing helps everyone\n\n**Popular Threads:**\n- Multiple related discussions available\n- Step-by-step guides from experienced members\n- Photo journals of successful projects\n- Troubleshooting help from the community")
        
        # Generate realistic confidence and processing time
        confidence = 0.7 + (hash(question) % 30) / 100  # 0.7 to 0.99
        processing_time = 1.0 + (hash(question) % 20) / 10  # 1.0 to 2.9 seconds
        
        # Generate analysis comparing F8 and community responses
        analysis = self.generate_analysis(f8_response, community_response, category)
        
        return {
            "f8_response": f8_response,
            "community_response": community_response,
            "analysis": analysis,
            "f8_confidence": round(confidence, 3),
            "f8_processing_time": round(processing_time, 2),
            "f8_sources": [
                "Cannabis Industry Best Practices Guide",
                "Community Knowledge Base",
                "Expert Consultation Database"
            ],
            "community_sources": [
                "Future4200 Forum Discussion",
                "Community Member Experiences",
                "Real-world Case Studies"
            ],
            "status": "success"
        }
    
    def generate_analysis(self, f8_response: str, community_response: str, category: str) -> str:
        """Generate analysis comparing F8 and community responses"""
        analyses = {
            "extraction": "**Analysis:** F8 provides comprehensive technical guidance while the community offers practical, real-world experiences. F8 emphasizes safety protocols and industry standards, while community members share specific equipment recommendations and common pitfalls. Both sources agree on safety being paramount, but community insights include cost considerations and equipment longevity that F8 doesn't cover.\n\n**Key Differences:**\n- F8: More structured, technical approach\n- Community: Practical tips and real user experiences\n- Both: Emphasize safety and proper equipment",
            
            "cultivation": "**Analysis:** F8 offers systematic growing guidance while the community provides hands-on experience and troubleshooting. F8 covers the fundamentals comprehensively, but community members share specific strain experiences, pest solutions, and environmental tips that come from real growing situations.\n\n**Key Differences:**\n- F8: Comprehensive growing methodology\n- Community: Specific strain and problem-solving advice\n- Both: Stress the importance of genetics and environment",
            
            "business": "**Analysis:** F8 provides regulatory and business structure guidance while the community shares real-world challenges and costs. F8 covers the formal requirements, but community members reveal the hidden costs, timeline realities, and practical obstacles that aren't in official documentation.\n\n**Key Differences:**\n- F8: Regulatory compliance and business structure\n- Community: Real costs, timelines, and practical challenges\n- Both: Emphasize thorough planning and legal compliance",
            
            "equipment": "**Analysis:** F8 offers systematic equipment selection criteria while the community provides specific brand recommendations and cost-effective alternatives. F8 covers the technical specifications, but community members share durability experiences and value assessments that help with actual purchasing decisions.\n\n**Key Differences:**\n- F8: Technical specifications and selection criteria\n- Community: Brand recommendations and value assessments\n- Both: Emphasize quality over price and proper research",
            
            "genetics": "**Analysis:** F8 provides scientific breeding and genetics information while the community shares specific strain experiences and growing characteristics. F8 covers the technical aspects of genetics, but community members provide practical growing advice for specific strains and breeders.\n\n**Key Differences:**\n- F8: Scientific genetics and breeding principles\n- Community: Specific strain experiences and grower recommendations\n- Both: Emphasize starting with good genetics"
        }
        
        return analyses.get(category, "**Analysis:** F8 provides comprehensive technical guidance while the community offers practical, real-world experiences. Both sources complement each other well, with F8 offering structured knowledge and the community providing hands-on insights and specific recommendations.")
    
    async def process_questions_sample(self, questions: List[Dict[str, Any]], sample_size: int = 50) -> List[Dict[str, Any]]:
        """Process a sample of questions through F8 simulation"""
        # Take a random sample
        import random
        sample_questions = random.sample(questions, min(sample_size, len(questions)))
        
        logger.info(f"Processing {len(sample_questions)} sample questions...")
        
        results = []
        for i, question in enumerate(sample_questions):
            logger.info(f"Processing question {i+1}/{len(sample_questions)}: {question['question'][:50]}...")
            
            try:
                f8_result = await self.simulate_f8_response(
                    question["question"],
                    question.get("category", "general")
                )
                
                result = {
                    "question_id": question.get("id", f"q_{i}"),
                    "question": question["question"],
                    "category": question.get("category", "general"),
                    "difficulty": question.get("difficulty", "intermediate"),
                    "source": question.get("source", "content"),
                    "thread_url": question.get("thread_url", ""),
                    "author": question.get("author", ""),
                    **f8_result,
                    "timestamp": datetime.now().isoformat()
                }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing question {i+1}: {e}")
                results.append({
                    "question_id": question.get("id", f"q_{i}"),
                    "question": question["question"],
                    "category": question.get("category", "general"),
                    "f8_response": "",
                    "f8_confidence": 0.0,
                    "f8_processing_time": 0.0,
                    "f8_sources": [],
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results

async def main():
    """Main function to process sample questions through F8"""
    # Load sample questions
    questions_file = Path("data/sample_questions_for_f8.json")
    if not questions_file.exists():
        logger.error(f"Questions file not found: {questions_file}")
        return
    
    logger.info("Loading extracted questions...")
    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    logger.info(f"Loaded {len(questions)} questions")
    
    # Process sample questions through F8
    async with F8DemoProcessor() as processor:
        logger.info("Starting F8 demo processing...")
        start_time = time.time()
        
        results = await processor.process_questions_sample(questions, sample_size=100)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"Demo processing completed in {processing_time:.2f} seconds")
        
        # Calculate statistics
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        avg_confidence = sum(r["f8_confidence"] for r in results if r["status"] == "success") / max(successful, 1)
        avg_processing_time = sum(r["f8_processing_time"] for r in results if r["status"] == "success") / max(successful, 1)
        
        # Save results
        output_file = Path("data/f8_responses_demo.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "processing_timestamp": datetime.now().isoformat(),
                "total_questions": len(questions),
                "sample_size": len(results),
                "successful_responses": successful,
                "failed_responses": failed,
                "processing_time_seconds": processing_time,
                "average_confidence": round(avg_confidence, 3),
                "average_processing_time": round(avg_processing_time, 3),
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Demo results saved to {output_file}")
        logger.info(f"Statistics: {successful}/{len(results)} successful, avg confidence: {avg_confidence:.3f}")
        
        # Generate summary by category
        by_category = {}
        for result in results:
            category = result["category"]
            if category not in by_category:
                by_category[category] = {"total": 0, "successful": 0, "avg_confidence": 0.0}
            
            by_category[category]["total"] += 1
            if result["status"] == "success":
                by_category[category]["successful"] += 1
                by_category[category]["avg_confidence"] += result["f8_confidence"]
        
        # Calculate average confidence by category
        for category, stats in by_category.items():
            if stats["successful"] > 0:
                stats["avg_confidence"] = round(stats["avg_confidence"] / stats["successful"], 3)
            else:
                stats["avg_confidence"] = 0.0
        
        # Save statistics
        stats_file = Path("data/f8_processing_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_questions": len(questions),
                "sample_processed": len(results),
                "successful": successful,
                "failed": failed,
                "average_confidence": round(avg_confidence, 3),
                "average_processing_time": round(avg_processing_time, 3),
                "processing_time_seconds": processing_time,
                "by_category": by_category
            }, f, indent=2, ensure_ascii=False)
        
        logger.info("Category breakdown:")
        for category, stats in by_category.items():
            logger.info(f"  {category}: {stats['successful']}/{stats['total']} successful, avg confidence: {stats['avg_confidence']}")

if __name__ == "__main__":
    asyncio.run(main())