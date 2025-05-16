TENANT_CONFIGS = {
    "slumberland": {
        "tenant": "slumberland",
        "origin": "<APP_ORIGIN>",
        "referer": "<APP_REFERER>"
    },
    # Add other tenants here...
}


def get_tenant_config(tenant_name="slumberland"):
    return TENANT_CONFIGS[tenant_name]
