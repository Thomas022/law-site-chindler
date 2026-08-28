from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from properties.api.views import public_properties

from .serializers import PublicLeadSerializer


class PropertyInterestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "interest"

    def post(self, request, property_id):
        property_item = public_properties().filter(public_id=property_id).first()
        if property_item is None:
            return Response(
                {"detail": "Imóvel não encontrado ou indisponível."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Campo-armadilha: robôs costumam preenchê-lo, pessoas não o veem.
        if request.data.get("website"):
            return Response(
                {"detail": "Interesse recebido com sucesso."},
                status=status.HTTP_201_CREATED,
            )

        serializer = PublicLeadSerializer(
            data=request.data,
            context={"property": property_item},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Interesse recebido com sucesso."},
            status=status.HTTP_201_CREATED,
        )

