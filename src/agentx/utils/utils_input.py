from urllib.parse import urlparse

def is_valid_url(site_url: str):
    if not site_url:
        return False
    try:
        result = urlparse(site_url)
        # Check if both scheme (http/https) and netloc (domain) are present
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
