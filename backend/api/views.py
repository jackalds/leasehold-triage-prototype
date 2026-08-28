from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .matching import NOT_SURE_SLUG, match_text
from .models import EnquiryCategory
from .serializers import EnquiryCategorySerializer, TriageMatchSerializer


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


class EnquiryCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EnquiryCategory.objects.all()
    serializer_class = EnquiryCategorySerializer
    lookup_field = "slug"


def _not_sure_response():
    not_sure = EnquiryCategory.objects.get(slug=NOT_SURE_SLUG)
    return Response(
        {
            "confident": False,
            "matches": TriageMatchSerializer(
                [{"category": not_sure, "score": 0, "confidence": 0.0}], many=True
            ).data,
        }
    )


@api_view(["POST"])
def triage(request):
    text = request.data.get("text")
    scenario_id = request.data.get("scenario_id")

    if not text and not scenario_id:
        return Response(
            {"detail": "Provide either 'text' or 'scenario_id'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if scenario_id:
        try:
            category = EnquiryCategory.objects.get(slug=scenario_id)
        except EnquiryCategory.DoesNotExist:
            return Response(
                {"detail": f"Unknown scenario_id '{scenario_id}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if category.slug == NOT_SURE_SLUG:
            return _not_sure_response()
        return Response(
            {
                "confident": True,
                "matches": TriageMatchSerializer(
                    [{"category": category, "score": None, "confidence": 1.0}], many=True
                ).data,
            }
        )

    matches = match_text(text)
    if not matches:
        return _not_sure_response()

    return Response(
        {
            "confident": True,
            "matches": TriageMatchSerializer(
                [
                    {"category": category, "score": score, "confidence": confidence}
                    for category, score, confidence in matches
                ],
                many=True,
            ).data,
        }
    )