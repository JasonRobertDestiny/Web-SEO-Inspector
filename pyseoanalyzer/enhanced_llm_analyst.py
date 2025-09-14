"""
Enhanced LLM Analyst with multi-data source integration for SEO Agent.

This module extends the existing LLM analysis capabilities to incorporate
Google Analytics and Search Console data for comprehensive SEO insights.
"""

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from .siliconflow_llm import SiliconFlowLLM

import asyncio
import json
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class DataDrivenInsights(BaseModel):
    """Enhanced insights incorporating Google data."""
    performance_summary: str = Field(description="Summary of overall performance")
    opportunity_areas: List[str] = Field(description="Key areas for improvement")
    strategic_priorities: List[str] = Field(description="Strategic priorities based on data")
    quick_wins: List[str] = Field(description="Quick improvements to implement")
    long_term_projects: List[str] = Field(description="Major projects for long-term success")


class TrendAnalysis(BaseModel):
    """Analysis of trends over time."""
    traffic_trends: str = Field(description="Analysis of traffic patterns")
    ranking_changes: str = Field(description="Search ranking trends")
    user_behavior_changes: str = Field(description="Changes in user behavior")
    content_performance: str = Field(description="Content performance trends")


class PredictiveInsights(BaseModel):
    """Predictive recommendations based on data patterns."""
    future_opportunities: List[str] = Field(description="Predicted opportunities")
    risk_areas: List[str] = Field(description="Potential risks to address")
    growth_predictions: str = Field(description="Growth predictions")
    competitive_advantages: List[str] = Field(description="Potential competitive advantages")


class EnhancedLLMSEOAnalyst:
    """Enhanced LLM SEO Analyst with multi-data source integration."""
    
    def __init__(self, model_name: str = "claude-3-sonnet-20240229", api_key: Optional[str] = None, use_siliconflow: bool = False, siliconflow_api_key: Optional[str] = None, siliconflow_model: Optional[str] = None):
        """Initialize the enhanced analyst.
        
        Args:
            model_name: Anthropic model name
            api_key: Anthropic API key
            use_siliconflow: Whether to use Silicon Flow API
            siliconflow_api_key: Silicon Flow API key
            siliconflow_model: Silicon Flow model to use (defaults to env var or Qwen/Qwen2.5-VL-72B-Instruct)
        """
        self.use_siliconflow = use_siliconflow or bool(os.getenv("SILICONFLOW_API_KEY"))
        
        if self.use_siliconflow:
            # Get model from parameter, env var, or default
            model = siliconflow_model or os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-VL-72B-Instruct")
            self.siliconflow_llm = SiliconFlowLLM(siliconflow_api_key, model)
            self.llm = None
        else:
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
            
            self.llm = ChatAnthropic(
                model=model_name,
                anthropic_api_key=self.api_key,
                temperature=0.1,
                max_tokens=4000
            )
            self.siliconflow_llm = None
        
        if not self.use_siliconflow:
            self.setup_parsers()
            self.setup_chains()
    
    def setup_parsers(self):
        """Setup output parsers for structured responses."""
        self.insights_parser = PydanticOutputParser(pydantic_object=DataDrivenInsights)
        self.trends_parser = PydanticOutputParser(pydantic_object=TrendAnalysis)
        self.predictive_parser = PydanticOutputParser(pydantic_object=PredictiveInsights)
    
    def setup_chains(self):
        """Setup analysis chains with enhanced prompts."""
        
        # Enhanced insights chain incorporating Google data
        insights_prompt = PromptTemplate(
            template="""
            You are an expert SEO analyst with access to comprehensive website data.
            Analyze the following combined data to provide strategic SEO insights:
            
            WEBSITE SEO ANALYSIS:
            {seo_analysis}
            
            GOOGLE ANALYTICS DATA:
            {analytics_data}
            
            SEARCH CONSOLE DATA:
            {search_data}
            
            PAGE PERFORMANCE:
            {page_performance}
            
            Based on this comprehensive data, provide:
            1. Overall performance summary
            2. Key opportunity areas for improvement
            3. Strategic priorities
            4. Quick wins (high impact, low effort)
            5. Long-term strategic projects
            
            {format_instructions}
            """,
            input_variables=["seo_analysis", "analytics_data", "search_data", "page_performance"],
            partial_variables={"format_instructions": self.insights_parser.get_format_instructions()}
        )
        
        # Trend analysis chain
        trends_prompt = PromptTemplate(
            template="""
            Analyze the following performance data to identify trends and patterns:
            
            CURRENT PERFORMANCE METRICS:
            {performance_summary}
            
            HISTORICAL CONTEXT (if available):
            {historical_data}
            
            PAGE-LEVEL INSIGHTS:
            {page_insights}
            
            Provide analysis on:
            1. Traffic trends and patterns
            2. Search ranking changes
            3. User behavior shifts
            4. Content performance trends
            5. Seasonal or cyclical patterns
            
            {format_instructions}
            """,
            input_variables=["performance_summary", "historical_data", "page_insights"],
            partial_variables={"format_instructions": self.trends_parser.get_format_instructions()}
        )
        
        # Predictive insights chain
        predictive_prompt = PromptTemplate(
            template="""
            Based on the comprehensive analysis below, provide predictive insights and recommendations:
            
            CURRENT STATE:
            {current_analysis}
            
            PERFORMANCE TRENDS:
            {trend_analysis}
            
            COMPETITIVE CONTEXT:
            {competitive_context}
            
            MARKET OPPORTUNITIES:
            {market_opportunities}
            
            Provide predictions for:
            1. Future growth opportunities
            2. Potential risks and challenges
            3. Growth trajectory predictions
            4. Sustainable competitive advantages
            
            {format_instructions}
            """,
            input_variables=["current_analysis", "trend_analysis", "competitive_context", "market_opportunities"],
            partial_variables={"format_instructions": self.predictive_parser.get_format_instructions()}
        )
        
        self.insights_chain = (
            {"seo_analysis": RunnablePassthrough(), 
             "analytics_data": RunnablePassthrough(),
             "search_data": RunnablePassthrough(),
             "page_performance": RunnablePassthrough()}
            | insights_prompt
            | self.llm
            | self.insights_parser
        )
        
        self.trends_chain = (
            {"performance_summary": RunnablePassthrough(),
             "historical_data": RunnablePassthrough(),
             "page_insights": RunnablePassthrough()}
            | trends_prompt
            | self.llm
            | self.trends_parser
        )
        
        self.predictive_chain = (
            {"current_analysis": RunnablePassthrough(),
             "trend_analysis": RunnablePassthrough(),
             "competitive_context": RunnablePassthrough(),
             "market_opportunities": RunnablePassthrough()}
            | predictive_prompt
            | self.llm
            | self.predictive_parser
        )
    
    async def analyze_comprehensive_data(
        self,
        seo_analysis: Dict[str, Any],
        google_insights: Dict[str, Any],
        competitive_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis combining all data sources.
        
        Args:
            seo_analysis: Traditional SEO analysis results
            google_insights: Google Analytics and Search Console data
            competitive_context: Optional competitive analysis data
            
        Returns:
            Comprehensive analysis results with strategic insights
        """
        # Extract data from Google insights
        analytics_summary = google_insights.get('analytics_summary', {})
        search_summary = google_insights.get('search_summary', {})
        page_performance = google_insights.get('page_performance', {})
        recommendations = google_insights.get('recommendations', [])
        
        # Prepare data for analysis
        seo_summary = self._prepare_seo_summary(seo_analysis)
        analytics_str = self._format_analytics_data(analytics_summary)
        search_str = self._format_search_data(search_summary)
        performance_str = self._format_page_performance(page_performance)
        
        # Run parallel analysis chains
        insights_task = self.insights_chain.ainvoke({
            "seo_analysis": seo_summary,
            "analytics_data": analytics_str,
            "search_data": search_str,
            "page_performance": performance_str
        })
        
        trends_task = self.trends_chain.ainvoke({
            "performance_summary": f"Analytics: {analytics_str}\nSearch: {search_str}",
            "historical_data": "Historical comparison data not available in current implementation",
            "page_insights": performance_str
        })
        
        predictive_task = self.predictive_chain.ainvoke({
            "current_analysis": f"SEO Analysis: {seo_summary}\nPerformance: {analytics_str}",
            "trend_analysis": "Trend analysis will be completed based on current metrics",
            "competitive_context": json.dumps(competitive_context or {}),
            "market_opportunities": "Market opportunities based on current search performance"
        })
        
        # Wait for all analyses to complete
        insights, trends, predictive = await asyncio.gather(
            insights_task, trends_task, predictive_task
        )
        
        # Combine all results
        comprehensive_analysis = {
            "data_driven_insights": insights.dict(),
            "trend_analysis": trends.dict(),
            "predictive_insights": predictive.dict(),
            "google_data_recommendations": recommendations,
            "analysis_timestamp": str(asyncio.get_event_loop().time())
        }
        
        return comprehensive_analysis
    
    def _prepare_seo_summary(self, seo_analysis: Dict[str, Any]) -> str:
        """Prepare SEO analysis summary for LLM processing."""
        summary_parts = []
        
        # Basic metrics
        pages_count = len(seo_analysis.get('pages', []))
        keywords_count = len(seo_analysis.get('keywords', []))
        errors_count = len(seo_analysis.get('errors', []))
        
        summary_parts.append(f"Website analyzed: {pages_count} pages, {keywords_count} keywords, {errors_count} errors")
        
        # SEO optimization insights
        optimization = seo_analysis.get('optimization_recommendations', {})
        if optimization:
            score = optimization.get('overall_score', 0)
            summary_parts.append(f"SEO Score: {score}/100")
            
            issues_by_priority = optimization.get('issues_by_priority', {})
            for priority, count in issues_by_priority.items():
                if count > 0:
                    summary_parts.append(f"{priority.title()} priority issues: {count}")
        
        return "\n".join(summary_parts)
    
    def _format_analytics_data(self, analytics_data: Dict[str, Any]) -> str:
        """Format Google Analytics data for LLM analysis."""
        if not analytics_data:
            return "No analytics data available"
        
        formatted_parts = []
        
        for metric, value in analytics_data.items():
            if isinstance(value, (int, float)):
                formatted_parts.append(f"{metric}: {value}")
        
        return "\n".join(formatted_parts)
    
    def _format_search_data(self, search_data: Dict[str, Any]) -> str:
        """Format Search Console data for LLM analysis."""
        if not search_data:
            return "No search console data available"
        
        formatted_parts = []
        
        for metric, value in search_data.items():
            if isinstance(value, (int, float)):
                if metric in ['avg_ctr', 'avg_position']:
                    formatted_parts.append(f"{metric}: {value:.2f}")
                else:
                    formatted_parts.append(f"{metric}: {value}")
        
        return "\n".join(formatted_parts)
    
    def _format_page_performance(self, page_performance: Dict[str, Any]) -> str:
        """Format page-level performance data."""
        if not page_performance:
            return "No page performance data available"
        
        # Show top 5 pages by performance
        formatted_parts = []
        top_pages = list(page_performance.items())[:5]
        
        for page_path, metrics in top_pages:
            pageviews = metrics.get('pageviews', 0)
            bounce_rate = metrics.get('bounce_rate', 0)
            search_data = metrics.get('search_data', {})
            
            page_info = f"Page {page_path}: {pageviews} views, {bounce_rate:.1%} bounce rate"
            if search_data:
                position = search_data.get('position', 0)
                ctr = search_data.get('ctr', 0)
                page_info += f", Search position: {position:.1f}, CTR: {ctr:.2%}"
            
            formatted_parts.append(page_info)
        
        return "\n".join(formatted_parts)
    
    def generate_strategic_report(self, comprehensive_analysis: Dict[str, Any]) -> str:
        """Generate a strategic SEO report based on comprehensive analysis."""
        
        insights = comprehensive_analysis.get('data_driven_insights', {})
        trends = comprehensive_analysis.get('trend_analysis', {})
        predictive = comprehensive_analysis.get('predictive_insights', {})
        
        report = """
# SEO Agent Strategic Analysis Report

## Executive Summary
{performance_summary}

## Key Opportunity Areas
{opportunity_areas}

## Strategic Priorities
{strategic_priorities}

## Quick Wins (High Impact, Low Effort)
{quick_wins}

## Long-term Strategic Projects
{long_term_projects}

## Performance Trends Analysis
{trend_analysis}

## Predictive Insights & Future Opportunities
{predictive_insights}

## Action Plan
1. Immediate actions (next 30 days)
2. Short-term projects (1-3 months)
3. Long-term initiatives (3-12 months)
""".format(
            performance_summary=insights.get('performance_summary', 'Analysis in progress'),
            opportunity_areas='\n'.join(f'- {area}' for area in insights.get('opportunity_areas', [])),
            strategic_priorities='\n'.join(f'- {priority}' for priority in insights.get('strategic_priorities', [])),
            quick_wins='\n'.join(f'- {win}' for win in insights.get('quick_wins', [])),
            long_term_projects='\n'.join(f'- {project}' for project in insights.get('long_term_projects', [])),
            trend_analysis=f"Traffic: {trends.get('traffic_trends', 'Analyzing...')}\nRankings: {trends.get('ranking_changes', 'Analyzing...')}",
            predictive_insights='\n'.join(f'- {insight}' for insight in predictive.get('future_opportunities', []))
        )
        
        return report


# Example usage
async def main():
    """Example of using the enhanced LLM analyst."""
    analyst = EnhancedLLMSEOAnalyst()
    
    # Sample data (in real usage, this would come from actual analysis)
    seo_analysis = {
        "pages": [{"url": "https://example.com"}],
        "keywords": [{"word": "example", "count": 10}],
        "errors": [],
        "optimization_recommendations": {
            "overall_score": 75,
            "issues_by_priority": {"critical": 2, "high": 5}
        }
    }
    
    google_insights = {
        "analytics_summary": {"sessions": 1000, "pageviews": 2500},
        "search_summary": {"total_clicks": 150, "total_impressions": 10000},
        "page_performance": {},
        "recommendations": []
    }
    
    # Run comprehensive analysis
    results = await analyst.analyze_comprehensive_data(
        seo_analysis=seo_analysis,
        google_insights=google_insights
    )
    
    # Generate strategic report
    report = analyst.generate_strategic_report(results)
    print(report)


if __name__ == "__main__":
    asyncio.run(main())