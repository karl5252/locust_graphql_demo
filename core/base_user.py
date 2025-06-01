import json
import random
import time
from abc import abstractmethod

from locust import HttpUser, between, task

from utils.config import get_tenant_config
from utils.graphql_loader import load_query


class MultiTenantUser(HttpUser):
    host = "https://<YOUR_API_GATEWAY_URL>"
    wait_time = between(1, 5)
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outlet_ids = None
        self.tenant_id = self.get_tenant_id()  # default tenant ID, to be overridden by subclasses
        self.config = get_tenant_config(self.tenant_id)
        self.client.headers.update(self.config["headers"])

        self.token = None

    @abstractmethod
    def get_tenant_id(self):
        """Abstract method to get tenant ID. Must be implemented by subclasses."""
        pass

    def on_start(self):
        """Called when a simulated user starts executing."""
        self.load_and_login()
        self.get_user_info_and_extract_outlets()

    def load_and_login(self):
        """Load user credentials from a JSON file and perform login."""
        if isinstance(self.config, dict):
            user_pool_file = self.config.get('user_pool')
            if not user_pool_file:
                user_pool_file = f"{self.tenant_id}_users.json"
        else:
            raise TypeError("self.config is not a dictionary")

        user_pools = [
            f"data/{user_pool_file}",
            "data/users.json"  # Fallback
        ]

        for users_file in user_pools:
            try:
                with open(users_file, "r") as f:
                    users = json.load(f)
                    user = random.choice(users)
                    self.login(user["username"], user["password"])
                    print(f"[{self.tenant_id}] Loaded user from {users_file}")
                    return
            except FileNotFoundError:
                continue

        raise FileNotFoundError(f"No user pool found for tenant {self.tenant_id}")

    def login(self, username, password, tenant="slumberland"):
        config = get_tenant_config(tenant)
        query = load_query("login.graphql")
        # Login payload
        test_login_payload = {
            "operationName": "Login",
            "variables": {
                "loginInput": {
                    "username": username,
                    "password": password
                }
            },
            "query": query
        }
        with self.client.post("/", json=test_login_payload, headers={"Content-Type": "application/json"},
                              catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                try:
                    self.token = data["data"]["login"]["response"]["accessToken"]
                    # Update headers with tenant identification and auth
                    auth_headers = {
                        "Authorization": f"Bearer {self.token}",
                        "YourApp-Token": self.token,
                        "YourApp-Tenant": self.tenant_id,  # Key tenant identifier
                        "Content-Type": "application/json"
                    }

                    # Add optional tenant-specific headers
                    if "origin" in self.config:
                        auth_headers["Origin"] = self.config["origin"]
                    if "referer" in self.config:
                        auth_headers["Referer"] = self.config["referer"]

                    self.client.headers.update(auth_headers)
                    print("Login successful. Token:", self.token)
                except Exception as e:
                    response.failure(f"Could not extract token: {e}")
            else:
                print("Login failed")

    def get_profile_rewards(self, outlet_id="", flow=""):
        """Get profile rewards for user"""
        query = {
            "operationName": "LoadProfilePointAndReward",
            "variables": {"outletId": outlet_id},
            "query": load_query("load_profile_rewards.graphql")
        }
        return self.graphql_post("LoadProfilePointAndReward", query, flow)

    def get_product_list(self, bp_key=None, bp_id=None, flow=""):
        """Get product list for a specific business partner"""
        if not isinstance(self.config, dict):
            raise TypeError("self.config must be a dictionary")

        bp_key = bp_key or self.config.get("default_bp_key", "1111111")
        bp_id = bp_id or self.config.get("default_bp_id", "2222222")

        query = {
            "operationName": "SearchResultItem",
            "variables": {
                "searchRequest": {
                    "businessPartner2Key": bp_key,
                    "operationalBusinessPartnerID": bp_id,
                    "pageInfo": {
                        "pageNumber": 1,
                        "pageSize": 50
                    },
                    "isProductRecommenderEnabled": True
                }
            },
            "query": load_query("search_result_item.graphql")
        }
        return self.graphql_post("SearchResultItem", query, flow)

    def get_user_info_and_extract_outlets(self):
        """Get user info and extract outlet IDs"""
        query = {
            "operationName": "GetUser",
            "variables": {},
            "query": load_query("get_user_info.graphql")  # Use external file
        }
        with self.client.post("/", json=query, name=f"{self.tenant_id} | GraphQL: GetUser",
                              catch_response=True) as resp:
            if self.validate_graphql_response(resp, "GetUser"):
                try:
                    data = resp.json()
                    self.outlet_ids = [
                        bp["globalBusinessPartnerID"]
                        for bp in data["data"]["getUser"]["userInfo"]
                        ["businessPartnerContactPerson"]["businessPartners"]
                        if bp.get("globalBusinessPartnerID")
                    ]
                    print(f"[{self.tenant_id}] Extracted {len(self.outlet_ids)} outlet IDs")
                except Exception as e:
                    print(f"[{self.tenant_id}] Failed to parse outlet IDs: {e}")

    def change_outlet(self, flow=""):
        """Change to random outlet"""
        if not self.outlet_ids:
            print(f"[{self.tenant_id}] No outlet IDs available")
            return False

        outlet_id = random.choice(self.outlet_ids)
        query = {
            "operationName": "ChangeOutlet",
            "variables": {"globalBusinessPartnerId": outlet_id},
            "query": load_query("change_outlet.graphql")
        }
        return self.graphql_post("ChangeOutlet", query, flow)

    def get_user_info(self,flow=""):
        """Get current user info"""
        query = {
            "operationName": "GetUser",
            "variables": {},
            "query": load_query("get_user.graphql")
        }
        return self.graphql_post("GetUser", query, flow)

    def get_cart(self, flow=""):
        """Get user's cart"""
        query = {
            "operationName": "Cart",
            "variables": {},
            "query": load_query("cart.graphql")
        }
        return self.graphql_post("Cart", query, flow)

    def get_notifications(self, flow=""):
        """Get user notifications"""
        query = {
            "operationName": "Notifications",
            "variables": {},
            "query": load_query("notifications.graphql")
        }
        return self.graphql_post("Notifications", query, flow)

    def get_order_streak_offers(self, flow=""):
        """Get order streak offers"""
        query = {
            "operationName": "OrderStreakOffers",
            "variables": {},
            "query": load_query("order_streak_offers.graphql")
        }
        return self.graphql_post("OrderStreakOffers", query, flow)

    def measure_task_duration(self, task_name, func, *args, **kwargs):
        """Helper method to measure and log task duration"""
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"[{self.tenant_id}] {task_name} duration: {duration:.2f}s")
        return result

    def validate_graphql_response(self, resp, label=""):
        try:
            if resp.status_code != 200:
                resp.failure(f"{label} HTTP status: {resp.status_code}")
                return False

            data = resp.json()

            if "errors" in data:
                error_list = [e.get("message", "unknown error") for e in data["errors"]]
                resp.failure(f"{label} GraphQL error(s): {error_list}")
                print(f"[GraphQL ERROR] {label}: {error_list}")
                return False
            else:
                size = len(resp.text)
                resp.success()
                print(f"[{label}] OK: {size / 1024:.1f} KB, status 200")
                return True
        except Exception as e:
            resp.failure(f"{label} JSON parse error: {e}")
            print(f"[PARSE ERROR] {label}: {e}")
            return False

    def graphql_post(self, query_name: str, payload: dict, flow: str = "") -> bool:
        full_label = f"{self.tenant_id} | {flow} | GraphQL: {query_name}"
        with self.client.post("/", json=payload, name=full_label, catch_response=True) as resp:
            return self.validate_graphql_response(resp, query_name)
