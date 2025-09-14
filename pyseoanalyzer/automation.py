"""
SEO Agent Automation System

This module provides automated scheduling and execution of SEO analysis
tasks using APScheduler and integrates with the enhanced analysis pipeline.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import asyncio

from .analyzer import analyze
from .google_integrator import GoogleDataIntegrator
from .enhanced_llm_analyst import EnhancedLLMSEOAnalyst
from .decision_engine import SEODecisionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AutomationConfig:
    """Configuration for SEO automation tasks."""
    website_url: str
    sitemap_url: Optional[str] = None
    analysis_schedule: str = "0 9 * * 1"  # Every Monday at 9 AM
    google_integration_enabled: bool = True
    llm_analysis_enabled: bool = True
    notifications_enabled: bool = True
    notification_email: Optional[str] = None
    data_retention_days: int = 90
    max_concurrent_analyses: int = 3


@dataclass
class AnalysisResult:
    """Result of an SEO analysis run."""
    timestamp: datetime
    website_url: str
    analysis_id: str
    status: str
    results: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None


class SEOAgentAutomation:
    """Main automation system for SEO analysis."""
    
    def __init__(self, config: AutomationConfig):
        """Initialize the automation system."""
        self.config = config
        self.scheduler = BackgroundScheduler()
        self.google_integrator = None
        self.llm_analyst = None
        self.decision_engine = None
        self.analysis_history: List[AnalysisResult] = []
        
        # Initialize components if enabled
        if config.google_integration_enabled:
            try:
                self.google_integrator = GoogleDataIntegrator()
                self.analytics_view_id = os.getenv('GOOGLE_ANALYTICS_VIEW_ID')
                self.analytics_measurement_id = os.getenv('GOOGLE_ANALYTICS_MEASUREMENT_ID')
                self.search_console_url = os.getenv('GOOGLE_SEARCH_CONSOLE_URL')
                
                if not (self.analytics_view_id or self.analytics_measurement_id) or not self.search_console_url:
                    logger.warning("Google Analytics configuration incomplete. Need GOOGLE_SEARCH_CONSOLE_URL and either GOOGLE_ANALYTICS_VIEW_ID or GOOGLE_ANALYTICS_MEASUREMENT_ID")
                    self.google_integrator = None
            except Exception as e:
                logger.warning(f"Failed to initialize Google integration: {e}")
        
        if config.llm_analysis_enabled:
            self.llm_analyst = EnhancedLLMSEOAnalyst()
        
        self.decision_engine = SEODecisionEngine()
        
        # Setup scheduler
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """Setup scheduled tasks."""
        # Main analysis job
        self.scheduler.add_job(
            self.run_scheduled_analysis,
            trigger=CronTrigger.from_crontab(self.config.analysis_schedule),
            id='main_analysis',
            name='Main SEO Analysis',
            replace_existing=True
        )
        
        # Data cleanup job (daily)
        self.scheduler.add_job(
            self.cleanup_old_data,
            trigger=IntervalTrigger(hours=24),
            id='data_cleanup',
            name='Data Cleanup',
            replace_existing=True
        )
        
        # Health check job (hourly)
        self.scheduler.add_job(
            self.health_check,
            trigger=IntervalTrigger(hours=1),
            id='health_check',
            name='Health Check',
            replace_existing=True
        )
        
        # Setup event listeners
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    def _job_listener(self, event):
        """Listen for job execution events."""
        if event.exception:
            logger.error(f"Job {event.job_id} failed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} completed successfully")
    
    async def run_scheduled_analysis(self):
        """Run the scheduled SEO analysis."""
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting scheduled analysis: {analysis_id}")
            
            # Run basic SEO analysis
            basic_results = analyze(
                url=self.config.website_url,
                sitemap_url=self.config.sitemap_url,
                analyze_headings=True,
                analyze_extra_tags=True,
                follow_links=False,  # Limit scope for scheduled runs
                run_llm_analysis=self.config.llm_analysis_enabled,
                enable_google_integration=self.config.google_integration_enabled
            )
            
            # Enhanced analysis with AI if enabled
            enhanced_results = basic_results.copy()
            
            if self.config.llm_analysis_enabled and self.llm_analyst:
                try:
                    # Get Google insights if available
                    google_insights = basic_results.get('google_insights', {})
                    
                    # Fetch Google insights if not already available
                    if not google_insights and self.google_integrator:
                        try:
                            google_insights = self.google_integrator.get_seo_insights(
                                search_console_site_url=self.search_console_url,
                                analytics_view_id=self.analytics_view_id,
                                analytics_measurement_id=self.analytics_measurement_id
                            )
                            enhanced_results['google_insights'] = google_insights
                        except Exception as e:
                            logger.error(f"Google integration failed during enhanced analysis: {e}")
                    
                    # Run enhanced LLM analysis
                    comprehensive_analysis = await self.llm_analyst.analyze_comprehensive_data(
                        seo_analysis=basic_results,
                        google_insights=google_insights
                    )
                    
                    enhanced_results['comprehensive_analysis'] = comprehensive_analysis
                    
                    # Generate strategic report
                    strategic_report = self.llm_analyst.generate_strategic_report(
                        comprehensive_analysis
                    )
                    enhanced_results['strategic_report'] = strategic_report
                    
                except Exception as e:
                    logger.error(f"Enhanced LLM analysis failed: {e}")
            
            # Run decision engine for recommendations
            if self.decision_engine:
                try:
                    google_insights = basic_results.get('google_insights', {})
                    llm_insights = enhanced_results.get('comprehensive_analysis')
                    
                    recommendations = self.decision_engine.analyze_and_recommend(
                        seo_analysis=basic_results,
                        google_insights=google_insights,
                        llm_insights=llm_insights
                    )
                    
                    enhanced_results['recommendations'] = recommendations
                    
                except Exception as e:
                    logger.error(f"Decision engine analysis failed: {e}")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            result = AnalysisResult(
                timestamp=start_time,
                website_url=self.config.website_url,
                analysis_id=analysis_id,
                status="completed",
                results=enhanced_results,
                execution_time=execution_time
            )
            
            self.analysis_history.append(result)
            
            # Send notifications if enabled
            if self.config.notifications_enabled:
                await self._send_notifications(result)
            
            logger.info(f"Analysis completed in {execution_time:.2f} seconds")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store error result
            result = AnalysisResult(
                timestamp=start_time,
                website_url=self.config.website_url,
                analysis_id=analysis_id,
                status="failed",
                results={},
                execution_time=execution_time,
                error_message=str(e)
            )
            
            self.analysis_history.append(result)
            logger.error(f"Analysis failed after {execution_time:.2f} seconds: {e}")
    
    async def _send_notifications(self, result: AnalysisResult):
        """Send notifications about analysis results."""
        if not self.config.notification_email:
            return
        
        try:
            # Simple email notification (can be enhanced with proper email service)
            subject = f"SEO Analysis Report - {result.timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            if result.status == "completed":
                recommendations = result.results.get('recommendations', {})
                summary = recommendations.get('summary', {})
                
                body = f"""
SEO Analysis Completed Successfully

Website: {result.website_url}
Analysis ID: {result.analysis_id}
Execution Time: {result.execution_time:.2f} seconds

Summary:
- Total Actions: {summary.get('total_actions', 0)}
- High Impact Actions: {summary.get('high_impact_actions', 0)}
- Quick Wins: {summary.get('quick_wins', 0)}
- Total Effort Required: {summary.get('total_effort_hours', 0)} hours

Recommendations available in the detailed results.
"""
            else:
                body = f"""
SEO Analysis Failed

Website: {result.website_url}
Analysis ID: {result.analysis_id}
Error: {result.error_message}

Please check the system logs for more details.
"""
            
            # Here you would integrate with your email service
            # For now, just log the notification
            logger.info(f"Notification email would be sent to {self.config.notification_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body:\n{body}")
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
    
    def cleanup_old_data(self):
        """Clean up old analysis data."""
        cutoff_date = datetime.now() - timedelta(days=self.config.data_retention_days)
        
        # Remove old analysis results
        original_count = len(self.analysis_history)
        self.analysis_history = [
            result for result in self.analysis_history
            if result.timestamp > cutoff_date
        ]
        
        removed_count = original_count - len(self.analysis_history)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old analysis results")
    
    def health_check(self):
        """Perform system health check."""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'scheduler_running': self.scheduler.running,
            'analysis_history_count': len(self.analysis_history),
            'google_integration': self.google_integrator is not None,
            'llm_analyst': self.llm_analyst is not None,
            'decision_engine': self.decision_engine is not None,
            'next_scheduled_run': None
        }
        
        # Get next scheduled run time
        job = self.scheduler.get_job('main_analysis')
        if job:
            health_status['next_scheduled_run'] = job.next_run_time.isoformat()
        
        logger.info(f"Health check: {health_status}")
        
        # Store health status
        return health_status
    
    def start(self):
        """Start the automation system."""
        logger.info("Starting SEO Agent Automation System")
        self.scheduler.start()
        logger.info(f"Scheduler started. Next analysis: {self.scheduler.get_job('main_analysis').next_run_time}")
    
    def stop(self):
        """Stop the automation system."""
        logger.info("Stopping SEO Agent Automation System")
        self.scheduler.shutdown()
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis history."""
        recent_results = sorted(
            self.analysis_history,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        return [asdict(result) for result in recent_results]
    
    def get_latest_analysis(self) -> Optional[Dict[str, Any]]:
        """Get the latest analysis results."""
        if not self.analysis_history:
            return None
        
        latest = max(self.analysis_history, key=lambda x: x.timestamp)
        return asdict(latest)
    
    def run_manual_analysis(self) -> str:
        """Trigger a manual analysis run."""
        logger.info("Triggering manual analysis")
        
        # Run analysis in background
        asyncio.create_task(self.run_scheduled_analysis())
        
        return "Manual analysis started"
    
    def update_config(self, **kwargs):
        """Update automation configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")
        
        # Restart scheduler if schedule changed
        if 'analysis_schedule' in kwargs:
            self.scheduler.remove_job('main_analysis')
            self.scheduler.add_job(
                self.run_scheduled_analysis,
                trigger=CronTrigger.from_crontab(self.config.analysis_schedule),
                id='main_analysis',
                name='Main SEO Analysis',
                replace_existing=True
            )
            logger.info("Updated analysis schedule")


class SEOAgentManager:
    """Manager class for SEO Agent operations."""
    
    def __init__(self):
        """Initialize the manager."""
        self.automation_systems: Dict[str, SEOAgentAutomation] = {}
    
    def add_website(self, website_url: str, config: AutomationConfig):
        """Add a website to automation."""
        self.automation_systems[website_url] = SEOAgentAutomation(config)
        logger.info(f"Added website to automation: {website_url}")
    
    def start_all(self):
        """Start all automation systems."""
        for system in self.automation_systems.values():
            system.start()
        logger.info(f"Started {len(self.automation_systems)} automation systems")
    
    def stop_all(self):
        """Stop all automation systems."""
        for system in self.automation_systems.values():
            system.stop()
        logger.info(f"Stopped {len(self.automation_systems)} automation systems")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all automation systems."""
        status = {
            'total_websites': len(self.automation_systems),
            'systems': {}
        }
        
        for url, system in self.automation_systems.items():
            status['systems'][url] = {
                'running': system.scheduler.running,
                'analysis_count': len(system.analysis_history),
                'latest_analysis': system.get_latest_analysis(),
                'health': system.health_check()
            }
        
        return status


# Example usage
def main():
    """Example of setting up and running the SEO Agent."""
    
    # Configuration for a website
    config = AutomationConfig(
        website_url="https://example.com",
        sitemap_url="https://example.com/sitemap.xml",
        analysis_schedule="0 9 * * 1",  # Every Monday at 9 AM
        google_integration_enabled=True,
        llm_analysis_enabled=True,
        notifications_enabled=True,
        notification_email="seo@example.com"
    )
    
    # Create and start automation
    automation = SEOAgentAutomation(config)
    
    try:
        automation.start()
        logger.info("SEO Agent is running. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        import time
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        automation.stop()


if __name__ == "__main__":
    main()