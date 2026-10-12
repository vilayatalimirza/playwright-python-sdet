import pytest
from playwright.sync_api import APIRequestContext, expect

from pages.api_client import PostsClient


@pytest.fixture
def posts(request: APIRequestContext) -> PostsClient:
    """Compose: pytest-playwright gives `request`, we wrap it."""
    return PostsClient(request)


def test_get_post_returns_expected_shape(posts: PostsClient):
    response = posts.get_post(1)

    assert response.status == 200          # plain assert - no retry needed

    body = response.json()
    assert body["id"] == 1
    assert "title" in body
    assert isinstance(body["title"], str)


def test_create_post(posts: PostsClient):
    response = posts.create_post(title="hello", body="world")

    assert response.status == 201          # 201 Created
    created = response.json()
    assert created["title"] == "hello"
    assert "id" in created                 # server assigned an id


def test_delete_post(posts: PostsClient):
    response = posts.delete_post(1)
    assert response.status in (200, 204)


@pytest.mark.parametrize("post_id", [1, 2, 3])
def test_multiple_posts(posts: PostsClient, post_id: int):
    response = posts.get_post(post_id)
    assert response.status == 200
    assert response.json()["id"] == post_id