"""
Email Integration using SendGrid for campaign notifications and digest emails.
"""

import os
import logging
from typing import List, Optional, Dict
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class SendGridEmailService:
    """Send emails using SendGrid API."""
    
    def __init__(self):
        """Initialize SendGrid service."""
        self.api_key = os.getenv("SENDGRID_API_KEY", "")
        self.from_email = os.getenv("EMAIL_FROM", "noreply@socialmanager.ai")
        self.base_url = "https://api.sendgrid.com/v3/mail/send"
        self.session = None
        
    async def initialize(self):
        """Initialize async session."""
        self.session = aiohttp.ClientSession()
        
    async def close(self):
        """Close async session."""
        if self.session:
            await self.session.close()
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> Dict:
        """Send a single email."""
        
        if not self.api_key:
            return self._log_demo_email(to_email, subject)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject
                    }
                ],
                "from": {"email": self.from_email},
                "content": [
                    {
                        "type": "text/html",
                        "value": html_content
                    }
                ]
            }
            
            if plain_text:
                payload["content"].insert(0, {
                    "type": "text/plain",
                    "value": plain_text
                })
            
            if reply_to:
                payload["reply_to"] = {"email": reply_to}
            
            async with self.session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status in [200, 202]:
                    return {
                        "success": True,
                        "to_email": to_email,
                        "subject": subject,
                        "sent_at": datetime.utcnow().isoformat(),
                        "message_id": resp.headers.get("X-Message-Id", "")
                    }
                else:
                    error_text = await resp.text()
                    logger.error(f"SendGrid error ({resp.status}): {error_text}")
                    return {"success": False, "error": error_text}
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"success": False, "error": str(e)}
    
    def _log_demo_email(self, to_email: str, subject: str) -> Dict:
        """Log email that would be sent (demo mode)."""
        logger.info(f"[DEMO EMAIL] To: {to_email}, Subject: {subject}")
        return {
            "success": True,
            "demo": True,
            "to_email": to_email,
            "subject": subject,
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def send_bulk_emails(
        self,
        recipients: List[Dict],  # [{"email": "...", "name": "..."}, ...]
        subject: str,
        html_template: str,
        template_vars: Optional[Dict] = None
    ) -> Dict:
        """Send emails to multiple recipients."""
        results = {"sent": 0, "failed": 0, "errors": []}
        
        for recipient in recipients:
            email = recipient.get("email")
            name = recipient.get("name", email.split("@")[0])
            
            # Personalize template
            personalized_html = html_template.replace("{{NAME}}", name)
            personalized_subject = subject.replace("{{NAME}}", name)
            
            if template_vars:
                for key, value in template_vars.items():
                    personalized_html = personalized_html.replace(f"{{{{{key}}}}}", str(value))
                    personalized_subject = personalized_subject.replace(f"{{{{{key}}}}}", str(value))
            
            result = await self.send_email(email, personalized_subject, personalized_html)
            
            if result.get("success"):
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"{email}: {result.get('error', 'Unknown error')}")
        
        return results
    
    async def send_campaign_digest(
        self,
        email: str,
        campaign_name: str,
        metrics: Dict,
        posts: List[Dict]
    ) -> Dict:
        """Send a campaign performance digest email."""
        
        posts_html = "\n".join([
            f"<li><strong>{p.get('title', 'Untitled')}</strong> - "
            f"Engagement: {p.get('engagement_rate', 0):.1f}%, "
            f"Reach: {p.get('reach', 0):,}</li>"
            for p in posts
        ])
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Campaign Digest: {campaign_name}</h2>
                
                <h3>Performance Metrics</h3>
                <ul>
                    <li>Total Reach: {metrics.get('total_reach', 0):,}</li>
                    <li>Total Engagement: {metrics.get('total_engagement', 0):,}</li>
                    <li>Average Engagement Rate: {metrics.get('avg_engagement_rate', 0):.1f}%</li>
                    <li>Follower Growth: +{metrics.get('follower_growth', 0):,}</li>
                </ul>
                
                <h3>Top Performing Posts</h3>
                <ol>{posts_html}</ol>
                
                <p>View more details in your Social Manager dashboard.</p>
            </body>
        </html>
        """
        
        return await self.send_email(
            email,
            f"Campaign Digest: {campaign_name}",
            html_content
        )
    
    async def send_approval_notification(
        self,
        email: str,
        post_title: str,
        post_id: int,
        platform: str,
        approval_url: str
    ) -> Dict:
        """Notify approver of pending content."""
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Content Approval Needed</h2>
                
                <p>A new post is waiting for your approval:</p>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 5px;">
                    <p><strong>Title:</strong> {post_title}</p>
                    <p><strong>Platform:</strong> {platform}</p>
                    <p><strong>Post ID:</strong> {post_id}</p>
                </div>
                
                <p>
                    <a href="{approval_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Review & Approve
                    </a>
                </p>
            </body>
        </html>
        """
        
        return await self.send_email(
            email,
            f"Approval Needed: {post_title}",
            html_content
        )


# Singleton instance
_email_service = None


def get_email_service() -> SendGridEmailService:
    """Get or create email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = SendGridEmailService()
    return _email_service
