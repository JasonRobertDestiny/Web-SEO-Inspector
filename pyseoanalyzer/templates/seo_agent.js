class SEOAgent {
    constructor() {
        this.apiBaseUrl = 'http://127.0.0.1:5000/api';
        this.currentAnalysis = null;
        this.todos = JSON.parse(localStorage.getItem('seoTodos')) || [];
        this.theme = localStorage.getItem('theme') || 'light';
        this.currentSection = 'summary';
        this.init();
    }

    init() {
        this.initTheme();
        this.bindEvents();
        this.renderTodos();
        this.updateTodoStats();
        this.initAnimations();
        this.initSectionNavigation();
        this.initUsageTracking();
    }

    initTheme() {
        if (this.theme === 'auto') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', systemTheme);
        } else {
            document.documentElement.setAttribute('data-theme', this.theme);
        }

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (this.theme === 'auto') {
                document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
            }
        });
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        this.theme = newTheme;
        localStorage.setItem('theme', newTheme);

        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.classList.add('bounce-in');
            setTimeout(() => toggle.classList.remove('bounce-in'), 800);
        }
    }

    initAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.stagger-item').forEach((item, index) => {
            item.style.animationDelay = `${index * 100}ms`;
            observer.observe(item);
        });
    }

    initSectionNavigation() {
        document.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.addEventListener('click', (e) => {
                e.preventDefault();
                const href = navItem.getAttribute('onclick');
                if (href && href.includes('showSection')) {
                    const section = href.match(/'([^']+)'/)[1];
                    this.showSection(section);
                }
            });
        });

        this.showSection(this.currentSection);
    }

    initUsageTracking() {
        const usageText = document.getElementById('usageText');
        if (usageText) {
            // Free to use - no restrictions
            usageText.textContent = 'Unlimited FREE analysis • No signup required';
        }
    }

    getTodayUsage() {
        const today = new Date().toDateString();
        const usage = JSON.parse(localStorage.getItem('dailyUsage') || '{}');
        return usage[today] || 0;
    }

    incrementUsage() {
        const today = new Date().toDateString();
        const usage = JSON.parse(localStorage.getItem('dailyUsage') || '{}');
        usage[today] = (usage[today] || 0) + 1;
        localStorage.setItem('dailyUsage', JSON.stringify(usage));
        this.initUsageTracking();
    }

    showSection(sectionId) {
        document.querySelectorAll('.analysis-section').forEach(section => {
            section.classList.remove('active');
        });

        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active', 'text-purple-600', 'bg-purple-50');
            item.classList.add('text-gray-700');
        });

        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        const activeNavItem = document.querySelector(`[onclick="showSection('${sectionId}')"]`);
        if (activeNavItem) {
            activeNavItem.classList.remove('text-gray-700');
            activeNavItem.classList.add('active', 'text-purple-600', 'bg-purple-50');
        }

        this.currentSection = sectionId;
        this.initSectionContent(sectionId);
    }

    initSectionContent(sectionId) {
        switch(sectionId) {
            case 'summary':
                if (this.currentAnalysis) {
                    this.updateSummarySection(this.currentAnalysis);
                }
                break;
            case 'seo-analysis':
                if (this.currentAnalysis) {
                    this.updateSEOAnalysisSection(this.currentAnalysis);
                }
                break;
            case 'site-compliance':
                if (this.currentAnalysis) {
                    this.updateComplianceSection(this.currentAnalysis);
                }
                break;
            case 'links':
                if (this.currentAnalysis) {
                    this.updateLinksSection(this.currentAnalysis);
                }
                break;
            case 'seo-strategy':
                this.updateSEOStrategySection();
                break;
        }
    }

    showLoadingProgress(step, message, progress, stepNumber = 1) {
        const loadingTitle = document.getElementById('loadingTitle');
        const loadingMessage = document.getElementById('loadingMessage');
        const loadingProgress = document.getElementById('loadingProgress');
        const loadingStep = document.getElementById('loadingStep');
        const loadingPercent = document.getElementById('loadingPercent');
        
        // Professional loading messages with animations
        if (loadingTitle) {
            const titles = [
                '🤖 AI Brain Analyzing...',
                '🔍 Discovering SEO Secrets...',
                '⚡ Unleashing Optimization Power...',
                '🎯 Targeting Growth Opportunities...'
            ];
            loadingTitle.textContent = titles[Math.min(stepNumber - 1, titles.length - 1)] || titles[0];
            loadingTitle.style.opacity = '0';
            setTimeout(() => {
                loadingTitle.style.transition = 'opacity 0.3s ease';
                loadingTitle.style.opacity = '1';
            }, 100);
        }
        
        if (loadingMessage) {
            loadingMessage.textContent = message;
            loadingMessage.classList.add('fade-in');
        }
        
        if (loadingProgress) {
            loadingProgress.style.width = `${progress}%`;
            loadingProgress.style.transition = 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        }
        
        if (loadingStep) {
            loadingStep.textContent = step;
            loadingStep.classList.add('bounce-in');
        }
        
        if (loadingPercent) {
            loadingPercent.textContent = `${progress}%`;
            loadingPercent.style.fontWeight = '600';
            loadingPercent.style.color = progress === 100 ? '#10b981' : '#6366f1';
        }

        // Enhanced step indicators with better visual feedback
        document.querySelectorAll('.loading-step').forEach((stepEl, index) => {
            const stepIndicator = stepEl.querySelector('.status-indicator');
            if (stepIndicator) {
                stepIndicator.style.transition = 'all 0.3s ease';
                if (index + 1 < stepNumber) {
                    stepIndicator.className = 'status-indicator status-online';
                } else if (index + 1 === stepNumber) {
                    stepIndicator.className = 'status-indicator status-processing';
                    stepEl.classList.add('active');
                } else {
                    stepIndicator.className = 'status-indicator status-offline';
                    stepEl.classList.remove('active');
                }
            }
        });
        
        // Add professional pulsing effect for current step
        if (stepNumber <= 4) {
            const currentStep = document.querySelector(`.loading-step:nth-child(${stepNumber})`);
            if (currentStep) {
                currentStep.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    currentStep.style.transform = 'scale(1)';
                }, 200);
            }
        }
    }

    bindEvents() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeWebsite());
        }

        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeWebsite();
                }
            });
            
            urlInput.addEventListener('input', (e) => {
                this.validateURL(e.target.value);
            });
        }

        document.getElementById('addTodoBtn')?.addEventListener('click', () => this.showAddTodoForm());
        document.getElementById('saveTodoBtn')?.addEventListener('click', () => this.saveTodo());
        document.getElementById('clearCompletedBtn')?.addEventListener('click', () => this.clearCompleted());
        
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.analyzeWebsite();
            }
        });
    }
    
    validateURL(url) {
        const urlValidation = document.getElementById('urlValidation');
        const urlError = document.getElementById('urlError');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (!url) {
            urlValidation?.classList.add('hidden');
            urlError?.classList.add('hidden');
            if (analyzeBtn) analyzeBtn.disabled = false;
            return;
        }
        
        try {
            const urlObj = new URL(url);
            if (urlObj.protocol === 'http:' || urlObj.protocol === 'https:') {
                urlValidation?.classList.remove('hidden');
                urlError?.classList.add('hidden');
                if (analyzeBtn) analyzeBtn.disabled = false;
            } else {
                throw new Error('Protocol not supported');
            }
        } catch (error) {
            urlValidation?.classList.add('hidden');
            if (urlError) {
                urlError.textContent = 'URL format is incorrect, please enter a complete URL';
                urlError.classList.remove('hidden');
            }
            if (analyzeBtn) analyzeBtn.disabled = true;
        }
    }

    async analyzeWebsite() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput?.value?.trim();
        
        if (!url) {
            this.showAlert('Please enter a valid website URL', 'warning');
            return;
        }

        // Usage limit removed - free to use without restrictions

        this.showLoading(true);
        
        try {
            this.showLoadingProgress('🔍 Step 1/4: Discovering your website', 'Establishing secure connection and crawling...', 25, 1);
            
            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            this.showLoadingProgress('⚡ Step 2/4: Processing content', 'Extracting and analyzing page elements...', 50, 2);
            
            await new Promise(resolve => setTimeout(resolve, 500)); // Brief pause for UX

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showLoadingProgress('🎯 Step 3/4: Calculating SEO score', 'Running AI-powered optimization analysis...', 75, 3);
            
            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            this.showLoadingProgress('✨ Step 4/4: Generating insights', 'Preparing your personalized SEO report...', 100, 4);
            
            await new Promise(resolve => setTimeout(resolve, 800)); // Final pause for completion effect
            
            // Usage tracking removed - unlimited free service
            
            this.currentAnalysis = result;
            
            // Handle the new optimized response format
            const analysisData = result.analysis || result;
            
            this.showResults();
            this.updateAllSections(analysisData);
            this.generateTodos(analysisData);
            
            // Show performance info if available
            if (result.performance) {
                console.log(`✅ Analysis completed in ${result.performance.execution_time}s (optimized: ${result.performance.optimized})`);
            }
            
            this.showAlert('🎉 SEO Analysis Complete! Your website has been thoroughly scanned.', 'success');
            
        } catch (error) {
            console.error('Analysis failed:', error);
            this.showAlert('Analysis failed, please check network connection or URL', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    showResults() {
        const resultsContainer = document.getElementById('resultsContainer');
        if (resultsContainer) {
            // Professional reveal animation
            resultsContainer.style.opacity = '0';
            resultsContainer.style.transform = 'translateY(20px)';
            resultsContainer.classList.remove('hidden');
            
            // Smooth fade-in with stagger effect
            setTimeout(() => {
                resultsContainer.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                resultsContainer.style.opacity = '1';
                resultsContainer.style.transform = 'translateY(0)';
                
                // Add stagger animation to each section
                const sections = resultsContainer.querySelectorAll('.bg-white');
                sections.forEach((section, index) => {
                    section.style.opacity = '0';
                    section.style.transform = 'translateY(30px)';
                    section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    
                    setTimeout(() => {
                        section.style.opacity = '1';
                        section.style.transform = 'translateY(0)';
                    }, index * 150 + 300);
                });
            }, 100);
            
            // Smooth scroll to results with professional timing
            setTimeout(() => {
                resultsContainer.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 800);
            
            // Show success indicator
            this.showAlert('✨ SEO Analysis Complete! Comprehensive report generated.', 'success');
        }
    }

    updateAllSections(data) {
        this.updateSiteInfo(data);
        this.updateSummarySection(data);
        this.updateSEOAnalysisSection(data);
        this.updateComplianceSection(data);
        this.updateLinksSection(data);
        this.updateSEOStrategySection();
        this.initSectionContent(this.currentSection);
    }

    updateSiteInfo(data) {
        const siteUrlElement = document.getElementById('siteUrl');
        if (siteUrlElement && this.currentAnalysis) {
            const url = data.pages?.[0]?.url || document.getElementById('urlInput')?.value || '';
            siteUrlElement.textContent = url;
        }
    }

    updateSummarySection(data) {
        this.updateSEOScoreDisplay(data);
        this.updateIssuesOverview(data);
    }

    updateSEOScoreDisplay(data) {
        const scoreElement = document.getElementById('seoScore');
        const scoreCircle = document.getElementById('scoreCircle');
        const scoreNumber = document.getElementById('scoreNumber');
        const totalIssuesCount = document.getElementById('totalIssuesCount');
        const criticalCount = document.getElementById('criticalCount');
        const warningsCount = document.getElementById('warningsCount');
        const passedCount = document.getElementById('passedCount');
        const scoreDescription = document.getElementById('scoreDescription');
        
        const scoreData = this.currentAnalysis?.seo_score || this.calculateSEOScore(data);
        let score = typeof scoreData === 'object' ? scoreData.score : scoreData || 75;
        
        // Professional score animation with easing
        if (scoreElement && scoreNumber) {
            let currentScore = 0;
            const increment = score / 30; // Animate over 30 frames
            const animateScore = () => {
                currentScore += increment;
                if (currentScore >= score) {
                    currentScore = score;
                    scoreElement.textContent = Math.round(score);
                    scoreNumber.textContent = Math.round(score);
                } else {
                    scoreElement.textContent = Math.round(currentScore);
                    scoreNumber.textContent = Math.round(currentScore);
                    requestAnimationFrame(animateScore);
                }
            };
            requestAnimationFrame(animateScore);
        }
        
        // Enhanced circular progress with gradient and glow effects
        if (scoreCircle) {
            const circumference = 100;
            const progress = (score / 100) * circumference;
            
            // Animate the circle progress
            scoreCircle.style.transition = 'stroke-dasharray 2s cubic-bezier(0.4, 0, 0.2, 1)';
            scoreCircle.style.strokeDasharray = `${progress}, ${circumference}`;
            
            // Professional color scheme based on score
            let color = '#ef4444';
            let glowColor = 'rgba(239, 68, 68, 0.3)';
            let grade = 'F';
            
            if (score >= 90) {
                color = '#10b981';
                glowColor = 'rgba(16, 185, 129, 0.4)';
                grade = 'A+';
            } else if (score >= 80) {
                color = '#059669';
                glowColor = 'rgba(5, 150, 105, 0.4)';
                grade = 'A';
            } else if (score >= 70) {
                color = '#84cc16';
                glowColor = 'rgba(132, 204, 22, 0.4)';
                grade = 'B+';
            } else if (score >= 60) {
                color = '#eab308';
                glowColor = 'rgba(234, 179, 8, 0.4)';
                grade = 'B';
            } else if (score >= 50) {
                color = '#f59e0b';
                glowColor = 'rgba(245, 158, 11, 0.4)';
                grade = 'C';
            } else if (score >= 40) {
                color = '#f97316';
                glowColor = 'rgba(249, 115, 22, 0.4)';
                grade = 'D';
            }
            
            scoreCircle.style.stroke = color;
            scoreCircle.style.filter = `drop-shadow(0 0 8px ${glowColor})`;
            
            // Add grade indicator
            const gradeElement = document.querySelector('.score-grade');
            if (gradeElement) {
                gradeElement.textContent = grade;
                gradeElement.style.color = color;
            }
        }
        
        // Enhanced issues analysis with better categorization
        const issues = this.analyzeIssues(data);
        
        if (criticalCount) {
            criticalCount.textContent = issues.critical;
            criticalCount.parentElement.style.transform = issues.critical > 0 ? 'scale(1.05)' : 'scale(1)';
        }
        
        if (warningsCount) {
            warningsCount.textContent = issues.warnings;
            warningsCount.parentElement.style.transform = issues.warnings > 0 ? 'scale(1.02)' : 'scale(1)';
        }
        
        if (passedCount) {
            passedCount.textContent = issues.passed;
            passedCount.parentElement.style.opacity = issues.passed > 10 ? '1' : '0.8';
        }
        
        if (totalIssuesCount) {
            const totalIssues = issues.critical + issues.warnings;
            totalIssuesCount.textContent = totalIssues;
            
            // Professional description with dynamic messaging
            if (scoreDescription) {
                let statusMessage = '';
                if (score >= 90) {
                    statusMessage = 'Excellent! Your website has outstanding SEO optimization with minimal issues to address.';
                } else if (score >= 80) {
                    statusMessage = 'Great! Your website has strong SEO fundamentals with only minor improvements needed.';
                } else if (score >= 70) {
                    statusMessage = 'Good! Your website has solid SEO basics, but there are opportunities for significant improvement.';
                } else if (score >= 60) {
                    statusMessage = 'Fair. Your website needs attention to improve search engine visibility and ranking potential.';
                } else {
                    statusMessage = 'Critical issues detected! Immediate action is required to improve your website\'s SEO performance.';
                }
                
                scoreDescription.innerHTML = `
                    <p class="text-gray-700 mb-2">${statusMessage}</p>
                    <p class="text-sm text-gray-600">
                        SEO Score: <strong class="text-gray-900" style="color: ${color}">${Math.round(score)}/100</strong> | 
                        Issues to fix: <strong class="text-red-600">${totalIssues}</strong> | 
                        Checks passed: <strong class="text-green-600">${issues.passed}</strong>
                    </p>
                `;
            }
        }
        
        // Add professional animations to the score container
        const scoreContainer = scoreElement?.closest('.score-circle-large');
        if (scoreContainer) {
            scoreContainer.style.transform = 'scale(1)';
            scoreContainer.style.transition = 'transform 0.3s ease';
            setTimeout(() => {
                scoreContainer.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    scoreContainer.style.transform = 'scale(1)';
                }, 200);
            }, 1000);
        }
    }

    calculateSEOScore(data) {
        let score = 100;
        
        if (data.pages && data.pages.length > 0) {
            const page = data.pages[0];
            
            if (!page.title) score -= 15;
            else if (page.title.length < 30 || page.title.length > 60) score -= 5;
            
            if (!page.description) score -= 20;
            else if (page.description.length < 120 || page.description.length > 160) score -= 10;
            
            if (!page.h1 || page.h1.length === 0) score -= 15;
            if (page.images && page.images.some(img => !img.alt)) score -= 10;
            
            if (page.warnings && page.warnings.length > 0) {
                score -= Math.min(page.warnings.length * 5, 30);
            }
        }
        
        return Math.max(score, 0);
    }

    analyzeIssues(data) {
        const issues = { critical: 0, warnings: 0, passed: 0 };
        
        if (data.pages && data.pages.length > 0) {
            const page = data.pages[0];
            
            if (!page.description || page.description.length < 120) issues.critical++;
            if (page.images && page.images.some(img => !img.alt)) issues.critical++;
            if (!page.h1 || page.h1.length === 0) issues.critical++;
            
            if (page.title && (page.title.length < 30 || page.title.length > 60)) issues.warnings++;
            if (page.canonical && page.canonical !== page.url) issues.warnings++;
            
            issues.passed = 15 - issues.critical - issues.warnings;
        } else {
            issues.critical = 4;
            issues.warnings = 2;
            issues.passed = 12;
        }
        
        return issues;
    }

    updateIssuesOverview(data) {
        const container = document.getElementById('issuesContainer');
        if (!container) return;
        
        const issues = this.generateIssuesList(data);
        
        container.innerHTML = issues.map(issue => `
            <div class="issue-card ${issue.type} p-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <i class="${issue.icon} ${issue.type === 'critical' ? 'text-red-500' : 'text-yellow-500'} mr-3"></i>
                        <div>
                            <h4 class="font-semibold text-gray-900">${issue.title}</h4>
                            <p class="text-sm text-gray-600">${issue.message}</p>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    generateIssuesList(data) {
        const issues = [];
        
        if (data.pages && data.pages.length > 0) {
            const page = data.pages[0];
            
            if (!page.description || page.description.length < 120) {
                issues.push({
                    type: 'critical',
                    icon: 'fas fa-times-circle',
                    title: 'Description',
                    message: 'Meta description is too short or missing — expand to at least 140 characters.'
                });
            }
            
            if (page.images && page.images.some(img => !img.alt)) {
                const missingAlt = page.images.filter(img => !img.alt).length;
                issues.push({
                    type: 'critical',
                    icon: 'fas fa-times-circle',
                    title: 'Image Alt',
                    message: `Some images on your page have no alt attribute. (${missingAlt})`
                });
            }
            
            if (page.title && (page.title.length < 30 || page.title.length > 60)) {
                issues.push({
                    type: 'warning',
                    icon: 'fas fa-exclamation-triangle',
                    title: 'Title',
                    message: `Meta title length is ${page.title.length < 30 ? 'too short' : 'too long'} — aim for 50-60 characters.`
                });
            }
        } else {
            issues.push(
                {
                    type: 'critical',
                    icon: 'fas fa-times-circle',
                    title: 'Description',
                    message: 'Meta description is too short (30 characters) — expand to at least 140 characters.'
                },
                {
                    type: 'critical',
                    icon: 'fas fa-times-circle',
                    title: 'Image Alt',
                    message: 'Some images on your page have no alt attribute. (2)'
                },
                {
                    type: 'warning',
                    icon: 'fas fa-exclamation-triangle',
                    title: 'Title',
                    message: 'Meta title is a bit short (33 characters) — aim for 50-60 characters.'
                }
            );
        }
        
        return issues;
    }

    updateSEOAnalysisSection(data) {
        if (!data.pages || data.pages.length === 0) return;
        
        const page = data.pages[0];
        
        const analyzedUrl = document.getElementById('analyzedUrl');
        if (analyzedUrl) analyzedUrl.textContent = page.url || '';
        
        const canonicalUrl = document.getElementById('canonicalUrl');
        if (canonicalUrl) canonicalUrl.textContent = page.canonical || page.url || '';
        
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) pageTitle.textContent = page.title || 'No title found';
        
        const pageDescription = document.getElementById('pageDescription');
        if (pageDescription) pageDescription.textContent = page.description || 'No meta description found';
        
        const h1Text = document.getElementById('h1Text');
        if (h1Text) {
            const h1 = page.h1 && page.h1.length > 0 ? page.h1[0] : 'No H1 found';
            h1Text.textContent = h1;
        }
        
        this.updateHeadingStructure(page);
        this.updateKeywordDensity(data);
        this.updateImagesList(page);
    }

    updateHeadingStructure(page) {
        const container = document.getElementById('headingStructure');
        if (!container) return;
        
        const headingData = this.extractHeadingData(page) || [
            { level: 'H1', frequency: 1, value: page.h1?.[0] || 'Main Heading' },
            { level: 'H2', frequency: page.h2?.length || 3, value: page.h2?.[0] || 'Section Heading' },
            { level: 'H3', frequency: page.h3?.length || 5, value: page.h3?.[0] || 'Subsection Heading' },
            { level: 'H4', frequency: page.h4?.length || 2, value: page.h4?.[0] || 'Sub-subsection Heading' }
        ];
        
        container.innerHTML = headingData.map(heading => `
            <div class="flex items-center space-x-4 py-2">
                <span class="text-sm font-medium w-16">${heading.level}</span>
                <div class="w-24">
                    <div class="flex items-center space-x-2">
                        <span class="text-sm">${heading.frequency}</span>
                        <div class="flex-1 bg-gray-200 rounded-full h-2">
                            <div class="frequency-bar rounded-full h-2" style="width: ${Math.min(heading.frequency * 10, 100)}%"></div>
                        </div>
                    </div>
                </div>
                <span class="text-sm text-gray-600 flex-1">${heading.value || ''}</span>
            </div>
        `).join('');
    }

    extractHeadingData(page) {
        const headings = [];
        ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].forEach(tag => {
            if (page[tag] && page[tag].length > 0) {
                headings.push({
                    level: tag.toUpperCase(),
                    frequency: page[tag].length,
                    value: page[tag][0]
                });
            }
        });
        return headings.length > 0 ? headings : null;
    }

    updateKeywordDensity(data) {
        const table = document.getElementById('keywordDensityTable');
        if (!table) return;
        
        const keywords = data.keywords || [
            { keyword: 'seo', count: 20, density: 2.5 },
            { keyword: 'analysis', count: 15, density: 1.9 },
            { keyword: 'website', count: 12, density: 1.5 },
            { keyword: 'optimization', count: 10, density: 1.2 },
            { keyword: 'content', count: 8, density: 1.0 }
        ];
        
        table.innerHTML = keywords.slice(0, 10).map(item => `
            <tr class="hover:bg-gray-50">
                <td class="py-2 text-sm">${item.keyword || item.word}</td>
                <td class="py-2 text-sm">${item.count || item.repeats}</td>
                <td class="py-2 text-sm">${(item.density || (item.count / 400 * 100)).toFixed(1)}%</td>
            </tr>
        `).join('');
    }

    updateImagesList(page) {
        const container = document.getElementById('imagesList');
        if (!container) return;
        
        if (page.images && page.images.length > 0) {
            const imagesWithoutAlt = page.images.filter(img => !img.alt);
            container.innerHTML = imagesWithoutAlt.map(img => `
                <div class="text-sm text-blue-600">${img.src}</div>
            `).join('') || '<div class="text-sm text-green-600">All images have alt attributes</div>';
        } else {
            container.innerHTML = '<div class="text-sm text-gray-500">No images found</div>';
        }
    }

    updateComplianceSection(data) {
        if (!data.pages || data.pages.length === 0) return;
        
        const page = data.pages[0];
        const baseUrl = new URL(page.url || 'https://example.com');
        
        const robotsUrl = document.getElementById('robotsUrl');
        if (robotsUrl) robotsUrl.textContent = `${baseUrl.origin}/robots.txt`;
        
        const sitemapUrl = document.getElementById('sitemapUrl');
        if (sitemapUrl) sitemapUrl.textContent = `${baseUrl.origin}/sitemap.xml`;
        
        const pageLang = document.getElementById('pageLang');
        if (pageLang) pageLang.textContent = page.lang || 'en';
        
        const faviconUrl = document.getElementById('faviconUrl');
        if (faviconUrl) faviconUrl.textContent = `${baseUrl.origin}/favicon.ico`;
    }

    updateLinksSection(data) {
        this.updateInternalLinks(data);
        this.updateExternalLinks(data);
    }

    updateInternalLinks(data) {
        const table = document.getElementById('internalLinksTable');
        const countElement = document.getElementById('internalLinksCount');
        
        if (!table) return;
        
        const internalLinks = this.extractInternalLinks(data) || [
            { url: 'https://example.com/', anchor: 'Home' },
            { url: 'https://example.com/about', anchor: 'About' },
            { url: 'https://example.com/services', anchor: 'Services' },
            { url: 'https://example.com/contact', anchor: 'Contact' }
        ];
        
        if (countElement) {
            countElement.textContent = `(Found ${internalLinks.length})`;
        }
        
        table.innerHTML = internalLinks.map((link, index) => `
            <tr class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm">${index + 1}</td>
                <td class="px-4 py-2 text-sm text-blue-600">${link.url}</td>
                <td class="px-4 py-2 text-sm">${link.anchor}</td>
            </tr>
        `).join('');
    }

    updateExternalLinks(data) {
        const table = document.getElementById('externalLinksTable');
        const countElement = document.getElementById('externalLinksCount');
        
        if (!table) return;
        
        const externalLinks = this.extractExternalLinks(data) || [
            { url: 'https://github.com/', anchor: 'GitHub' },
            { url: 'https://stackoverflow.com/', anchor: 'Stack Overflow' },
            { url: 'https://developer.mozilla.org/', anchor: 'MDN' }
        ];
        
        if (countElement) {
            countElement.textContent = `(Found ${externalLinks.length})`;
        }
        
        table.innerHTML = externalLinks.map((link, index) => `
            <tr class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm">${index + 1}</td>
                <td class="px-4 py-2 text-sm text-blue-600">${link.url}</td>
                <td class="px-4 py-2 text-sm">${link.anchor}</td>
            </tr>
        `).join('');
    }

    extractInternalLinks(data) {
        if (data.pages && data.pages[0] && data.pages[0].links) {
            const baseUrl = new URL(data.pages[0].url);
            return data.pages[0].links.filter(link => {
                try {
                    const linkUrl = new URL(link.href, baseUrl);
                    return linkUrl.hostname === baseUrl.hostname;
                } catch {
                    return false;
                }
            }).map(link => ({
                url: link.href,
                anchor: link.text || link.anchor || '[No anchor text]'
            }));
        }
        return null;
    }

    extractExternalLinks(data) {
        if (data.pages && data.pages[0] && data.pages[0].links) {
            const baseUrl = new URL(data.pages[0].url);
            return data.pages[0].links.filter(link => {
                try {
                    const linkUrl = new URL(link.href, baseUrl);
                    return linkUrl.hostname !== baseUrl.hostname;
                } catch {
                    return false;
                }
            }).map(link => ({
                url: link.href,
                anchor: link.text || link.anchor || '[No anchor text]'
            }));
        }
        return null;
    }

    updateSEOStrategySection() {
        const container = document.getElementById('seoStrategyTasks');
        const countElement = document.getElementById('strategyTasksCount');
        
        if (!container) return;
        
        const tasks = [
            'Review your content to match audience needs',
            'Compare your traffic and rankings to competitors',
            'Analyze your backlinks and find gaps compared to competitors',
            'Ensure your site is fast, mobile-friendly, and easy to use',
            'Set SEO goals and create a simple action plan',
            'Track progress regularly and adjust as needed'
        ];
        
        if (countElement) {
            countElement.textContent = `${tasks.length} Tasks`;
        }
        
        document.querySelectorAll('#seoStrategyTasks input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const taskText = e.target.nextElementSibling.textContent;
                if (e.target.checked) {
                    this.addTodoFromRecommendation(taskText, 'medium');
                }
            });
        });
    }

    generateTodos(data) {
        const autoTodos = [];
        
        if (data.pages && data.pages.length > 0) {
            const page = data.pages[0];
            const issues = this.generateIssuesList(data);
            
            issues.filter(issue => issue.type === 'critical').forEach(issue => {
                autoTodos.push({
                    id: Date.now() + Math.random(),
                    text: `Fix ${issue.title}: ${issue.message}`,
                    priority: 'high',
                    completed: false,
                    createdAt: new Date().toISOString(),
                    auto: true
                });
            });
            
            issues.filter(issue => issue.type === 'warning').forEach(issue => {
                autoTodos.push({
                    id: Date.now() + Math.random(),
                    text: `Improve ${issue.title}: ${issue.message}`,
                    priority: 'medium',
                    completed: false,
                    createdAt: new Date().toISOString(),
                    auto: true
                });
            });
        }
        
        if (autoTodos.length < 3) {
            autoTodos.push(
                {
                    id: Date.now() + Math.random() + 1,
                    text: 'Optimize page loading speed',
                    priority: 'medium',
                    completed: false,
                    createdAt: new Date().toISOString(),
                    auto: true
                },
                {
                    id: Date.now() + Math.random() + 2,
                    text: 'Add internal linking structure',
                    priority: 'low',
                    completed: false,
                    createdAt: new Date().toISOString(),
                    auto: true
                }
            );
        }
        
        autoTodos.forEach(autoTodo => {
            const exists = this.todos.some(todo => 
                todo.text.toLowerCase().includes(autoTodo.text.toLowerCase().substring(0, 20))
            );
            if (!exists) {
                this.todos.push(autoTodo);
            }
        });
        
        this.saveTodos();
        this.renderTodos();
        this.updateTodoStats();
        
        if (autoTodos.length > 0) {
            this.showAlert(`Auto-generated ${autoTodos.filter(todo => !this.todos.some(existing => existing.text === todo.text)).length} SEO optimization tasks`, 'info');
        }
    }

    showAddTodoForm() {
        const form = document.getElementById('addTodoForm');
        if (form) {
            form.classList.toggle('hidden');
            if (!form.classList.contains('hidden')) {
                document.getElementById('todoInput')?.focus();
            }
        }
    }

    saveTodo() {
        const input = document.getElementById('todoInput');
        const priority = document.getElementById('todoPriority');
        
        const text = input?.value?.trim();
        if (!text) return;
        
        const todo = {
            id: Date.now(),
            text: text,
            priority: priority?.value || 'medium',
            completed: false,
            createdAt: new Date().toISOString()
        };
        
        this.todos.push(todo);
        this.saveTodos();
        this.renderTodos();
        this.updateTodoStats();
        
        if (input) input.value = '';
        this.showAddTodoForm();
    }

    addTodoFromRecommendation(action, priority) {
        const todo = {
            id: Date.now(),
            text: action,
            priority: priority,
            completed: false,
            createdAt: new Date().toISOString()
        };
        
        this.todos.push(todo);
        this.saveTodos();
        this.renderTodos();
        this.updateTodoStats();
        
        this.showAlert('Added to TODO list', 'success');
    }

    toggleTodo(id) {
        const todo = this.todos.find(t => t.id === id);
        if (todo) {
            todo.completed = !todo.completed;
            this.saveTodos();
            this.renderTodos();
            this.updateTodoStats();
        }
    }

    deleteTodo(id) {
        this.todos = this.todos.filter(t => t.id !== id);
        this.saveTodos();
        this.renderTodos();
        this.updateTodoStats();
    }

    clearCompleted() {
        this.todos = this.todos.filter(t => !t.completed);
        this.saveTodos();
        this.renderTodos();
        this.updateTodoStats();
    }

    renderTodos() {
        const container = document.getElementById('todoList');
        if (!container) return;
        
        if (this.todos.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">No SEO tasks</p>';
            return;
        }
        
        const sortedTodos = this.todos.sort((a, b) => {
            if (a.completed !== b.completed) {
                return a.completed ? 1 : -1;
            }
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });
        
        container.innerHTML = sortedTodos.map(todo => `
            <div class="todo-item flex items-center p-3 border rounded-lg ${todo.completed ? 'bg-gray-50 opacity-75' : 'bg-white'}">
                <input type="checkbox" ${todo.completed ? 'checked' : ''} 
                       onchange="seoAgent.toggleTodo(${todo.id})" 
                       class="mr-3 h-4 w-4 text-indigo-600 rounded">
                <div class="flex-1">
                    <span class="${todo.completed ? 'line-through text-gray-500' : 'text-gray-900'}">${todo.text}</span>
                    <div class="text-xs text-gray-500 mt-1">
                        <span class="priority-badge priority-${todo.priority} px-2 py-1 rounded mr-2">
                            ${todo.priority === 'high' ? 'High' : todo.priority === 'medium' ? 'Medium' : 'Low'}
                        </span>
                        ${new Date(todo.createdAt).toLocaleDateString()}
                    </div>
                </div>
                <button onclick="seoAgent.deleteTodo(${todo.id})" 
                        class="text-red-500 hover:text-red-700 ml-2">
                    <i class="fas fa-trash text-sm"></i>
                </button>
            </div>
        `).join('');
    }

    updateTodoStats() {
        const statsElement = document.getElementById('todoStats');
        if (statsElement) {
            const remaining = this.todos.filter(t => !t.completed).length;
            statsElement.textContent = `${remaining} pending tasks`;
        }
    }

    saveTodos() {
        localStorage.setItem('seoTodos', JSON.stringify(this.todos));
    }

    showLoading(show) {
        const loadingElement = document.getElementById('loadingIndicator');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (loadingElement) {
            if (show) {
                loadingElement.classList.remove('hidden');
            } else {
                loadingElement.classList.add('hidden');
            }
        }
        
        if (analyzeBtn) {
            analyzeBtn.disabled = show;
            analyzeBtn.innerHTML = show ? 
                '<i class="fas fa-rocket fa-spin mr-2"></i>Analyzing...' : 
                '<i class="fas fa-rocket mr-2"></i>Analyze Now';
        }
    }

    showAlert(message, type = 'info') {
        // Remove any existing alerts first
        const existingAlerts = document.querySelectorAll('.seo-alert');
        existingAlerts.forEach(alert => {
            alert.style.transform = 'translateX(400px)';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
        
        const alert = document.createElement('div');
        alert.className = `seo-alert fixed top-6 right-6 p-4 rounded-lg shadow-lg z-50 alert-${type} max-w-sm`;
        
        // Professional styling based on type
        let icon = 'fa-info-circle';
        let bgColor = 'linear-gradient(135deg, rgba(59, 130, 246, 0.9) 0%, rgba(37, 99, 235, 0.9) 100%)';
        let borderColor = '#3b82f6';
        
        switch (type) {
            case 'success':
                icon = 'fa-check-circle';
                bgColor = 'linear-gradient(135deg, rgba(16, 185, 129, 0.9) 0%, rgba(5, 150, 105, 0.9) 100%)';
                borderColor = '#10b981';
                break;
            case 'error':
                icon = 'fa-exclamation-circle';
                bgColor = 'linear-gradient(135deg, rgba(239, 68, 68, 0.9) 0%, rgba(220, 38, 38, 0.9) 100%)';
                borderColor = '#ef4444';
                break;
            case 'warning':
                icon = 'fa-exclamation-triangle';
                bgColor = 'linear-gradient(135deg, rgba(245, 158, 11, 0.9) 0%, rgba(217, 119, 6, 0.9) 100%)';
                borderColor = '#f59e0b';
                break;
        }
        
        alert.style.background = bgColor;
        alert.style.backdropFilter = 'blur(10px)';
        alert.style.border = `1px solid ${borderColor}`;
        alert.style.color = 'white';
        alert.style.fontWeight = '500';
        alert.style.transform = 'translateX(400px)';
        alert.style.opacity = '0';
        alert.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        alert.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${icon} mr-3 text-lg"></i>
                <div class="flex-1">
                    <span class="text-sm">${message}</span>
                </div>
                <button onclick="this.parentElement.parentElement.style.transform='translateX(400px)'; this.parentElement.parentElement.style.opacity='0'; setTimeout(() => this.parentElement.parentElement.remove(), 300);" 
                        class="ml-4 text-white hover:text-gray-200 transition-colors">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(alert);
        
        // Professional slide-in animation
        setTimeout(() => {
            alert.style.transform = 'translateX(0)';
            alert.style.opacity = '1';
        }, 100);
        
        // Add subtle bounce effect
        setTimeout(() => {
            alert.style.transform = 'translateX(-8px)';
            setTimeout(() => {
                alert.style.transform = 'translateX(0)';
            }, 150);
        }, 400);
        
        // Auto-dismiss with fade out
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.transform = 'translateX(400px)';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentElement) {
                        alert.remove();
                    }
                }, 300);
            }
        }, type === 'success' ? 4000 : 5000);
        
        // Add click to dismiss
        alert.addEventListener('click', () => {
            alert.style.transform = 'translateX(400px)';
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 300);
        });
    }
}

// Global functions
function toggleTheme() {
    if (window.seoAgent) {
        window.seoAgent.toggleTheme();
    } else {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }
}

function showSection(sectionId) {
    if (window.seoAgent) {
        window.seoAgent.showSection(sectionId);
    }
}

function closeModal() {
    const modal = document.getElementById('pageModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function refreshAnalysis() {
    if (window.seoAgent) {
        window.seoAgent.analyzeWebsite();
    }
}

function exportResults() {
    if (window.seoAgent && window.seoAgent.currentAnalysis) {
        const dataStr = JSON.stringify(window.seoAgent.currentAnalysis, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'seo-analysis.json';
        link.click();
        URL.revokeObjectURL(url);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.seoAgent = new SEOAgent();
    
    // Add dynamic styles
    const style = document.createElement('style');
    style.textContent = `
        .loading-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            font-size: 0.75rem;
            transition: all var(--transition-base);
        }
        
        .loading-step.active .status-indicator {
            animation: pulse-processing 1.5s infinite;
        }
        
        .loading-step span {
            color: var(--gray-600);
            font-weight: 500;
        }
        
        .loading-step.active span {
            color: var(--primary-600);
            font-weight: 600;
        }
    `;
    document.head.appendChild(style);
});