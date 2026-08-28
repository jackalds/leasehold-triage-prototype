from django.core.cache import cache
from rest_framework.test import APITestCase

from .matching import match_text
from .models import EnquiryCategory


class MatchTextTests(APITestCase):
    """Relies on the categories seeded by api/migrations/0002_seed_categories.py."""

    def test_matches_category_by_keyword(self):
        matches = match_text("My landlord sent an invoice for the service charge")
        self.assertEqual(matches[0][0].slug, "service-charges")
        self.assertGreater(matches[0][1], 0)

    def test_excludes_not_sure_category(self):
        matches = match_text("service charge invoice unreasonable charge")
        slugs = [category.slug for category, _, _ in matches]
        self.assertNotIn("not-sure", slugs)

    def test_no_keyword_hits_returns_empty(self):
        matches = match_text("something about my cat")
        self.assertEqual(matches, [])

    def test_more_keyword_hits_ranks_higher(self):
        matches = match_text(
            "service charge invoice unreasonable charge, also ground rent"
        )
        self.assertEqual(matches[0][0].slug, "service-charges")
        self.assertGreater(matches[0][1], matches[1][1])

    def test_confidence_increases_with_score(self):
        matches = match_text("service charge invoice unreasonable charge")
        self.assertEqual(matches[0][1], 3)
        self.assertGreaterEqual(matches[0][2], 0.9)

    def test_urgent_category_matches_on_its_keywords(self):
        matches = match_text("My landlord is threatening forfeiture over a breach of lease")
        self.assertEqual(matches[0][0].slug, "breach-of-lease-forfeiture")
        self.assertTrue(matches[0][0].is_urgent)


class TriageAPITests(APITestCase):
    """Relies on the categories seeded by api/migrations/0002_seed_categories.py."""

    def setUp(self):
        # The triage endpoint is rate-limited; clear throttle state between
        # tests so one test's requests don't count against another's quota.
        cache.clear()

    def test_requires_text_or_scenario_id(self):
        response = self.client.post("/api/triage/", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_happy_path_text_match(self):
        response = self.client.post(
            "/api/triage/",
            {"text": "I got an invoice for a service charge I don't understand"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["confident"])
        self.assertEqual(response.data["matches"][0]["category"]["slug"], "service-charges")

    def test_no_match_returns_not_sure(self):
        response = self.client.post(
            "/api/triage/", {"text": "my cat is unwell"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["confident"])
        self.assertEqual(response.data["matches"][0]["category"]["slug"], "not-sure")

    def test_scenario_id_returns_matching_category(self):
        response = self.client.post(
            "/api/triage/", {"scenario_id": "service-charges"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["confident"])
        self.assertEqual(response.data["matches"][0]["category"]["slug"], "service-charges")
        self.assertEqual(response.data["matches"][0]["confidence"], 1.0)

    def test_scenario_id_not_sure_is_not_confident(self):
        response = self.client.post(
            "/api/triage/", {"scenario_id": "not-sure"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["confident"])

    def test_unknown_scenario_id_returns_400(self):
        response = self.client.post(
            "/api/triage/", {"scenario_id": "made-up-slug"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_ensure_seed_data_present(self):
        self.assertEqual(EnquiryCategory.objects.count(), 8)

    def test_non_string_text_returns_400(self):
        response = self.client.post(
            "/api/triage/", {"text": ["not", "a", "string"]}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_text_exceeding_max_length_returns_400(self):
        response = self.client.post(
            "/api/triage/", {"text": "a" * 1201}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_whitespace_only_text_returns_not_sure(self):
        response = self.client.post(
            "/api/triage/", {"text": "   "}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["confident"])
        self.assertEqual(response.data["matches"][0]["category"]["slug"], "not-sure")


class TriageThrottleTests(APITestCase):
    """Relies on the categories seeded by api/migrations/0002_seed_categories.py."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_exceeding_rate_limit_returns_429(self):
        for _ in range(20):
            response = self.client.post(
                "/api/triage/", {"scenario_id": "not-sure"}, format="json"
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/api/triage/", {"scenario_id": "not-sure"}, format="json"
        )
        self.assertEqual(response.status_code, 429)
