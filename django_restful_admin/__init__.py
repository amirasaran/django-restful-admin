
# these are updated by admin module itself once fully loaded
# to avoid issues caused by importing rest_framework too soon
site = None
RestFulModelAdmin = None
RestFulAdminSite = None

__all__ = [
    'site',
    'RestFulModelAdmin',
    'RestFulAdminSite'
]
