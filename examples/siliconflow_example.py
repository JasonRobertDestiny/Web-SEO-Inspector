#!/usr/bin/env python3
"""
Example script demonstrating how to use Silicon Flow API for SEO analysis.

This script shows how to:
1. Configure Silicon Flow API
2. Run SEO analysis with Silicon Flow LLM
3. Compare results with traditional analysis

Usage:
    python examples/siliconflow_example.py

Requirements:
    - SILICONFLOW_API_KEY environment variable set
    - aiohttp package installed
"""

import os
import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import pyseoanalyzer
sys.path.insert(0, str(Path(__file__).parent.parent))

from pyseoanalyzer.analyzer import analyze
from pyseoanalyzer.llm_analyst import LLMSEOEnhancer
from pyseoanalyzer.siliconflow_llm import enhanced_seo_analysis_with_siliconflow
from dotenv import load_dotenv

load_dotenv()


async def main():
    """Main example function."""
    # Configuration
    SILICONFLOW_API_KEY = "sk-omysgcreevtaaengykwkmqkreqmukmolgzexkwfnainhwttb"  # Your Silicon Flow API key
    MODEL = "Qwen/Qwen2.5-VL-72B-Instruct"  # Advanced vision-language model
    
    # Check if Silicon Flow API key is available
    siliconflow_key = SILICONFLOW_API_KEY or os.getenv("SILICONFLOW_API_KEY")
    if not siliconflow_key:
        print("❌ SILICONFLOW_API_KEY not found in environment variables.")
        print("Please set your Silicon Flow API key:")
        print("export SILICONFLOW_API_KEY='your_api_key_here'")
        print("\nOr add it to your .env file:")
        print("echo 'SILICONFLOW_API_KEY=your_api_key_here' >> .env")
        return
    
    print("🚀 Silicon Flow SEO Analysis Example")
    print("=" * 50)
    
    # Example website to analyze
    test_url = "https://example.com"
    print(f"📊 Analyzing: {test_url}")
    
    try:
        # Method 1: Using the enhanced function
        print("\n🔍 Method 1: Using enhanced_seo_analysis_with_siliconflow()")
        enhanced_results = await enhanced_seo_analysis_with_siliconflow(
            site=test_url,
            api_key=siliconflow_key
        )
        
        print("✅ Enhanced analysis completed!")
        print(f"📈 Entity Score: {enhanced_results.get('summary', {}).get('entity_score', 'N/A')}")
        print(f"🛡️ Credibility Score: {enhanced_results.get('summary', {}).get('credibility_score', 'N/A')}")
        print(f"💬 Conversation Score: {enhanced_results.get('summary', {}).get('conversation_score', 'N/A')}")
        print(f"🌐 Platform Score: {enhanced_results.get('summary', {}).get('platform_score', 'N/A')}")
        
        # Method 2: Using LLMSEOEnhancer directly
        print("\n🔍 Method 2: Using LLMSEOEnhancer with Silicon Flow")
        
        # First get basic SEO analysis
        basic_results = analyze(test_url)
        print("✅ Basic SEO analysis completed")
        
        # Then enhance with Silicon Flow
        enhancer = LLMSEOEnhancer(use_siliconflow=True, siliconflow_api_key=siliconflow_key, siliconflow_model=MODEL)
        enhanced_results_2 = await enhancer.enhance_seo_analysis(basic_results)
        
        print("✅ LLM enhancement completed!")
        
        # Display quick wins if available
        quick_wins = enhanced_results_2.get('quick_wins', [])
        if quick_wins:
            print("\n🎯 Quick Wins:")
            for i, win in enumerate(quick_wins[:3], 1):
                print(f"   {i}. {win}")
        
        # Display strategic recommendations if available
        strategic_recs = enhanced_results_2.get('strategic_recommendations', [])
        if strategic_recs:
            print("\n📋 Strategic Recommendations:")
            for i, rec in enumerate(strategic_recs[:3], 1):
                print(f"   {i}. {rec}")
        
        print("\n🎉 Analysis completed successfully!")
        print("\n💡 Tips:")
        print("   - Silicon Flow API is cost-effective for Chinese users")
        print("   - Supports multiple models including deepseek-chat")
        print("   - Provides comprehensive SEO analysis in Chinese")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your SILICONFLOW_API_KEY is valid")
        print("   2. Ensure you have internet connection")
        print("   3. Verify the target website is accessible")
        print("   4. Check if you have sufficient API credits")


def compare_providers():
    """Compare different AI providers."""
    print("\n🔄 AI Provider Comparison")
    print("=" * 30)
    
    providers = [
        {
            "name": "Anthropic Claude",
            "pros": ["High quality analysis", "English optimized", "Reliable"],
            "cons": ["More expensive", "Requires VPN in some regions"],
            "env_var": "ANTHROPIC_API_KEY"
        },
        {
            "name": "Silicon Flow (硅基流动)",
            "pros": ["Cost-effective", "Chinese optimized", "Multiple models"],
            "cons": ["Newer service", "Primarily Chinese"],
            "env_var": "SILICONFLOW_API_KEY"
        }
    ]
    
    for provider in providers:
        print(f"\n📊 {provider['name']}")
        print(f"   Environment Variable: {provider['env_var']}")
        print("   Pros:")
        for pro in provider['pros']:
            print(f"     ✅ {pro}")
        print("   Cons:")
        for con in provider['cons']:
            print(f"     ⚠️ {con}")


if __name__ == "__main__":
    print("🌟 Web SEO Inspector - Silicon Flow Integration Example")
    
    # Show provider comparison
    compare_providers()
    
    # Run the main example
    asyncio.run(main())