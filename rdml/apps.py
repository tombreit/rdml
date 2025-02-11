from django.contrib.admin.apps import AdminConfig

class RDAdminConfig(AdminConfig):
    default_site = 'rdml.admin.RDAdminSite'
