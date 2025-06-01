import json
import random
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
        self.tenant_id = 'slumberland'  # Default tenant
        self.outlet_id = self.get_tenant_id()
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

    def get_profile_rewards(self, outlet_id=""):
        query = {
            "operationName": "LoadProfilePointAndReward",
            "variables": {
                "outletId": outlet_id
            },
            "query": load_query("load_profile_rewards.graphql")
        }
        with self.client.post("/", json=query, name="GraphQL: LoadProfilePointAndReward", catch_response=True) as resp:
            self.validate_graphql_response(resp, "LoadProfilePointAndReward")

    def get_product_list(self, bp_key="1111111", bp_id="2222222"):
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
        with self.client.post("/", json=query, name="GraphQL: SearchResultItem", catch_response=True) as resp:
            self.validate_graphql_response(resp, "SearchResultItem")

    def validate_graphql_response(self, resp, label=""):
        try:
            if resp.status_code != 200:
                resp.failure(f"{label} HTTP status: {resp.status_code}")
                return

            data = resp.json()

            if "errors" in data:
                error_list = [e.get("message", "unknown error") for e in data["errors"]]
                resp.failure(f"{label} GraphQL error(s): {error_list}")
                print(f"[GraphQL ERROR] {label}: {error_list}")
            else:
                size = len(resp.text)
                resp.success()
                print(f"[{label}] OK: {size / 1024:.1f} KB, status 200")
        except Exception as e:
            resp.failure(f"{label} JSON parse error: {e}")
            print(f"[PARSE ERROR] {label}: {e}")

    def get_user_info_and_extract_outlets(self):
        query = {
            "operationName": "GetUser",
            "variables": {},
            "query": """
                query GetUser {
                  getUser {
                    ... on UserSuccessfulResponse {
                      userInfo {
                        businessPartnerContactPerson {
                          businessPartners {
                            globalBusinessPartnerID
                          }
                        }
                      }
                    }
                  }
                }
            """
        }
        with self.client.post("/", json=query, name="GraphQL: GetUser", catch_response=True) as resp:
            try:
                data = resp.json()
                self.outlet_ids = [
                    bp["globalBusinessPartnerID"]
                    for bp in data["data"]["getUser"]["userInfo"]["businessPartnerContactPerson"]["businessPartners"]
                    if bp.get("globalBusinessPartnerID")
                ]
                print(f"[Extracted outlet IDs] → {self.outlet_ids}")
            except Exception as e:
                resp.failure(f"Failed to parse outlet IDs: {e}")

    def get_user_info(self):
        query = {
            "operationName": "GetUser",
            "variables": {},
            "query": load_query("get_user.graphql")
        }
        with self.client.post("/", json=query, name="GraphQL: GetUser", catch_response=True) as resp:
            self.validate_graphql_response(resp, label="GetUser")

    def get_cart(self):
        query = {
            "operationName": "Cart",
            "variables": {},
            "query": load_query("cart.graphql")
        }

        with self.client.post("/", json=query, name="GraphQL: Cart", catch_response=True) as resp:
            self.validate_graphql_response(resp, label="Cart")

    def get_notifications(self):
        query = {
            "operationName": "Notifications",
            "variables": {},
            "query": load_query("notifications.graphql")
        }
        with self.client.post("/", json=query, name="GraphQL: Notifications", catch_response=True) as resp:
            self.validate_graphql_response(resp, label="Notifications")

    def change_outlet(self):
        if not hasattr(self, "outlet_ids") or not self.outlet_ids:
            print("No outlet IDs loaded, skipping outlet change.")
            return

        outlet_id = random.choice(self.outlet_ids)
        query = {
            "operationName": "ChangeOutlet",
            "variables": {
                "globalBusinessPartnerId": outlet_id
            },
            "query": """
                mutation ChangeOutlet($globalBusinessPartnerId: String!) {
                  changeOutlet(globalBusinessPartnerID: $globalBusinessPartnerId) {
                    errorCode
                    errorMessage
                    success
                    __typename
                  }
                }
            """
        }
        with self.client.post("/", json=query, name="GraphQL: ChangeOutlet", catch_response=True) as resp:
            self.validate_graphql_response(resp, label="ChangeOutlet")

    def get_order_streak_offers(self):
        query = {
            "operationName": "OrderStreakOffers",
            "variables": {},
            "query": """
                query OrderStreakOffers {
                  orderStreakOffers {
                    offerName
                    offerCode
                    shortDescription
                    fullDescription
                    offerEndDate
                    __typename
                  }
                }
            """
        }
        with self.client.post("/", json=query, name="GraphQL: OrderStreakOffers", catch_response=True) as resp:
            self.validate_graphql_response(resp, label="OrderStreakOffers")

    @task(0)
    def _noop(self):
        """ No operation task to keep the user active without performing any actions."""
        pass


