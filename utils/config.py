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


def get_tenant_config(tenant_name="slumberland"):
    return TENANT_CONFIGS[tenant_name]
