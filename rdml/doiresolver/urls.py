from django.urls import path
from .views import (
    # DoiListView,
    landing_page_list,
    landing_page,
)


app_name = 'doiresolver'

urlpatterns = [
    path('', landing_page_list, name="doi-list"),
    path('<uuid:pk_uuid>/', landing_page, name="landing-page"),
    path('<slug:identifier>/', landing_page, name="landing-page"),
    # path('<str:identifier>/', landing_page, name="landing-page"),
]
