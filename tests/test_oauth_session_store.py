from oauth_session_store import OAuthSessionStore


def test_oauth_session_store_create_get_update_delete(tmp_path):
    db_path = tmp_path / "oauth_sessions.db"
    store = OAuthSessionStore(str(db_path))

    created = store.create_session(
        oauth_token="access-token",
        refresh_token="refresh-token",
        client_id="client-id",
        client_secret="client-secret",
        token_uri="https://oauth2.googleapis.com/token",
        label="primary",
    )
    session_id = created["session_id"]

    loaded = store.get_session(session_id)
    assert loaded is not None
    assert loaded["oauth_token"] == "access-token"
    assert loaded["label"] == "primary"

    updated = store.update_access_token(session_id, "new-access-token")
    assert updated is True
    loaded_after = store.get_session(session_id)
    assert loaded_after["oauth_token"] == "new-access-token"

    deleted = store.delete_session(session_id)
    assert deleted is True
    assert store.get_session(session_id) is None
