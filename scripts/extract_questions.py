#!/usr/bin/env python3
"""
Extract Questions Script
Extracts questions from thread data, with support for incremental updates
"""

import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Set
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuestionExtractor:
    """Extracts questions from thread data"""
    
    def __init__(self):
        self.existing_questions = []
        self.existing_question_hashes = set()
        self.new_questions = []
        self.question_patterns = [
            r'[?]',  # Contains question mark
            r'how\s+do\s+i',  # How do I...
            r'what\s+is',  # What is...
            r'where\s+can\s+i',  # Where can I...
            r'when\s+should\s+i',  # When should I...
            r'why\s+does',  # Why does...
            r'which\s+is\s+better',  # Which is better...
            r'can\s+i',  # Can I...
            r'should\s+i',  # Should I...
            r'is\s+it\s+safe',  # Is it safe...
            r'does\s+anyone\s+know',  # Does anyone know...
            r'has\s+anyone\s+tried',  # Has anyone tried...
            r'what\s+are\s+the\s+best',  # What are the best...
            r'how\s+much\s+does',  # How much does...
            r'what\s+size',  # What size...
            r'how\s+long',  # How long...
            r'what\s+kind\s+of',  # What kind of...
        ]
    
    def load_existing_questions(self, file_path: str):
        """Load existing questions to avoid duplicates"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.existing_questions = data.get('questions', [])
            
            # Create hash set for quick duplicate checking
            for question in self.existing_questions:
                question_text = question.get('question', '')
                question_hash = self.hash_question(question_text)
                self.existing_question_hashes.add(question_hash)
            
            logger.info(f"Loaded {len(self.existing_questions)} existing questions")
            
        except Exception as e:
            logger.warning(f"Could not load existing questions: {e}")
            self.existing_questions = []
            self.existing_question_hashes = set()
    
    def hash_question(self, question: str) -> str:
        """Create a hash for question deduplication"""
        # Normalize question for hashing
        normalized = re.sub(r'\s+', ' ', question.lower().strip())
        normalized = re.sub(r'[^\w\s?]', '', normalized)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def is_question(self, text: str) -> bool:
        """Check if text contains a question"""
        text_lower = text.lower()
        
        # Check for question patterns
        for pattern in self.question_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def extract_questions_from_text(self, text: str, thread_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract questions from text content"""
        questions = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:  # Skip very short sentences
                continue
            
            if self.is_question(sentence):
                # Check for duplicates
                question_hash = self.hash_question(sentence)
                if question_hash not in self.existing_question_hashes:
                    question_data = {
                        'question': sentence,
                        'source': 'content',
                        'thread_url': thread_data.get('url', ''),
                        'author': thread_data.get('author', ''),
                        'context': text[:200] + '...' if len(text) > 200 else text,
                        'category': self.categorize_question(sentence),
                        'difficulty': self.assess_difficulty(sentence),
                        'thread_id': thread_data.get('thread_id', ''),
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    questions.append(question_data)
                    self.existing_question_hashes.add(question_hash)
        
        return questions
    
    def categorize_question(self, question: str) -> str:
        """Categorize question based on content"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['extract', 'extraction', 'distill', 'distillation', 'concentrate']):
            return 'extraction'
        elif any(word in question_lower for word in ['grow', 'cultivate', 'plant', 'seed', 'flower', 'harvest']):
            return 'cultivation'
        elif any(word in question_lower for word in ['business', 'legal', 'regulation', 'license', 'compliance', 'permit']):
            return 'business'
        elif any(word in question_lower for word in ['equipment', 'machine', 'tool', 'device', 'setup', 'gear']):
            return 'equipment'
        elif any(word in question_lower for word in ['genetic', 'strain', 'breed', 'hybrid', 'phenotype', 'genotype']):
            return 'genetics'
        elif any(word in question_lower for word in ['process', 'processing', 'cure', 'dry', 'trim', 'cure']):
            return 'processing'
        else:
            return 'general'
    
    def assess_difficulty(self, question: str) -> str:
        """Assess question difficulty level"""
        question_lower = question.lower()
        
        # Advanced indicators
        advanced_terms = ['molecular', 'distillation', 'fractional', 'chromatography', 'terpenes', 'cannabinoids', 'phytocannabinoids']
        if any(term in question_lower for term in advanced_terms):
            return 'advanced'
        
        # Intermediate indicators
        intermediate_terms = ['extract', 'concentrate', 'rosin', 'hash', 'kief', 'bubble', 'ice water']
        if any(term in question_lower for term in intermediate_terms):
            return 'intermediate'
        
        # Basic indicators
        basic_terms = ['grow', 'plant', 'seed', 'soil', 'water', 'light', 'nutrient']
        if any(term in question_lower for term in basic_terms):
            return 'beginner'
        
        return 'intermediate'  # Default to intermediate
    
    def extract_from_threads(self, threads_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract questions from thread data"""
        all_questions = []
        
        for thread in threads_data:
            if not thread.get('success', False):
                continue
            
            thread_data = thread.get('data', {})
            content = thread_data.get('content', '')
            title = thread_data.get('title', '')
            
            # Extract from title
            if self.is_question(title):
                question_hash = self.hash_question(title)
                if question_hash not in self.existing_question_hashes:
                    question_data = {
                        'question': title,
                        'source': 'title',
                        'thread_url': thread_data.get('url', ''),
                        'author': thread_data.get('author', ''),
                        'context': content[:200] + '...' if len(content) > 200 else content,
                        'category': self.categorize_question(title),
                        'difficulty': self.assess_difficulty(title),
                        'thread_id': thread_data.get('thread_id', ''),
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    all_questions.append(question_data)
                    self.existing_question_hashes.add(question_hash)
            
            # Extract from content
            content_questions = self.extract_questions_from_text(content, thread_data)
            all_questions.extend(content_questions)
        
        return all_questions
    
    def update_questions_data(self, new_questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update the questions data structure"""
        # Combine existing and new questions
        all_questions = self.existing_questions + new_questions
        
        # Count questions by category
        category_counts = {}
        for question in all_questions:
            category = question.get('category', 'general')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count questions by source
        source_counts = {}
        for question in all_questions:
            source = question.get('source', 'content')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'extraction_timestamp': datetime.now().isoformat(),
            'total_questions': len(all_questions),
            'new_questions_added': len(new_questions),
            'questions_by_source': source_counts,
            'questions_by_category': category_counts,
            'questions': all_questions,
            'update_summary': {
                'timestamp': datetime.now().isoformat(),
                'new_questions': len(new_questions),
                'total_after_update': len(all_questions)
            }
        }

def main():
    parser = argparse.ArgumentParser(description='Extract questions from thread data')
    parser.add_argument('--input', required=True, help='Input thread data file')
    parser.add_argument('--output', required=True, help='Output questions file')
    parser.add_argument('--incremental', action='store_true', help='Incremental update mode')
    parser.add_argument('--existing-questions', default='data/extracted_questions.json', 
                       help='Existing questions file for incremental updates')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    extractor = QuestionExtractor()
    
    # Load existing questions if doing incremental update
    if args.incremental and Path(args.existing_questions).exists():
        extractor.load_existing_questions(args.existing_questions)
    
    try:
        # Load thread data
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        threads = data.get('results', [])
        logger.info(f"Processing {len(threads)} threads")
        
        # Extract questions
        new_questions = extractor.extract_from_threads(threads)
        logger.info(f"Extracted {len(new_questions)} new questions")
        
        # Update questions data
        questions_data = extractor.update_questions_data(new_questions)
        
        # Save updated questions
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Questions saved to {args.output}")
        logger.info(f"Total questions: {questions_data['total_questions']}")
        logger.info(f"New questions: {questions_data['new_questions_added']}")
        
        # Print category breakdown
        for category, count in questions_data['questions_by_category'].items():
            logger.info(f"  {category}: {count}")
        
    except Exception as e:
        logger.error(f"Question extraction failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())