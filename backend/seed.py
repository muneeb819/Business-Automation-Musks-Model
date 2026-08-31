import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_session_factory, init_db
from app.models.user import User
from app.models.organization import Organization, Membership
from app.models.agent import Agent, AgentType
from app.core.security import get_password_hash
import uuid


async def seed_default_agents(org_id, db):
    default_agents = [
        ("Lead Hunter", AgentType.HUNTING, "Discovers leads across platforms"),
        ("Enrichment Agent", AgentType.ENRICHMENT, "Enriches and verifies leads"),
        ("Outreach Agent", AgentType.OUTREACH, "Sends personalized proposals with human handoff"),
        ("Supervisor Agent", AgentType.SUPERVISOR, "Control tower - monitors all operations"),
        ("Optimization Agent", AgentType.OPTIMIZATION, "Identifies improvement opportunities"),
        ("Content Agent", AgentType.CONTENT, "Creates marketing content"),
        ("SEO Agent", AgentType.SEO, "Optimizes search visibility"),
        ("Paid Traffic Agent", AgentType.PAID_TRAFFIC, "Manages paid campaigns"),
        ("Social Media Agent", AgentType.SOCIAL_MEDIA, "Manages social presence"),
        ("Engagement Agent", AgentType.ENGAGEMENT, "Monitors engagement"),
        ("Marketplace Agent", AgentType.MARKETPLACE, "Detects buyer/renter demand"),
    ]

    for name, atype, desc in default_agents:
        agent = Agent(
            organization_id=org_id,
            name=name,
            agent_type=atype,
            description=desc,
            status="idle",
        )
        db.add(agent)


async def main():
    await init_db()

    async with async_session_factory() as db:
        email = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("SEED_ADMIN_PASSWORD", "AdminPassword123!")

        from sqlalchemy import select
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            print(f"Admin user {email} already exists. Skipping.")
            return

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Platform Admin",
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        await db.flush()

        org = Organization(
            name="Default Organization",
            slug="default-org",
            description="Default seeded organization",
        )
        db.add(org)
        await db.flush()

        permissions = [
            "leads.read", "leads.write", "leads.delete",
            "companies.read", "companies.write", "companies.delete",
            "contacts.read", "contacts.write", "contacts.delete",
            "campaigns.read", "campaigns.write", "campaigns.delete",
            "agents.read", "agents.write", "agents.delete",
            "approvals.read", "approvals.write", "approvals.approve",
            "settings.read", "settings.write",
            "audit.read",
            "users.read", "users.write",
        ]

        membership = Membership(
            user_id=user.id,
            organization_id=org.id,
            role="owner",
            permissions=permissions,
        )
        db.add(membership)

        await seed_default_agents(org.id, db)

        await db.commit()
        print(f"Seeded admin user: {email}")
        print(f"Seeded organization: {org.name}")
        print(f"Seeded {len([
            'Lead Hunter','Enrichment Agent','Outreach Agent','Supervisor Agent',
            'Optimization Agent','Content Agent','SEO Agent','Paid Traffic Agent',
            'Social Media Agent','Engagement Agent','Marketplace Agent'])} default agents")


if __name__ == "__main__":
    asyncio.run(main())
