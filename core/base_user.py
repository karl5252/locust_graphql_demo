from locust import HttpUser, between

from utils.config import get_tenant_config


class MultiTenantUser(HttpUser):
    host = "https://<YOUR_API_GATEWAY_URL>"
    wait_time = between(1, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant_id = 'slumberland'  # Default tenant
        self.config = get_tenant_config(self.tenant_id)
        self.client.headers.update(self.config["headers"])
        self.outlet_ids = None
