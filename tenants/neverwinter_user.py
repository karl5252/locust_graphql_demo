from locust import task, between

from core.base_user import MultiTenantUser


class NeverwinterUser(MultiTenantUser):
    """Neverwinter tenant specific user behavior"""
    abstract = True
    wait_time = between(1, 4)  # Faster interaction pattern

    def get_tenant_id(self):
        return "neverwinter"

    @task(5)  # This tenant focuses heavily on product browsing
    def rapid_product_browsing(self):
        """Rapid product browsing - different pattern than Slumberland"""
        self.measure_task_duration("rapid_product_browsing", lambda:self.get_product_list(flow="rapid_product_browsing"))

    @task(2)
    def quick_rewards_check(self):
        """Quick rewards check"""
        self.measure_task_duration("quick_rewards_check", lambda:self.get_profile_rewards(flow="quick_rewards_check"))

    @task(1)
    def minimal_outlet_flow(self):
        """Minimal outlet interaction - different from Slumberland"""
        success = self.change_outlet(flow="minimal_outlet_flow")
        if success:
            self.get_user_info(flow="minimal_outlet_flow")