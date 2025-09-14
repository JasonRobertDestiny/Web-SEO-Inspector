"""Silicon Flow API integration for SEO analysis.

This module provides integration with Silicon Flow's API as an alternative
to Anthropic's Claude for LLM-powered SEO analysis.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class SiliconFlowLLM:
    """Silicon Flow API client for LLM analysis."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Silicon Flow LLM client.
        
        Args:
            api_key: Silicon Flow API key (defaults to SILICONFLOW_API_KEY env var)
            model: Model to use (defaults to SILICONFLOW_MODEL env var or Qwen/Qwen2.5-VL-72B-Instruct)
        """
        self.api_key = api_key or os.getenv("SILICONFLOW_API_KEY")
        self.model = model or os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-VL-72B-Instruct")
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("Silicon Flow API key is required. Set SILICONFLOW_API_KEY environment variable.")
    
    async def _make_request(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        """
        Make async request to Silicon Flow API.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            
        Returns:
            Response content as string
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Silicon Flow API error {response.status}: {error_text}")
                        raise Exception(f"API request failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error making request to Silicon Flow API: {e}")
            raise
    
    async def analyze_seo_data(self, seo_data: Dict[str, Any], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze SEO data using Silicon Flow LLM.
        
        Args:
            seo_data: SEO analysis data
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        if analysis_type == "entity":
            return await self._analyze_entity_optimization(seo_data)
        elif analysis_type == "credibility":
            return await self._analyze_credibility(seo_data)
        elif analysis_type == "conversation":
            return await self._analyze_conversation_readiness(seo_data)
        elif analysis_type == "platform":
            return await self._analyze_platform_presence(seo_data)
        elif analysis_type == "recommendations":
            return await self._generate_recommendations(seo_data)
        else:
            return await self._comprehensive_analysis(seo_data)
    
    async def _analyze_entity_optimization(self, seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze entity optimization aspects."""
        prompt = f"""
        分析以下SEO数据的实体优化情况：
        
        数据：
        {json.dumps(seo_data, indent=2, ensure_ascii=False)}
        
        请分析：
        1. 实体理解和知识面板准备度
        2. 品牌可信度信号
        3. 实体关系和提及
        4. 主题实体连接
        5. Schema标记有效性
        
        请以JSON格式返回分析结果，包含：
        - entity_assessment: 详细的实体优化分析
        - knowledge_panel_readiness: 0-100的评分
        - key_improvements: 需要改进的前3个方面
        
        只返回JSON格式的结果，不要包含其他解释文字。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self._make_request(messages)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response}")
            return {
                "entity_assessment": "分析失败",
                "knowledge_panel_readiness": 0,
                "key_improvements": ["需要重新分析"]
            }
    
    async def _analyze_credibility(self, seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze credibility aspects."""
        prompt = f"""
        评估以下网站的可信度方面：
        
        数据：
        {json.dumps(seo_data, indent=2, ensure_ascii=False)}
        
        请评估：
        1. N-E-E-A-T-T信号
        2. 实体理解和验证
        3. 内容创作者资质
        4. 发布者权威性
        5. 主题专业性信号
        
        请以JSON格式返回分析结果，包含：
        - credibility_assessment: 整体可信度分析
        - neeat_scores: 各个N-E-E-A-T-T组件的评分（0-100）
        - trust_signals: 识别的信任信号列表
        
        只返回JSON格式的结果，不要包含其他解释文字。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self._make_request(messages)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "credibility_assessment": "分析失败",
                "neeat_scores": {"expertise": 0, "experience": 0, "authoritativeness": 0, "trustworthiness": 0},
                "trust_signals": []
            }
    
    async def _analyze_conversation_readiness(self, seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation readiness."""
        prompt = f"""
        分析内容的对话搜索准备度：
        
        数据：
        {json.dumps(seo_data, indent=2, ensure_ascii=False)}
        
        请分析：
        1. 查询模式匹配
        2. 意图覆盖范围
        3. 自然语言理解
        4. 后续内容可用性
        5. 对话触发器
        
        请以JSON格式返回分析结果，包含：
        - conversation_readiness: 整体评估
        - query_patterns: 识别的查询模式
        - engagement_score: 参与度评分（0-100）
        - gaps: 识别的对话缺口
        
        只返回JSON格式的结果，不要包含其他解释文字。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self._make_request(messages)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "conversation_readiness": "分析失败",
                "query_patterns": [],
                "engagement_score": 0,
                "gaps": []
            }
    
    async def _analyze_platform_presence(self, seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze platform presence."""
        prompt = f"""
        分析跨平台存在情况：
        
        数据：
        {json.dumps(seo_data, indent=2, ensure_ascii=False)}
        
        请分析：
        1. 搜索引擎（Google、百度）
        2. 知识图谱
        3. AI平台（ChatGPT、文心一言）
        4. 社交平台
        5. 行业特定平台
        
        请以JSON格式返回分析结果，包含：
        - platform_coverage: 各平台覆盖分析
        - visibility_scores: 各平台类型的可见性评分
        - optimization_opportunities: 优化机会列表
        
        只返回JSON格式的结果，不要包含其他解释文字。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self._make_request(messages)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "platform_coverage": {},
                "visibility_scores": {},
                "optimization_opportunities": []
            }
    
    async def _generate_recommendations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic recommendations."""
        prompt = f"""
        基于完整的分析结果，提供战略性建议：
        
        分析结果：
        {json.dumps(analysis_data, indent=2, ensure_ascii=False)}
        
        请提供：
        1. 实体优化策略
        2. 跨平台内容策略
        3. 可信度建设行动
        4. 对话优化
        5. 跨平台存在改进
        
        请以JSON格式返回建议，包含：
        - strategic_recommendations: 主要战略建议
        - quick_wins: 立即行动项目
        - long_term_strategy: 长期战略目标
        - priority_matrix: 按影响/努力的优先级矩阵
        
        只返回JSON格式的结果，不要包含其他解释文字。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self._make_request(messages)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "strategic_recommendations": [],
                "quick_wins": [],
                "long_term_strategy": [],
                "priority_matrix": {}
            }
    
    async def _comprehensive_analysis(self, seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive SEO analysis."""
        # Run all analysis types in parallel
        entity_results, credibility_results, conversation_results, platform_results = await asyncio.gather(
            self._analyze_entity_optimization(seo_data),
            self._analyze_credibility(seo_data),
            self._analyze_conversation_readiness(seo_data),
            self._analyze_platform_presence(seo_data)
        )
        
        # Combine analyses
        combined_analysis = {
            "entity_analysis": entity_results,
            "credibility_analysis": credibility_results,
            "conversation_analysis": conversation_results,
            "cross_platform_presence": platform_results
        }
        
        # Generate final recommendations
        recommendations = await self._generate_recommendations(combined_analysis)
        
        # Combine all results
        final_results = {
            **seo_data,
            **combined_analysis,
            "recommendations": recommendations
        }
        
        return self._format_output(final_results)
    
    def _format_output(self, raw_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis results into a clean, structured output."""
        try:
            entity_score = raw_analysis.get("entity_analysis", {}).get("knowledge_panel_readiness", 0)
            credibility_scores = raw_analysis.get("credibility_analysis", {}).get("neeat_scores", {})
            credibility_score = sum(credibility_scores.values()) / max(len(credibility_scores), 1) if credibility_scores else 0
            conversation_score = raw_analysis.get("conversation_analysis", {}).get("engagement_score", 0)
            visibility_scores = raw_analysis.get("cross_platform_presence", {}).get("visibility_scores", {})
            platform_score = sum(visibility_scores.values()) / max(len(visibility_scores), 1) if visibility_scores else 0
            
            return {
                "summary": {
                    "entity_score": entity_score,
                    "credibility_score": credibility_score,
                    "conversation_score": conversation_score,
                    "platform_score": platform_score
                },
                "detailed_analysis": raw_analysis,
                "quick_wins": raw_analysis.get("recommendations", {}).get("quick_wins", []),
                "strategic_recommendations": raw_analysis.get("recommendations", {}).get("strategic_recommendations", [])
            }
        except Exception as e:
            logger.error(f"Error formatting output: {e}")
            return {
                "summary": {
                    "entity_score": 0,
                    "credibility_score": 0,
                    "conversation_score": 0,
                    "platform_score": 0
                },
                "detailed_analysis": raw_analysis,
                "quick_wins": [],
                "strategic_recommendations": []
            }


# Example usage
async def enhanced_seo_analysis_with_siliconflow(
    site: str, 
    sitemap: Optional[str] = None, 
    api_key: Optional[str] = None, 
    **kwargs
) -> Dict[str, Any]:
    """
    Enhanced SEO analysis using Silicon Flow API.
    
    Args:
        site: Website URL to analyze
        sitemap: Optional sitemap URL
        api_key: Silicon Flow API key
        **kwargs: Additional arguments for analysis
        
    Returns:
        Enhanced analysis results
    """
    from .analyzer import analyze
    
    # Run original analysis
    original_results = analyze(site, sitemap, **kwargs)
    
    # Enhance with Silicon Flow LLM analysis if API key provided
    if api_key or os.getenv("SILICONFLOW_API_KEY"):
        try:
            llm = SiliconFlowLLM(api_key)
            enhanced_results = await llm.analyze_seo_data(original_results)
            return enhanced_results
        except Exception as e:
            logger.error(f"Silicon Flow analysis failed: {e}")
            return original_results
    
    return original_results