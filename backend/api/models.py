from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class EnquiryCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="Used as the category id in API responses.")
    summary = models.TextField(
        help_text="Plain-English explanation of what this usually means."
    )
    next_step = models.TextField(help_text="The single clear next action for this category.")
    keywords = models.TextField(
        blank=True,
        help_text="Comma-separated words/phrases used to match free-text enquiries to this category.",
    )
    guide_link = models.URLField(
        blank=True, help_text="Link to the full LEASE guidance page, if there is one."
    )
    is_urgent = models.BooleanField(
        default=False, help_text="Flag urgent categories (e.g. forfeiture threats)."
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("summary"),
        FieldPanel("next_step"),
        FieldPanel("keywords"),
        FieldPanel("guide_link"),
        FieldPanel("is_urgent"),
    ]

    class Meta:
        verbose_name = "Enquiry category"
        verbose_name_plural = "Enquiry categories"
        ordering = ["name"]

    def __str__(self):
        return self.name
