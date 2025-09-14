from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import time
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyseoanalyzer.analyzer import analyze
from pyseoanalyzer.seo_optimizer import SEOOptimizer
from pyseoanalyzer.llm_analyst import enhanced_modern_analyze

app = Flask(__name__, template_folder='templates', static_folder='templates')
CORS(app)

# SEO预警阈值配置
SEO_THRESHOLDS = {
    'title_length': {'min': 30, 'max': 60},
    'description_length': {'min': 120, 'max': 160},
    'h1_count': {'min': 1, 'max': 1},
    'h2_count': {'min': 1, 'max': 6},
    'image_alt_missing': {'max': 0},
    'internal_links': {'min': 3},
    'external_links': {'max': 10},
    'page_load_time': {'max': 3.0},
    'keyword_density': {'min': 0.5, 'max': 3.0}
}

# SEO建议模板
SEO_RECOMMENDATIONS = {
    'title_too_short': '标题过短，建议增加到30-60个字符以提高SEO效果',
    'title_too_long': '标题过长，建议缩短到60个字符以内',
    'description_too_short': 'Meta描述过短，建议增加到120-160个字符',
    'description_too_long': 'Meta描述过长，建议缩短到160个字符以内',
    'missing_h1': '缺少H1标签，每个页面应该有且仅有一个H1标签',
    'multiple_h1': '存在多个H1标签，建议每个页面只使用一个H1标签',
    'insufficient_h2': 'H2标签数量不足，建议添加1-6个H2标签来改善内容结构',
    'excessive_h2': 'H2标签过多，建议控制在6个以内',
    'missing_alt_text': '存在缺少alt属性的图片，影响可访问性和SEO',
    'insufficient_internal_links': '内部链接不足，建议增加至少3个内部链接',
    'excessive_external_links': '外部链接过多，可能影响页面权重分配',
    'slow_loading': '页面加载时间过长，建议优化到3秒以内',
    'keyword_density_low': '关键词密度过低，建议适当增加关键词使用',
    'keyword_density_high': '关键词密度过高，可能被视为关键词堆砌'
}

@app.route('/')
def index():
    """提供主页面"""
    return render_template('index.html')

@app.route('/seo_styles.css')
def serve_css():
    return send_from_directory('templates', 'seo_styles.css')

@app.route('/seo_agent.js')
def serve_js():
    return send_from_directory('templates', 'seo_agent.js')

def analyze_seo_issues(analysis_result):
    """分析SEO问题并生成预警和建议"""
    issues = []
    recommendations = []
    
    # 检查每个页面的SEO指标
    for page in analysis_result.get('pages', []):
        page_issues = []
        page_recommendations = []
        
        # 标题长度检查
        title = page.get('title', '')
        if len(title) < SEO_THRESHOLDS['title_length']['min']:
            page_issues.append('title_too_short')
            page_recommendations.append(SEO_RECOMMENDATIONS['title_too_short'])
        elif len(title) > SEO_THRESHOLDS['title_length']['max']:
            page_issues.append('title_too_long')
            page_recommendations.append(SEO_RECOMMENDATIONS['title_too_long'])
        
        # Meta描述长度检查
        description = page.get('description', '')
        if len(description) < SEO_THRESHOLDS['description_length']['min']:
            page_issues.append('description_too_short')
            page_recommendations.append(SEO_RECOMMENDATIONS['description_too_short'])
        elif len(description) > SEO_THRESHOLDS['description_length']['max']:
            page_issues.append('description_too_long')
            page_recommendations.append(SEO_RECOMMENDATIONS['description_too_long'])
        
        # H1标签检查
        h1_count = len(page.get('h1', []))
        if h1_count == 0:
            page_issues.append('missing_h1')
            page_recommendations.append(SEO_RECOMMENDATIONS['missing_h1'])
        elif h1_count > 1:
            page_issues.append('multiple_h1')
            page_recommendations.append(SEO_RECOMMENDATIONS['multiple_h1'])
        
        # H2标签检查
        h2_count = len(page.get('h2', []))
        if h2_count < SEO_THRESHOLDS['h2_count']['min']:
            page_issues.append('insufficient_h2')
            page_recommendations.append(SEO_RECOMMENDATIONS['insufficient_h2'])
        elif h2_count > SEO_THRESHOLDS['h2_count']['max']:
            page_issues.append('excessive_h2')
            page_recommendations.append(SEO_RECOMMENDATIONS['excessive_h2'])
        
        # 图片alt属性检查
        images_without_alt = page.get('images_without_alt', 0)
        if images_without_alt > SEO_THRESHOLDS['image_alt_missing']['max']:
            page_issues.append('missing_alt_text')
            page_recommendations.append(SEO_RECOMMENDATIONS['missing_alt_text'])
        
        # 链接检查
        internal_links = len(page.get('internal_links', []))
        external_links = len(page.get('external_links', []))
        
        if internal_links < SEO_THRESHOLDS['internal_links']['min']:
            page_issues.append('insufficient_internal_links')
            page_recommendations.append(SEO_RECOMMENDATIONS['insufficient_internal_links'])
        
        if external_links > SEO_THRESHOLDS['external_links']['max']:
            page_issues.append('excessive_external_links')
            page_recommendations.append(SEO_RECOMMENDATIONS['excessive_external_links'])
        
        # 添加页面特定的问题和建议
        if page_issues:
            issues.append({
                'url': page.get('url', ''),
                'issues': page_issues,
                'severity': 'high' if any(issue in ['missing_h1', 'multiple_h1'] for issue in page_issues) else 'medium'
            })
        
        if page_recommendations:
            recommendations.extend([{
                'url': page.get('url', ''),
                'recommendation': rec,
                'priority': 'high' if any(issue in ['missing_h1', 'multiple_h1'] for issue in page_issues) else 'medium',
                'category': 'content'
            } for rec in page_recommendations])
    
    return {
        'issues': issues,
        'recommendations': recommendations,
        'summary': {
            'total_issues': len(issues),
            'high_priority': len([i for i in issues if i['severity'] == 'high']),
            'medium_priority': len([i for i in issues if i['severity'] == 'medium']),
            'total_recommendations': len(recommendations)
        }
    }

def calculate_seo_score(analysis_result, seo_analysis):
    """计算SEO评分 (0-100)"""
    score = 100
    
    # 根据问题严重程度扣分，使用更合理的扣分机制
    issues = seo_analysis.get('issues', [])
    print(f"Debug: Found {len(issues)} issues")
    
    # 统计不同严重程度的问题数量
    high_count = 0
    medium_count = 0
    low_count = 0
    
    for issue in issues:
        severity = issue.get('severity')
        print(f"Debug: Issue severity: {severity}")
        if severity == 'high':
            high_count += 1
        elif severity == 'medium':
            medium_count += 1
        else:
            low_count += 1
    
    # 使用更合理的扣分算法：基于问题比例而非绝对数量
    total_issues = len(issues)
    if total_issues > 0:
        # 高严重度问题最多扣40分
        high_penalty = min(40, (high_count / max(1, total_issues)) * 40)
        # 中等严重度问题最多扣30分
        medium_penalty = min(30, (medium_count / max(1, total_issues)) * 30)
        # 低严重度问题最多扣20分
        low_penalty = min(20, (low_count / max(1, total_issues)) * 20)
        
        score = score - high_penalty - medium_penalty - low_penalty
    
    print(f"Debug: High issues: {high_count}, Medium: {medium_count}, Low: {low_count}")
    print(f"Debug: Final score: {score}")
    
    # 确保分数在0-100范围内
    score = max(0, min(100, score))
    
    # 评级
    if score >= 90:
        grade = 'A+'
    elif score >= 80:
        grade = 'A'
    elif score >= 70:
        grade = 'B'
    elif score >= 60:
        grade = 'C'
    else:
        grade = 'D'
    
    result = {
        'score': score,
        'grade': grade,
        'status': 'excellent' if score >= 90 else 'good' if score >= 70 else 'needs_improvement'
    }
    
    print(f"Debug: Returning score result: {result}")
    return result

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """分析网站SEO并返回结果"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': '缺少URL参数'}), 400
        
        # 执行SEO分析
        analysis_result = analyze(
            url=url,
            sitemap_url=data.get('sitemap'),
            follow_links=data.get('follow_links', True),
            analyze_headings=data.get('analyze_headings', True),
            analyze_extra_tags=data.get('analyze_extra_tags', True)
        )
        
        # 生成SEO预警和建议
        seo_analysis = analyze_seo_issues(analysis_result)
        
        # 计算SEO评分
        seo_score = calculate_seo_score(analysis_result, seo_analysis)
        
        # 使用SEO优化器生成详细的优化建议
        optimizer = SEOOptimizer()
        pages_data = analysis_result.get('pages', [])
        optimization_plan = optimizer.generate_optimization_plan(pages_data)
        
        # 合并结果
        result = {
            'analysis': analysis_result,
            'seo_insights': seo_analysis,
            'seo_score': seo_score,
            'optimization': optimization_plan,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """获取SEO建议列表"""
    return jsonify({
        'recommendations': list(SEO_RECOMMENDATIONS.values()),
        'categories': ['content', 'technical', 'performance', 'accessibility']
    })

@app.route('/api/thresholds', methods=['GET', 'POST'])
def manage_thresholds():
    """管理SEO阈值配置"""
    if request.method == 'GET':
        return jsonify(SEO_THRESHOLDS)
    
    elif request.method == 'POST':
        try:
            new_thresholds = request.get_json()
            SEO_THRESHOLDS.update(new_thresholds)
            return jsonify({'message': '阈值更新成功', 'thresholds': SEO_THRESHOLDS})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # 根据环境变量决定是否启用调试模式
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)