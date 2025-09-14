#!/usr/bin/env python3
"""
Test suite for Silicon Flow API integration.

This module tests the Silicon Flow LLM integration for SEO analysis.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from pyseoanalyzer.siliconflow_llm import SiliconFlowLLM, enhanced_seo_analysis_with_siliconflow
from pyseoanalyzer.llm_analyst import LLMSEOEnhancer


class TestSiliconFlowLLM:
    """Test cases for SiliconFlowLLM class."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        api_key = "test_api_key"
        llm = SiliconFlowLLM(api_key=api_key)
        assert llm.api_key == api_key
        assert llm.model == "deepseek-chat"
        assert llm.base_url == "https://api.siliconflow.cn/v1/chat/completions"
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Silicon Flow API key is required"):
                SiliconFlowLLM()
    
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        test_key = "env_test_key"
        with patch.dict(os.environ, {"SILICONFLOW_API_KEY": test_key}):
            llm = SiliconFlowLLM()
            assert llm.api_key == test_key
    
    def test_custom_model(self):
        """Test initialization with custom model."""
        llm = SiliconFlowLLM(api_key="test", model="custom-model")
        assert llm.model == "custom-model"
    
    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Test successful API request."""
        llm = SiliconFlowLLM(api_key="test_key")
        
        # Mock response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Test response content"
                }
            }]
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.status = 200
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            
            messages = [{"role": "user", "content": "test message"}]
            result = await llm._make_request(messages)
            
            assert result == "Test response content"
    
    @pytest.mark.asyncio
    async def test_make_request_failure(self):
        """Test API request failure."""
        llm = SiliconFlowLLM(api_key="test_key")
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.status = 400
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.text = AsyncMock(return_value="Bad Request")
            
            messages = [{"role": "user", "content": "test message"}]
            
            with pytest.raises(Exception, match="API request failed"):
                await llm._make_request(messages)
    
    @pytest.mark.asyncio
    async def test_analyze_entity_optimization(self):
        """Test entity optimization analysis."""
        llm = SiliconFlowLLM(api_key="test_key")
        
        # Mock the _make_request method
        mock_response = '{
            "entity_assessment": "Good entity optimization",
            "knowledge_panel_readiness": 85,
            "key_improvements": ["Add schema markup", "Improve entity mentions"]
        }'
        
        with patch.object(llm, '_make_request', return_value=mock_response):
            seo_data = {"title": "Test Page", "meta_description": "Test description"}
            result = await llm._analyze_entity_optimization(seo_data)
            
            assert result["entity_assessment"] == "Good entity optimization"
            assert result["knowledge_panel_readiness"] == 85
            assert len(result["key_improvements"]) == 2
    
    @pytest.mark.asyncio
    async def test_analyze_entity_optimization_invalid_json(self):
        """Test entity optimization analysis with invalid JSON response."""
        llm = SiliconFlowLLM(api_key="test_key")
        
        # Mock invalid JSON response
        with patch.object(llm, '_make_request', return_value="invalid json"):
            seo_data = {"title": "Test Page"}
            result = await llm._analyze_entity_optimization(seo_data)
            
            assert result["entity_assessment"] == "分析失败"
            assert result["knowledge_panel_readiness"] == 0
            assert "需要重新分析" in result["key_improvements"]
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self):
        """Test comprehensive analysis."""
        llm = SiliconFlowLLM(api_key="test_key")
        
        # Mock all analysis methods
        mock_entity = {"knowledge_panel_readiness": 80}
        mock_credibility = {"neeat_scores": {"expertise": 70, "trustworthiness": 80}}
        mock_conversation = {"engagement_score": 75}
        mock_platform = {"visibility_scores": {"google": 85, "social": 70}}
        mock_recommendations = {"quick_wins": ["Add meta tags"], "strategic_recommendations": ["Improve content"]}
        
        with patch.object(llm, '_analyze_entity_optimization', return_value=mock_entity), \
             patch.object(llm, '_analyze_credibility', return_value=mock_credibility), \
             patch.object(llm, '_analyze_conversation_readiness', return_value=mock_conversation), \
             patch.object(llm, '_analyze_platform_presence', return_value=mock_platform), \
             patch.object(llm, '_generate_recommendations', return_value=mock_recommendations):
            
            seo_data = {"title": "Test Page"}
            result = await llm._comprehensive_analysis(seo_data)
            
            assert "summary" in result
            assert "detailed_analysis" in result
            assert "quick_wins" in result
            assert "strategic_recommendations" in result
            
            # Check summary scores
            summary = result["summary"]
            assert summary["entity_score"] == 80
            assert summary["credibility_score"] == 75  # Average of 70 and 80
            assert summary["conversation_score"] == 75
            assert summary["platform_score"] == 77.5  # Average of 85 and 70


class TestLLMSEOEnhancerIntegration:
    """Test cases for LLMSEOEnhancer with Silicon Flow integration."""
    
    def test_init_with_siliconflow(self):
        """Test initialization with Silicon Flow."""
        with patch.dict(os.environ, {"SILICONFLOW_API_KEY": "test_key"}):
            enhancer = LLMSEOEnhancer(use_siliconflow=True)
            assert enhancer.use_siliconflow is True
            assert enhancer.siliconflow_llm is not None
            assert enhancer.llm is None
    
    def test_init_with_anthropic(self):
        """Test initialization with Anthropic (default)."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}, clear=True):
            enhancer = LLMSEOEnhancer(api_key="test_anthropic_key")
            assert enhancer.use_siliconflow is False
            assert enhancer.siliconflow_llm is None
            assert enhancer.llm is not None
    
    def test_auto_detect_siliconflow(self):
        """Test auto-detection of Silicon Flow from environment."""
        with patch.dict(os.environ, {"SILICONFLOW_API_KEY": "test_key"}):
            enhancer = LLMSEOEnhancer()
            assert enhancer.use_siliconflow is True
    
    @pytest.mark.asyncio
    async def test_enhance_seo_analysis_with_siliconflow(self):
        """Test SEO analysis enhancement with Silicon Flow."""
        with patch.dict(os.environ, {"SILICONFLOW_API_KEY": "test_key"}):
            enhancer = LLMSEOEnhancer(use_siliconflow=True)
            
            # Mock the Silicon Flow LLM analysis
            mock_result = {
                "summary": {"entity_score": 85},
                "detailed_analysis": {},
                "quick_wins": ["Improve meta tags"],
                "strategic_recommendations": ["Add schema markup"]
            }
            
            with patch.object(enhancer.siliconflow_llm, 'analyze_seo_data', return_value=mock_result):
                seo_data = {"title": "Test Page"}
                result = await enhancer.enhance_seo_analysis(seo_data)
                
                assert result == mock_result
                enhancer.siliconflow_llm.analyze_seo_data.assert_called_once_with(seo_data, "comprehensive")


class TestEnhancedSEOAnalysisFunction:
    """Test cases for the enhanced_seo_analysis_with_siliconflow function."""
    
    @pytest.mark.asyncio
    async def test_enhanced_analysis_with_api_key(self):
        """Test enhanced analysis with API key provided."""
        # Mock the analyze function
        mock_basic_results = {"title": "Test", "score": 70}
        
        # Mock the SiliconFlowLLM
        mock_enhanced_results = {
            "summary": {"entity_score": 85},
            "detailed_analysis": mock_basic_results,
            "quick_wins": ["Add meta tags"]
        }
        
        with patch('pyseoanalyzer.siliconflow_llm.analyze', return_value=mock_basic_results), \
             patch('pyseoanalyzer.siliconflow_llm.SiliconFlowLLM') as mock_llm_class:
            
            mock_llm_instance = Mock()
            mock_llm_instance.analyze_seo_data = AsyncMock(return_value=mock_enhanced_results)
            mock_llm_class.return_value = mock_llm_instance
            
            result = await enhanced_seo_analysis_with_siliconflow(
                site="https://example.com",
                api_key="test_key"
            )
            
            assert result == mock_enhanced_results
            mock_llm_class.assert_called_once_with("test_key")
            mock_llm_instance.analyze_seo_data.assert_called_once_with(mock_basic_results)
    
    @pytest.mark.asyncio
    async def test_enhanced_analysis_without_api_key(self):
        """Test enhanced analysis without API key falls back to basic analysis."""
        mock_basic_results = {"title": "Test", "score": 70}
        
        with patch('pyseoanalyzer.siliconflow_llm.analyze', return_value=mock_basic_results), \
             patch.dict(os.environ, {}, clear=True):
            
            result = await enhanced_seo_analysis_with_siliconflow(
                site="https://example.com"
            )
            
            assert result == mock_basic_results
    
    @pytest.mark.asyncio
    async def test_enhanced_analysis_with_env_var(self):
        """Test enhanced analysis with environment variable."""
        mock_basic_results = {"title": "Test", "score": 70}
        mock_enhanced_results = {"summary": {"entity_score": 85}}
        
        with patch('pyseoanalyzer.siliconflow_llm.analyze', return_value=mock_basic_results), \
             patch('pyseoanalyzer.siliconflow_llm.SiliconFlowLLM') as mock_llm_class, \
             patch.dict(os.environ, {"SILICONFLOW_API_KEY": "env_key"}):
            
            mock_llm_instance = Mock()
            mock_llm_instance.analyze_seo_data = AsyncMock(return_value=mock_enhanced_results)
            mock_llm_class.return_value = mock_llm_instance
            
            result = await enhanced_seo_analysis_with_siliconflow(
                site="https://example.com"
            )
            
            assert result == mock_enhanced_results
            mock_llm_class.assert_called_once_with(None)  # Uses env var
    
    @pytest.mark.asyncio
    async def test_enhanced_analysis_llm_failure(self):
        """Test enhanced analysis falls back to basic results on LLM failure."""
        mock_basic_results = {"title": "Test", "score": 70}
        
        with patch('pyseoanalyzer.siliconflow_llm.analyze', return_value=mock_basic_results), \
             patch('pyseoanalyzer.siliconflow_llm.SiliconFlowLLM') as mock_llm_class:
            
            mock_llm_instance = Mock()
            mock_llm_instance.analyze_seo_data = AsyncMock(side_effect=Exception("API Error"))
            mock_llm_class.return_value = mock_llm_instance
            
            result = await enhanced_seo_analysis_with_siliconflow(
                site="https://example.com",
                api_key="test_key"
            )
            
            assert result == mock_basic_results


if __name__ == "__main__":
    pytest.main([__file__])