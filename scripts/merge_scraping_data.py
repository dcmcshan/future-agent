#!/usr/bin/env python3
"""
Merge Scraping Data Script
Merges incremental scraping results with existing comprehensive data
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataMerger:
    """Handles merging of scraping data"""
    
    def __init__(self):
        self.existing_data = {}
        self.incremental_data = {}
        self.merged_data = {}
    
    def load_existing_data(self, file_path: str):
        """Load existing comprehensive data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.existing_data = json.load(f)
            logger.info(f"Loaded existing data with {len(self.existing_data.get('results', []))} threads")
        except Exception as e:
            logger.error(f"Failed to load existing data: {e}")
            self.existing_data = {
                'scraping_timestamp': datetime.now().isoformat(),
                'total_threads': 0,
                'scraped_threads': 0,
                'failed_threads': 0,
                'results': []
            }
    
    def load_incremental_data(self, file_path: str):
        """Load incremental scraping data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.incremental_data = json.load(f)
            logger.info(f"Loaded incremental data with {self.incremental_data.get('new_threads_count', 0)} new threads")
        except Exception as e:
            logger.error(f"Failed to load incremental data: {e}")
            raise
    
    def merge_data(self) -> Dict[str, Any]:
        """Merge existing and incremental data"""
        # Start with existing data
        self.merged_data = self.existing_data.copy()
        
        # Update metadata
        self.merged_data['scraping_timestamp'] = self.incremental_data['scraping_timestamp']
        self.merged_data['last_update'] = datetime.now().isoformat()
        
        # Update counts
        existing_results = self.existing_data.get('results', [])
        incremental_results = self.incremental_data.get('results', [])
        
        # Count successful and failed threads
        existing_successful = sum(1 for r in existing_results if r.get('success', False))
        existing_failed = len(existing_results) - existing_successful
        
        incremental_successful = self.incremental_data.get('successful_scrapes', 0)
        incremental_failed = self.incremental_data.get('failed_scrapes', 0)
        
        # Update totals
        self.merged_data['total_threads'] = len(existing_results) + len(incremental_results)
        self.merged_data['scraped_threads'] = existing_successful + incremental_successful
        self.merged_data['failed_threads'] = existing_failed + incremental_failed
        
        # Add incremental results
        self.merged_data['results'].extend(incremental_results)
        
        # Add update summary
        self.merged_data['update_summary'] = {
            'timestamp': datetime.now().isoformat(),
            'new_threads_added': len(incremental_results),
            'successful_new_threads': incremental_successful,
            'failed_new_threads': incremental_failed,
            'total_threads_after_update': len(self.merged_data['results']),
            'processing_time': self.incremental_data.get('processing_time', 0)
        }
        
        logger.info(f"Merged data: {len(incremental_results)} new threads added")
        logger.info(f"Total threads: {len(self.merged_data['results'])}")
        
        return self.merged_data
    
    def save_merged_data(self, output_path: str):
        """Save merged data to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.merged_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Merged data saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save merged data: {e}")
            raise
    
    def validate_merge(self) -> bool:
        """Validate the merged data"""
        try:
            # Check that all required fields are present
            required_fields = ['scraping_timestamp', 'total_threads', 'scraped_threads', 'failed_threads', 'results']
            for field in required_fields:
                if field not in self.merged_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Check that results is a list
            if not isinstance(self.merged_data['results'], list):
                logger.error("Results field is not a list")
                return False
            
            # Check that counts are consistent
            total_results = len(self.merged_data['results'])
            if self.merged_data['total_threads'] != total_results:
                logger.warning(f"Total threads count ({self.merged_data['total_threads']}) doesn't match results length ({total_results})")
            
            # Count successful results
            successful_count = sum(1 for r in self.merged_data['results'] if r.get('success', False))
            if self.merged_data['scraped_threads'] != successful_count:
                logger.warning(f"Scraped threads count ({self.merged_data['scraped_threads']}) doesn't match successful results ({successful_count})")
            
            logger.info("Data validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Merge scraping data')
    parser.add_argument('--existing', required=True, help='Existing comprehensive data file')
    parser.add_argument('--incremental', required=True, help='Incremental scraping data file')
    parser.add_argument('--output', required=True, help='Output file for merged data')
    parser.add_argument('--validate', action='store_true', help='Validate merged data')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    merger = DataMerger()
    
    try:
        # Load data
        merger.load_existing_data(args.existing)
        merger.load_incremental_data(args.incremental)
        
        # Merge data
        merged_data = merger.merge_data()
        
        # Validate if requested
        if args.validate:
            if not merger.validate_merge():
                logger.error("Data validation failed")
                return 1
        
        # Save merged data
        merger.save_merged_data(args.output)
        
        logger.info("Data merge completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Data merge failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())