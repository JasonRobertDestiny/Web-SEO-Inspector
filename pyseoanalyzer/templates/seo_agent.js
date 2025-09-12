class SEOAgent {
    constructor() {
        this.apiBaseUrl = 'http://127.0.0.1:5000/api';
        this.currentAnalysis = null;
        this.todos = JSON.parse(localStorage.getItem('seoTodos')) || [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadRecommendations();
        this.renderTodos();
        this.updateTodoStats();
    }

    bindEvents() {
        // 分析按钮事件
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeWebsite());
        }

        // URL输入框事件
        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeWebsite();
                }
            });
            
            // 实时URL验证
            urlInput.addEventListener('input', (e) => {
                this.validateURL(e.target.value);
            });
        }
        
        // 使用指南关闭按钮
        const hideGuideBtn = document.getElementById('hideGuide');
        if (hideGuideBtn) {
            hideGuideBtn.addEventListener('click', () => {
                const guideElement = hideGuideBtn.closest('.bg-blue-50');
                if (guideElement) {
                    guideElement.style.display = 'none';
                    localStorage.setItem('hideGuide', 'true');
                }
            });
        }
        
        // 检查是否需要隐藏使用指南
        if (localStorage.getItem('hideGuide') === 'true') {
            const guideElement = document.querySelector('.bg-blue-50');
            if (guideElement) {
                guideElement.style.display = 'none';
            }
        }

        // TODO相关事件
        document.getElementById('addTodoBtn')?.addEventListener('click', () => this.showAddTodoForm());
        document.getElementById('saveTodoBtn')?.addEventListener('click', () => this.saveTodo());
        document.getElementById('clearCompletedBtn')?.addEventListener('click', () => this.clearCompleted());
        
        // 键盘快捷键
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
            urlValidation.classList.add('hidden');
            urlError.classList.add('hidden');
            analyzeBtn.disabled = false;
            return;
        }
        
        try {
            const urlObj = new URL(url);
            if (urlObj.protocol === 'http:' || urlObj.protocol === 'https:') {
                urlValidation.classList.remove('hidden');
                urlError.classList.add('hidden');
                analyzeBtn.disabled = false;
            } else {
                throw new Error('协议不支持');
            }
        } catch (error) {
            urlValidation.classList.add('hidden');
            urlError.textContent = 'URL格式不正确，请输入完整的网址';
            urlError.classList.remove('hidden');
            analyzeBtn.disabled = true;
        }
    }
    
    showLoadingProgress(step, message, progress) {
        const loadingTitle = document.getElementById('loadingTitle');
        const loadingMessage = document.getElementById('loadingMessage');
        const loadingProgress = document.getElementById('loadingProgress');
        const loadingStep = document.getElementById('loadingStep');
        
        if (loadingTitle) loadingTitle.textContent = '正在分析中...';
        if (loadingMessage) loadingMessage.textContent = message;
        if (loadingProgress) loadingProgress.style.width = `${progress}%`;
        if (loadingStep) loadingStep.textContent = step;
    }

    async analyzeWebsite() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput?.value?.trim();
        
        if (!url) {
            this.showAlert('请输入有效的网站URL', 'warning');
            return;
        }

        this.showLoading(true);
        
        try {
            // 显示进度步骤
            this.showLoadingProgress('步骤 1/4', '连接到网站', 25);
            
            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            this.showLoadingProgress('步骤 2/4', '获取页面内容', 50);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showLoadingProgress('步骤 3/4', '分析SEO数据', 75);
            
            const result = await response.json();
            
            // 检查API返回的数据结构
            if (result.error) {
                throw new Error(result.error);
            }
            
            this.showLoadingProgress('步骤 4/4', '生成分析报告', 100);
            
            // 保存完整的API响应数据
            this.currentAnalysis = result;
            // 提取分析数据用于UI更新
            const data = result.analysis || result;
            this.updateUI(data);
            this.generateTodos(data);
            
        } catch (error) {
            console.error('分析失败:', error);
            this.showAlert('分析失败，请检查网络连接或URL是否正确', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    updateUI(data) {
        // 更新SEO评分
        this.updateSEOScore(data);
        
        // 更新预警
        this.updateAlerts(data);
        
        // 更新建议
        this.updateRecommendations(data);
    }

    updateSEOScore(data) {
        const scoreElement = document.getElementById('seoScore');
        // seo_score在API响应的顶层，不在analysis中
        const scoreData = this.currentAnalysis?.seo_score || data.seo_score;
        
        if (scoreElement && scoreData !== undefined) {
            // 处理评分数据，可能是对象或数字
            let score, grade, status;
            if (typeof scoreData === 'object' && scoreData !== null) {
                score = scoreData.score;
                grade = scoreData.grade;
                status = scoreData.status;
            } else {
                score = scoreData;
                grade = score >= 90 ? 'A+' : score >= 80 ? 'A' : score >= 70 ? 'B' : score >= 60 ? 'C' : 'D';
                status = score >= 90 ? 'excellent' : score >= 70 ? 'good' : 'needs_improvement';
            }
            
            let scoreClass = 'text-red-600';
            let bgClass = 'bg-red-100';
            
            if (score >= 80) {
                scoreClass = 'text-green-600';
                bgClass = 'bg-green-100';
            } else if (score >= 60) {
                scoreClass = 'text-yellow-600';
                bgClass = 'bg-yellow-100';
            }
            
            scoreElement.innerHTML = `
                <div class="${bgClass} rounded-lg shadow-md p-6 text-center">
                    <div class="text-3xl font-bold ${scoreClass} mb-2">${score}</div>
                    <div class="text-sm font-medium ${scoreClass} mb-1">等级: ${grade}</div>
                    <div class="text-gray-600">SEO评分</div>
                    <div class="mt-2">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div class="${scoreClass.replace('text-', 'bg-')} h-2 rounded-full" style="width: ${score}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    updateAlerts(data) {
        const alertsContainer = document.getElementById('alertsContainer');
        if (!alertsContainer) return;

        const alerts = this.generateAlerts(data);
        
        alertsContainer.innerHTML = alerts.map(alert => `
            <div class="alert-card ${alert.type} p-4 rounded-lg border-l-4">
                <div class="flex items-start">
                    <i class="${alert.icon} text-lg mr-3 mt-1"></i>
                    <div class="flex-1">
                        <h4 class="font-semibold mb-1">${alert.title}</h4>
                        <p class="text-sm opacity-90">${alert.message}</p>
                        ${alert.action ? `<button class="mt-2 text-sm underline hover:no-underline" onclick="${alert.action}">${alert.actionText}</button>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    generateAlerts(data) {
        const alerts = [];
        
        if (data.pages) {
            const totalIssues = data.pages.reduce((sum, page) => sum + (page.warnings?.length || 0), 0);
            
            if (totalIssues > 10) {
                alerts.push({
                    type: 'alert-error',
                    icon: 'fas fa-exclamation-triangle',
                    title: '严重SEO问题',
                    message: `发现 ${totalIssues} 个SEO问题需要立即处理`,
                    action: 'scrollToSection("pageAnalysis")',
                    actionText: '查看详情'
                });
            } else if (totalIssues > 5) {
                alerts.push({
                    type: 'alert-warning',
                    icon: 'fas fa-exclamation-circle',
                    title: 'SEO优化建议',
                    message: `发现 ${totalIssues} 个可优化的SEO问题`,
                    action: 'scrollToSection("pageAnalysis")',
                    actionText: '查看详情'
                });
            }
        }
        
        if (data.keywords && data.keywords.length < 10) {
            alerts.push({
                type: 'alert-info',
                icon: 'fas fa-key',
                title: '关键词密度偏低',
                message: '建议增加相关关键词以提升SEO效果',
                action: 'scrollToSection("keywordAnalysis")',
                actionText: '查看关键词分析'
            });
        }
        
        return alerts;
    }

    async loadRecommendations() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/recommendations`);
            if (response.ok) {
                const recommendations = await response.json();
                this.updateRecommendationsUI(recommendations);
            }
        } catch (error) {
            console.error('加载建议失败:', error);
        }
    }

    updateRecommendations(data) {
        const recommendations = this.generateRecommendations(data);
        this.updateRecommendationsUI(recommendations);
    }

    generateRecommendations(data) {
        const recommendations = [];
        
        if (data.pages) {
            data.pages.forEach((page, index) => {
                if (page.warnings && page.warnings.length > 0) {
                    page.warnings.forEach(warning => {
                        recommendations.push({
                            type: 'page',
                            priority: warning.includes('title') || warning.includes('description') ? 'high' : 'medium',
                            title: `页面 ${index + 1} 优化`,
                            description: warning,
                            action: `优化 ${page.url || '页面'}`
                        });
                    });
                }
            });
        }
        
        if (data.keywords && data.keywords.length > 0) {
            const topKeywords = data.keywords.slice(0, 5);
            recommendations.push({
                type: 'keyword',
                priority: 'medium',
                title: '关键词优化',
                description: `重点优化关键词: ${topKeywords.map(k => k.keyword).join(', ')}`,
                action: '优化关键词密度和分布'
            });
        }
        
        return recommendations;
    }

    updateRecommendationsUI(recommendations) {
        const container = document.querySelector('#recommendationsContainer .bg-white');
        if (!container) return;
        
        if (recommendations.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">暂无SEO建议</p>';
            return;
        }
        
        container.innerHTML = `
            <div class="space-y-4">
                ${recommendations.map((rec, index) => `
                    <div class="recommendation-item border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <div class="flex items-center mb-2">
                                    <span class="priority-badge priority-${rec.priority} px-2 py-1 rounded text-xs font-medium mr-2">
                                        ${rec.priority === 'high' ? '高优先级' : rec.priority === 'medium' ? '中优先级' : '低优先级'}
                                    </span>
                                    <h4 class="font-semibold text-gray-900">${rec.title}</h4>
                                </div>
                                <p class="text-gray-600 text-sm mb-3">${rec.description}</p>
                                <button class="text-indigo-600 hover:text-indigo-800 text-sm font-medium" 
                                        onclick="seoAgent.addTodoFromRecommendation('${rec.action}', '${rec.priority}')">
                                    <i class="fas fa-plus mr-1"></i>添加到TODO
                                </button>
                            </div>
                            <div class="ml-4">
                                <i class="fas ${rec.type === 'page' ? 'fa-file-alt' : 'fa-key'} text-gray-400"></i>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // TODO管理功能
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
        
        // 清空表单
        if (input) input.value = '';
        this.showAddTodoForm(); // 隐藏表单
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
        
        this.showAlert('已添加到TODO清单', 'success');
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
            container.innerHTML = '<p class="text-gray-500 text-center py-8">暂无SEO任务</p>';
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
                            ${todo.priority === 'high' ? '高' : todo.priority === 'medium' ? '中' : '低'}
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
            statsElement.textContent = `${remaining} 个待完成任务`;
        }
    }

    saveTodos() {
        localStorage.setItem('seoTodos', JSON.stringify(this.todos));
    }

    generateTodos(data) {
        // 基于分析结果自动生成TODO项
        const autoTodos = [];
        
        if (data.pages) {
            data.pages.forEach((page, index) => {
                if (page.warnings && page.warnings.length > 0) {
                    page.warnings.forEach(warning => {
                        autoTodos.push({
                            id: Date.now() + Math.random(),
                            text: `修复页面 ${index + 1}: ${warning}`,
                            priority: warning.includes('title') || warning.includes('description') ? 'high' : 'medium',
                            completed: false,
                            createdAt: new Date().toISOString(),
                            auto: true
                        });
                    });
                }
            });
        }
        
        // 添加自动生成的TODO（避免重复）
        autoTodos.forEach(autoTodo => {
            const exists = this.todos.some(todo => todo.text === autoTodo.text);
            if (!exists) {
                this.todos.push(autoTodo);
            }
        });
        
        this.saveTodos();
        this.renderTodos();
        this.updateTodoStats();
    }

    showLoading(show) {
        const loadingElement = document.getElementById('loadingIndicator');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (loadingElement) {
            loadingElement.style.display = show ? 'block' : 'none';
        }
        
        if (analyzeBtn) {
            analyzeBtn.disabled = show;
            analyzeBtn.innerHTML = show ? 
                '<i class="fas fa-spinner fa-spin mr-2"></i>分析中...' : 
                '<i class="fas fa-search mr-2"></i>开始分析';
        }
    }

    showAlert(message, type = 'info') {
        // 创建临时提示
        const alert = document.createElement('div');
        alert.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 alert-${type}`;
        alert.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} mr-2"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-lg">&times;</button>
            </div>
        `;
        
        document.body.appendChild(alert);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 3000);
    }
}

// 全局实例将在HTML文件中初始化

// Legacy函数映射（保持向后兼容）
function toggleNotification(element) {
    const content = element.nextElementSibling;
    const icon = element.querySelector('i');
    
    if (content.style.display === 'none' || !content.style.display) {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    } else {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    }
}

function sortTable(columnIndex) {
    // 表格排序逻辑
    const table = document.querySelector('#keywordTable');
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent.trim();
        const bVal = b.cells[columnIndex].textContent.trim();
        
        if (columnIndex === 1) { // Count column
            return parseInt(bVal) - parseInt(aVal);
        } else {
            return aVal.localeCompare(bVal);
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

function showPageDetails(pageIndex) {
    // 显示页面详情的模态框逻辑
    console.log('显示页面详情:', pageIndex);
}

function closeModal() {
    // 关闭模态框逻辑
    const modal = document.getElementById('pageModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function refreshAnalysis() {
    if (seoAgent) {
        seoAgent.analyzeWebsite();
    }
}

function exportResults() {
    if (seoAgent && seoAgent.currentAnalysis) {
        const dataStr = JSON.stringify(seoAgent.currentAnalysis, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'seo-analysis.json';
        link.click();
        URL.revokeObjectURL(url);
    }
}