import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state before and after each test."""
    original = copy.deepcopy(app_module.activities)
    try:
        yield
    finally:
        app_module.activities = original

def test_get_activities():
    """アクティビティ一覧取得の確認。

    - `GET /activities` が 200 を返すこと
    - 期待するアクティビティ（例: "Chess Club"）が含まれていること
    """
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_reflect():
    """サインアップ後にサーバー状態が更新され、GET でも反映されることを確認。

    - `POST /activities/{activity}/signup` が 200 を返すこと
    - in-memory の participants に追加されること
    - `GET /activities` でも参加者が見えること
    """
    email = "test_user_signup@example.com"
    activity = "Chess Club"
    path_activity = quote(activity, safe="")

    resp = client.post(f"/activities/{path_activity}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 200
    # Ensure in-memory state updated
    assert email in app_module.activities[activity]["participants"]

    # Confirm via GET /activities
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    data = resp2.json()
    assert email in data[activity]["participants"]


def test_unregister():
    """登録解除（unregister）の動作確認。

    - まず signup で登録し、その後 unregister を呼び出して 200 が返ること
    - 最終的に in-memory の participants から削除されていること
    """
    email = "test_user_unregister@example.com"
    activity = "Programming Class"
    path_activity = quote(activity, safe="")

    # Sign up first
    resp = client.post(f"/activities/{path_activity}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 200

    # Then unregister
    resp2 = client.post(f"/activities/{path_activity}/unregister?email={quote(email, safe='')}")
    assert resp2.status_code == 200

    # Ensure removed from in-memory state
    assert email not in app_module.activities[activity]["participants"]
