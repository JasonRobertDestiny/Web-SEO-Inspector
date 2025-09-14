"""
SEO Decision Engine for automated optimization recommendations.

This module implements a rule-based and AI-powered decision engine
that analyzes comprehensive SEO data to generate actionable recommendations.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PriorityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionType(Enum):
    CONTENT_OPTIMIZATION = "content_optimization"
    TECHNICAL_SEO = "technical_seo"
    USER_EXPERIENCE = "user_experience"
    LINK_BUILDING = "link_building"
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    PERFORMANCE = "performance"
    STRUCTURED_DATA = "structured_data"


@dataclass
class DecisionFactor:
    """Represents a factor in the decision-making process."""
    name: str
    value: float
    weight: float
    threshold: float
    impact: str


@dataclass
class SEOAction:
    """Represents a recommended SEO action."""
    title: str
    description: str
    action_type: ActionType
    priority: PriorityLevel
    estimated_effort: int  # Hours
    estimated_impact: float  # 0-1 scale
    confidence: float  # 0-1 scale
    implementation_steps: List[str]
    success_metrics: List[str]
    dependencies: List[str] = None
    resources_needed: List[str] = None


class SEODecisionEngine:
    """Intelligent SEO decision engine."""
    
    def __init__(self):
        """Initialize the decision engine with configured rules and weights."""
        self.setup_decision_rules()
        self.setup_thresholds()
        self.setup_impact_calculators()
    
    def setup_decision_rules(self):
        """Setup decision rules for different SEO aspects."""
        self.rules = {
            'content_quality': {
                'bounce_rate_threshold': 0.7,
                'session_duration_threshold': 60,
                'content_length_threshold': 300,
                'keyword_density_min': 0.5,
                'keyword_density_max': 3.0
            },
            'technical_seo': {
                'page_load_threshold': 3.0,
                'mobile_friendly_threshold': 0.9,
                'ssl_required': True,
                'crawl_errors_max': 10
            },
            'search_performance': {
                'position_threshold': 10,
                'ctr_threshold': 0.02,
                'impression_threshold': 100,
                'ranking_drop_threshold': 5
            },
            'user_experience': {
                'core_web_vitals_threshold': 0.9,
                'mobile_usability_threshold': 0.95,
                'readability_score_threshold': 60
            }
        }
    
    def setup_thresholds(self):
        """Setup priority thresholds."""
        self.thresholds = {
            PriorityLevel.CRITICAL: 0.8,
            PriorityLevel.HIGH: 0.6,
            PriorityLevel.MEDIUM: 0.4,
            PriorityLevel.LOW: 0.2
        }
    
    def setup_impact_calculators(self):
        """Setup impact calculation methods."""
        self.impact_weights = {
            'traffic_potential': 0.3,
            'ranking_improvement': 0.25,
            'conversion_impact': 0.2,
            'user_experience': 0.15,
            'technical_health': 0.1
        }
    
    def analyze_and_recommend(
        self,
        seo_analysis: Dict[str, Any],
        google_insights: Optional[Dict[str, Any]] = None,
        llm_insights: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze comprehensive SEO data and generate recommendations.
        
        Args:
            seo_analysis: Traditional SEO analysis results
            google_insights: Google Analytics and Search Console data
            llm_insights: AI-powered insights
            
        Returns:
            Dictionary containing prioritized recommendations and analysis
        """
        recommendations = []
        
        # Analyze different aspects
        content_actions = self._analyze_content_quality(seo_analysis, google_insights)
        technical_actions = self._analyze_technical_seo(seo_analysis)
        performance_actions = self._analyze_search_performance(google_insights or {})
        ux_actions = self._analyze_user_experience(seo_analysis, google_insights)
        
        # Combine all recommendations
        all_actions = content_actions + technical_actions + performance_actions + ux_actions
        
        # Prioritize actions
        prioritized_actions = self._prioritize_actions(all_actions)
        
        # Generate implementation plan
        implementation_plan = self._create_implementation_plan(prioritized_actions)
        
        return {
            'recommendations': prioritized_actions,
            'implementation_plan': implementation_plan,
            'summary': self._generate_summary(prioritized_actions),
            'estimated_timeline': self._calculate_timeline(implementation_plan),
            'success_metrics': self._define_success_metrics(prioritized_actions)
        }
    
    def _analyze_content_quality(
        self, 
        seo_analysis: Dict[str, Any], 
        google_insights: Optional[Dict[str, Any]] = None
    ) -> List[SEOAction]:
        """Analyze content quality and generate recommendations."""
        actions = []
        
        pages = seo_analysis.get('pages', [])
        for page in pages:
            page_url = page.get('url', '')
            
            # Check bounce rate
            if google_insights:
                page_performance = google_insights.get('page_performance', {})
                if page_url in page_performance:
                    metrics = page_performance[page_url]
                    bounce_rate = metrics.get('bounce_rate', 0)
                    
                    if bounce_rate > self.rules['content_quality']['bounce_rate_threshold']:
                        actions.append(SEOAction(
                            title=f"Reduce bounce rate for {page_url}",
                            description=f"High bounce rate ({bounce_rate:.1%}) indicates content or user experience issues",
                            action_type=ActionType.CONTENT_OPTIMIZATION,
                            priority=PriorityLevel.HIGH,
                            estimated_effort=8,
                            estimated_impact=0.7,
                            confidence=0.8,
                            implementation_steps=[
                                "Review content relevance and quality",
                                "Improve page load speed",
                                "Enhance readability and formatting",
                                "Add internal links to related content"
                            ],
                            success_metrics=[
                                "Reduce bounce rate below 60%",
                                "Increase average session duration",
                                "Improve pages per session"
                            ]
                        ))
        
        # Analyze content length and keyword optimization
        for page in pages:
            content_length = len(page.get('content', ''))
            if content_length < self.rules['content_quality']['content_length_threshold']:
                actions.append(SEOAction(
                    title=f"Expand content for {page.get('url', '')}",
                    description=f"Content appears too short ({content_length} chars) for comprehensive topic coverage",
                    action_type=ActionType.CONTENT_OPTIMIZATION,
                    priority=PriorityLevel.MEDIUM,
                    estimated_effort=6,
                    estimated_impact=0.6,
                    confidence=0.7,
                    implementation_steps=[
                        "Research topic comprehensively",
                        "Add relevant sections and details",
                        "Include examples and case studies",
                        "Optimize for semantic keywords"
                    ],
                    success_metrics=[
                        "Increase content length to 1000+ words",
                        "Improve keyword rankings",
                        "Increase user engagement"
                    ]
                ))
        
        return actions
    
    def _analyze_technical_seo(self, seo_analysis: Dict[str, Any]) -> List[SEOAction]:
        """Analyze technical SEO aspects and generate recommendations."""
        actions = []
        
        errors = seo_analysis.get('errors', [])
        
        # Group errors by type
        technical_errors = [error for error in errors if any(
            keyword in str(error).lower() 
            for keyword in ['404', '500', 'timeout', 'ssl', 'certificate']
        )]
        
        if technical_errors:
            actions.append(SEOAction(
                title="Fix critical technical SEO errors",
                description=f"Found {len(technical_errors)} technical errors affecting site performance",
                action_type=ActionType.TECHNICAL_SEO,
                priority=PriorityLevel.CRITICAL,
                estimated_effort=12,
                estimated_impact=0.9,
                confidence=0.95,
                implementation_steps=[
                    "Identify and fix all 404 errors",
                    "Resolve server errors (500s)",
                    "Ensure SSL certificate is valid",
                    "Fix timeout and connection issues"
                ],
                success_metrics=[
                    "Reduce technical errors to zero",
                    "Improve crawl efficiency",
                    "Enhance site reliability"
                ]
            ))
        
        # Check for missing SEO elements
        pages = seo_analysis.get('pages', [])
        pages_missing_meta = []
        
        for page in pages:
            title = page.get('title', '')
            description = page.get('description', '')
            
            if not title or len(title) < 30:
                pages_missing_meta.append(page.get('url', ''))
        
        if pages_missing_meta:
            actions.append(SEOAction(
                title="Optimize missing page titles and meta descriptions",
                description=f"{len(pages_missing_meta)} pages have missing or suboptimal titles/descriptions",
                action_type=ActionType.TECHNICAL_SEO,
                priority=PriorityLevel.HIGH,
                estimated_effort=len(pages_missing_meta) * 0.5,
                estimated_impact=0.8,
                confidence=0.9,
                implementation_steps=[
                    "Write compelling titles (50-60 characters)",
                    "Create descriptive meta descriptions (150-160 characters)",
                    "Include primary keywords naturally",
                    "Ensure uniqueness across pages"
                ],
                success_metrics=[
                    "100% pages have optimized titles",
                    "100% pages have meta descriptions",
                    "Improve search result CTR"
                ]
            ))
        
        return actions
    
    def _analyze_search_performance(self, google_insights: Dict[str, Any]) -> List[SEOAction]:
        """Analyze search performance and generate recommendations."""
        actions = []
        
        if not google_insights:
            return actions
        
        page_performance = google_insights.get('page_performance', {})
        
        for page_path, metrics in page_performance.items():
            search_data = metrics.get('search_data', {})
            
            # Check search position
            position = search_data.get('position', 0)
            if position > self.rules['search_performance']['position_threshold']:
                actions.append(SEOAction(
                    title=f"Improve search ranking for {page_path}",
                    description=f"Page ranking at position {position:.1f}, improvement needed",
                    action_type=ActionType.KEYWORD_OPTIMIZATION,
                    priority=PriorityLevel.HIGH,
                    estimated_effort=10,
                    estimated_impact=0.85,
                    confidence=0.75,
                    implementation_steps=[
                        "Analyze top-ranking competitors",
                        "Optimize content for target keywords",
                        "Improve internal linking structure",
                        "Build quality backlinks",
                        "Enhance user experience signals"
                    ],
                    success_metrics=[
                        "Achieve top 10 ranking",
                        "Increase organic traffic",
                        "Improve search visibility"
                    ]
                ))
            
            # Check CTR
            ctr = search_data.get('ctr', 0)
            impressions = search_data.get('impressions', 0)
            
            if (ctr < self.rules['search_performance']['ctr_threshold'] and 
                impressions > self.rules['search_performance']['impression_threshold']):
                actions.append(SEOAction(
                    title=f"Improve search CTR for {page_path}",
                    description=f"Low CTR ({ctr:.2%}) despite good impressions ({impressions})",
                    action_type=ActionType.CONTENT_OPTIMIZATION,
                    priority=PriorityLevel.MEDIUM,
                    estimated_effort=4,
                    estimated_impact=0.6,
                    confidence=0.8,
                    implementation_steps=[
                        "Optimize title tags for clickability",
                        "Write compelling meta descriptions",
                        "Implement structured data for rich snippets",
                        "Test different title/description combinations"
                    ],
                    success_metrics=[
                        "Increase CTR to 3%+",
                        "Maintain or improve rankings",
                        "Increase organic traffic"
                    ]
                ))
        
        return actions
    
    def _analyze_user_experience(
        self, 
        seo_analysis: Dict[str, Any], 
        google_insights: Optional[Dict[str, Any]] = None
    ) -> List[SEOAction]:
        """Analyze user experience aspects and generate recommendations."""
        actions = []
        
        if google_insights:
            page_performance = google_insights.get('page_performance', {})
            
            for page_path, metrics in page_performance.items():
                # Check session duration
                session_duration = metrics.get('avg_session_duration', 0)
                if session_duration < self.rules['content_quality']['session_duration_threshold']:
                    actions.append(SEOAction(
                        title=f"Improve user engagement for {page_path}",
                        description=f"Short session duration ({session_duration:.0f}s) indicates engagement issues",
                        action_type=ActionType.USER_EXPERIENCE,
                        priority=PriorityLevel.MEDIUM,
                        estimated_effort=6,
                        estimated_impact=0.65,
                        confidence=0.7,
                        implementation_steps=[
                            "Improve content readability",
                            "Add multimedia elements",
                            "Enhance page layout and navigation",
                            "Include clear calls-to-action"
                        ],
                        success_metrics=[
                            "Increase average session duration to 90+ seconds",
                            "Reduce bounce rate",
                            "Improve pages per session"
                        ]
                    ))
        
        return actions
    
    def _prioritize_actions(self, actions: List[SEOAction]) -> List[SEOAction]:
        """Prioritize actions based on impact, effort, and confidence."""
        
        def calculate_priority_score(action: SEOAction) -> float:
            """Calculate priority score for an action."""
            impact_weight = 0.5
            effort_weight = 0.3
            confidence_weight = 0.2
            
            # Normalize effort (lower effort = higher score)
            effort_score = 1 - min(action.estimated_effort / 40, 1)  # 40 hours max
            
            priority_score = (
                action.estimated_impact * impact_weight +
                effort_score * effort_weight +
                action.confidence * confidence_weight
            )
            
            return priority_score
        
        # Sort by priority score
        sorted_actions = sorted(actions, key=calculate_priority_score, reverse=True)
        
        # Assign priority levels based on scores
        for action in sorted_actions:
            score = calculate_priority_score(action)
            if score >= self.thresholds[PriorityLevel.CRITICAL]:
                action.priority = PriorityLevel.CRITICAL
            elif score >= self.thresholds[PriorityLevel.HIGH]:
                action.priority = PriorityLevel.HIGH
            elif score >= self.thresholds[PriorityLevel.MEDIUM]:
                action.priority = PriorityLevel.MEDIUM
            else:
                action.priority = PriorityLevel.LOW
        
        return sorted_actions
    
    def _create_implementation_plan(self, actions: List[SEOAction]) -> Dict[str, Any]:
        """Create a structured implementation plan."""
        
        plan = {
            'phases': {
                'immediate': [],
                'short_term': [],
                'medium_term': [],
                'long_term': []
            },
            'total_effort_hours': sum(action.estimated_effort for action in actions),
            'resource_allocation': {},
            'timeline': {}
        }
        
        for action in actions:
            # Assign to phase based on priority and effort
            if action.priority == PriorityLevel.CRITICAL:
                plan['phases']['immediate'].append(action)
            elif action.priority == PriorityLevel.HIGH and action.estimated_effort <= 16:
                plan['phases']['short_term'].append(action)
            elif action.priority == PriorityLevel.HIGH or action.estimated_effort <= 24:
                plan['phases']['medium_term'].append(action)
            else:
                plan['phases']['long_term'].append(action)
        
        # Calculate resource allocation
        for phase, phase_actions in plan['phases'].items():
            plan['resource_allocation'][phase] = {
                'hours': sum(action.estimated_effort for action in phase_actions),
                'actions_count': len(phase_actions),
                'priority_breakdown': {}
            }
            
            # Count actions by priority
            for action in phase_actions:
                priority = action.priority.value
                plan['resource_allocation'][phase]['priority_breakdown'][priority] = \
                    plan['resource_allocation'][phase]['priority_breakdown'].get(priority, 0) + 1
        
        return plan
    
    def _generate_summary(self, actions: List[SEOAction]) -> Dict[str, Any]:
        """Generate a summary of the analysis."""
        
        summary = {
            'total_actions': len(actions),
            'priority_distribution': {},
            'type_distribution': {},
            'total_effort_hours': sum(action.estimated_effort for action in actions),
            'high_impact_actions': len([a for a in actions if a.estimated_impact > 0.7]),
            'quick_wins': len([a for a in actions if a.estimated_effort <= 4 and a.estimated_impact > 0.6])
        }
        
        # Count by priority
        for action in actions:
            priority = action.priority.value
            summary['priority_distribution'][priority] = \
                summary['priority_distribution'].get(priority, 0) + 1
        
        # Count by type
        for action in actions:
            action_type = action.action_type.value
            summary['type_distribution'][action_type] = \
                summary['type_distribution'].get(action_type, 0) + 1
        
        return summary
    
    def _calculate_timeline(self, implementation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate implementation timeline."""
        
        # Assume 20 hours/week for SEO work
        weekly_capacity = 20
        
        timeline = {}
        cumulative_weeks = 0
        
        for phase, data in implementation_plan['phases'].items():
            hours = data['hours']
            weeks_needed = max(1, round(hours / weekly_capacity))
            
            timeline[phase] = {
                'duration_weeks': weeks_needed,
                'start_week': cumulative_weeks + 1,
                'end_week': cumulative_weeks + weeks_needed,
                'hours': hours,
                'actions_count': len(data)
            }
            
            cumulative_weeks += weeks_needed
        
        timeline['total_weeks'] = cumulative_weeks
        timeline['total_months'] = round(cumulative_weeks / 4.33, 1)
        
        return timeline
    
    def _define_success_metrics(self, actions: List[SEOAction]) -> List[str]:
        """Define overall success metrics for the optimization plan."""
        
        metrics = [
            "Improve organic search traffic by 25%+",
            "Achieve top 10 rankings for target keywords",
            "Reduce bounce rate to below 60%",
            "Increase average session duration to 90+ seconds",
            "Fix all technical SEO errors",
            "Improve mobile usability score to 95+",
            "Increase conversion rate from organic traffic"
        ]
        
        # Add action-specific metrics
        for action in actions:
            metrics.extend(action.success_metrics)
        
        # Remove duplicates
        unique_metrics = list(set(metrics))
        
        return unique_metrics


# Example usage
def example_usage():
    """Example of using the SEO decision engine."""
    engine = SEODecisionEngine()
    
    # Sample data
    seo_analysis = {
        "pages": [
            {
                "url": "https://example.com/page1",
                "title": "Short Title",
                "description": "",
                "content": "Short content example"
            }
        ],
        "errors": ["404 error on /missing-page", "SSL certificate expiring soon"],
        "keywords": []
    }
    
    google_insights = {
        "page_performance": {
            "/page1": {
                "bounce_rate": 0.8,
                "avg_session_duration": 45,
                "search_data": {
                    "position": 15.0,
                    "ctr": 0.01,
                    "impressions": 500
                }
            }
        }
    }
    
    # Generate recommendations
    results = engine.analyze_and_recommend(
        seo_analysis=seo_analysis,
        google_insights=google_insights
    )
    
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    example_usage()