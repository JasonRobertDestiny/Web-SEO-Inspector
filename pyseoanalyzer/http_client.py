import urllib3
from urllib3.exceptions import HTTPError


class Http:
    """HTTP client wrapper using urllib3"""
    
    def __init__(self):
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=10.0, read=30.0),
            headers={
                'User-Agent': 'Python-SEO-Analyzer/2025.4.3 (https://github.com/sethblack/python-seo-analyzer)'
            },
            cert_reqs='CERT_REQUIRED',
            ca_certs=None
        )
    
    def get(self, url):
        """Perform HTTP GET request"""
        try:
            response = self.http.request('GET', url)
            return response
        except Exception as e:
            raise HTTPError(f"HTTP request failed: {e}")


# Thread-safe singleton instance
http = Http()