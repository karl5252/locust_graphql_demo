import copy

TENANT_CONFIGS = {
    "slumberland": {
        "headers":{
            "User-Agent":"SlumberlandApp/1,0",
            "X-Tenant-ID":"slumberland",
            "X-Client-Type":"desktop-app",
            "X-Client-Version":"1.0.0",
        },
        "origin": "http://localhost:5000",
        "referer": "http://localhost:5000/app",
        "default_bp_key": "SL001",
        "default_bp_id": "SL002",
        "user_pool": "slumberland_users.json",

    },
    "wonderland": {
        "headers":{
            "User-Agent": "WonderlandApp/1.0",
            "X-Tenant-ID": "wonderland",
            "X-Client-Type": "mobile-app",
            "X-Client-Version": "1.0.0",
        },
        "origin": "http://localhost:5000",
        "referer": "http://localhost:5000/app",
        "default_bp_key": "WL001",
        "default_bp_id": "WL002",
        "user_pool": "wonderland_users.json",
    },
    "dreamland": {
        "headers":{
            "User-Agent": "DreamlandApp/1.0",
            "X-Tenant-ID": "dreamland",
            "X-Client-Type": "web-app",
            "X-Client-Version": "1.0.0",
        },
    },
    "neverwinter": {
        "headers":{
            "User-Agent": "NeverwinterApp/1.0",
            "X-Tenant-ID": "neverwinter",
            "X-Client-Type": "desktop-app",
            "X-Client-Version": "1.0.0",
        },
        "origin": "http://localhost:5000",
        "referer": "http://localhost:5000/app",
        "default_bp_key": "NW001",
        "default_bp_id": "NW002",
        "user_pool": "neverwinter_users.json",
    },
}


def get_tenant_config(tenant_name: object = "slumberland") -> object:
    base = copy.deepcopy(TENANT_CONFIGS[tenant_name])
    base["origin"] = base["origin"].replace("<APP_ORIGIN>", "http://localhost:5000")
    base["referer"] = base["referer"].replace("<APP_REFERER>", "http://localhost:5000/app")
    return base

