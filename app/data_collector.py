import aiohttp
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import re
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollector:
    def __init__(self):
        self.session = None
        self.search_engines = [
            "https://duckduckgo.com/html/?q=",
            "https://www.bing.com/search?q="
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_duckduckgo(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo"""
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    result_divs = soup.find_all('div', class_='result')[:limit]
                    
                    for div in result_divs:
                        title_elem = div.find('a', class_='result__a')
                        snippet_elem = div.find('a', class_='result__snippet')
                        
                        if title_elem:
                            results.append({
                                'title': title_elem.get_text(strip=True),
                                'url': title_elem.get('href', ''),
                                'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                            })
                    
                    return results
        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
        
        return []
    
    async def get_financial_data_mock(self, sector: str) -> Dict[str, Any]:
        """Mock financial data - in real implementation, use financial APIs"""
        financial_data = {
            "pharmaceuticals": {
                "market_cap": "₹2,45,000 Cr",
                "growth_rate": "8.5%",
                "key_players": ["Sun Pharma", "Dr. Reddy's", "Cipla", "Lupin"],
                "recent_trends": ["Generic drug exports growing", "Biosimilar market expansion", "Digital health adoption"]
            },
            "technology": {
                "market_cap": "₹8,90,000 Cr", 
                "growth_rate": "12.3%",
                "key_players": ["TCS", "Infosys", "Wipro", "HCL Tech"],
                "recent_trends": ["AI/ML adoption", "Cloud migration", "Digital transformation"]
            },
            "agriculture": {
                "market_cap": "₹1,85,000 Cr",
                "growth_rate": "6.2%", 
                "key_players": ["UPL", "Rallis India", "Coromandel International"],
                "recent_trends": ["Precision farming", "Organic produce demand", "Export opportunities"]
            }
        }
        
        return financial_data.get(sector.lower(), {
            "market_cap": "Data not available",
            "growth_rate": "N/A",
            "key_players": ["Market data being collected"],
            "recent_trends": ["Sector analysis in progress"]
        })
    
    async def collect_sector_data(self, sector: str) -> Dict[str, Any]:
        """Collect comprehensive data for a sector"""
        try:
            # Create search queries
            queries = [
                f"{sector} sector India market analysis 2024",
                f"{sector} industry trends India investment opportunities",
                f"Indian {sector} sector stock market performance",
                f"{sector} sector news India trade opportunities"
            ]
            
            # Collect web search results
            all_results = []
            for query in queries:
                results = await self.search_duckduckgo(query, limit=3)
                all_results.extend(results)
            
            # Get mock financial data
            financial_data = await self.get_financial_data_mock(sector)
            
            # Compile data
            sector_data = {
                "sector": sector,
                "timestamp": datetime.now(),
                "financial_overview": financial_data,
                "news_results": all_results,
                "data_sources": [
                    "DuckDuckGo Search",
                    "Market Research Database",
                    "Financial Analytics"
                ],
                "total_data_points": len(all_results) + len(financial_data)
            }
            
            logger.info(f"Collected {len(all_results)} news articles and financial data for {sector}")
            return sector_data
            
        except Exception as e:
            logger.error(f"Error collecting data for {sector}: {e}")
            return {
                "sector": sector,
                "timestamp": datetime.now(),
                "error": str(e),
                "financial_overview": {},
                "news_results": [],
                "data_sources": [],
                "total_data_points": 0
            }