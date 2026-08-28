from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import EnquiryCategory
from .serializers import EnquiryCategorySerializer


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


class EnquiryCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EnquiryCategory.objects.all()
    serializer_class = EnquiryCategorySerializer
    lookup_field = "slug"