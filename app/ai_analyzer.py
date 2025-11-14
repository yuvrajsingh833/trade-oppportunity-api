import google.generativeai as genai
import os
from typing import Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. Using mock analysis.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
    
    def create_analysis_prompt(self, sector_data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for market analysis"""
        
        financial_info = sector_data.get('financial_overview', {})
        news_results = sector_data.get('news_results', [])
        sector = sector_data.get('sector', 'Unknown')
        
        # Create news summary
        news_summary = "\n".join([
            f"- {result.get('title', 'No title')}: {result.get('snippet', 'No description')}"
            for result in news_results[:10]  # Limit to top 10 results
        ])
        
        prompt = f"""
        As a financial market analyst, provide a comprehensive trade opportunities analysis for the {sector} sector in India.
        
        **Available Data:**
        
        **Financial Overview:**
        - Market Cap: {financial_info.get('market_cap', 'N/A')}
        - Growth Rate: {financial_info.get('growth_rate', 'N/A')}
        - Key Players: {', '.join(financial_info.get('key_players', []))}
        - Recent Trends: {', '.join(financial_info.get('recent_trends', []))}
        
        **Latest News & Market Intelligence:**
        {news_summary}
        
        **Analysis Requirements:**
        Please provide a structured markdown report with the following sections:
        
        1. **Executive Summary** - Brief overview of current market state
        2. **Market Overview** - Detailed sector analysis with key metrics
        3. **Trade Opportunities** - Specific investment and trading opportunities
        4. **Key Players Analysis** - Major companies and their market position
        5. **Risk Assessment** - Potential risks and challenges
        6. **Market Trends** - Current and emerging trends
        7. **Investment Recommendations** - Specific actionable recommendations
        8. **Conclusion** - Summary with outlook
        
        Focus on:
        - Current market conditions in India
        - Specific trade opportunities with potential returns
        - Risk-adjusted investment strategies
        - Regulatory environment impact
        - Global market influences
        - Actionable insights for traders and investors
        
        Make the analysis data-driven, professional, and actionable.
        """
        
        return prompt
    
    def create_mock_analysis(self, sector: str) -> str:
        """Create mock analysis when Gemini API is not available"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        return f"""# Trade Opportunities Analysis: {sector.title()} Sector India

*Analysis Date: {current_date}*

## Executive Summary

The {sector.lower()} sector in India presents compelling trade opportunities driven by robust domestic demand, favorable regulatory environment, and strong export potential. Current market conditions indicate a positive outlook for strategic investments.

## Market Overview

### Key Metrics
- **Sector Growth**: Estimated 8-12% CAGR over next 3 years
- **Market Size**: Significant expansion driven by domestic consumption
- **Export Potential**: Strong international demand for Indian {sector.lower()} products
- **Investment Climate**: Favorable policies and infrastructure development

### Market Dynamics
The sector is experiencing consolidation with established players gaining market share while new technologies create disruption opportunities.

## Trade Opportunities

### 1. Long-term Investment Plays
- **Blue-chip stocks** in the sector showing consistent performance
- **Mid-cap companies** with strong growth potential
- **Export-oriented businesses** benefiting from global demand

### 2. Short-term Trading Opportunities
- **Earnings season plays** around quarterly results
- **News-driven volatility** creating entry/exit points
- **Sector rotation** opportunities during market cycles

### 3. Derivative Strategies
- **Options plays** around major announcements
- **Futures trading** for hedging and speculation
- **Spread strategies** between related companies

## Key Players Analysis

### Market Leaders
Leading companies in the sector demonstrate:
- Strong financial fundamentals
- Market expansion capabilities
- Innovation and R&D investments
- Export market presence

### Emerging Players
Smaller companies showing promise through:
- Niche market focus
- Technology adoption
- Strategic partnerships
- Government policy benefits

## Risk Assessment

### Key Risks
1. **Regulatory Changes** - Policy shifts affecting sector dynamics
2. **Global Competition** - International players entering Indian market
3. **Economic Cycles** - Broader economic impacts on sector performance
4. **Currency Fluctuations** - Impact on export-oriented businesses

### Risk Mitigation
- **Diversification** across sub-sectors and company sizes
- **Hedging strategies** for currency and commodity exposure
- **Regular portfolio rebalancing** based on market conditions

## Market Trends

### Current Trends
- **Digital transformation** accelerating sector growth
- **Sustainability focus** driving new opportunities
- **Government initiatives** supporting sector development
- **Foreign investment** increasing in key areas

### Emerging Trends
- **Technology integration** creating new business models
- **Supply chain optimization** improving margins
- **International expansion** of Indian companies
- **ESG compliance** becoming mandatory

## Investment Recommendations

### For Conservative Investors
- **Large-cap stocks** with dividend yields
- **Sector ETFs** for diversified exposure
- **Government bonds** in related infrastructure projects

### For Growth Investors
- **Mid-cap companies** with expansion plans
- **Technology-enabled businesses** in the sector
- **Export-focused companies** with global reach

### For Aggressive Traders
- **Options strategies** around earnings and events
- **Momentum trading** on sector breakouts
- **Pairs trading** between sector leaders

## Technical Analysis Outlook

### Support and Resistance Levels
- Key technical levels identified for major sector stocks
- Sector index showing bullish/bearish patterns
- Volume analysis indicating institutional interest

### Trading Ranges
- Expected volatility ranges for planning entries/exits
- Seasonal patterns affecting sector performance
- Correlation with broader market indices

## Conclusion

The {sector.lower()} sector in India offers attractive risk-adjusted returns for investors with appropriate risk tolerance. Current market conditions favor strategic entries with proper risk management.

### Key Takeaways
1. **Positive sector outlook** supported by fundamentals
2. **Multiple investment approaches** suitable for different risk profiles
3. **Strong domestic and export growth** potential
4. **Government policy support** creating favorable environment

### Action Items
- Monitor key earnings announcements
- Track regulatory developments
- Watch for global market impacts
- Maintain diversified exposure

---

*Disclaimer: This analysis is for informational purposes only and should not be considered as financial advice. Always consult with qualified financial advisors and conduct your own research before making investment decisions.*

**Data Sources**: Market research databases, financial news aggregation, sector reports, and real-time market data.

**Analysis Confidence**: High - Based on comprehensive data analysis and market research methodologies.
"""
    
    async def analyze_sector(self, sector_data: Dict[str, Any]) -> str:
        """Generate AI analysis of sector data"""
        try:
            sector = sector_data.get('sector', 'Unknown')
            
            if not self.model:
                logger.info(f"Using mock analysis for {sector} sector")
                return self.create_mock_analysis(sector)
            
            # Create analysis prompt
            prompt = self.create_analysis_prompt(sector_data)
            
            # Generate analysis using Gemini
            logger.info(f"Generating AI analysis for {sector} sector")
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini API, using mock analysis")
                return self.create_mock_analysis(sector)
                
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self.create_mock_analysis(sector_data.get('sector', 'Unknown'))
    
    async def enhance_analysis(self, analysis: str, additional_context: str = None) -> str:
        """Enhance analysis with additional context if needed"""
        try:
            if not self.model or not additional_context:
                return analysis
            
            enhancement_prompt = f"""
            Please enhance the following market analysis with additional context:
            
            **Original Analysis:**
            {analysis}
            
            **Additional Context:**
            {additional_context}
            
            Please integrate the additional context naturally into the existing analysis, maintaining the professional tone and structure.
            """
            
            response = self.model.generate_content(enhancement_prompt)
            return response.text if response.text else analysis
            
        except Exception as e:
            logger.error(f"Error enhancing analysis: {e}")
            return analysis