from rest_framework import serializers

from .models import EnquiryCategory


class EnquiryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryCategory
        fields = [
            "id",
            "slug",
            "name",
            "summary",
            "next_step",
            "keywords",
            "guide_link",
            "is_urgent",
        ]
