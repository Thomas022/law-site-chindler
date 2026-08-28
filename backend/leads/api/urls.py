from django.urls import path

from .views import PropertyInterestView


urlpatterns = [
    path(
        "properties/<uuid:property_id>/interest/",
        PropertyInterestView.as_view(),
        name="property-interest",
    ),
]
