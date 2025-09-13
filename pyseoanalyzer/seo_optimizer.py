#!/usr/bin/env python3
"""
SEO优化建议生成器
为每个页面的SEO问题生成具体的优化建议和行动步骤
"""

from typing import Dict, List, Tuple
from datetime import datetime
import json


class SEOOptimizer:
    """
    SEO优化建议生成器
    根据页面分析结果生成详细的优化建议和todo清单
    """
    
    def __init__(self):
        self.priority_levels = {
            'critical': {'score': 100, 'color': '#dc2626', 'icon': '🚨'},
            'high': {'score': 80, 'color': '#ea580c', 'icon': '⚠️'},
            'medium': {'score': 60, 'color': '#d97706', 'icon': '📋'},
            'low': {'score': 40, 'color': '#059669', 'icon': '💡'}
        }
        
        # SEO问题类型和对应的优化建议模板
        self.optimization_rules = {
            'title': {
                'missing': {
                    'priority': 'critical',
                    'category': '基础SEO',
                    'title': '添加页面标题',
                    'description': '页面缺少title标签，这是最基本的SEO要素',
                    'action': '为页面添加描述性的title标签',
                    'implementation': [
                        '在HTML的<head>部分添加<title>标签',
                        '标题长度控制在50-60个字符',
                        '包含主要关键词，但避免关键词堆砌',
                        '确保标题准确描述页面内容'
                    ],
                    'expected_impact': '提高搜索引擎理解页面内容的能力，显著改善搜索排名',
                    'time_estimate': '15分钟'
                },
                'too_short': {
                    'priority': 'high',
                    'category': '内容优化',
                    'title': '优化页面标题长度',
                    'description': '标题过短，无法充分描述页面内容',
                    'action': '扩展标题内容，增加相关关键词',
                    'implementation': [
                        '分析页面主要内容和目标关键词',
                        '将标题扩展到30-60个字符',
                        '添加品牌名称或网站名称',
                        '确保标题仍然简洁明了'
                    ],
                    'expected_impact': '提高点击率和搜索引擎理解度',
                    'time_estimate': '10分钟'
                },
                'too_long': {
                    'priority': 'medium',
                    'category': '内容优化',
                    'title': '缩短页面标题',
                    'description': '标题过长，在搜索结果中可能被截断',
                    'action': '精简标题内容，保留核心关键词',
                    'implementation': [
                        '识别标题中的核心关键词',
                        '移除不必要的修饰词',
                        '将标题控制在60个字符以内',
                        '确保截断后的标题仍有意义'
                    ],
                    'expected_impact': '提高搜索结果显示完整性和用户体验',
                    'time_estimate': '10分钟'
                }
            },
            'description': {
                'missing': {
                    'priority': 'critical',
                    'category': '基础SEO',
                    'title': '添加页面描述',
                    'description': '页面缺少meta description，影响搜索结果展示',
                    'action': '为页面添加吸引人的meta description',
                    'implementation': [
                        '在HTML的<head>部分添加meta description标签',
                        '描述长度控制在150-160个字符',
                        '包含主要关键词和页面价值主张',
                        '撰写吸引用户点击的描述文案'
                    ],
                    'expected_impact': '提高搜索结果点击率，改善用户体验',
                    'time_estimate': '20分钟'
                },
                'too_short': {
                    'priority': 'high',
                    'category': '内容优化',
                    'title': '扩展页面描述',
                    'description': '描述过短，无法充分展示页面价值',
                    'action': '扩展描述内容，增加吸引力',
                    'implementation': [
                        '分析页面核心价值和卖点',
                        '将描述扩展到120-160个字符',
                        '添加行动号召语',
                        '包含相关的长尾关键词'
                    ],
                    'expected_impact': '提高搜索结果吸引力和点击率',
                    'time_estimate': '15分钟'
                },
                'too_long': {
                    'priority': 'medium',
                    'category': '内容优化',
                    'title': '精简页面描述',
                    'description': '描述过长，在搜索结果中会被截断',
                    'action': '精简描述内容，突出核心信息',
                    'implementation': [
                        '识别描述中的核心信息',
                        '移除冗余内容',
                        '将描述控制在160个字符以内',
                        '确保截断后仍能传达主要信息'
                    ],
                    'expected_impact': '提高搜索结果显示完整性',
                    'time_estimate': '10分钟'
                }
            },
            'headings': {
                'missing_h1': {
                    'priority': 'critical',
                    'category': '结构优化',
                    'title': '添加H1标题',
                    'description': '页面缺少H1标签，影响内容结构和SEO',
                    'action': '为页面添加唯一的H1标题',
                    'implementation': [
                        '在页面主要内容区域添加H1标签',
                        '确保每个页面只有一个H1标签',
                        'H1内容应该概括页面主题',
                        '包含主要目标关键词'
                    ],
                    'expected_impact': '改善页面结构，提高搜索引擎理解度',
                    'time_estimate': '10分钟'
                }
            },
            'images': {
                'missing_alt': {
                    'priority': 'high',
                    'category': '可访问性',
                    'title': '添加图片Alt属性',
                    'description': '图片缺少alt属性，影响可访问性和SEO',
                    'action': '为所有图片添加描述性的alt属性',
                    'implementation': [
                        '检查页面所有img标签',
                        '为每个图片添加alt属性',
                        'Alt文本应描述图片内容',
                        '装饰性图片可使用空alt属性'
                    ],
                    'expected_impact': '提高可访问性，改善图片搜索排名',
                    'time_estimate': '30分钟'
                }
            },
            'links': {
                'missing_title': {
                    'priority': 'medium',
                    'category': '用户体验',
                    'title': '添加链接标题属性',
                    'description': '链接缺少title属性，影响用户体验',
                    'action': '为重要链接添加title属性',
                    'implementation': [
                        '识别页面重要链接',
                        '为链接添加描述性title属性',
                        'Title应说明链接目标',
                        '避免与链接文本重复'
                    ],
                    'expected_impact': '提高用户体验和可访问性',
                    'time_estimate': '20分钟'
                },
                'generic_text': {
                    'priority': 'medium',
                    'category': '内容优化',
                    'title': '优化链接文本',
                    'description': '链接使用了通用文本，不利于SEO',
                    'action': '使用描述性的链接文本',
                    'implementation': [
                        '识别使用通用文本的链接',
                        '将"点击这里"等改为描述性文本',
                        '链接文本应说明目标页面内容',
                        '包含相关关键词'
                    ],
                    'expected_impact': '提高链接价值传递和用户体验',
                    'time_estimate': '25分钟'
                }
            },
            'open_graph': {
                'missing_og_title': {
                    'priority': 'medium',
                    'category': '社交媒体',
                    'title': '添加Open Graph标题',
                    'description': '缺少og:title，影响社交媒体分享效果',
                    'action': '添加Open Graph标题标签',
                    'implementation': [
                        '在<head>中添加<meta property="og:title" content="...">',
                        '内容可与页面title相同或略有不同',
                        '针对社交媒体优化标题',
                        '长度控制在60个字符以内'
                    ],
                    'expected_impact': '改善社交媒体分享展示效果',
                    'time_estimate': '10分钟'
                },
                'missing_og_description': {
                    'priority': 'medium',
                    'category': '社交媒体',
                    'title': '添加Open Graph描述',
                    'description': '缺少og:description，影响社交媒体分享',
                    'action': '添加Open Graph描述标签',
                    'implementation': [
                        '在<head>中添加<meta property="og:description" content="...">',
                        '内容可与meta description相同',
                        '针对社交媒体用户优化描述',
                        '长度控制在200个字符以内'
                    ],
                    'expected_impact': '提高社交媒体分享吸引力',
                    'time_estimate': '10分钟'
                },
                'missing_og_image': {
                    'priority': 'medium',
                    'category': '社交媒体',
                    'title': '添加Open Graph图片',
                    'description': '缺少og:image，社交分享缺少视觉吸引力',
                    'action': '添加Open Graph图片标签',
                    'implementation': [
                        '选择或创建适合的分享图片',
                        '图片尺寸建议1200x630像素',
                        '在<head>中添加<meta property="og:image" content="...">',
                        '确保图片URL可公开访问'
                    ],
                    'expected_impact': '显著提高社交媒体分享的视觉吸引力',
                    'time_estimate': '30分钟'
                }
            }
        }
    
    def analyze_page_issues(self, page_data: Dict) -> List[Dict]:
        """
        分析页面问题并生成优化建议
        """
        issues = []
        warnings = page_data.get('warnings', [])
        
        for warning in warnings:
            issue = self._categorize_warning(warning)
            if issue:
                issues.append(issue)
        
        return issues
    
    def _categorize_warning(self, warning: str) -> Dict:
        """
        将警告信息分类并生成对应的优化建议
        """
        warning_lower = warning.lower()
        
        # 标题相关问题
        if 'missing title' in warning_lower:
            return self._create_issue('title', 'missing', warning)
        elif 'title tag is too short' in warning_lower:
            return self._create_issue('title', 'too_short', warning)
        elif 'title tag is too long' in warning_lower:
            return self._create_issue('title', 'too_long', warning)
        
        # 描述相关问题
        elif 'missing description' in warning_lower:
            return self._create_issue('description', 'missing', warning)
        elif 'description is too short' in warning_lower:
            return self._create_issue('description', 'too_short', warning)
        elif 'description is too long' in warning_lower:
            return self._create_issue('description', 'too_long', warning)
        
        # H1标签问题
        elif 'should have at least one h1' in warning_lower:
            return self._create_issue('headings', 'missing_h1', warning)
        
        # 图片问题
        elif 'image missing alt tag' in warning_lower:
            return self._create_issue('images', 'missing_alt', warning)
        
        # 链接问题
        elif 'anchor missing title tag' in warning_lower:
            return self._create_issue('links', 'missing_title', warning)
        elif 'anchor text contains generic text' in warning_lower:
            return self._create_issue('links', 'generic_text', warning)
        
        # Open Graph问题
        elif 'missing og:title' in warning_lower:
            return self._create_issue('open_graph', 'missing_og_title', warning)
        elif 'missing og:description' in warning_lower:
            return self._create_issue('open_graph', 'missing_og_description', warning)
        elif 'missing og:image' in warning_lower:
            return self._create_issue('open_graph', 'missing_og_image', warning)
        
        # 未分类的问题
        return {
            'id': f"unknown_{hash(warning) % 10000}",
            'category': '其他问题',
            'priority': 'medium',
            'title': '需要关注的问题',
            'description': warning,
            'action': '请手动检查并解决此问题',
            'implementation': ['分析具体问题', '制定解决方案', '实施修复'],
            'expected_impact': '改善页面质量',
            'time_estimate': '待评估',
            'original_warning': warning
        }
    
    def _create_issue(self, category: str, issue_type: str, original_warning: str) -> Dict:
        """
        根据问题类型创建标准化的问题对象
        """
        rule = self.optimization_rules.get(category, {}).get(issue_type, {})
        if not rule:
            return None
        
        priority_info = self.priority_levels[rule['priority']]
        
        return {
            'id': f"{category}_{issue_type}_{hash(original_warning) % 10000}",
            'category': rule['category'],
            'priority': rule['priority'],
            'priority_score': priority_info['score'],
            'priority_color': priority_info['color'],
            'priority_icon': priority_info['icon'],
            'title': rule['title'],
            'description': rule['description'],
            'action': rule['action'],
            'implementation': rule['implementation'],
            'expected_impact': rule['expected_impact'],
            'time_estimate': rule['time_estimate'],
            'original_warning': original_warning,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
    
    def generate_optimization_plan(self, pages_data: List[Dict]) -> Dict:
        """
        为整个网站生成优化计划
        """
        all_issues = []
        page_summaries = []
        
        for page_data in pages_data:
            page_issues = self.analyze_page_issues(page_data)
            all_issues.extend(page_issues)
            
            page_summary = {
                'url': page_data.get('url', ''),
                'title': page_data.get('title', ''),
                'issues_count': len(page_issues),
                'critical_issues': len([i for i in page_issues if i['priority'] == 'critical']),
                'high_issues': len([i for i in page_issues if i['priority'] == 'high']),
                'issues': page_issues
            }
            page_summaries.append(page_summary)
        
        # 按优先级排序问题
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_issues.sort(key=lambda x: (priority_order[x['priority']], x['title']))
        
        # 生成统计信息
        stats = self._generate_stats(all_issues)
        
        # 生成优化建议
        recommendations = self._generate_recommendations(all_issues, stats)
        
        return {
            'summary': {
                'total_pages': len(pages_data),
                'total_issues': len(all_issues),
                'critical_issues': stats['critical'],
                'high_issues': stats['high'],
                'medium_issues': stats['medium'],
                'low_issues': stats['low'],
                'estimated_time': self._calculate_total_time(all_issues)
            },
            'pages': page_summaries,
            'issues': all_issues,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_stats(self, issues: List[Dict]) -> Dict:
        """
        生成问题统计信息
        """
        stats = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        category_stats = {}
        
        for issue in issues:
            priority = issue['priority']
            category = issue['category']
            
            stats[priority] += 1
            
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        stats['by_category'] = category_stats
        return stats
    
    def _calculate_total_time(self, issues: List[Dict]) -> str:
        """
        计算总预估时间
        """
        total_minutes = 0
        
        for issue in issues:
            time_str = issue.get('time_estimate', '0分钟')
            if '分钟' in time_str:
                minutes = int(time_str.replace('分钟', '').replace('待评估', '0'))
                total_minutes += minutes
        
        if total_minutes < 60:
            return f"{total_minutes}分钟"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}小时{minutes}分钟" if minutes > 0 else f"{hours}小时"
    
    def _generate_recommendations(self, issues: List[Dict], stats: Dict) -> Dict:
        """
        生成优化建议
        """
        recommendations = {
            'immediate_actions': [],
            'short_term_goals': [],
            'long_term_strategy': [],
            'priority_matrix': {
                'quick_wins': [],  # 高影响，低工作量
                'major_projects': [],  # 高影响，高工作量
                'fill_ins': [],  # 低影响，低工作量
                'questionable': []  # 低影响，高工作量
            }
        }
        
        # 立即行动项（关键和高优先级问题）
        critical_and_high = [i for i in issues if i['priority'] in ['critical', 'high']]
        recommendations['immediate_actions'] = critical_and_high[:5]  # 前5个最重要的
        
        # 短期目标（中优先级问题）
        medium_priority = [i for i in issues if i['priority'] == 'medium']
        recommendations['short_term_goals'] = medium_priority[:10]
        
        # 长期策略建议
        if stats['critical'] > 0:
            recommendations['long_term_strategy'].append({
                'title': '建立SEO质量控制流程',
                'description': '制定内容发布前的SEO检查清单，避免基础SEO问题',
                'priority': 'high'
            })
        
        if stats['by_category'].get('社交媒体', 0) > 0:
            recommendations['long_term_strategy'].append({
                'title': '完善社交媒体优化策略',
                'description': '系统性地优化所有页面的社交媒体分享效果',
                'priority': 'medium'
            })
        
        # 优先级矩阵分类
        for issue in issues:
            time_estimate = issue.get('time_estimate', '0分钟')
            priority = issue['priority']
            
            # 简单的工作量评估
            if '分钟' in time_estimate:
                minutes = int(time_estimate.replace('分钟', '').replace('待评估', '30'))
                is_low_effort = minutes <= 20
            else:
                is_low_effort = False
            
            is_high_impact = priority in ['critical', 'high']
            
            if is_high_impact and is_low_effort:
                recommendations['priority_matrix']['quick_wins'].append(issue)
            elif is_high_impact and not is_low_effort:
                recommendations['priority_matrix']['major_projects'].append(issue)
            elif not is_high_impact and is_low_effort:
                recommendations['priority_matrix']['fill_ins'].append(issue)
            else:
                recommendations['priority_matrix']['questionable'].append(issue)
        
        return recommendations


def enhance_analysis_with_optimization(analysis_result: Dict) -> Dict:
    """
    为现有分析结果添加优化建议
    """
    optimizer = SEOOptimizer()
    
    # 获取页面数据
    pages_data = analysis_result.get('pages', [])
    
    # 生成优化计划
    optimization_plan = optimizer.generate_optimization_plan(pages_data)
    
    # 将优化建议添加到原始结果中
    enhanced_result = analysis_result.copy()
    enhanced_result['optimization'] = optimization_plan
    
    return enhanced_result