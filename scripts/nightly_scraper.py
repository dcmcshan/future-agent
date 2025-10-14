#!/usr/bin/env python3
"""
Nightly Future4200 Thread Scraper
Incremental scraping script to get new threads since last run
"""

import json
import asyncio
import aiohttp
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set
import logging
from datetime import datetime, timedelta
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Future4200NightlyScraper:
    """Handles incremental scraping of Future4200 threads"""
    
    def __init__(self, base_url: str = "https://future4200.com"):
        self.base_url = base_url
        self.session = None
        self.existing_thread_ids = set()
        self.new_threads = []
        self.failed_threads = []
        self.last_scrape_time = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Future-Agent-Bot/1.0 (Cannabis Research)'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def load_existing_threads(self, existing_file: str):
        """Load existing thread IDs to avoid duplicates"""
        try:
            with open(existing_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract thread IDs from existing data
            for result in data.get("results", []):
                if result.get("success", False):
                    thread_data = result.get("data", {})
                    thread_id = thread_data.get("thread_id")
                    if thread_id:
                        self.existing_thread_ids.add(thread_id)
            
            # Get last scrape time
            self.last_scrape_time = data.get("scraping_timestamp")
            logger.info(f"Loaded {len(self.existing_thread_ids)} existing thread IDs")
            
        except Exception as e:
            logger.warning(f"Could not load existing threads: {e}")
            self.existing_thread_ids = set()
    
    async def get_latest_threads(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Get the latest threads from Future4200"""
        all_threads = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/latest?page={page}"
                logger.info(f"Scraping page {page}: {url}")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        threads = self.parse_thread_list(content)
                        
                        if not threads:
                            logger.info(f"No threads found on page {page}, stopping")
                            break
                        
                        # Filter out existing threads
                        new_threads = [t for t in threads if t.get('thread_id') not in self.existing_thread_ids]
                        
                        if not new_threads:
                            logger.info(f"No new threads on page {page}, stopping")
                            break
                        
                        all_threads.extend(new_threads)
                        logger.info(f"Found {len(new_threads)} new threads on page {page}")
                        
                        # Add small delay to be respectful
                        await asyncio.sleep(1)
                        
                    else:
                        logger.error(f"Failed to fetch page {page}: {response.status}")
                        break
                        
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        return all_threads
    
    def parse_thread_list(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse thread list from HTML content"""
        threads = []
        
        # Simple regex-based parsing (could be enhanced with BeautifulSoup)
        thread_pattern = r'href="/t/([^"]+)/(\d+)"'
        matches = re.findall(thread_pattern, html_content)
        
        for slug, thread_id in matches:
            threads.append({
                'thread_id': thread_id,
                'slug': slug,
                'url': f"{self.base_url}/t/{slug}/{thread_id}",
                'discovered_at': datetime.now().isoformat()
            })
        
        return threads
    
    async def scrape_thread_content(self, thread_info: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape detailed content of a single thread"""
        try:
            url = thread_info['url']
            logger.info(f"Scraping thread: {url}")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse thread content
                    thread_data = self.parse_thread_content(content, thread_info)
                    thread_data['scraped_at'] = datetime.now().isoformat()
                    thread_data['success'] = True
                    
                    return {
                        'success': True,
                        'data': thread_data
                    }
                else:
                    logger.error(f"Failed to scrape thread {url}: {response.status}")
                    return {
                        'success': False,
                        'error': f"HTTP {response.status}",
                        'url': url
                    }
                    
        except Exception as e:
            logger.error(f"Error scraping thread {thread_info['url']}: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': thread_info['url']
            }
    
    def parse_thread_content(self, html_content: str, thread_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse detailed thread content from HTML"""
        # Extract title
        title_match = re.search(r'<title>([^<]+)</title>', html_content)
        title = title_match.group(1) if title_match else thread_info.get('slug', 'Untitled')
        
        # Extract author
        author_match = re.search(r'<span class="username">([^<]+)</span>', html_content)
        author = author_match.group(1) if author_match else "Unknown"
        
        # Extract post count
        post_count_match = re.search(r'(\d+)\s+replies?', html_content)
        post_count = int(post_count_match.group(1)) if post_count_match else 0
        
        # Extract view count
        view_count_match = re.search(r'(\d+\.?\d*[kK]?)\s+views?', html_content)
        view_count = self.parse_view_count(view_count_match.group(1)) if view_count_match else 0
        
        # Extract content (simplified - just get the main content area)
        content_match = re.search(r'<div class="post-content">(.*?)</div>', html_content, re.DOTALL)
        content = content_match.group(1) if content_match else ""
        
        # Clean up content
        content = self.clean_html_content(content)
        
        # Generate markdown version
        markdown = self.html_to_markdown(content)
        
        # Extract links
        links = re.findall(r'href="([^"]+)"', content)
        
        return {
            'thread_id': thread_info['thread_id'],
            'title': title,
            'author': author,
            'content': content,
            'markdown': markdown,
            'post_count': post_count,
            'view_count': view_count,
            'url': thread_info['url'],
            'linksOnPage': links,
            'category': self.categorize_thread(title, content),
            'last_activity': datetime.now().isoformat()
        }
    
    def parse_view_count(self, view_str: str) -> int:
        """Parse view count string (e.g., '1.2k' -> 1200)"""
        try:
            if 'k' in view_str.lower():
                return int(float(view_str.lower().replace('k', '')) * 1000)
            return int(view_str)
        except:
            return 0
    
    def clean_html_content(self, content: str) -> str:
        """Clean HTML content"""
        # Remove script and style tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def html_to_markdown(self, html_content: str) -> str:
        """Convert HTML to markdown (simplified)"""
        # Basic HTML to markdown conversion
        markdown = html_content
        
        # Convert headers
        markdown = re.sub(r'<h([1-6])[^>]*>(.*?)</h[1-6]>', r'\n#\1 \2\n', markdown)
        
        # Convert bold
        markdown = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', markdown)
        markdown = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', markdown)
        
        # Convert italic
        markdown = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', markdown)
        markdown = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', markdown)
        
        # Convert links
        markdown = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', markdown)
        
        # Convert line breaks
        markdown = re.sub(r'<br[^>]*>', '\n', markdown)
        
        # Remove remaining HTML tags
        markdown = re.sub(r'<[^>]+>', '', markdown)
        
        return markdown.strip()
    
    def categorize_thread(self, title: str, content: str) -> str:
        """Categorize thread based on title and content"""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ["extract", "extraction", "distill", "distillation", "concentrate"]):
            return "extraction"
        elif any(word in text for word in ["grow", "cultivate", "plant", "seed", "flower"]):
            return "cultivation"
        elif any(word in text for word in ["business", "legal", "regulation", "license", "compliance"]):
            return "business"
        elif any(word in text for word in ["equipment", "machine", "tool", "device", "setup"]):
            return "equipment"
        elif any(word in text for word in ["genetic", "strain", "breed", "hybrid", "phenotype"]):
            return "genetics"
        elif any(word in text for word in ["process", "processing", "cure", "dry", "trim"]):
            return "processing"
        else:
            return "general"
    
    async def scrape_incremental(self, max_pages: int = 10) -> Dict[str, Any]:
        """Run incremental scraping"""
        start_time = time.time()
        
        # Get latest threads
        logger.info("Discovering latest threads...")
        thread_list = await self.get_latest_threads(max_pages)
        
        if not thread_list:
            logger.info("No new threads found")
            return {
                'scraping_timestamp': datetime.now().isoformat(),
                'new_threads_count': 0,
                'total_attempted': 0,
                'successful_scrapes': 0,
                'failed_scrapes': 0,
                'processing_time': time.time() - start_time,
                'results': []
            }
        
        logger.info(f"Found {len(thread_list)} new threads to scrape")
        
        # Scrape thread contents
        results = []
        successful = 0
        failed = 0
        
        for i, thread_info in enumerate(thread_list, 1):
            logger.info(f"Scraping thread {i}/{len(thread_list)}: {thread_info['url']}")
            
            result = await self.scrape_thread_content(thread_info)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
            
            # Add delay between requests
            await asyncio.sleep(0.5)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Scraping complete: {successful} successful, {failed} failed in {processing_time:.2f}s")
        
        return {
            'scraping_timestamp': datetime.now().isoformat(),
            'new_threads_count': len(thread_list),
            'total_attempted': len(thread_list),
            'successful_scrapes': successful,
            'failed_scrapes': failed,
            'processing_time': processing_time,
            'last_scrape_time': self.last_scrape_time,
            'results': results
        }

async def main():
    parser = argparse.ArgumentParser(description='Nightly Future4200 thread scraper')
    parser.add_argument('--output', required=True, help='Output file for scraped data')
    parser.add_argument('--existing', default='data/comprehensive_scraping_results.json', 
                       help='Existing data file to check for duplicates')
    parser.add_argument('--last-run', action='store_true', 
                       help='Use last run time for incremental scraping')
    parser.add_argument('--max-pages', type=int, default=10, 
                       help='Maximum pages to scrape')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    scraper = Future4200NightlyScraper()
    
    # Load existing threads if doing incremental scraping
    if args.last_run and Path(args.existing).exists():
        scraper.load_existing_threads(args.existing)
    
    async with scraper:
        result = await scraper.scrape_incremental(args.max_pages)
    
    # Save results
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to {args.output}")
    logger.info(f"Summary: {result['new_threads_count']} new threads, "
               f"{result['successful_scrapes']} successful, "
               f"{result['failed_scrapes']} failed")

if __name__ == "__main__":
    asyncio.run(main())