"""
Google Analytics and Search Console data integration module for SEO Agent.

This module provides functionality to fetch data from Google Analytics
and Google Search Console APIs for comprehensive SEO analysis.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleDataIntegrator:
    """Integrates Google Analytics and Search Console data with SEO analysis."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/analytics.readonly',
        'https://www.googleapis.com/auth/webmasters.readonly'
    ]
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.json'):
        """
        Initialize Google API integrator.
        
        Args:
            credentials_file: Path to OAuth2 credentials file
            token_file: Path to store access token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.analytics_service = None
        self.searchconsole_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google APIs."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}. "
                        "Please download from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Build service clients
        self.analytics_service = build('analyticsreporting', 'v4', credentials=creds)
        self.searchconsole_service = build('searchconsole', 'v1', credentials=creds)
    
    def get_analytics_data(
        self, 
        view_id: str = None,
        measurement_id: str = None,
        start_date: str = '30daysAgo', 
        end_date: str = 'today',
        metrics: List[str] = None,
        dimensions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch data from Google Analytics.
        
        Args:
            view_id: Google Analytics Universal Analytics view ID (legacy)
            measurement_id: Google Analytics 4 Measurement ID (e.g., G-XXXXXXXXXX)
            start_date: Start date in GA format (e.g., '30daysAgo', '2024-01-01')
            end_date: End date in GA format
            metrics: List of metrics to fetch (default: sessions, pageviews, users)
            dimensions: List of dimensions to group by
            
        Returns:
            Dictionary containing analytics data
        """
        # Determine which Analytics version to use
        if measurement_id:
            # Use GA4 Data API
            return self._get_ga4_data(measurement_id, start_date, end_date, metrics, dimensions)
        elif view_id:
            # Use Universal Analytics Reporting API
            return self._get_universal_analytics_data(view_id, start_date, end_date, metrics, dimensions)
        else:
            raise ValueError("Either view_id (Universal Analytics) or measurement_id (GA4) must be provided")
    
    def _get_universal_analytics_data(self, view_id: str, start_date: str, end_date: str, metrics: List[str], dimensions: List[str]) -> Dict[str, Any]:
        """Fetch data from Universal Analytics."""
        if metrics is None:
            metrics = ['ga:sessions', 'ga:pageviews', 'ga:users']
        
        if dimensions is None:
            dimensions = ['ga:pagePath']
        
        try:
            request_body = {
                'reportRequests': [{
                    'viewId': view_id,
                    'dateRanges': [{
                        'startDate': start_date,
                        'endDate': end_date
                    }],
                    'metrics': [{'expression': metric} for metric in metrics],
                    'dimensions': [{'name': dimension} for dimension in dimensions],
                    'pageSize': 10000
                }]
            }
            
            response = self.analytics_service.reports().batchGet(
                body=request_body
            ).execute()
            
            return self._parse_analytics_response(response)
        except HttpError as e:
            logger.error(f"Universal Analytics API error: {e}")
            return {}
    
    def _get_ga4_data(self, measurement_id: str, start_date: str, end_date: str, metrics: List[str], dimensions: List[str]) -> Dict[str, Any]:
        """Fetch data from GA4 Data API."""
        # Note: This is a placeholder for GA4 implementation
        # GA4 uses different API endpoints and metric names
        logger.warning("GA4 integration is not yet fully implemented. Using placeholder data.")
        
        # Convert GA4 date format
        if start_date.endswith('daysAgo'):
            days = int(start_date.replace('daysAgo', ''))
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        elif start_date == 'today':
            start_date = datetime.now().strftime('%Y-%m-%d')
            
        if end_date == 'today':
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Return placeholder structure for GA4
        try:
            # TODO: Implement actual GA4 API calls here
            return {
                'reports': [{
                    'column_headers': ['ga:pagePath', 'ga:sessions', 'ga:pageviews', 'ga:users'],
                    'rows': []
                }],
                'summary': {
                    'ga:sessions': 0,
                    'ga:pageviews': 0,
                    'ga:users': 0
                },
                'measurement_id': measurement_id,
                'date_range': f"{start_date} to {end_date}",
                'note': 'GA4 integration is in development. This is placeholder data.'
            }
            
        except HttpError as e:
            logger.error(f"Google Analytics API error: {e}")
            return {}
    
    def _parse_analytics_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Google Analytics API response."""
        parsed_data = {
            'reports': [],
            'summary': {}
        }
        
        for report in response.get('reports', []):
            report_data = {
                'column_headers': [header['name'] for header in report['columnHeader']['dimensions']] + 
                                [metric['name'] for metric in report['columnHeader']['metricHeader']['metricHeaderEntries']],
                'rows': []
            }
            
            total_values = {}
            
            for row in report.get('data', {}).get('rows', []):
                dimensions = row.get('dimensions', [])
                metrics = row.get('metrics', [{}])[0].get('values', [])
                report_data['rows'].append(dimensions + metrics)
                
                # Calculate totals
                for i, metric in enumerate(report['columnHeader']['metricHeader']['metricHeaderEntries']):
                    metric_name = metric['name']
                    try:
                        total_values[metric_name] = total_values.get(metric_name, 0) + int(metrics[i])
                    except (ValueError, IndexError):
                        continue
            
            parsed_data['reports'].append(report_data)
            parsed_data['summary'] = total_values
        
        return parsed_data
    
    def get_search_console_data(
        self,
        site_url: str,
        start_date: str = None,
        end_date: str = None,
        dimensions: List[str] = None,
        row_limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Fetch data from Google Search Console.
        
        Args:
            site_url: Property URL in Search Console
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            dimensions: List of dimensions (default: ['query', 'page'])
            row_limit: Maximum number of rows to return
            
        Returns:
            Dictionary containing Search Console data
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if dimensions is None:
            dimensions = ['query', 'page']
        
        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'rowLimit': row_limit,
                'startRow': 0
            }
            
            response = self.searchconsole_service.searchanalytics().query(
                siteUrl=site_url,
                body=request_body
            ).execute()
            
            return self._parse_search_console_response(response)
            
        except HttpError as e:
            logger.error(f"Google Search Console API error: {e}")
            return {}
    
    def _parse_search_console_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Search Console API response."""
        parsed_data = {
            'rows': [],
            'summary': {
                'total_clicks': 0,
                'total_impressions': 0,
                'avg_ctr': 0.0,
                'avg_position': 0.0
            }
        }
        
        rows = response.get('rows', [])
        if not rows:
            return parsed_data
        
        total_clicks = 0
        total_impressions = 0
        total_ctr = 0.0
        total_position = 0.0
        
        for row in rows:
            row_data = {
                'keys': row.get('keys', []),
                'clicks': row.get('clicks', 0),
                'impressions': row.get('impressions', 0),
                'ctr': row.get('ctr', 0.0),
                'position': row.get('position', 0.0)
            }
            parsed_data['rows'].append(row_data)
            
            total_clicks += row_data['clicks']
            total_impressions += row_data['impressions']
            total_ctr += row_data['ctr']
            total_position += row_data['position']
        
        # Calculate averages
        if rows:
            parsed_data['summary']['total_clicks'] = total_clicks
            parsed_data['summary']['total_impressions'] = total_impressions
            parsed_data['summary']['avg_ctr'] = total_ctr / len(rows)
            parsed_data['summary']['avg_position'] = total_position / len(rows)
        
        return parsed_data
    
    def get_seo_insights(
        self,
        search_console_site_url: str,
        analytics_view_id: str = None,
        analytics_measurement_id: str = None,
        start_date: str = '30daysAgo',
        end_date: str = 'today'
    ) -> Dict[str, Any]:
        """
        Get comprehensive SEO insights by combining data from both services.
        
        Args:
            search_console_site_url: Search Console property URL
            analytics_view_id: Google Analytics Universal Analytics view ID (optional)
            analytics_measurement_id: Google Analytics 4 Measurement ID (optional)
            start_date: Start date
            end_date: End date
            
        Returns:
            Combined SEO insights data
        """
        # Fetch data from both services
        analytics_data = self.get_analytics_data(
            view_id=analytics_view_id,
            measurement_id=analytics_measurement_id,
            start_date=start_date,
            end_date=end_date,
            metrics=['ga:sessions', 'ga:pageviews', 'ga:users', 'ga:bounceRate', 'ga:avgSessionDuration'],
            dimensions=['ga:pagePath']
        )
        
        search_data = self.get_search_console_data(
            site_url=search_console_site_url,
            start_date=self._convert_date_format(start_date),
            end_date=self._convert_date_format(end_date) if end_date != 'today' else datetime.now().strftime('%Y-%m-%d'),
            dimensions=['page']
        )
        
        # Combine and analyze data
        insights = self._analyze_seo_data(analytics_data, search_data)
        
        return insights
    
    def _convert_date_format(self, date_str: str) -> str:
        """Convert Google Analytics date format to YYYY-MM-DD."""
        if date_str == 'today':
            return datetime.now().strftime('%Y-%m-%d')
        elif date_str == 'yesterday':
            return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        elif date_str.endswith('daysAgo'):
            days = int(date_str.replace('daysAgo', ''))
            return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        else:
            # Assume it's already in YYYY-MM-DD format
            return date_str
    
    def _analyze_seo_data(self, analytics_data: Dict[str, Any], search_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze combined SEO data to generate insights."""
        insights = {
            'analytics_summary': analytics_data.get('summary', {}),
            'search_summary': search_data.get('summary', {}),
            'page_performance': {},
            'recommendations': []
        }
        
        # Analyze page performance
        analytics_rows = analytics_data.get('reports', [{}])[0].get('rows', [])
        search_rows = search_data.get('rows', [])
        
        # Create page-level performance mapping
        for row in analytics_rows:
            page_path = row[0]  # First dimension is page path
            page_data = {
                'pageviews': int(row[1]) if len(row) > 1 else 0,
                'sessions': int(row[2]) if len(row) > 2 else 0,
                'users': int(row[3]) if len(row) > 3 else 0,
                'bounce_rate': float(row[4]) if len(row) > 4 else 0.0,
                'avg_session_duration': float(row[5]) if len(row) > 5 else 0.0,
                'search_data': {}
            }
            insights['page_performance'][page_path] = page_data
        
        # Add search console data
        for row in search_rows:
            page_path = row['keys'][0] if row['keys'] else ''
            if page_path in insights['page_performance']:
                insights['page_performance'][page_path]['search_data'] = {
                    'clicks': row['clicks'],
                    'impressions': row['impressions'],
                    'ctr': row['ctr'],
                    'position': row['position']
                }
        
        # Generate recommendations
        insights['recommendations'] = self._generate_seo_recommendations(insights)
        
        return insights
    
    def _generate_seo_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate SEO recommendations based on data analysis."""
        recommendations = []
        
        # Analyze bounce rates
        for page_path, page_data in insights['page_performance'].items():
            if page_data['bounce_rate'] > 0.7:  # High bounce rate
                recommendations.append({
                    'type': 'user_experience',
                    'priority': 'high',
                    'page': page_path,
                    'issue': f'High bounce rate ({page_data["bounce_rate"]:.1%})',
                    'recommendation': 'Improve content engagement and user experience',
                    'impact': 'reduce bounce rate, increase session duration'
                })
            
            if page_data['avg_session_duration'] < 60:  # Short sessions
                recommendations.append({
                    'type': 'content_quality',
                    'priority': 'medium',
                    'page': page_path,
                    'issue': f'Short average session duration ({page_data["avg_session_duration"]:.0f}s)',
                    'recommendation': 'Enhance content depth and readability',
                    'impact': 'increase user engagement and time on page'
                })
            
            # Check search performance
            search_data = page_data.get('search_data', {})
            if search_data.get('position', 0) > 10:  # Low ranking
                recommendations.append({
                    'type': 'search_ranking',
                    'priority': 'high',
                    'page': page_path,
                    'issue': f'Low search position (avg: {search_data["position"]:.1f})',
                    'recommendation': 'Optimize content for target keywords and improve backlink profile',
                    'impact': 'improve search rankings and organic traffic'
                })
        
        return recommendations

# Example usage
if __name__ == "__main__":
    # Initialize integrator
    integrator = GoogleDataIntegrator()
    
    # Get SEO insights
    insights = integrator.get_seo_insights(
        analytics_view_id="YOUR_VIEW_ID",
        search_console_site_url="https://example.com"
    )
    
    print(json.dumps(insights, indent=2))