import time

from locust import between, task

from core.base_user import MultiTenantUser


class LoginOnlyUser(MultiTenantUser):
    host = "https://<YOUR_API_GATEWAY_URL>"
    wait_time = between(1, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outlet_ids = None

    @task
    def spam_product_list(self):
        start = time.time()
        self.get_product_list()
        print(f"[TASK] spam_product_list duration: {time.time() - start:.2f}s")

    @task
    def spam_profile_rewards(self):
        start = time.time()
        self.get_profile_rewards()
        print(f"[TASK] spam_profile_rewards duration: {time.time() - start:.2f}s")

    @task
    def club_page_flow(self):
        start = time.time()
        self.get_profile_rewards()
        self.get_product_list()
        print(f"[TASK] club_page_flow duration: {time.time() - start:.2f}s")

    @task
    def outlet_change_flow(self):
        print("[TASK] outlet_change_flow: start")
        self.change_outlet()
        self.get_user_info()
        self.get_profile_rewards()
        self.get_order_streak_offers()
        self.get_product_list()
        self.get_profile_rewards()
        self.get_cart()
        self.get_notifications()
        print("[TASK] outlet_change_flow: end")
