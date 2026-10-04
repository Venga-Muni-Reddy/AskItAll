import pytest
import uuid
import httpx

BASE_URL = "http://localhost:8000/api/v1"


def random_email():
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


@pytest.mark.asyncio
async def test_full_auth_and_multi_tenancy_lifecycle():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Register User 1 with an Organization
        email1 = random_email()
        password = "SecurePassword123!"
        reg_payload = {
            "email": email1,
            "password": password,
            "display_name": "Test Owner",
            "organization_name": "Acme Global Tech",
        }
        res = await client.post("/auth/register", json=reg_payload)
        assert res.status_code == 201, res.text
        data1 = res.json()
        assert "access_token" in data1
        assert "refresh_token" in data1
        token1 = data1["access_token"]
        user1 = data1["user"]
        assert user1["email"] == email1

        headers1 = {"Authorization": f"Bearer {token1}"}

        # 2. Verify duplicate registration fails
        res_dup = await client.post("/auth/register", json=reg_payload)
        assert res_dup.status_code == 409

        # 3. Test Login
        login_res = await client.post("/auth/login", json={"email": email1, "password": password})
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

        # 4. Test /auth/me returns organization and default workspace
        me_res = await client.get("/auth/me", headers=headers1)
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["user"]["email"] == email1
        assert len(me_data["organizations"]) >= 1
        org_id = me_data["organizations"][0]["organization_id"]
        assert me_data["organizations"][0]["role"] == "owner"
        assert len(me_data["workspaces"]) >= 1
        workspace_id = me_data["workspaces"][0]["workspace_id"]
        assert me_data["workspaces"][0]["role"] == "admin"

        # 5. Register User 2 (different tenant)
        email2 = random_email()
        res2 = await client.post("/auth/register", json={
            "email": email2,
            "password": password,
            "display_name": "Test Member",
            "organization_name": "Beta Labs",
        })
        assert res2.status_code == 201
        token2 = res2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # 6. Verify Tenant Isolation: User 2 CANNOT access User 1's Workspace
        unauth_ws = await client.get(f"/workspaces/{workspace_id}", headers=headers2)
        assert unauth_ws.status_code in [403, 404]

        # 7. Add User 2 to User 1's Workspace as member
        add_member_res = await client.post(
            f"/workspaces/{workspace_id}/members",
            headers=headers1,
            json={"email": email2, "role": "member"},
        )
        assert add_member_res.status_code == 201
        assert add_member_res.json()["role"] == "member"

        # 8. User 2 can now view User 1's Workspace
        auth_ws = await client.get(f"/workspaces/{workspace_id}", headers=headers2)
        assert auth_ws.status_code == 200
        assert auth_ws.json()["id"] == workspace_id
        assert auth_ws.json()["user_role"] == "member"

        # 9. Verify User 2 (member) CANNOT delete or update workspace (Requires admin)
        update_ws = await client.patch(
            f"/workspaces/{workspace_id}",
            headers=headers2,
            json={"name": "Hacked Workspace"},
        )
        assert update_ws.status_code == 403

        # 10. Owner User 1 updates workspace successfully
        update_ws_owner = await client.patch(
            f"/workspaces/{workspace_id}",
            headers=headers1,
            json={"name": "Acme Engineering Hub"},
        )
        assert update_ws_owner.status_code == 200
        assert update_ws_owner.json()["name"] == "Acme Engineering Hub"

        # 11. Test Password Change
        new_pw = "BrandNewPassword456!"
        pw_res = await client.post(
            "/auth/change-password",
            headers=headers1,
            json={"current_password": password, "new_password": new_pw},
        )
        assert pw_res.status_code == 200

        # Login with new password works
        new_login = await client.post("/auth/login", json={"email": email1, "password": new_pw})
        assert new_login.status_code == 200

        # Old password rejected
        old_login = await client.post("/auth/login", json={"email": email1, "password": password})
        assert old_login.status_code == 401

        # 12. Test Token Refresh
        ref_res = await client.post("/auth/refresh", json={"refresh_token": data1["refresh_token"]})
        assert ref_res.status_code == 200
        assert "access_token" in ref_res.json()
