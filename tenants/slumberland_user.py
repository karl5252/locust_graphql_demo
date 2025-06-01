from locust import task, between

from core.base_user import MultiTenantUser


class SlumberLandUser(MultiTenantUser):
    """SlumberLand tenant specific user behavior"""
    abstract = True
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

    def _browse_products_flow(self, flow="browse_products_flow"):
        success = True
        success &= self.get_product_list(flow=flow)
        if success:
            success &= self.get_profile_rewards(flow=flow)
        return success

    @task(2)
    def rewards_check_flow(self):
        """Check rewards and offers"""
        self.measure_task_duration("rewards_check_flow", self._rewards_check_flow)

    def _rewards_check_flow(self, flow="rewards_check_flow"):
        success = True
        success &= self.get_profile_rewards(flow=flow)
        if success:
            success &= self.get_order_streak_offers(flow=flow)
        return success

    @task(1)
    def outlet_management_flow(self):
        """Complete outlet change flow"""
        self.measure_task_duration("outlet_management_flow", self._outlet_management_flow)

    def _outlet_management_flow(self, flow="outlet_management_flow"):
        print(f"[{self.tenant_id}] Starting outlet management flow")
        success = True

        # Change outlet
        success &= self.change_outlet(flow=flow)
        if not success:
            return False

        # Refresh user data after outlet change
        success &= self.get_user_info(flow=flow)
        if success:
            success &= self.get_profile_rewards(flow=flow)
            success &= self.get_order_streak_offers(flow=flow)
            success &= self.get_product_list(flow=flow)
            success &= self.get_cart(flow=flow)
            success &= self.get_notifications(flow=flow)

        print(f"[{self.tenant_id}] Outlet management flow completed: {'SUCCESS' if success else 'FAILED'}")
        return success

    @task(1)
    def cart_and_notifications_flow(self):
        """Check cart and notifications"""
        self.measure_task_duration("cart_and_notifications_flow", self._cart_and_notifications_flow)

    def _cart_and_notifications_flow(self, flow="cart_and_notifications_flow"):
        success = True
        success &= self.get_cart(flow=flow)
        if success:
            success &= self.get_notifications(flow=flow)
        return success
