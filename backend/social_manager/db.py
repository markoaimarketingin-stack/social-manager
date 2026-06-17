"""
Database layer with models, repositories, and initialization.
Supports SQLite (dev) and PostgreSQL (production).
"""

from __future__ import annotations
import random
import string
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, JSON, Float, DateTime, Boolean, ForeignKey, Enum, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from social_manager.config import settings

# Initialize engine and session
DB_URL = settings.social_manager_db_url
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
    pool_recycle=3600,  # PostgreSQL connection timeout handling
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ===== CORE AUTHENTICATION TABLES =====

class User(Base):
    """User account."""
    __tablename__ = "sm_users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    social_connections = relationship("SocialConnection", back_populates="user", cascade="all, delete-orphan")

class SocialConnection(Base):
    """OAuth tokens and connection details per user per platform."""
    __tablename__ = "social_connections"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("sm_users.id"), index=True)
    user = relationship("User", back_populates="social_connections")
    
    platform = Column(String, index=True)  # facebook, instagram, linkedin, x, youtube
    platform_account_id = Column(String, nullable=True)  # e.g., Page ID, IG User ID
    platform_account_name = Column(String, nullable=True)
    
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    access_token_secret = Column(String, nullable=True)  # For X OAuth 1.0a
    
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ===== EXISTING TABLES (REFACTORED) =====

class SocialContentCalendar(Base):
    __tablename__ = "social_content_calendar"
    id = Column(Integer, primary_key=True)
    date = Column(String, index=True)
    platform = Column(String, index=True)
    pillar = Column(String)
    format = Column(String)
    hook = Column(Text)
    caption_outline = Column(Text)
    cta = Column(String)
    category = Column(String)

class ContentPillar(Base):
    __tablename__ = "content_pillars"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    goal = Column(Text)
    post_types = Column(JSON)
    cta_types = Column(JSON)
    weight = Column(Float)

class EngagementLog(Base):
    __tablename__ = "engagement_logs"
    id = Column(Integer, primary_key=True)
    ts = Column(String, index=True)
    platform = Column(String)
    action = Column(String)
    meta = Column(JSON)

class InfluencerCollab(Base):
    __tablename__ = "influencer_collaborations"
    id = Column(Integer, primary_key=True)
    influencer_handle = Column(String)
    tier = Column(String)
    outreach = Column(Text)
    collab_ideas = Column(JSON)
    giveaway = Column(Text)
    affiliate = Column(Text)

class UGCCampaign(Base):
    __tablename__ = "ugc_campaigns"
    id = Column(Integer, primary_key=True)
    theme = Column(String)
    hashtag = Column(String)
    incentive = Column(String)
    submission_method = Column(String)
    repurposing_plan = Column(JSON)

class LoyaltyProgram(Base):
    __tablename__ = "loyalty_programs"
    id = Column(Integer, primary_key=True)
    vip_group = Column(String)
    referral_incentives = Column(String)
    exclusive_content = Column(JSON)
    early_access = Column(String)
    badge_system = Column(String)

class SocialStrategyLog(Base):
    __tablename__ = "social_strategy_logs"
    id = Column(Integer, primary_key=True)
    ts = Column(String, index=True)
    event = Column(String)
    details = Column(Text)

# ===== NEW CORE TABLES =====

class Campaign(Base):
    """Master campaign entity."""
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default="draft")  # draft, active, paused, completed
    objectives = Column(JSON)  # {"engagement": 0.5, "reach": 0.3, ...}
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    posts = relationship("Post", back_populates="campaign", cascade="all, delete-orphan")
    consent_records = relationship("ConsentRecord", back_populates="campaign")

class Asset(Base):
    """Media asset (image, video, etc.)."""
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)
    file_type = Column(String)  # image, video, document
    url = Column(String)
    alt_text = Column(Text)
    asset_metadata = Column(JSON)  # dimensions, duration, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    """Individual social post."""
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)
    campaign = relationship("Campaign", back_populates="posts")
    platform = Column(String, index=True)  # instagram, linkedin, x, youtube
    content = Column(Text)
    copy_variant = Column(String)  # A, B, C for experiments
    asset_ids = Column(JSON)  # [1, 2, 3]
    status = Column(String, default="draft")  # draft, approved, scheduled, published
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime)
    published_at = Column(DateTime)
    approval_status = Column(String)  # pending, approved, rejected
    approved_by = Column(String)  # user ID
    publishing_jobs = relationship("PublishingJob", back_populates="post")

class PublishingJob(Base):
    """Async task for publishing."""
    __tablename__ = "publishing_jobs"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    platform = Column(String, index=True)
    post = relationship("Post", back_populates="publishing_jobs")
    platform_post_id = Column(String)  # Remote platform ID
    status = Column(String, default="pending")  # pending, in_progress, published, failed
    attempt_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    error_message = Column(Text)
    idempotency_key = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MetricSnapshot(Base):
    """Periodic metric ingestion from platforms."""
    __tablename__ = "metric_snapshots"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    platform = Column(String, index=True)
    platform_post_id = Column(String)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    snapshot_at = Column(DateTime, default=datetime.utcnow, index=True)

class Conversation(Base):
    """Community inbox: mentions, DMs, comments."""
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    platform = Column(String, index=True)
    author_handle = Column(String, index=True)
    author_id = Column(String)
    content = Column(Text)
    conversation_type = Column(String)  # mention, dm, comment, reply
    parent_post_id = Column(String)  # Platform-specific post ID
    status = Column(String, default="new")  # new, triaged, responded, archived
    assigned_to = Column(String)  # User ID
    response = Column(Text)
    response_sent_at = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow, index=True)
    extra_metadata = Column(JSON)

class Influencer(Base):
    """Influencer profile for collaboration tracking."""
    __tablename__ = "influencers"
    id = Column(Integer, primary_key=True)
    platform = Column(String, index=True)
    handle = Column(String, index=True)
    name = Column(String)
    tier = Column(String)  # nano, micro, macro, mega
    follower_count = Column(Integer)
    engagement_rate = Column(Float)
    niche = Column(String)
    contact_email = Column(String)
    outreach_template = Column(Text)
    collaboration_history = Column(JSON)
    consent_status = Column(String, default="unknown")  # unknown, agreed, declined
    last_contacted = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConsentRecord(Base):
    """GDPR/compliance: consent tracking."""
    __tablename__ = "consent_records"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)
    campaign = relationship("Campaign", back_populates="consent_records")
    entity_type = Column(String)  # influencer, ugc_participant, audience_segment
    entity_id = Column(String, index=True)
    consent_given = Column(Boolean, default=False)
    given_at = Column(DateTime)
    expires_at = Column(DateTime)
    policy_version = Column(String)
    channel = Column(String)  # email, in_app, verbal
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== REPOSITORY PATTERN =====

class BaseRepository:
    """Base repository with CRUD operations."""
    
    def __init__(self, session, model):
        self.session = session
        self.model = model
    
    def create(self, **kwargs):
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        return obj
    
    def get_by_id(self, obj_id):
        return self.session.query(self.model).filter(self.model.id == obj_id).first()
    
    def get_all(self):
        return self.session.query(self.model).all()
    
    def update(self, obj_id, **kwargs):
        obj = self.get_by_id(obj_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.session.commit()
        return obj
    
    def delete(self, obj_id):
        obj = self.get_by_id(obj_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj


class UserRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, User)
        
    def get_by_email(self, email: str):
        return self.session.query(User).filter(User.email == email).first()

class SocialConnectionRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, SocialConnection)
        
    def get_user_connections(self, user_id: int):
        return self.session.query(SocialConnection).filter(SocialConnection.user_id == user_id).all()
        
    def get_user_connection(self, user_id: int, platform: str):
        return self.session.query(SocialConnection).filter(
            SocialConnection.user_id == user_id,
            SocialConnection.platform == platform
        ).first()

class CampaignRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Campaign)
    
    def get_active(self):
        return self.session.query(Campaign).filter(Campaign.status.in_(["draft", "active"])).all()


class PostRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Post)
    
    def get_by_platform(self, platform):
        return self.session.query(Post).filter(Post.platform == platform).all()
    
    def get_pending_approval(self):
        return self.session.query(Post).filter(Post.approval_status == "pending").all()
    
    def get_scheduled(self):
        return self.session.query(Post).filter(Post.status == "scheduled").all()


class PublishingJobRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, PublishingJob)
    
    def get_pending(self):
        return self.session.query(PublishingJob).filter(PublishingJob.status == "pending").all()
    
    def get_failed(self):
        return self.session.query(PublishingJob).filter(PublishingJob.status == "failed").all()


class ConversationRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Conversation)
    
    def get_new_conversations(self):
        return self.session.query(Conversation).filter(Conversation.status == "new").all()
    
    def get_by_platform(self, platform):
        return self.session.query(Conversation).filter(Conversation.platform == platform).all()


class SocialStrategyLogRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, SocialStrategyLog)
        
    def log_event(self, event: str, details: str) -> SocialStrategyLog:
        return self.create(
            ts=datetime.utcnow().isoformat(),
            event=event,
            details=details
        )


def init_db(seed: int = 42):
    """
    Initialize database with deterministic seed for reproducibility.
    Creates all tables and seeds default data if needed.
    """
    random.seed(seed)
    dialect = engine.dialect.name
    is_postgres = dialect in {"postgresql", "postgres"}

    if is_postgres:
        # On PostgreSQL (Render) all tables already exist — skip create_all.
        # create_all calls has_table() for every model which fires pg_class queries
        # that get killed by Render's role-level statement_timeout, crashing startup.
        print("[OK] PostgreSQL detected — skipping create_all (tables already exist)")
    else:
        # SQLite (local dev) — create tables as normal.
        try:
            Base.metadata.create_all(bind=engine)
            print("[OK] create_all completed")
        except Exception as e:
            print(f"[WARN] create_all skipped: {e}")

    # Schema repair: no-op on PostgreSQL (returns immediately), runs for SQLite.
    _repair_existing_schema()
    print(f"[OK] Database initialized with seed={seed}")


def _repair_existing_schema():
    """Add missing columns to pre-existing databases (dev/SQLite only).

    On PostgreSQL (Render production) this function is a deliberate NO-OP.
    The live database schema is already fully up-to-date, so there is nothing
    to repair. Skipping this avoids ALL pg_catalog introspection queries which
    were being killed by Render's role-level statement_timeout.
    """
    dialect = engine.dialect.name
    is_postgres = dialect in {"postgresql", "postgres"}

    if is_postgres:
        # Production DB schema is already correct — nothing to do.
        print("[OK] _repair_existing_schema: PostgreSQL detected, skipping (schema already up-to-date)")
        return

    # ---- SQLite (local dev) only ----
    datetime_type = "DATETIME"
    repairs = {
        "posts": {
            "user_id": "INTEGER",
            "campaign_id": "INTEGER",
            "platform": "VARCHAR",
            "content": "TEXT",
            "copy_variant": "VARCHAR",
            "asset_ids": "TEXT",
            "status": "VARCHAR",
            "created_at": datetime_type,
            "scheduled_at": datetime_type,
            "published_at": datetime_type,
            "approval_status": "VARCHAR",
            "approved_by": "VARCHAR",
        },
        "publishing_jobs": {
            "post_id": "INTEGER",
            "platform": "VARCHAR",
            "platform_post_id": "VARCHAR",
            "status": "VARCHAR",
            "attempt_count": "INTEGER",
            "max_attempts": "INTEGER",
            "error_message": "TEXT",
            "idempotency_key": "VARCHAR",
            "created_at": datetime_type,
            "updated_at": datetime_type,
        },
    }
    with engine.begin() as connection:
        inspector = inspect(engine)
        for table_name, columns in repairs.items():
            if not inspector.has_table(table_name):
                continue
            present = {col["name"] for col in inspector.get_columns(table_name)}
            for column_name, column_type in columns.items():
                if column_name in present:
                    continue
                try:
                    connection.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                    )
                    print(f"[OK] Added column {table_name}.{column_name}")
                except Exception as e:
                    print(f"[WARN] Could not add {table_name}.{column_name}: {e}")



