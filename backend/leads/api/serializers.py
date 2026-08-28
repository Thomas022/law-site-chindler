import re

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from leads.models import Lead


class PublicLeadSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=2, max_length=150, trim_whitespace=True)
    phone = serializers.CharField(min_length=8, max_length=30, trim_whitespace=True)
    email = serializers.EmailField(max_length=254)
    message = serializers.CharField(min_length=10, max_length=2000, trim_whitespace=True)
    consent = serializers.BooleanField()
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate_phone(self, value):
        digits = re.sub(r"\D", "", value)
        if not 10 <= len(digits) <= 13:
            raise serializers.ValidationError("Informe um telefone válido com DDD.")
        return value

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError(
                "É necessário autorizar o uso dos dados para receber atendimento."
            )
        return value

    def create(self, validated_data):
        validated_data.pop("consent")
        validated_data.pop("website", None)
        property_item = self.context["property"]
        return Lead.objects.create(
            property=property_item,
            property_title=property_item.title,
            consent_version=settings.PRIVACY_POLICY_VERSION,
            consent_at=timezone.now(),
            **validated_data,
        )
