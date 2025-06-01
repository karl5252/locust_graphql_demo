import os
import random
import time
from datetime import datetime

from flask import Flask, request, jsonify

app = Flask(__name__)
TENANT_CONFIGS = {
    "slumberland": {
        "error_rate": 0.3,  # 30% error rate
        "latency_range": (0.4, 1.2),  # Latency between 0.4 and 1.2 seconds
        "error_message": "Gamma crash",
        "response_size": "large"  # maybe in the future change to kb?
    },
    "wonderland": {
        "error_rate": 0.05,  # 5% error rate
        "latency_range": (0.2, 0.4),  # Latency between 0.2 and 0.4 seconds
        "error_message": "Wunderland timeout",
        "response_size": "medium"
    },
    "neverwinter": {
        "error_rate": 0.1,  # 10% error rate
        "latency_range": (0.05, 0.1),  # Latency between 0.05 and 0.1 seconds
        "error_message": "Neverwinter service unavailable",
        "response_size": "small"
    },
    "default": {
        "error_rate": 0.01,  # ALMOST no errors for default tenant
        "latency_range": (0.05, 0.1),  # Default latency range
        "error_message": "Service error",
        "response_size": "small"
    }
}


def get_response_size_data(size_type):
    """    Generate response size data based on the specified size type.
    Args:
        size_type (str): The type of response size ('small', 'medium', 'large').
        Returns:            dict: A dictionary containing the response size data."""
    if size_type == "small":
        return {"padding": "x" * 100}
    elif size_type == "medium":
        return {"padding": "x" * 1000, "extra_data": list(range(100))}
    elif size_type == "large":
        return {"padding": "x" * 10000, "extra_data": list(range(1000))}
    else:
        return {"response_size": "unknown", "data": {}}


def generate_mock_user_info(tenant):
    """Generate mock user info"""
    outlet_count = random.randint(1, 5)
    outlets = []
    for i in range(outlet_count):
        outlets.append({
            "globalBusinessPartnerID": f"{tenant.upper()}_OUTLET_{i:03d}"
        })

    return {
        "userInfo": {
            "id": f"user_{tenant}_{random.randint(1000, 9999)}",
            "email": f"test@{tenant}.com",
            "businessPartnerContactPerson": {
                "businessPartners": outlets
            }
        }
    }


def generate_mock_products(tenant, count=50):
    """Generate mock product data based on tenant"""
    products = []
    for i in range(count):
        products.append({
            "id": f"{tenant.upper()}_{i:04d}",
            "name": f"{tenant.title()} Product {i}",
            "price": round(random.uniform(10.0, 999.99), 2),
            "category": random.choice(["electronics", "clothing", "books", "home"]),
            "inStock": random.choice([True, False])
        })
    return products


def generate_mock_rewards(tenant):
    """Generate mock rewards data"""
    return {
        "points": random.randint(0, 10000),
        "tier": random.choice(["Bronze", "Silver", "Gold"]),
        "offers": [
            {
                "id": f"{tenant}_offer_{i}",
                "title": f"{tenant.title()} Special Offer {i}",
                "discount": f"{random.randint(5, 50)}%"
            } for i in range(random.randint(1, 5))
        ]
    }


def generate_operation_response(operation_name, tenant):
    """Generate a mock response for the given GraphQL operation name and tenant."""
    base_response = {
        "data": {
            "operationName": operation_name,
            "tenant": tenant,
            "timestamp": datetime.now().isoformat()
        }
    }

    #     Simulate different responses based on operation name
    if operation_name == "Login":
        base_response["data"]["login"] = {
            "response": {
                "accessToken": f"mock_token_{tenant}_{random.randint(10000, 99999)}",
                "refreshToken": f"refresh_{tenant}_{random.randint(10000, 99999)}",
                "expiresIn": 3600
            }
        }
    elif operation_name == "GetUser":
        generate_mock_user_info(tenant)

    elif operation_name == "SearchResultItem":
        base_response["data"]["searchResults"] = {
            "items": generate_mock_products(tenant),
            "totalCount": random.randint(100, 1000),
            "pageInfo": {
                "hasNextPage": True,
                "pageNumber": 1
            }
        }

    elif operation_name == "LoadProfilePointAndReward":
        generate_mock_rewards(tenant)

    elif operation_name == "Cart":
        base_response["data"]["cart"] = {
            "items": generate_mock_products(tenant),
            "total": round(random.uniform(0, 500), 2),
            "itemCount": random.randint(0, 5)
        }

    elif operation_name == "Notifications":
        base_response["data"]["notifications"] = [
            {
                "id": f"notif_{i}",
                "message": f"Notification {i} for {tenant}",
                "read": random.choice([True, False]),
                "timestamp": datetime.now().isoformat()
            } for i in range(random.randint(0, 10))
        ]

    elif operation_name == "ChangeOutlet":
        base_response["data"]["changeOutlet"] = {
            "success": random.choice([True, True, True, False]),  # 75% success rate
            "errorCode": None,
            "errorMessage": None
        }
        if not base_response["data"]["changeOutlet"]["success"]:
            base_response["data"]["changeOutlet"].update({
                "errorCode": "OUTLET_CHANGE_FAILED",
                "errorMessage": "Unable to change outlet at this time"
            })

    elif operation_name == "OrderStreakOffers":
        base_response["data"]["orderStreakOffers"] = [
            {
                "offerName": f"Streak Offer {i}",
                "offerCode": f"STREAK{i}",
                "shortDescription": f"Get {random.randint(5, 25)}% off",
                "fullDescription": f"Complete {random.randint(3, 10)} orders to unlock",
                "offerEndDate": "2025-12-31T23:59:59Z"
            } for i in range(random.randint(1, 3))
        ]

    else:
        # Generic response for unknown operations
        base_response["data"]["result"] = {
            "status": "success",
            "message": f"Mock response for {operation_name}"
        }

    return base_response


@app.route("/", methods=["POST"])
def graphql_handler():
    """Handle GraphQL requests with different response times and error rates based on tenant ID."""
    tenant = request.headers.get("X-Tenant-ID", "unknown")
    operation_name = None
    try:
        request_data = request.get_json() or {}
        operation_name = request_data.get("operationName", "Unknown")
    except Exception as e:
        print(f"Error parsing JSON request: {e}")
        pass
    config = TENANT_CONFIGS.get(tenant, TENANT_CONFIGS["default"])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")[:-3]  # Format timestamp to seconds
    print(f"[{timestamp}] Received request for operation: {operation_name} from tenant: {tenant}")

    # Simulate error rate
    if random.random() < config["error_rate"]:
        print(f"[{timestamp}] Simulated error for operation: {operation_name} from tenant: {tenant}")
        error_code = random.choice([500, 502, 503, 504])
        return jsonify({
            "errors": [{
                "message": config["error_message"],
                "code": error_code,
                "tenant": tenant
            }]
        }), error_code

    # Simulate latency
    latency = random.uniform(*config["latency_range"])
    time.sleep(latency)

    # generate response data
    response_data = generate_operation_response(operation_name, tenant)

    # Simulate response size
    size_data = get_response_size_data(config["response_size"])
    response_data.update(size_data)

    print(f"[{timestamp}] {tenant}: OK ({latency:.3f}s)")
    return jsonify(response_data)


@app.route("/health", methods=["POST"])
def health_check():
    """Health check endpoint to verify service status."""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200


@app.route("/tenant-stats", methods=["POST"])
def tenant_stats():
    """Endpoint to retrieve tenant statistics."""
    tenant = request.headers.get("X-Tenant-ID", "unknown")
    config = TENANT_CONFIGS.get(tenant, TENANT_CONFIGS["default"])

    stats = {
        "tenant": tenant,
        "error_rate": config["error_rate"],
        "latency_range": config["latency_range"],
        "response_size": config["response_size"]
    }

    return jsonify(stats), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT environment variable or default to 5000
    print(f"Starting mock backend on port {port}...")
    print("Available tenants:", ", ".join(TENANT_CONFIGS.keys()))
    print("health check endpoint: /health")
    print("tenant stats endpoint: /tenant-stats")

    app.run(host='0.0.0.0', port=port, debug=True)
