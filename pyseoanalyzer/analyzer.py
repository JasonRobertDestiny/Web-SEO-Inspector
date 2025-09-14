import time
from operator import itemgetter
from .website import Website
from .seo_optimizer import enhance_analysis_with_optimization
from .google_integrator import GoogleDataIntegrator


def calc_total_time(start_time):
    return time.time() - start_time


def analyze(
    url,
    sitemap_url=None,
    analyze_headings=False,
    analyze_extra_tags=False,
    follow_links=True,
    run_llm_analysis=False,
    enable_google_integration=False,
):
    start_time = time.time()

    output = {
        "pages": [],
        "keywords": [],
        "errors": [],
        "total_time": 0,  # Initialize to 0 before calculation
        "google_insights": None,
    }

    site = Website(
        base_url=url,
        sitemap=sitemap_url,
        analyze_headings=analyze_headings,
        analyze_extra_tags=analyze_extra_tags,
        follow_links=follow_links,
        run_llm_analysis=run_llm_analysis,
    )

    site.crawl()

    for p in site.crawled_pages:
        output["pages"].append(p.as_dict())

    output["duplicate_pages"] = [
        list(site.content_hashes[p])
        for p in site.content_hashes
        if len(site.content_hashes[p]) > 1
    ]

    sorted_words = sorted(site.wordcount.items(), key=itemgetter(1), reverse=True)
    sorted_bigrams = sorted(site.bigrams.items(), key=itemgetter(1), reverse=True)
    sorted_trigrams = sorted(site.trigrams.items(), key=itemgetter(1), reverse=True)

    output["keywords"] = []

    for w in sorted_words:
        if w[1] > 4:
            output["keywords"].append(
                {
                    "word": w[0],
                    "count": w[1],
                }
            )

    for w, v in sorted_bigrams:
        if v > 4:
            output["keywords"].append(
                {
                    "word": w,
                    "count": v,
                }
            )

    for w, v in sorted_trigrams:
        if v > 4:
            output["keywords"].append(
                {
                    "word": w,
                    "count": v,
                }
            )

    # Sort one last time...
    output["keywords"] = sorted(
        output["keywords"], key=itemgetter("count"), reverse=True
    )

    output["total_time"] = calc_total_time(start_time)

    # 添加SEO优化建议
    enhanced_output = enhance_analysis_with_optimization(output)
    
    # 如果启用Google集成，添加Google数据洞察
    if enable_google_integration:
        try:
            import os
            analytics_view_id = os.getenv('GOOGLE_ANALYTICS_VIEW_ID')
            analytics_measurement_id = os.getenv('GOOGLE_ANALYTICS_MEASUREMENT_ID')
            search_console_url = os.getenv('GOOGLE_SEARCH_CONSOLE_URL')
            
            if (analytics_view_id or analytics_measurement_id) and search_console_url:
                google_integrator = GoogleDataIntegrator()
                insights = google_integrator.get_seo_insights(
                    search_console_site_url=search_console_url,
                    analytics_view_id=analytics_view_id,
                    analytics_measurement_id=analytics_measurement_id
                )
                enhanced_output['google_insights'] = insights
            else:
                enhanced_output['errors'].append("Google integration requires GOOGLE_SEARCH_CONSOLE_URL and either GOOGLE_ANALYTICS_VIEW_ID or GOOGLE_ANALYTICS_MEASUREMENT_ID")
        except Exception as e:
            enhanced_output['errors'].append(f"Google integration failed: {str(e)}")
    
    return enhanced_output
