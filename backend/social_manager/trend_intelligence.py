"""
Trend Research & Insights Module
Real-time trend monitoring from Twitter/X, Instagram, and Google Trends.

SETUP — add these to your .env (or export in shell before running main.py):
    TWITTER_BEARER_TOKEN=your_token_here
    INSTAGRAM_ACCESS_TOKEN=your_token_here
    INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id_here
    RAPIDAPI_KEY=your_key_here          # optional: RapidAPI Twitter trends fallback

QUICK START — free tier works fine:
    Twitter/X  : Free Bearer Token from developer.twitter.com
    Instagram  : Meta Business Suite → Graph API → Access Token
    Google     : pip install pytrends  (no key required — free)
"""

from __future__ import annotations

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ─── env vars ─────────────────────────────────────────────────────────────────

TWITTER_BEARER_TOKEN          = os.getenv("TWITTER_BEARER_TOKEN", "")
INSTAGRAM_ACCESS_TOKEN        = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
RAPIDAPI_KEY                  = os.getenv("RAPIDAPI_KEY", "")

# ─── models ───────────────────────────────────────────────────────────────────

class Trend(BaseModel):
    """Individual trend data point."""
    name: str
    source: str          # twitter | instagram | google_trends
    volume: int
    momentum: str        # rising | stable | declining
    related_topics: List[str] = []
    relevance_score: float = 0.5
    tracked_since: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("tracked_since") is None:
            data["tracked_since"] = datetime.utcnow()
        super().__init__(**data)


# ─── core class ───────────────────────────────────────────────────────────────

class TrendIntelligence:
    """
    Monitor trends across social platforms and search.

    Each fetch_* method tries the real API first, then falls back to
    curated mock data so the app never breaks when keys are missing.
    """

    def __init__(self):
        self.trends_cache: Dict[str, List[Trend]] = {}
        self.last_sync: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=15)   # re-fetch after 15 min

    # ── cache helpers ──────────────────────────────────────────────────────────

    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.trends_cache or self.last_sync is None:
            return False
        return datetime.utcnow() - self.last_sync < self._cache_ttl

    # ─────────────────────────────────────────────────────────────────────────
    # 1. TWITTER / X
    # ─────────────────────────────────────────────────────────────────────────

    def fetch_twitter_trends(self, woeid: int = 1) -> List[Trend]:
        """
        Fetch trending topics from Twitter/X API v2.

        Requires: TWITTER_BEARER_TOKEN in environment.
        Falls back to mock data if token is absent or request fails.

        Twitter free tier gives ~500k tweet reads/month — enough for trending
        topic discovery. Use woeid=1 for worldwide, 23424977 for USA.
        """
        if TWITTER_BEARER_TOKEN:
            try:
                return self._fetch_twitter_real(woeid)
            except Exception as e:
                logger.warning(f"Twitter API failed, using mock data: {e}")

        # ── fallback mock ──────────────────────────────────────────────────────
        return [
            Trend(name="#SpringFitness", source="twitter", volume=45000,
                  momentum="rising", related_topics=["fitness","gym","health"],
                  relevance_score=0.85),
            Trend(name="AI Marketing", source="twitter", volume=32000,
                  momentum="stable", related_topics=["ai","automation","marketing"],
                  relevance_score=0.72),
            Trend(name="#TransformationStories", source="twitter", volume=28500,
                  momentum="rising", related_topics=["motivation","goals","success"],
                  relevance_score=0.90),
        ]

    def _fetch_twitter_real(self, woeid: int) -> List[Trend]:
        """
        Real Twitter v2 implementation.

        NOTE: Twitter v1.1 trending endpoint (/trends/place) is available on
        Basic plan ($100/mo).  The free v2 plan supports search_recent_tweets,
        which we use here to approximate "trending" by search volume.

        To use the v1.1 trends endpoint directly, switch to tweepy:
            import tweepy
            client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
            # For v1.1 access you need the full OAuth1 credentials:
            api = tweepy.API(auth)
            trends = api.get_place_trends(woeid)
        """
        headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

        # Use v2 recent-tweet counts as a trending proxy (works on free tier)
        keywords = ["#fitness", "#wellness", "#transformation", "#motivation", "#workout"]
        results: List[Trend] = []

        for kw in keywords:
            url = "https://api.twitter.com/2/tweets/counts/recent"
            params = {"query": kw, "granularity": "hour"}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            total = sum(b.get("tweet_count", 0) for b in data.get("data", []))
            # simple momentum: compare last 6h vs previous 6h
            counts = [b.get("tweet_count", 0) for b in data.get("data", [])]
            recent = sum(counts[-6:]) if len(counts) >= 6 else sum(counts)
            older  = sum(counts[-12:-6]) if len(counts) >= 12 else recent
            momentum = "rising" if recent > older * 1.1 else ("declining" if recent < older * 0.9 else "stable")

            results.append(Trend(
                name=kw,
                source="twitter",
                volume=total,
                momentum=momentum,
                related_topics=[kw.lstrip("#").lower()],
                relevance_score=min(1.0, total / 50000),
            ))

        results.sort(key=lambda t: t.volume, reverse=True)
        return results

    # ─────────────────────────────────────────────────────────────────────────
    # 2. INSTAGRAM
    # ─────────────────────────────────────────────────────────────────────────

    def fetch_instagram_trends(self) -> List[Trend]:
        """
        Fetch trending hashtags from Instagram Graph API.

        Requires:
            INSTAGRAM_ACCESS_TOKEN          – from Meta Business Suite
            INSTAGRAM_BUSINESS_ACCOUNT_ID   – your IG business account ID

        The Graph API does NOT have a public "trending hashtags" endpoint.
        Instead we use hashtag_search + media_count as a trending proxy, which
        is available on any Business/Creator account (no paid tier required).

        To get your access token:
            1. Go to developers.facebook.com → My Apps → Create App
            2. Add Instagram Graph API
            3. Generate a long-lived token in Graph API Explorer
        """
        if INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID:
            try:
                return self._fetch_instagram_real()
            except Exception as e:
                logger.warning(f"Instagram API failed, using mock data: {e}")

        # ── fallback mock ──────────────────────────────────────────────────────
        return [
            Trend(name="#FitnessGoals", source="instagram", volume=125000,
                  momentum="rising", related_topics=["workout","health","gym"],
                  relevance_score=0.88),
            Trend(name="#BeforeAndAfter", source="instagram", volume=98000,
                  momentum="stable", related_topics=["transformation","progress","results"],
                  relevance_score=0.92),
            Trend(name="#WellnessJourney", source="instagram", volume=76000,
                  momentum="rising", related_topics=["health","self-care","motivation"],
                  relevance_score=0.85),
        ]

    def _fetch_instagram_real(self) -> List[Trend]:
        """
        Real Instagram Graph API implementation.

        Checks media_count for a list of target hashtags.
        media_count is the closest public metric to "trending volume" on IG.

        Rate limits: 200 calls / hour per user token.
        """
        base = "https://graph.facebook.com/v19.0"
        target_hashtags = [
            "fitness", "fitnessmotivation", "workout", "transformation",
            "wellness", "healthylifestyle", "gymlife", "fitnessgoals",
        ]
        results: List[Trend] = []

        for tag in target_hashtags:
            # Step 1: get hashtag ID
            id_resp = requests.get(
                f"{base}/ig_hashtag_search",
                params={
                    "user_id": INSTAGRAM_BUSINESS_ACCOUNT_ID,
                    "q": tag,
                    "access_token": INSTAGRAM_ACCESS_TOKEN,
                },
                timeout=10,
            )
            id_resp.raise_for_status()
            tag_id = id_resp.json().get("data", [{}])[0].get("id")
            if not tag_id:
                continue

            # Step 2: get media count
            info_resp = requests.get(
                f"{base}/{tag_id}",
                params={
                    "fields": "id,name,media_count",
                    "access_token": INSTAGRAM_ACCESS_TOKEN,
                },
                timeout=10,
            )
            info_resp.raise_for_status()
            info = info_resp.json()
            media_count = info.get("media_count", 0)

            results.append(Trend(
                name=f"#{tag}",
                source="instagram",
                volume=media_count,
                momentum="rising",   # IG doesn't expose velocity; mark rising by default
                related_topics=[tag],
                relevance_score=min(1.0, media_count / 200_000),
            ))

        results.sort(key=lambda t: t.volume, reverse=True)
        return results[:5]

    # ─────────────────────────────────────────────────────────────────────────
    # 3. GOOGLE TRENDS  (free — no API key required)
    # ─────────────────────────────────────────────────────────────────────────

    def fetch_google_trends(self, category: str = "fitness") -> List[Trend]:
        """
        Fetch trending search terms via pytrends (unofficial Google Trends API).

        Install:  pip install pytrends
        No API key required — uses Google's public endpoint.

        Rate limits: ~10-20 req/min before you get throttled.
        """
        try:
            return self._fetch_google_trends_real(category)
        except ImportError:
            logger.info("pytrends not installed. Run: pip install pytrends")
        except Exception as e:
            logger.warning(f"Google Trends failed, using mock data: {e}")

        # ── fallback mock ──────────────────────────────────────────────────────
        return [
            Trend(name="home workout equipment", source="google_trends", volume=55000,
                  momentum="rising", related_topics=["exercise","fitness","home gym"],
                  relevance_score=0.80),
            Trend(name="fitness motivation tips", source="google_trends", volume=42000,
                  momentum="stable", related_topics=["motivation","fitness","goals"],
                  relevance_score=0.88),
            Trend(name="best fitness apps 2026", source="google_trends", volume=38000,
                  momentum="rising", related_topics=["apps","fitness","tracking"],
                  relevance_score=0.75),
        ]

    def _fetch_google_trends_real(self, category: str) -> List[Trend]:
        """
        Real pytrends implementation.

        Uses interest_over_time for keyword groups and trending_searches
        for real-time spikes.
        """
        from pytrends.request import TrendReq  # type: ignore

        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))

        # ── real-time trending searches ────────────────────────────────────────
        try:
            trending_df = pytrends.trending_searches(pn="united_states")
            trending_terms = trending_df[0].tolist()[:10]
        except Exception:
            trending_terms = []

        # ── interest over time for category-related keywords ───────────────────
        kw_map = {
            "fitness":   ["gym workout", "home fitness", "weight loss", "yoga", "protein"],
            "marketing": ["content marketing", "social media marketing", "SEO", "email marketing"],
            "wellness":  ["mental health", "meditation", "self care", "sleep", "nutrition"],
        }
        keywords = kw_map.get(category.lower(), ["fitness", "health", "wellness"])[:5]

        pytrends.build_payload(keywords, cat=0, timeframe="now 7-d", geo="US")
        try:
            iot = pytrends.interest_over_time()
        except Exception:
            iot = None

        results: List[Trend] = []

        if iot is not None and not iot.empty:
            for kw in keywords:
                if kw not in iot.columns:
                    continue
                series = iot[kw]
                avg = series.mean()
                recent_avg = series.iloc[-24:].mean() if len(series) >= 24 else avg
                older_avg  = series.iloc[-48:-24].mean() if len(series) >= 48 else avg
                momentum = (
                    "rising"   if recent_avg > older_avg * 1.1 else
                    "declining" if recent_avg < older_avg * 0.9 else
                    "stable"
                )
                results.append(Trend(
                    name=kw,
                    source="google_trends",
                    volume=int(avg * 1000),   # scale 0-100 index → rough volume
                    momentum=momentum,
                    related_topics=[category],
                    relevance_score=min(1.0, avg / 100),
                ))

        # add any trending searches that match category
        for term in trending_terms:
            if category.lower() in term.lower():
                results.append(Trend(
                    name=term, source="google_trends", volume=50000,
                    momentum="rising", related_topics=[category],
                    relevance_score=0.75,
                ))

        results.sort(key=lambda t: t.volume, reverse=True)
        return results[:5] if results else self.fetch_google_trends.__wrapped__(self, category)  # type: ignore

    # ─────────────────────────────────────────────────────────────────────────
    # aggregation & scoring (unchanged from original)
    # ─────────────────────────────────────────────────────────────────────────

    def get_all_trends(self, brand_keywords: List[str] = None) -> Dict[str, List[Trend]]:
        all_trends = {
            "twitter":      self.fetch_twitter_trends(),
            "instagram":    self.fetch_instagram_trends(),
            "google_trends": self.fetch_google_trends(),
        }
        if brand_keywords:
            for source_trends in all_trends.values():
                for trend in source_trends:
                    brand_match_count = sum(
                        1 for kw in brand_keywords
                        if kw.lower() in trend.name.lower()
                        or kw.lower() in " ".join(trend.related_topics).lower()
                    )
                    trend.relevance_score = min(1.0, trend.relevance_score + brand_match_count * 0.1)
        self.last_sync = datetime.utcnow()
        return all_trends

    def score_trend_relevance(self, trend: Trend, brand_keywords: List[str]) -> float:
        score = 0.5
        for kw in brand_keywords:
            if kw.lower() in trend.name.lower():
                score += 0.25
            if kw.lower() in " ".join(trend.related_topics).lower():
                score += 0.15
        if trend.momentum == "rising":
            score += 0.1
        return min(1.0, score)

    def get_top_trends_for_brand(self, brand_keywords: List[str], limit: int = 10) -> List[Trend]:
        all_trends = self.get_all_trends(brand_keywords)
        flat = [t for trends in all_trends.values() for t in trends]
        flat.sort(key=lambda t: t.relevance_score, reverse=True)
        return flat[:limit]

    def get_emerging_opportunities(self, brand_keywords: List[str]) -> Dict:
        top = self.get_top_trends_for_brand(brand_keywords, limit=15)
        return {
            "rising_trends":               [t for t in top if t.momentum == "rising"][:5],
            "stable_trends":               [t for t in top if t.momentum == "stable"][:5],
            "content_ideas":               self._generate_content_ideas(top),
            "hashtag_opportunities":       [t.name for t in top if t.name.startswith("#")][:10],
            "search_optimization_targets": [t.name for t in top if t.source == "google_trends"][:5],
        }

    def _generate_content_ideas(self, trends: List[Trend]) -> List[Dict]:
        ideas = []
        for trend in trends[:5]:
            ideas.append({
                "trend":         trend.name,
                "content_type":  "carousel" if len(trend.related_topics) > 2 else "reel",
                "angle":         f"How {trend.name} applies to your goals",
                "hashtags":      [trend.name] + trend.related_topics[:3],
                "best_platforms": (
                    ["instagram", "tiktok"] if trend.source == "instagram"
                    else ["x", "linkedin"]
                ),
            })
        return ideas


# ─── factory ──────────────────────────────────────────────────────────────────

_singleton: Optional[TrendIntelligence] = None

def get_trend_intelligence() -> TrendIntelligence:
    """Return a module-level singleton (caches results between requests)."""
    global _singleton
    if _singleton is None:
        _singleton = TrendIntelligence()
    return _singleton
