import copy

TENANT_CONFIGS = {
    "slumberland": {
        "tenant": "slumberland",
        "origin": "<APP_ORIGIN>",
        "referer": "<APP_REFERER>",
        "headers": {
            "X-Tenant-ID": "slumberland"
        }
    },
    "wonderland": {
        "tenant": "wonderland",
        "origin": "<APP_ORIGIN>",
        "referer": "<APP_REFERER>",
        "headers": {
            "X-Tenant-ID": "wonderland"
        }
    },
    "neverwinter": {
        "tenant": "neverwinter",
        "origin": "<APP_ORIGIN>",
        "referer": "<APP_REFERER>",
        "headers": {
            "X-Tenant-ID": "neverwinter"
        }
    },
}


def get_tenant_config(tenant_name: object = "slumberland") -> object:
    base = copy.deepcopy(TENANT_CONFIGS[tenant_name])
    base["origin"] = base["origin"].replace("<APP_ORIGIN>", "http://localhost:5000")
    base["referer"] = base["referer"].replace("<APP_REFERER>", "http://localhost:5000/app")
    return base

