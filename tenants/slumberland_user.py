from locust import task, between

from core.base_user import MultiTenantUser


class SlumberLandUser(MultiTenantUser):
    """SlumberLand tenant specific user behavior"""
    wait_time = between(2, 8)  # Tenant-specific wait times

    def get_tenant_id(self):
        return "slumberland"

    def on_tenant_start(self):
        """SlumberLand-specific initialization"""
        # Maybe load specific data or perform tenant-specific setup
        print(f"[{self.tenant_id}] Tenant-specific initialization complete")

    @task(3)  # Higher weight for important flows
    def browse_products_flow(self):
        """Main product browsing flow for SlumberLand"""
        self.measure_task_duration("browse_products_flow", self._browse_products_flow)

    def _browse_products_flow(self):
        success = True
        success &= self.get_product_list()
        if success:
            success &= self.get_profile_rewards()
        return success

    @task(2)
    def rewards_check_flow(self):
        """Check rewards and offers"""
        self.measure_task_duration("rewards_check_flow", self._rewards_check_flow)

    def _rewards_check_flow(self):
        success = True
        success &= self.get_profile_rewards()
        if success:
            success &= self.get_order_streak_offers()
        return success

    @task(1)
    def outlet_management_flow(self):
        """Complete outlet change flow"""
        self.measure_task_duration("outlet_management_flow", self._outlet_management_flow)

    def _outlet_management_flow(self):
        print(f"[{self.tenant_id}] Starting outlet management flow")
        success = True

        # Change outlet
        success &= self.change_outlet()
        if not success:
            return False

        # Refresh user data after outlet change
        success &= self.get_user_info()
        if success:
            success &= self.get_profile_rewards()
            success &= self.get_order_streak_offers()
            success &= self.get_product_list()
            success &= self.get_cart()
            success &= self.get_notifications()

        print(f"[{self.tenant_id}] Outlet management flow completed: {'SUCCESS' if success else 'FAILED'}")
        return success

    @task(1)
    def cart_and_notifications_flow(self):
        """Check cart and notifications"""
        self.measure_task_duration("cart_and_notifications_flow", self._cart_and_notifications_flow)

    def _cart_and_notifications_flow(self):
        success = True
        success &= self.get_cart()
        if success:
            success &= self.get_notifications()
        return success
