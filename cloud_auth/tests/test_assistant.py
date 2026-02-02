import pytest


def test_assistant_requires_auth(fastapi):
    res = fastapi.post("/assistant", json={"message": "hello"})
    assert res.status_code == 401


def test_assistant_reply(fastapi, secret):
    res = fastapi.post(
        "/assistant",
        json={"message": "hello"},
        headers={"Authorization": "Bearer " + "placeholder"},
    )
    # unauthorized because header invalid
    assert res.status_code == 401


def test_assistant_with_valid_user(fastapi, secret, api_auth, userstore):
    from arxiv.cloud_auth.jwt import user_jwt

    token = user_jwt(2, secret)  # moderator user
    res = fastapi.post(
        "/assistant", json={"message": "hi"}, headers={"Authorization": "Bearer " + token}
    )
    assert res.status_code == 200
    assert res.json()["reply"] == "AI assistant reply: hi"
