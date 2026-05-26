"""
Seed Script to populate the database with dummy historical data
for the "Sustainable Fashion" brand. This helps with testing the 
Analytics Dashboard and Publishing Queue.
"""
import random
from datetime import datetime, timedelta
from social_manager.db import (
    SessionLocal, Campaign, Post, MetricSnapshot, 
    Conversation, init_db
)

def seed_database():
    session = SessionLocal()
    
    # Check if we already seeded
    if session.query(Campaign).filter_by(name="Summer Sustainable Launch").first():
        print("Database already seeded.")
        session.close()
        return

    print("Seeding dummy data...")
    
    # 1. Create a Campaign
    campaign = Campaign(
        name="Summer Sustainable Launch",
        description="Launch of the new organic summer collection.",
        status="active",
        objectives={"engagement": 0.5, "reach": 0.5},
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    session.add(campaign)
    session.commit()

    # 2. Create Historical Posts & Metrics
    platforms = ["instagram", "linkedin", "x"]
    copy_variants = ["A", "B", "C"]
    
    for i in range(15):
        days_ago = random.randint(1, 28)
        created = datetime.utcnow() - timedelta(days=days_ago)
        
        platform = random.choice(platforms)
        
        post = Post(
            campaign_id=campaign.id,
            platform=platform,
            content=f"Looking for sustainable options? 🌿 Check out our new organic cotton basics! Perfect for #Summer. #{platform} #sustainable",
            copy_variant=random.choice(copy_variants),
            status="published",
            created_at=created,
            published_at=created + timedelta(hours=2)
        )
        session.add(post)
        session.commit()
        
        # Add Metrics
        base_likes = random.randint(50, 500)
        snapshot = MetricSnapshot(
            post_id=post.id,
            platform=platform,
            likes=base_likes,
            comments=int(base_likes * 0.1),
            shares=int(base_likes * 0.05),
            impressions=base_likes * 10,
            engagement_rate=round(random.uniform(2.0, 8.5), 2),
            snapshot_at=datetime.utcnow()
        )
        session.add(snapshot)

    # 3. Create Community Inbox Conversations
    for i in range(5):
        days_ago = random.randint(1, 5)
        conv = Conversation(
            platform="instagram",
            author_handle=f"@eco_user_{i}",
            content=f"Do you ship internationally? I love the new shirts! 💚",
            conversation_type="comment",
            status="new",
            ingested_at=datetime.utcnow() - timedelta(days=days_ago)
        )
        session.add(conv)

    session.commit()
    session.close()
    print("Seeding complete!")

if __name__ == "__main__":
    init_db()
    seed_database()
