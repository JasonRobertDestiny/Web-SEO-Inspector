from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

import asyncio
import json
import os
import logging
from .siliconflow_llm import SiliconFlowLLM

load_dotenv()
logger = logging.getLogger(__name__)


# Pydantic models for structured output
class EntityAnalysis(BaseModel):
    entity_assessment: str = Field(
        description="Detailed analysis of entity optimization"
    )
    knowledge_panel_readiness: int = Field(description="Score from 0-100")
    key_improvements: List[str] = Field(description="Top 3 improvements needed")


class CredibilityAnalysis(BaseModel):
    credibility_assessment: str = Field(description="Overall credibility analysis")
    neeat_scores: Dict[str, int] = Field(
        description="Individual N-E-E-A-T-T component scores"
    )
    trust_signals: List[str] = Field(description="Identified trust signals")


class ConversationAnalysis(BaseModel):
    conversation_readiness: str = Field(description="Overall assessment")
    query_patterns: List[str] = Field(description="Identified query patterns")
    engagement_score: int = Field(description="Score from 0-100")
    gaps: List[str] = Field(description="Identified conversational gaps")


class PlatformPresence(BaseModel):
    platform_coverage: Dict[str, str] = Field(
        description="Coverage analysis per platform"
    )
    visibility_scores: Dict[str, int] = Field(description="Scores per platform type")
    optimization_opportunities: List[str] = Field(description="List of opportunities")


class SEORecommendations(BaseModel):
    strategic_recommendations: List[str] = Field(
        description="Major strategic recommendations"
    )
    quick_wins: List[str] = Field(description="Immediate action items")
    long_term_strategy: List[str] = Field(description="Long-term strategic goals")
    priority_matrix: Dict[str, str] = Field(
        description="Priority matrix by impact/effort"
    )


class LLMSEOEnhancer:
    """Enhanced SEO analyzer using Claude or Silicon Flow for intelligent insights."""
    
    def __init__(self, api_key: Optional[str] = None, use_siliconflow: bool = False, siliconflow_api_key: Optional[str] = None, siliconflow_model: Optional[str] = None):
        """
        Initialize the LLM SEO enhancer.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            use_siliconflow: Whether to use Silicon Flow API instead of Anthropic
            siliconflow_api_key: Silicon Flow API key (defaults to SILICONFLOW_API_KEY env var)
            siliconflow_model: Silicon Flow model to use (defaults to SILICONFLOW_MODEL env var or Qwen/Qwen2.5-VL-72B-Instruct)
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
                model="claude-3-sonnet-20240229",
                anthropic_api_key=self.api_key,
                temperature=0,
                timeout=30,
                max_retries=3,
            )
            self.siliconflow_llm = None
        
        if not self.use_siliconflow:
            self._setup_chains()

    def _setup_chains(self):
        """Setup modern LangChain runnable sequences using pipe syntax"""
        # Entity Analysis Chain
        entity_parser = PydanticOutputParser(pydantic_object=EntityAnalysis)

        entity_prompt = PromptTemplate.from_template(
            """Analyze these SEO elements for entity optimization:
            1. Entity understanding (Knowledge Panel readiness)
            2. Brand credibility signals (N-E-E-A-T-T principles)
            3. Entity relationships and mentions
            4. Topic entity connections
            5. Schema markup effectiveness
            
            Data to analyze:
            {seo_data}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.entity_chain = (
            {
                "seo_data": RunnablePassthrough(),
                "format_instructions": lambda _: entity_parser.get_format_instructions(),
            }
            | entity_prompt
            | self.llm
            | entity_parser
        )

        # Credibility Analysis Chain
        credibility_parser = PydanticOutputParser(pydantic_object=CredibilityAnalysis)

        credibility_prompt = PromptTemplate.from_template(
            """Evaluate these credibility aspects:
            1. N-E-E-A-T-T signals
            2. Entity understanding and validation
            3. Content creator credentials
            4. Publisher authority
            5. Topic expertise signals
            
            Data to analyze:
            {seo_data}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.credibility_chain = (
            {
                "seo_data": RunnablePassthrough(),
                "format_instructions": lambda _: credibility_parser.get_format_instructions(),
            }
            | credibility_prompt
            | self.llm
            | credibility_parser
        )

        # Conversation Analysis Chain
        conversation_parser = PydanticOutputParser(pydantic_object=ConversationAnalysis)

        conversation_prompt = PromptTemplate.from_template(
            """Analyze content for conversational search readiness:
            1. Query pattern matching
            2. Intent coverage across funnel
            3. Natural language understanding
            4. Follow-up content availability
            5. Conversational triggers
            
            Data to analyze:
            {seo_data}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.conversation_chain = (
            {
                "seo_data": RunnablePassthrough(),
                "format_instructions": lambda _: conversation_parser.get_format_instructions(),
            }
            | conversation_prompt
            | self.llm
            | conversation_parser
        )

        # Platform Presence Chain
        platform_parser = PydanticOutputParser(pydantic_object=PlatformPresence)

        platform_prompt = PromptTemplate.from_template(
            """Analyze presence across different platforms:
            1. Search engines (Google, Bing)
            2. Knowledge graphs
            3. AI platforms (ChatGPT, Bard)
            4. Social platforms
            5. Industry-specific platforms
            
            Data to analyze:
            {seo_data}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.platform_chain = (
            {
                "seo_data": RunnablePassthrough(),
                "format_instructions": lambda _: platform_parser.get_format_instructions(),
            }
            | platform_prompt
            | self.llm
            | platform_parser
        )

        # Recommendations Chain
        recommendations_parser = PydanticOutputParser(
            pydantic_object=SEORecommendations
        )

        recommendations_prompt = PromptTemplate.from_template(
            """Based on this complete analysis, provide strategic recommendations:
            1. Entity optimization strategy
            2. Content strategy across platforms
            3. Credibility building actions
            4. Conversational optimization
            5. Cross-platform presence improvement
            
            Analysis results:
            {analysis_results}
            
            {format_instructions}

            Only return your ouput in JSON format. Do not include any explanations any other text.
            """
        )

        self.recommendations_chain = (
            {
                "analysis_results": RunnablePassthrough(),
                "format_instructions": lambda _: recommendations_parser.get_format_instructions(),
            }
            | recommendations_prompt
            | self.llm
            | recommendations_parser
        )

    async def enhance_seo_analysis(self, seo_data: Dict) -> Dict:
        """
        Enhanced SEO analysis using modern LangChain patterns
        """
        try:
            if self.use_siliconflow:
                # Use Silicon Flow API for analysis
                return await self.siliconflow_llm.analyze_seo_data(seo_data, "comprehensive")
            else:
                # Use Anthropic Claude for analysis
                # Convert seo_data to string for prompt insertion
                seo_data_str = json.dumps(seo_data, indent=2)

                # Run analysis chains in parallel
                entity_results, credibility_results, conversation_results, platform_results = (
                    await asyncio.gather(
                        self.entity_chain.ainvoke(seo_data_str),
                        self.credibility_chain.ainvoke(seo_data_str),
                        self.conversation_chain.ainvoke(seo_data_str),
                        self.platform_chain.ainvoke(seo_data_str),
                    )
                )

                # Combine analyses
                combined_analysis = {
                    "entity_analysis": entity_results.model_dump(),
                    "credibility_analysis": credibility_results.model_dump(),
                    "conversation_analysis": conversation_results.model_dump(),
                    "cross_platform_presence": platform_results.model_dump(),
                }

                # Generate final recommendations
                recommendations = await self.recommendations_chain.ainvoke(
                    json.dumps(combined_analysis, indent=2)
                )

                # Combine all results
                final_results = {
                    **seo_data,
                    **combined_analysis,
                    "recommendations": recommendations.model_dump(),
                }

                return self._format_output(final_results)
                
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            # Return original data if LLM analysis fails
            return seo_data

    def _format_output(self, raw_analysis: Dict) -> Dict:
        """Format analysis results into a clean, structured output"""
        return {
            "summary": {
                "entity_score": raw_analysis["entity_analysis"][
                    "knowledge_panel_readiness"
                ],
                "credibility_score": sum(
                    raw_analysis["credibility_analysis"]["neeat_scores"].values()
                )
                / 6,
                "conversation_score": raw_analysis["conversation_analysis"][
                    "engagement_score"
                ],
                "platform_score": sum(
                    raw_analysis["cross_platform_presence"][
                        "visibility_scores"
                    ].values()
                )
                / len(raw_analysis["cross_platform_presence"]["visibility_scores"]),
            },
            "detailed_analysis": raw_analysis,
            "quick_wins": raw_analysis["recommendations"]["quick_wins"],
            "strategic_recommendations": raw_analysis["recommendations"][
                "strategic_recommendations"
            ],
        }


# Example usage with async support
async def enhanced_modern_analyze(
    site: str, sitemap: Optional[str] = None, api_key: str = None, **kwargs
):
    """
    Enhanced analysis incorporating modern SEO principles using LangChain
    """
    from pyseoanalyzer import analyze

    # Run original analysis
    original_results = analyze(site, sitemap, **kwargs)

    # Enhance with modern SEO analysis if API key provided
    if api_key:
        enhancer = LLMSEOEnhancer()
        enhanced_results = await enhancer.enhance_seo_analysis(original_results)
        return enhancer._format_output(enhanced_results)

    return original_results
