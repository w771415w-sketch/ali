from urllib.parse import urlparse
ALLOWED_SCHEMES={'http','https'}
def validate_url(url:str)->bool:
    try:u=urlparse(url); return u.scheme in ALLOWED_SCHEMES and bool(u.netloc)
    except Exception:return False
def research_policy(enabled:bool)->dict:return {'internet_enabled':bool(enabled),'offline_default':not enabled,'save_requires_sources':True}
