from tenants.neverwinter_user import NeverwinterUser
from tenants.slumberland_user import SlumberLandUser


# Main orchestration user class for login-only users

class SlumberlandStrategy(SlumberLandUser):
    """Slumberland Strategy A"""
    weight = 1


class NeverwinterStrategy(NeverwinterUser):
    """Neverwinter Strategy B"""
    weight = 2
