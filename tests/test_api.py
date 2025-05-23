import datetime
import json
from http.client import HTTPException

import pytest
import requests


@pytest.fixture(scope="session", autouse=True)
def api_healthcheck(api_url):
    response = requests.get(f"{api_url}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def login_user(api_url: str, email: str, password: str) -> str:
    """Logs in a user and returns a JWT access token."""
    login_data = {
        "username": email,
        "password": password,
    }

    resp = requests.post(f"{api_url}/auth/login", data=login_data)
    assert resp.status_code == 200, f"Login failed: {resp.text}"

    return resp.json()["access_token"]


def load_data_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.mark.users  # Marker for the whole suite
class TestUsersEndpoints:
    @pytest.mark.parametrize(
        "user_payload",
        [
            {
                "username": "user1",
                "email": "user1@example.com",
                "hashed_password": "pass1",
                "role": "USER",
            },
            {
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": "adminpass",
                "role": "ADMIN",
            },
        ],
    )
    def test_create_user(self, api_url, user_payload):
        response = requests.post(f"{api_url}/users/", json=user_payload)
        assert response.status_code in (200, 201)
        created_user = response.json()

        assert created_user["username"] == user_payload["username"]
        assert created_user["email"] == user_payload["email"]
        assert created_user["role"] == user_payload["role"]
        assert "id" in created_user

    @pytest.mark.parametrize(
        "user_payload",
        [
            {
                "username": "get_me1",
                "email": "get_me1_@example.com",
                "hashed_password": "get_me1_pass",
                "role": "USER",
            },
            {
                "username": "get_me_2",
                "email": "get_me_2@example.com",
                "hashed_password": "get_me_2_pass",
                "role": "ADMIN",
            },
        ],
    )
    def test_get_user(self, api_url, user_payload):
        create_resp = requests.post(f"{api_url}/users/", json=user_payload)
        assert create_resp.status_code in (200, 201), (
            f"Create failed: {create_resp.text}"
        )
        user_id = create_resp.json()["id"]

        # Get JWT
        token = login_user(
            api_url, user_payload["email"], user_payload["hashed_password"]
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Send request with JWT
        get_resp = requests.get(f"{api_url}/users/{user_id}", headers=headers)
        assert get_resp.status_code == 200, f"Get failed: {get_resp.text}"

        fetched_user = get_resp.json()
        assert fetched_user["username"] == user_payload["username"]
        assert fetched_user["email"] == user_payload["email"]
        assert fetched_user["role"] == user_payload["role"]


@pytest.mark.road_networks
class TestRoadNetworksEndpoints:
    @pytest.mark.parametrize(
        "file_path, user_payload",
        [
            (
                "./tests/test_data/York_cycle_network.geojson",
                {
                    "username": "file_upload_user",
                    "email": "file_upload_user@example.com",
                    "hashed_password": "file_upload_user_pass",
                    "role": "USER",
                },
            )
        ],
    )
    def test_upload_road_network_file(self, api_url, file_path, user_payload):
        create_resp = requests.post(f"{api_url}/users/", json=user_payload)
        assert create_resp.status_code in (200, 201), (
            f"Create failed: {create_resp.text}"
        )

        # Get JWT
        token = login_user(
            api_url, user_payload["email"], user_payload["hashed_password"]
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Open and send file
        with open(file_path, "rb") as f:
            files = {"file": ("York_cycle_network.geojson", f, "application/geo+json")}

            upload_resp = requests.post(
                f"{api_url}/networks/upload", files=files, headers=headers
            )

        assert upload_resp.status_code == 201, f"Upload failed: {upload_resp.text}"
        assert upload_resp.json().get("message") == "File Uploaded"

    def test_get_network_file(self, api_url):
        # user the same user to being able to access the file
        token = login_user(
            api_url, "file_upload_user@example.com", "file_upload_user_pass"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # WARNING: IF YOU ADD MORE USERS AND THIS TEST FAILS THE REASON IS HOW MANY USERS YOU CREATED PRIOR
        user_id = 1  # Since we move to this test suite this was the first user created

        user_networks = requests.get(f"{api_url}/users/{1}/networks", headers=headers)

        file_resp = requests.get(f"{api_url}/networks/{1}/edges", headers=headers)

        file = load_data_file("./tests/test_data/York_cycle_network.geojson")
        assert len(file["features"]) == len(file_resp.json()["features"])
        assert len(file["type"]) == len(file_resp.json()["type"])


@pytest.mark.role_based_permissions
class TestPermissions:
    @pytest.fixture(scope="class")
    def created_users(self, api_url):
        users = [
            {
                "username": "delete_user1",
                "email": "delete_user1@example.com",
                "hashed_password": "pass1",
                "role": "USER",
            },
            {
                "username": "delete_admin",
                "email": "delete_admin@example.com",
                "hashed_password": "adminpass",
                "role": "ADMIN",
            },
            {
                "username": "network_user_1",
                "email": "network_user_1@example.com",
                "hashed_password": "pass1",
                "role": "USER",
            },
            {
                "username": "network_user_2",
                "email": "network_user_2@example.com",
                "hashed_password": "pass2",
                "role": "USER",
            },
        ]

        created = {}
        for user_payload in users:
            resp = requests.post(f"{api_url}/users/", json=user_payload)
            assert resp.status_code in (200, 201), (
                f"Failed to create user {user_payload['email']}"
            )
            user_data = resp.json()
            created[user_payload["username"]] = {
                "id": user_data["id"],
                "email": user_payload["email"],
                "password": user_payload["hashed_password"],
            }
        return created

    @pytest.fixture(scope="class")
    def tokens(self, api_url, created_users):
        tokens = {}
        for username, info in created_users.items():
            token = login_user(api_url, info["email"], info["password"])
            tokens[username] = token
        return tokens

    def test_user_cannot_see_other_user(self, api_url, created_users, tokens):
        user_token = tokens["network_user_1"]  # use actual username key here
        headers = {"Authorization": f"Bearer {user_token}"}

        admin_id = created_users["delete_admin"]["id"]  # use actual username key here
        response = requests.get(f"{api_url}/users/{admin_id}", headers=headers)
        assert response.status_code in (401, 403), (
            "USER should not access another user's data"
        )

    def test_admin_can_see_other_users(self, api_url, created_users, tokens):
        admin_token = tokens["delete_admin"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        user_id = created_users["network_user_1"]["id"]
        response = requests.get(f"{api_url}/users/{user_id}", headers=headers)
        assert response.status_code == 200, "ADMIN should access other users' data"
        data = response.json()
        assert data["id"] == user_id

    def test_user_cannot_delete_other_user(self, api_url, created_users, tokens):
        user_token = tokens["network_user_1"]
        headers = {"Authorization": f"Bearer {user_token}"}

        admin_id = created_users["delete_admin"]["id"]
        response = requests.delete(f"{api_url}/users/{admin_id}", headers=headers)
        assert response.status_code in (401, 403), "USER should not delete other users"

    def test_admin_can_delete_user(self, api_url, created_users, tokens):
        admin_token = tokens["delete_admin"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        temp_user_payload = {
            "username": "temp_user_to_delete",
            "email": "tempuser@example.com",
            "hashed_password": "temppass",
            "role": "USER",
        }
        resp = requests.post(f"{api_url}/users/", json=temp_user_payload)
        assert resp.status_code in (200, 201)
        temp_user_id = resp.json()["id"]

        delete_resp = requests.delete(
            f"{api_url}/users/{temp_user_id}", headers=headers
        )
        assert delete_resp.status_code == 200, "ADMIN should delete users"

        get_resp = requests.get(f"{api_url}/users/{temp_user_id}", headers=headers)
        assert get_resp.status_code == 404, "Deleted user should not be found"

    def test_user_cannot_access_or_modify_other_users_network(
        self, api_url, created_users, tokens
    ):
        user1_info = created_users.get("network_user_1")
        user2_info = created_users.get("network_user_2")

        user1_token = tokens.get("network_user_1")
        user2_token = tokens.get("network_user_2")

        headers_user1 = {"Authorization": f"Bearer {user1_token}"}
        headers_user2 = {"Authorization": f"Bearer {user2_token}"}

        # User 1 uploads a network (must succeed)
        with open("./tests/test_data/York_cycle_network.geojson", "rb") as f:
            files = {"file": ("York_cycle_network.geojson", f, "application/geo+json")}
            upload_resp = requests.post(
                f"{api_url}/networks/upload", files=files, headers=headers_user1
            )
        assert upload_resp.status_code in (200, 201), (
            "User 1 should be able to upload network"
        )

        # user 2 tries to get user_1 network:
        get_resp = requests.get(f"{api_url}/networks/{1}/edges", headers=headers_user2)
        assert get_resp.status_code == 404  # this is intended, I don't return 401

        # User 2 tries to UPDATE user 1's network - expect 401, 403, or 404
        with open("./tests/test_data/Bradford_Public_Paths.geojson", "rb") as f:
            files = {
                "file": ("Bradford_Public_Paths.geojson", f, "application/geo+json")
            }
            update_resp = requests.post(
                f"{api_url}/networks/{1}/update", files=files, headers=headers_user2
            )
            assert update_resp.status_code == 404
