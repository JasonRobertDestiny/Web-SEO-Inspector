# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
```bash
# Install package in development mode
pip install -e .

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install additional dependencies for Google integration (if needed)
pip install google-api-python-client google-auth google-auth-oauthlib

# Build package
python -m build
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_analyzer.py

# Run specific test function
pytest tests/test_analyzer.py::test_analyze_basic

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=pyseoanalyzer
```

### Docker Development
```bash
# Build Docker image
docker build -t python-seo-analyzer .

# Run Docker container
docker run --rm python-seo-analyzer http://example.com/

# Run with AI analysis (requires ANTHROPIC_API_KEY or SILICONFLOW_API_KEY)
docker run --rm -e ANTHROPIC_API_KEY="your_key" python-seo-analyzer http://example.com/ --run-llm-analysis
# Or use Silicon Flow API
docker run --rm -e SILICONFLOW_API_KEY="your_key" python-seo-analyzer http://example.com/ --run-llm-analysis
```

### CLI Usage
```bash
# Basic analysis
python-seo-analyzer http://example.com/

# With sitemap
python-seo-analyzer http://example.com/ --sitemap sitemap.xml

# HTML output
python-seo-analyzer http://example.com/ --output-format html

# With AI analysis
python-seo-analyzer http://example.com/ --run-llm-analysis

# Web interface
python -m pyseoanalyzer.api
```

### Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys and configuration
# Required: ANTHROPIC_API_KEY or SILICONFLOW_API_KEY
# Optional: Google Analytics and Search Console settings
```

### Web Interface Development
```bash
# Start development server
python -m pyseoanalyzer.api --debug

# Start with custom port
SEO_ANALYZER_PORT=8080 python -m pyseoanalyzer.api

# Run with production settings
export FLASK_ENV=production
python -m pyseoanalyzer.api
```

## Architecture Overview

### Core Components

**analyzer.py** - Main entry point that orchestrates the analysis:
- `analyze()` function is the primary API
- Handles keyword extraction and aggregation
- Processes results from individual pages
- Calculates total execution time

**website.py** - Website-level crawling logic:
- `Website` class manages the crawling process
- Handles sitemap parsing (XML and TXT formats)
- Manages page queue and crawling state
- Aggregates word counts and content hashes across pages

**page.py** - Individual page analysis:
- `Page` class handles single-page SEO analysis
- Extracts metadata using trafilatura
- Analyzes HTML structure (title, description, headings, images, links)
- Tokenizes text and generates n-grams
- Optional LLM analysis for modern SEO evaluation

**http_client.py** - HTTP client wrapper:
- Single `Http` class using urllib3
- Configured with proper timeouts and user agent
- Certificate verification enabled
- Thread-safe singleton instance

**llm_analyst.py** - Advanced SEO analysis with AI:
- `LLMSEOEnhancer` class supports both Anthropic's Claude and Silicon Flow API
- `SiliconFlowLLM` class provides Silicon Flow integration
- Analyzes entity optimization, credibility, and conversational readiness
- Uses LangChain with modern runnable patterns
- Parallel execution of multiple analysis chains

**api.py** - Flask web interface:
- RESTful API endpoints for SEO analysis
- Real-time web dashboard with responsive design
- SEO scoring and recommendations engine
- Support for both synchronous and asynchronous analysis

**automation.py** - Scheduled SEO analysis:
- APScheduler-based automation system
- Configurable cron schedules for regular analysis
- Integration with Google Analytics and Search Console
- Automated reporting and notification system

**decision_engine.py** - AI-powered decision making:
- Rule-based and ML-driven recommendations
- Priority-based action categorization
- Trend analysis and predictive insights
- Multi-factor decision scoring system

**enhanced_llm_analyst.py** - Advanced AI analysis:
- Multi-data source integration (content + Google data)
- Predictive insights and trend analysis
- Competitive analysis recommendations
- Strategic SEO prioritization

**google_integrator.py** - Google API integration:
- Google Analytics data fetching
- Search Console performance metrics
- OAuth2 authentication handling
- Historical trend analysis

**seo_optimizer.py** - Actionable recommendations:
- Detailed optimization action plans
- Priority-based task management
- Implementation guidance with time estimates
- Expected impact assessment

### New Components (Recent Additions)

**siliconflow_llm.py** - Silicon Flow API integration:
- Cost-effective alternative to Anthropic Claude
- Supports multiple Chinese AI models (Qwen, DeepSeek)
- Async/await support for concurrent analysis
- Automatic fallback and error handling

### Key Design Patterns

**Dependency Injection**: The `analyze()` function accepts configuration parameters and passes them through the stack.

**Modular Analysis**: Each analysis type (headings, extra tags, LLM) is optional and can be enabled/disabled independently.

**Content Hashing**: SHA1 hashes detect duplicate content across pages.

**Token Processing**: Text is processed through multiple stages - raw tokenization, stopword filtering, and n-gram generation.

**Error Handling**: Each page analysis returns success/failure status, allowing partial results when some pages fail.

### AI/LLM Integration

The tool supports multiple AI providers for enhanced SEO analysis:

**Anthropic Claude (claude-3-sonnet-20240229):**
- High-quality English analysis
- Comprehensive SEO insights
- Requires `ANTHROPIC_API_KEY` environment variable

**Silicon Flow (硅基流动) API:**
- Cost-effective Chinese AI service
- Multiple model options (default: deepseek-chat)
- Optimized for Chinese content analysis
- Requires `SILICONFLOW_API_KEY` environment variable

**Analysis Features (both providers):**
- Entity optimization and knowledge panel readiness
- N-E-E-A-T-T credibility analysis
- Conversational search optimization
- Cross-platform presence evaluation
- Strategic recommendations

### Testing Strategy

Tests are located in `tests/` directory:
- `test_analyzer.py` - Unit tests for main analysis logic
- `test_page.py` - Tests for page-level analysis
- `test_http.py` - HTTP client tests
- `test_llm_analyst.py` - LLM analysis integration tests
- `test_siliconflow_integration.py` - Silicon Flow API specific tests
- Uses pytest with mocking for network calls
- Tests both happy paths and edge cases

### Configuration

**pyproject.toml** - Modern Python packaging with:
- Hatchling build backend
- Entry point for CLI tool
- Dependencies including LangChain and Anthropic integration
- Python 3.8+ requirement

**requirements.txt** - Pinned dependencies for reproducible builds.

### HTML Templates

Uses Jinja2 templates for HTML report generation located in `pyseoanalyzer/templates/`.

### GitHub Actions Automation

The project includes automated SEO analysis via GitHub Actions:

```bash
# Manually trigger analysis
gh workflow run seo-agent.yml \
  -f website_url="https://yourdomain.com" \
  -f run_llm_analysis=true \
  -f enable_google_integration=true

# Required secrets in GitHub repository:
# - ANTHROPIC_API_KEY (or SILICONFLOW_API_KEY)
# - GOOGLE_ANALYTICS_VIEW_ID (optional)
# - GOOGLE_SEARCH_CONSOLE_URL (optional)
# - SLACK_WEBHOOK_URL (optional for notifications)
```

### Error Handling Patterns

- Network errors are caught and logged as warnings
- Failed pages don't stop the entire analysis
- DNS resolution failures are handled gracefully
- Content encoding issues are detected and reported
- API rate limiting and authentication failures are handled with retry logic
- Memory usage monitoring for large-scale crawling operations

### Advanced Features

**SEO Agent Automation**:
- Scheduled analysis with configurable cron expressions
- Integration with Google Analytics and Search Console
- Automated reporting and notification systems
- Multi-website monitoring capabilities

**Decision Engine**:
- AI-powered prioritization of SEO actions
- Trend analysis and predictive insights
- Competitive analysis recommendations
- Multi-factor scoring system

**Enhanced LLM Analysis**:
- Integration of content analysis with performance data
- Predictive SEO recommendations
- Strategic opportunity identification
- Long-term project planning

**Web Dashboard**:
- Real-time SEO scoring and visualization
- Interactive issue tracking and resolution
- Historical performance trends
- Multi-format report generation (HTML, JSON, CSV)