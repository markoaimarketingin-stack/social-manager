from __future__ import annotations
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# ===== EXISTING MODELS =====

class ConversationTurn(BaseModel):
    role: Literal["user", "agent"]
    content: str
    ts: Optional[str] = None

class ContentPillar(BaseModel):
    name: str
    goal: str
    post_types: List[str]
    cta_types: List[str]
    weight: float = 1.0

class CalendarEntry(BaseModel):
    date: str
    platform: str
    pillar: str
    format: str
    hook: str
    caption_outline: str
    cta: str
    category: Literal["value", "engagement", "social_proof", "promotional"]

class Suggestion(BaseModel):
    title: str
    description: str
    why_it_matters: str
    action_id: str

class EngagementPlan(BaseModel):
    comment_response: str
    dm_script: str
    poll_ideas: List[str]
    weekly_live: str
    qa_topics: List[str]
    gamification: List[str]

class UGCStrategy(BaseModel):
    theme: str
    hashtag: str
    incentive: str
    submission_method: str
    repurposing_plan: List[str]

class InfluencerStrategy(BaseModel):
    micro_vs_macro: str
    outreach_template: str
    collab_ideas: List[str]
    giveaway_strategy: str
    affiliate_model: str

class LoyaltyStrategy(BaseModel):
    vip_group: str
    referral_incentives: str
    exclusive_content: List[str]
    early_access: str
    badge_system: str

class PlatformStrategy(BaseModel):
    platform: str
    post_format_mix: Dict[str, int]
    frequency_per_week: int
    tone_variation: str
    reel_vs_carousel_ratio: Optional[str] = None
    story_cadence: Optional[str] = None

class EngagementMetrics(BaseModel):
    engagement_rate: Optional[float] = None
    follower_growth: Optional[int] = None
    post_consistency_score: Optional[float] = None

# ===== NEW MODELS FOR POSTS & CAMPAIGNS =====

class Asset(BaseModel):
    """Media asset reference."""
    id: Optional[int] = None
    file_type: str  # image, video, document
    url: str
    alt_text: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)

class PostVariant(BaseModel):
    """A/B test variant of a post."""
    variant_id: str  # A, B, C, etc.
    content: str
    asset_ids: List[int] = Field(default_factory=list)
    copy_tone: Optional[str] = None

class Post(BaseModel):
    """Individual social post."""
    id: Optional[int] = None
    campaign_id: Optional[int] = None
    platform: str  # instagram, linkedin, x, youtube
    content: str
    variants: List[PostVariant] = Field(default_factory=list)
    status: Literal["draft", "approved", "scheduled", "published", "failed"] = "draft"
    approval_status: Literal["pending", "approved", "rejected"] = "pending"
    approved_by: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class PublishingJob(BaseModel):
    """Async publishing task."""
    id: Optional[int] = None
    post_id: int
    platform_post_id: Optional[str] = None
    status: Literal["pending", "in_progress", "published", "failed"] = "pending"
    attempt_count: int = 0
    max_attempts: int = 3
    error_message: Optional[str] = None
    idempotency_key: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class MetricSnapshot(BaseModel):
    """Metric data from a platform."""
    id: Optional[int] = None
    post_id: int
    platform: str
    platform_post_id: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    impressions: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    snapshot_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Conversation(BaseModel):
    """Community inbox entry."""
    id: Optional[int] = None
    platform: str
    author_handle: str
    author_id: Optional[str] = None
    content: str
    conversation_type: Literal["mention", "dm", "comment", "reply"]
    parent_post_id: Optional[str] = None
    status: Literal["new", "triaged", "responded", "archived"] = "new"
    assigned_to: Optional[str] = None
    response: Optional[str] = None
    response_sent_at: Optional[datetime] = None
    ingested_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ConsentRecord(BaseModel):
    """GDPR/compliance consent tracking."""
    id: Optional[int] = None
    campaign_id: Optional[int] = None
    entity_type: str  # influencer, ugc_participant, audience_segment
    entity_id: str
    consent_given: bool = False
    given_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    policy_version: str
    channel: str  # email, in_app, verbal
    notes: Optional[str] = None

class Influencer(BaseModel):
    """Influencer collaboration entity."""
    id: Optional[int] = None
    platform: str
    handle: str
    name: Optional[str] = None
    tier: str  # nano, micro, macro, mega
    follower_count: int = 0
    engagement_rate: float = 0.0
    niche: Optional[str] = None
    contact_email: Optional[str] = None
    consent_status: Literal["unknown", "agreed", "declined"] = "unknown"
    collaboration_history: List[str] = Field(default_factory=list)
    last_contacted: Optional[datetime] = None

class Campaign(BaseModel):
    """Master campaign entity."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    status: Literal["draft", "active", "paused", "completed"] = "draft"
    objectives: Dict[str, float] = Field(default_factory=dict)  # engagement, reach, etc.
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    posts: List[Post] = Field(default_factory=list)
    consent_records: List[ConsentRecord] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

# ===== MAIN STATE OBJECT =====

class SocialManagerState(BaseModel):
    # Strategy & onboarding
    structured_context: Dict = Field(default_factory=dict)
    brand_profile: Dict = Field(default_factory=dict)
    target_persona: Dict = Field(default_factory=dict)
    active_platforms: List[str] = Field(default_factory=list)
    posting_frequency: Dict[str, int] = Field(default_factory=dict)
    engagement_metrics: EngagementMetrics = Field(default_factory=EngagementMetrics)
    
    # Content & strategy
    content_pillars: List[ContentPillar] = Field(default_factory=list)
    monthly_calendar: List[CalendarEntry] = Field(default_factory=list)
    ugc_strategy: Optional[UGCStrategy] = None
    influencer_strategy: Optional[InfluencerStrategy] = None
    engagement_plan: Optional[EngagementPlan] = None
    loyalty_strategy: Optional[LoyaltyStrategy] = None
    suggestions_list: List[Suggestion] = Field(default_factory=list)
    conversation_history: List[ConversationTurn] = Field(default_factory=list)
    platform_strategies: Dict[str, PlatformStrategy] = Field(default_factory=dict)
    
    # Publishing & campaigns
    active_campaign: Optional[Campaign] = None
    campaigns: List[Campaign] = Field(default_factory=list)
    posts: List[Post] = Field(default_factory=list)
    assets: List[Asset] = Field(default_factory=list)
    publishing_jobs: List[PublishingJob] = Field(default_factory=list)
    
    # Community & metrics
    conversations: List[Conversation] = Field(default_factory=list)
    metric_snapshots: List[MetricSnapshot] = Field(default_factory=list)
    influencers: List[Influencer] = Field(default_factory=list)
    
    # Compliance
    consent_records: List[ConsentRecord] = Field(default_factory=list)

    def is_onboarding_complete(self) -> bool:
        required = [bool(self.brand_profile), bool(self.target_persona)]
        return all(required)

    def has_platforms(self) -> bool:
        return len(self.active_platforms) > 0
    
    def get_pending_approvals(self) -> List[Post]:
        """Get posts awaiting approval."""
        return [p for p in self.posts if p.approval_status == "pending"]
    
    def get_scheduled_posts(self) -> List[Post]:
        """Get posts scheduled for publishing."""
        return [p for p in self.posts if p.status == "scheduled"]
