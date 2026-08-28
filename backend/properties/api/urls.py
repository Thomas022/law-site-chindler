from django.urls import path

from .views import (
    PropertyFilterOptionsView,
    PublicPropertyDetailView,
    PublicPropertyListView,
)


urlpatterns = [
    path("properties/", PublicPropertyListView.as_view(), name="property-list"),
    path("properties/filters/", PropertyFilterOptionsView.as_view(), name="property-filters"),
    path(
        "properties/<uuid:property_id>/",
        PublicPropertyDetailView.as_view(),
        name="property-detail",
    ),
]
