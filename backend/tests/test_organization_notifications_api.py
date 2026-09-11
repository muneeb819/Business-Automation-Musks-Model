import pytest
from sqlalchemy import select

from app.models.organization import Membership
from app.models.notification import Notification, NotificationType


class TestNotificationsAPI:
    @pytest.mark.asyncio
    async def test_list_notifications_empty(self, auth_client):
        resp = await auth_client.get("/api/v1/notifications")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "notifications" in data
        assert "unread" in data
        assert "total" in data
        assert data["total"] == 0
        assert data["unread"] == 0

    @pytest.mark.asyncio
    async def test_mark_single_notification_read(self, test_db, auth_client):
        async with test_db() as session:
            membership = (
                await session.execute(select(Membership).limit(1))
            ).scalars().first()
            assert membership is not None

            notification = Notification(
                organization_id=membership.organization_id,
                type=NotificationType.SYSTEM_ISSUE,
                title="Test notification",
                message="Something happened",
            )
            session.add(notification)
            await session.commit()
            notification_id = str(notification.id)

        resp = await auth_client.get("/api/v1/notifications")
        assert resp.json()["unread"] == 1

        resp = await auth_client.post(f"/api/v1/notifications/{notification_id}/read")
        assert resp.status_code == 200, resp.text
        assert resp.json()["notification_id"] == notification_id

        resp = await auth_client.get("/api/v1/notifications")
        assert resp.json()["unread"] == 0

    @pytest.mark.asyncio
    async def test_mark_all_notifications_read(self, test_db, auth_client):
        async with test_db() as session:
            membership = (
                await session.execute(select(Membership).limit(1))
            ).scalars().first()

            session.add_all([
                Notification(
                    organization_id=membership.organization_id,
                    type=NotificationType.SYSTEM_ISSUE,
                    title="A",
                    message="a",
                ),
                Notification(
                    organization_id=membership.organization_id,
                    type=NotificationType.SYSTEM_ISSUE,
                    title="B",
                    message="b",
                ),
            ])
            await session.commit()

        resp = await auth_client.post("/api/v1/notifications/read-all")
        assert resp.status_code == 200, resp.text
        assert resp.json()["updated"] == 2

        resp = await auth_client.get("/api/v1/notifications")
        assert resp.json()["unread"] == 0


class TestOrganizationAPI:
    @pytest.mark.asyncio
    async def test_get_organization(self, auth_client):
        resp = await auth_client.get("/api/v1/organization")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["name"]
        assert data["slug"]
        assert isinstance(data["members"], list)
        assert len(data["members"]) >= 1
        member = data["members"][0]
        assert member["email"]
        assert member["role"]
