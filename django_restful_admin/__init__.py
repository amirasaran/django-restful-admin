from . import admin

site = admin.site
RestFulModelAdmin = admin.RestFulModelAdmin
RestFulAdminSite = admin.RestFulAdminSite

__all__ = [
    'admin',
    'site',
    'RestFulModelAdmin',
    'RestFulAdminSite'
]
