from rest_framework import status, viewsets
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .matching import NOT_SURE_SLUG, match_text
from .models import EnquiryCategory
from .serializers import EnquiryCategorySerializer, TriageMatchSerializer

# ~200 words at ~6 characters per word (average English word + space).
MAX_TEXT_LENGTH = 1200


class TriageRateThrottle(AnonRateThrottle):
    scope = "triage"


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
@throttle_classes([TriageRateThrottle])
def triage(request):
    text = request.data.get("text")
    scenario_id = request.data.get("scenario_id")

    if not text and not scenario_id:
        return Response(
            {"detail": "Provide either 'text' or 'scenario_id'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if text is not None and not isinstance(text, str):
        return Response(
            {"detail": "'text' must be a string."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(text, str) and len(text) > MAX_TEXT_LENGTH:
        return Response(
            {"detail": f"'text' must be {MAX_TEXT_LENGTH} characters or fewer."},
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