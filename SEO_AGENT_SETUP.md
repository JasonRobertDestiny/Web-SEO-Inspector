# SEO Agent Setup Guide

## Overview

The SEO Agent is now enhanced with AI-powered analysis, Google data integration, and automated scheduling capabilities. This guide will help you set up and use the enhanced features.

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
# Install package in development mode
pip install -e .

# Install additional dependencies for Google integration
pip install google-api-python-client google-auth google-auth-oauthlib
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# Required for basic SEO analysis
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Required for Google integration
# Google Analytics Universal Analytics (optional)
GOOGLE_ANALYTICS_VIEW_ID=123456789

# Google Analytics 4 (optional)
GOOGLE_ANALYTICS_MEASUREMENT_ID=G-DNFKJG8R74

# Google Search Console (required if using Google integration)
GOOGLE_SEARCH_CONSOLE_URL=https://yourdomain.com

# Optional: Email notifications
NOTIFICATION_EMAIL=your@email.com
```

### 3. Google API Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable APIs**
   - Google Analytics Reporting API
   - Google Search Console API

3. **Create OAuth2 Credentials**
   - Go to APIs & Services > Credentials
   - Create OAuth2 Client ID (Desktop application)
   - Download the credentials file as `credentials.json`

4. **First Run Authorization**
   - The first time you run with Google integration, you'll be redirected to Google
   - Authorize the application and the token will be saved as `token.json`

## 🚀 Usage

### Basic SEO Analysis

```bash
# Run basic analysis
python-seo-analyzer https://example.com

# Run with enhanced features
python-seo-analyzer https://example.com \
  --enable-google-integration \
  --run-llm-analysis \
  --output-format html
```

### Automated SEO Agent

```python
import asyncio
from pyseoanalyzer.automation import SEOAgentAutomation, AutomationConfig

# Configuration
config = AutomationConfig(
    website_url="https://example.com",
    sitemap_url="https://example.com/sitemap.xml",
    analysis_schedule="0 9 * * 1",  # Every Monday at 9 AM
    google_integration_enabled=True,
    llm_analysis_enabled=True,
    notifications_enabled=True,
    notification_email="your@email.com"
)

# Create and start automation
automation = SEOAgentAutomation(config)
automation.start()

# Keep running
try:
    while True:
        asyncio.sleep(60)
except KeyboardInterrupt:
    automation.stop()
```

### Manual Analysis with All Features

```python
import asyncio
from pyseoanalyzer.analyzer import analyze
from pyseoanalyzer.google_integrator import GoogleDataIntegrator
from pyseoanalyzer.enhanced_llm_analyst import EnhancedLLMSEOAnalyst
from pyseoanalyzer.decision_engine import SEODecisionEngine

async def comprehensive_analysis():
    # Run basic SEO analysis
    results = analyze(
        url="https://example.com",
        enable_google_integration=True,
        run_llm_analysis=True
    )
    
    # Enhanced LLM analysis
    llm_analyst = EnhancedLLMSEOAnalyst()
    comprehensive_insights = await llm_analyst.analyze_comprehensive_data(
        seo_analysis=results,
        google_insights=results.get('google_insights', {})
    )
    
    # Generate strategic recommendations
    decision_engine = SEODecisionEngine()
    recommendations = decision_engine.analyze_and_recommend(
        seo_analysis=results,
        google_insights=results.get('google_insights', {}),
        llm_insights=comprehensive_insights
    )
    
    return {
        'basic_analysis': results,
        'comprehensive_insights': comprehensive_insights,
        'recommendations': recommendations
    }

# Run analysis
analysis_results = asyncio.run(comprehensive_analysis())
```

## 🤖 GitHub Actions Automation

### 1. Repository Secrets

Add the following secrets to your GitHub repository:

- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `GOOGLE_ANALYTICS_VIEW_ID`: Google Analytics view ID
- `GOOGLE_SEARCH_CONSOLE_URL`: Search Console property URL
- `SLACK_WEBHOOK_URL`: (Optional) Slack webhook for notifications

### 2. Manual Trigger

You can manually trigger the SEO analysis:

```bash
gh workflow run seo-agent.yml \
  -f website_url="https://yourdomain.com" \
  -f run_llm_analysis=true \
  -f enable_google_integration=true
```

### 3. Scheduled Analysis

The workflow is configured to run every Monday at 9 AM UTC. You can modify the schedule in `.github/workflows/seo-agent.yml`.

## 📊 Output Features

### Enhanced Analysis Results

The enhanced SEO Agent provides:

1. **Traditional SEO Analysis**
   - Page structure analysis
   - Keyword extraction and frequency
   - Technical SEO issues
   - Duplicate content detection

2. **Google Data Integration**
   - Traffic and user behavior metrics
   - Search performance data
   - Page-level insights
   - Trend analysis

3. **AI-Powered Insights**
   - Entity optimization analysis
   - Credibility assessment (N-E-E-A-T-T)
   - Conversational search readiness
   - Strategic recommendations

4. **Intelligent Recommendations**
   - Prioritized action items
   - Implementation plans
   - Timeline estimates
   - Success metrics

### Report Formats

**JSON Output:**
```json
{
  "pages": [...],
  "keywords": [...],
  "google_insights": {...},
  "comprehensive_analysis": {...},
  "recommendations": {
    "recommendations": [...],
    "implementation_plan": {...},
    "summary": {...},
    "timeline": {...}
  }
}
```

**HTML Report:**
- Interactive dashboard with TailwindCSS
- Real-time SEO alerts and recommendations
- Keyword analysis visualizations
- Progress tracking for optimization tasks

## 🎯 Key Features

### Multi-Data Source Integration
- Google Analytics (traffic, user behavior)
- Search Console (rankings, CTR, impressions)
- Traditional SEO analysis (on-page factors)
- AI-powered content analysis

### Intelligent Decision Making
- Rule-based priority scoring
- Impact/effort analysis
- Confidence levels for recommendations
- Implementation timeline planning

### Automated Workflows
- Scheduled analysis (cron-based)
- GitHub Actions automation
- Email/Slack notifications
- Report generation and archiving

### Strategic Insights
- Performance trend analysis
- Competitive context awareness
- Predictive recommendations
- Long-term strategy planning

## 🔍 Troubleshooting

### Common Issues

1. **Google API Authentication**
   - Ensure `credentials.json` is in the correct location
   - Check API enablement in Google Cloud Console
   - Verify OAuth scopes are correct

2. **LLM Analysis Errors**
   - Check `ANTHROPIC_API_KEY` is valid
   - Verify API credits are available
   - Check internet connectivity

3. **Scheduler Issues**
   - Ensure timezone settings are correct
   - Check system time synchronization
   - Verify cron expression syntax

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check

Run system diagnostics:

```python
from pyseoanalyzer.automation import SEOAgentAutomation

automation = SEOAgentAutomation(config)
health_status = automation.health_check()
print(health_status)
```

## 📈 Advanced Configuration

### Custom Decision Rules

Modify the decision engine rules in `pyseoanalyzer/decision_engine.py`:

```python
# Update threshold values
self.rules['content_quality']['bounce_rate_threshold'] = 0.6

# Add new rules
self.rules['custom_metrics'] = {
    'engagement_threshold': 0.8
}
```

### Custom Analysis Chains

Extend the LLM analysis in `pyseoanalyzer/enhanced_llm_analyst.py`:

```python
# Add new analysis chains
self.custom_chain = (
    {"input_data": RunnablePassthrough()}
    | custom_prompt
    | self.llm
    | custom_parser
)
```

### Scheduling Configuration

Customize analysis schedules:

```python
# Daily at 9 AM
analysis_schedule="0 9 * * *"

# Weekly on Monday at 2 PM
analysis_schedule="0 14 * * 1"

# Every 6 hours
analysis_schedule="0 */6 * * *"
```

## 🤝 Contributing

The SEO Agent is designed to be extensible. You can:

1. Add new data sources (Social media, SEMrush, Ahrefs)
2. Implement custom analysis rules
3. Enhance the decision engine
4. Add new output formats
5. Improve UI/UX components

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code documentation
3. Check GitHub issues
4. Create a new issue with detailed information

---

Happy SEO optimizing! 🚀