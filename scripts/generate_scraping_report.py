#!/usr/bin/env python3
"""
Generate Scraping Report Script
Generates a comprehensive report of the nightly scraping results
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScrapingReportGenerator:
    """Generates comprehensive scraping reports"""
    
    def __init__(self):
        self.report_data = {}
    
    def generate_report(self, new_threads: int, incremental_file: str = None) -> Dict[str, Any]:
        """Generate scraping report"""
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'scraping_summary': {
                'new_threads_found': new_threads,
                'scraping_successful': new_threads > 0,
                'report_generated_at': datetime.now().isoformat()
            },
            'data_metrics': self.calculate_data_metrics(),
            'trends': self.analyze_trends(),
            'recommendations': self.generate_recommendations(new_threads),
            'next_scrape_scheduled': self.calculate_next_scrape_time()
        }
        
        # Add incremental data if available
        if incremental_file and Path(incremental_file).exists():
            try:
                with open(incremental_file, 'r', encoding='utf-8') as f:
                    incremental_data = json.load(f)
                
                report['incremental_details'] = {
                    'scraping_timestamp': incremental_data.get('scraping_timestamp'),
                    'processing_time': incremental_data.get('processing_time', 0),
                    'successful_scrapes': incremental_data.get('successful_scrapes', 0),
                    'failed_scrapes': incremental_data.get('failed_scrapes', 0),
                    'success_rate': self.calculate_success_rate(incremental_data)
                }
            except Exception as e:
                logger.warning(f"Could not load incremental data: {e}")
        
        return report
    
    def calculate_data_metrics(self) -> Dict[str, Any]:
        """Calculate data metrics"""
        try:
            # Load comprehensive data
            with open('data/comprehensive_scraping_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_threads = data.get('total_threads', 0)
            scraped_threads = data.get('scraped_threads', 0)
            failed_threads = data.get('failed_threads', 0)
            
            # Calculate success rate
            success_rate = (scraped_threads / total_threads * 100) if total_threads > 0 else 0
            
            # Estimate data size
            file_size = Path('data/comprehensive_scraping_results.json').stat().st_size
            data_size_mb = file_size / (1024 * 1024)
            
            return {
                'total_threads': total_threads,
                'successful_scrapes': scraped_threads,
                'failed_scrapes': failed_threads,
                'success_rate_percent': round(success_rate, 2),
                'data_size_mb': round(data_size_mb, 2),
                'last_updated': data.get('scraping_timestamp', 'Unknown')
            }
        except Exception as e:
            logger.warning(f"Could not calculate data metrics: {e}")
            return {
                'total_threads': 0,
                'successful_scrapes': 0,
                'failed_scrapes': 0,
                'success_rate_percent': 0,
                'data_size_mb': 0,
                'last_updated': 'Unknown'
            }
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze scraping trends"""
        try:
            # Load questions data for trend analysis
            with open('data/extracted_questions.json', 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            total_questions = questions_data.get('total_questions', 0)
            category_breakdown = questions_data.get('questions_by_category', {})
            
            # Calculate category percentages
            category_percentages = {}
            for category, count in category_breakdown.items():
                percentage = (count / total_questions * 100) if total_questions > 0 else 0
                category_percentages[category] = round(percentage, 2)
            
            return {
                'total_questions_extracted': total_questions,
                'category_distribution': category_percentages,
                'most_common_category': max(category_breakdown.items(), key=lambda x: x[1])[0] if category_breakdown else 'None',
                'questions_per_thread': round(total_questions / max(1, self.calculate_data_metrics()['total_threads']), 2)
            }
        except Exception as e:
            logger.warning(f"Could not analyze trends: {e}")
            return {
                'total_questions_extracted': 0,
                'category_distribution': {},
                'most_common_category': 'None',
                'questions_per_thread': 0
            }
    
    def calculate_success_rate(self, incremental_data: Dict[str, Any]) -> float:
        """Calculate success rate from incremental data"""
        total_attempted = incremental_data.get('total_attempted', 0)
        successful = incremental_data.get('successful_scrapes', 0)
        
        if total_attempted == 0:
            return 0.0
        
        return round((successful / total_attempted) * 100, 2)
    
    def generate_recommendations(self, new_threads: int) -> List[str]:
        """Generate recommendations based on scraping results"""
        recommendations = []
        
        if new_threads == 0:
            recommendations.append("No new threads found - consider increasing scraping frequency or expanding search criteria")
            recommendations.append("Review scraping patterns to ensure we're not missing new content")
        elif new_threads < 5:
            recommendations.append("Low number of new threads - monitor for potential issues with scraping")
            recommendations.append("Consider adjusting scraping parameters for better coverage")
        elif new_threads > 100:
            recommendations.append("High number of new threads - consider optimizing scraping performance")
            recommendations.append("Monitor system resources during peak scraping times")
        
        # Data quality recommendations
        data_metrics = self.calculate_data_metrics()
        if data_metrics['success_rate_percent'] < 80:
            recommendations.append("Low success rate detected - investigate failed scraping attempts")
        
        if data_metrics['data_size_mb'] > 500:
            recommendations.append("Large data file size - consider data compression or archiving old threads")
        
        # General recommendations
        recommendations.append("Monitor scraping logs for any recurring errors")
        recommendations.append("Consider implementing data validation checks")
        recommendations.append("Review and update scraping patterns based on forum changes")
        
        return recommendations
    
    def calculate_next_scrape_time(self) -> str:
        """Calculate next scheduled scrape time"""
        # Next scrape is scheduled for 2 AM UTC daily
        now = datetime.now()
        next_scrape = now.replace(hour=2, minute=0, second=0, microsecond=0)
        
        # If it's already past 2 AM today, schedule for tomorrow
        if now.hour >= 2:
            next_scrape += timedelta(days=1)
        
        return next_scrape.isoformat()
    
    def save_report(self, report: Dict[str, Any], output_path: str):
        """Save report to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Generate scraping report')
    parser.add_argument('--output', required=True, help='Output report file')
    parser.add_argument('--new-threads', type=int, default=0, help='Number of new threads found')
    parser.add_argument('--incremental-file', help='Incremental scraping data file')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    generator = ScrapingReportGenerator()
    
    try:
        # Generate report
        report = generator.generate_report(args.new_threads, args.incremental_file)
        
        # Save report
        generator.save_report(report, args.output)
        
        # Print summary
        logger.info("Scraping Report Generated:")
        logger.info(f"  New threads: {args.new_threads}")
        logger.info(f"  Total threads: {report['data_metrics']['total_threads']}")
        logger.info(f"  Success rate: {report['data_metrics']['success_rate_percent']}%")
        logger.info(f"  Data size: {report['data_metrics']['data_size_mb']} MB")
        logger.info(f"  Next scrape: {report['next_scrape_scheduled']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())