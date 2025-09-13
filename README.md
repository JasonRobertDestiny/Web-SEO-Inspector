# Web SEO Inspector

[![PyPI version](https://badge.fury.io/py/pyseoanalyzer.svg)](https://badge.fury.io/py/pyseoanalyzer)
[![Docker Pulls](https://img.shields.io/docker/pulls/sethblack/python-seo-analyzer.svg)](https://hub.docker.com/r/sethblack/python-seo-analyzer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

🔍 **A comprehensive SEO analysis tool with AI-powered insights and modern web interface**

Web SEO Inspector is a modern SEO and GEO (Generative AI Engine Optimization) analysis tool that combines technical optimization with AI-driven content evaluation. It provides both command-line analysis and a beautiful web interface for comprehensive website optimization.

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [💻 Command Line Interface](#-command-line-interface)
- [🔧 Python API](#-python-api)
- [🤖 AI-Powered Analysis](#-ai-powered-analysis)
- [⚙️ Configuration](#️-configuration)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Key Features

- 🤖 **AI-Powered Analysis**: Uses Anthropic's Claude to evaluate content quality and provide optimization recommendations
- 🌐 **Web Interface**: Modern, responsive dashboard for interactive SEO analysis
- 📊 **Comprehensive Reports**: Technical SEO, content analysis, and performance metrics
- 🎯 **Smart Recommendations**: Actionable insights with priority-based task management
- 📈 **Real-time Scoring**: Dynamic SEO score calculation with visual indicators
- 🔗 **Link Analysis**: Internal and external link evaluation
- 📱 **Mobile-Friendly**: Responsive design for analysis on any device
- 🐳 **Docker Support**: Easy deployment with containerization
- 📋 **Export Options**: Multiple output formats (JSON, HTML, CSV)

The AI features are influenced by modern SEO best practices and the evolving landscape of AI search optimization.

## 🚀 Quick Start

### Web Interface (Recommended)

1. **Install the package**:
   ```bash
   pip install pyseoanalyzer
   ```

2. **Start the web server**:
   ```bash
   python -m pyseoanalyzer.api
   ```

3. **Open your browser** and navigate to `http://localhost:5000`

4. **Analyze any website** by entering the URL in the web interface

### Command Line Usage

```bash
# Basic analysis
python-seo-analyzer https://example.com

# With AI analysis (requires ANTHROPIC_API_KEY)
python-seo-analyzer https://example.com --run-llm-analysis

# Generate HTML report
python-seo-analyzer https://example.com --output-format html
```

## 📦 Installation

### 🐍 Python Package

```bash
pip install pyseoanalyzer
```

### 🐳 Docker

#### Using the Pre-built Image from Docker Hub

The easiest way to use the Docker image is to pull it directly from [Docker Hub](https://hub.docker.com/r/sethblack/python-seo-analyzer).

```bash
# Pull the latest image
docker pull sethblack/python-seo-analyzer:latest

# Run the analyzer (replace example.com with the target URL)
# The --rm flag automatically removes the container when it exits
docker run --rm sethblack/python-seo-analyzer http://example.com/

# Run with specific arguments (e.g., sitemap and HTML output)
# Note: If the sitemap is local, you'll need to mount it (see mounting example below)
docker run --rm sethblack/python-seo-analyzer http://example.com/ --sitemap /path/inside/container/sitemap.xml --output-format html

# Run with AI analysis (requires ANTHROPIC_API_KEY)
# Replace "your_api_key_here" with your actual Anthropic API key
docker run --rm -e ANTHROPIC_API_KEY="your_api_key_here" sethblack/python-seo-analyzer http://example.com/ --run-llm-analysis

# Save HTML output to your local machine
# This mounts the current directory (.) into /app/output inside the container.
# The output file 'results.html' will be saved in your current directory.
# The tool outputs JSON by default to stdout, so we redirect it for HTML.
# Since the ENTRYPOINT handles the command, we redirect the container's stdout.
# We need a shell inside the container to handle the redirection.
docker run --rm -v "$(pwd):/app/output" sethblack/python-seo-analyzer /bin/sh -c "seoanalyze http://example.com/ --output-format html > /app/output/results.html"
# Note for Windows CMD users: Use %cd% instead of $(pwd)
# docker run --rm -v "%cd%:/app/output" sethblack/python-seo-analyzer /bin/sh -c "seoanalyze http://example.com/ --output-format html > /app/output/results.html"
# Note for Windows PowerShell users: Use ${pwd} instead of $(pwd)
# docker run --rm -v "${pwd}:/app/output" sethblack/python-seo-analyzer /bin/sh -c "seoanalyze http://example.com/ --output-format html > /app/output/results.html"


# Mount a local sitemap file
# This mounts 'local-sitemap.xml' from the current directory to '/app/sitemap.xml' inside the container
docker run --rm -v "$(pwd)/local-sitemap.xml:/app/sitemap.xml" sethblack/python-seo-analyzer http://example.com/ --sitemap /app/sitemap.xml
# Adjust paths and Windows commands as needed (see volume mounting example above)

```

#### Building the Image Locally

You can also build the Docker image yourself from the source code. Make sure you have Docker installed and running.

```bash
# Clone the repository (if you haven't already)
# git clone https://github.com/sethblack/python-seo-analyzer.git
# cd python-seo-analyzer

# Build the Docker image (tag it as 'my-seo-analyzer' for easy reference)
docker build -t my-seo-analyzer .

# Run the locally built image
docker run --rm my-seo-analyzer http://example.com/

# Run with AI analysis using the locally built image
docker run --rm -e ANTHROPIC_API_KEY="your_api_key_here" my-seo-analyzer http://example.com/ --run-llm-analysis

# Run with HTML output saved locally using the built image
docker run --rm -v "$(pwd):/app/output" my-seo-analyzer /bin/sh -c "python-seo-analyzer http://example.com/ --output-format html > /app/output/results.html"
# Adjust Windows commands as needed (see volume mounting example above)
```

## 💻 Command Line Interface

### Basic Usage

If you run without a sitemap, it will start crawling from the homepage:

```bash
python-seo-analyzer https://www.example.com/
```

### Advanced Options

```bash
# Analyze with sitemap
python-seo-analyzer https://www.example.com/ --sitemap path/to/sitemap.xml

# Generate HTML report
python-seo-analyzer https://www.example.com/ --output-format html

# Run with AI analysis
ANTHROPIC_API_KEY="your_key" python-seo-analyzer https://www.example.com/ --run-llm-analysis

# Analyze only specific URL (don't follow links)
python-seo-analyzer https://www.example.com/ --no-follow-links

# Include heading analysis
python-seo-analyzer https://www.example.com/ --analyze-headings
```

## 🔧 Python API

The `analyze` function returns a comprehensive dictionary with crawl results:

```python
from pyseoanalyzer import analyze

# Basic analysis
result = analyze("https://example.com")
print(result)
```

### Advanced API Usage

```python
from pyseoanalyzer import analyze

# Full analysis with all options
result = analyze(
    site="https://example.com",
    sitemap="path/to/sitemap.xml",
    analyze_headings=True,
    analyze_extra_tags=True,
    follow_links=True  # Set to False for single-page analysis
)

# Access specific results
print(f"SEO Score: {result['seo_score']}")
print(f"Issues Found: {len(result['issues'])}")
print(f"Recommendations: {result['recommendations']}")
```

### Running as Module

```bash
# Generate HTML report
python -m pyseoanalyzer https://example.com -f html > results.html

# JSON output with AI analysis
python -m pyseoanalyzer https://example.com --run-llm-analysis
```

## 🤖 AI-Powered Analysis

Web SEO Inspector uses Anthropic's Claude AI to provide intelligent content analysis and optimization recommendations.

### Setup AI Analysis

1. **Get an API key** from [Anthropic](https://www.anthropic.com/)

2. **Set the environment variable**:
   ```bash
   # Option 1: Export in terminal
   export ANTHROPIC_API_KEY="your_api_key_here"
   
   # Option 2: Create .env file
   echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
   ```

3. **Run analysis with AI**:
   ```bash
   python-seo-analyzer https://example.com --run-llm-analysis
   ```

### AI Features

- 📝 **Content Quality Assessment**: Evaluates expertise, authority, and trustworthiness
- 🎯 **Optimization Recommendations**: Specific, actionable improvement suggestions
- 📊 **Competitive Analysis**: Insights based on industry best practices
- 🔍 **Semantic Analysis**: Understanding of content context and relevance

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key for AI analysis | For AI features |
| `SEO_ANALYZER_PORT` | Web server port (default: 5000) | No |
| `SEO_ANALYZER_HOST` | Web server host (default: localhost) | No |

### Configuration File

Create a `config.json` file for advanced settings:

```json
{
  "max_pages": 100,
  "timeout": 30,
  "user_agent": "Web-SEO-Inspector/1.0",
  "follow_redirects": true,
  "analyze_images": true,
  "check_mobile_friendly": true
}
```

## 🔧 Troubleshooting

### Common Issues

**SSL Certificate Errors**
```bash
# Try using HTTP instead of HTTPS
python-seo-analyzer http://example.com
```

**Connection Timeouts**
```bash
# Increase timeout
python-seo-analyzer https://example.com --timeout 60
```

**Memory Issues with Large Sites**
```bash
# Limit pages analyzed
python-seo-analyzer https://example.com --max-pages 50
```

### Getting Help

- 📖 Check the [documentation](https://github.com/sethblack/python-seo-analyzer/wiki)
- 🐛 Report bugs on [GitHub Issues](https://github.com/sethblack/python-seo-analyzer/issues)
- 💬 Join discussions in [GitHub Discussions](https://github.com/sethblack/python-seo-analyzer/discussions)

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `python -m pytest`
5. **Submit a pull request**

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sethblack/python-seo-analyzer.git
cd python-seo-analyzer

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest

# Start development server
python -m pyseoanalyzer.api --debug
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by modern SEO best practices and AI search optimization
- Built with ❤️ by the open-source community
- Special thanks to all [contributors](https://github.com/sethblack/python-seo-analyzer/graphs/contributors)

---

**Made with ❤️ for the SEO community**
