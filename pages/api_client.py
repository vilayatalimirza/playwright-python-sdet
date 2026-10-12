from playwright.sync_api import APIRequestContext, APIResponse
BASE = "https://jsonplaceholder.typicode.com"
class PostsClient:
    """Wraps the /posts endpoint. Tests call intent-level methods."""
    def __init__(self, request: APIRequestContext):
        self.request = request

    def get_post(self, post_id: int) -> APIResponse:
        return self.request.get(f"{BASE}/posts/{post_id}")

    def create_post(self, title: str, body: str, user_id: int = 1) -> APIResponse:
        return self.request.post(
            f"{BASE}/posts",
            data={"title": title, "body": body, "user_id": user_id},
        )

    def delete_post(self, post_id: int) -> APIResponse:
        return self.request.delete(f"{BASE}/posts/{post_id}")