# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
```bash
# Install package in development mode
pip install -e .

# Install dependencies from requirements.txt
pip install -r requirements.txt

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

# Run with AI analysis (requires ANTHROPIC_API_KEY)
docker run --rm -e ANTHROPIC_API_KEY="your_key" python-seo-analyzer http://example.com/ --run-llm-analysis
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

**http.py** - HTTP client wrapper:
- Single `Http` class using urllib3
- Configured with proper timeouts and user agent
- Certificate verification enabled
- Thread-safe singleton instance

**llm_analyst.py** - Advanced SEO analysis with AI:
- `LLMSEOEnhancer` class uses Anthropic's Claude
- Analyzes entity optimization, credibility, and conversational readiness
- Uses LangChain with modern runnable patterns
- Parallel execution of multiple analysis chains

### Key Design Patterns

**Dependency Injection**: The `analyze()` function accepts configuration parameters and passes them through the stack.

**Modular Analysis**: Each analysis type (headings, extra tags, LLM) is optional and can be enabled/disabled independently.

**Content Hashing**: SHA1 hashes detect duplicate content across pages.

**Token Processing**: Text is processed through multiple stages - raw tokenization, stopword filtering, and n-gram generation.

**Error Handling**: Each page analysis returns success/failure status, allowing partial results when some pages fail.

### AI/LLM Integration

The tool uses Anthropic's Claude-3-Sonnet model for enhanced SEO analysis:
- Entity optimization and knowledge panel readiness
- N-E-E-A-T-T credibility analysis  
- Conversational search optimization
- Cross-platform presence evaluation
- Strategic recommendations

Requires `ANTHROPIC_API_KEY` environment variable.

### Testing Strategy

Tests are located in `tests/` directory:
- `test_analyzer.py` - Unit tests for main analysis logic
- `test_page.py` - Tests for page-level analysis
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

### Error Handling Patterns

- Network errors are caught and logged as warnings
- Failed pages don't stop the entire analysis
- DNS resolution failures are handled gracefully
- Content encoding issues are detected and reported