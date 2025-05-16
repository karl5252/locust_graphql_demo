# locust_graphql_demo

This project demonstrates how to build a performance testing setup using [Locust](https://locust.io/) to interact with a GraphQL API in an e-commerce application deployed across multiple countries (tenants).
It is based on real-world testing experience from a distributed system, where regional APIs began to degrade under minimal load (as few as 10 concurrent users).

The goal of this demo is to showcase:
- A modular approach to performance testing
- Integration with GraphQL payloads
- Per-tenant configuration and simulation
- Response validation and reporting

> Note: The actual `.graphql` query files have been intentionally removed to avoid exposing any domain-specific or sensitive information. The project focuses on structure and testing strategy, not the exact business logic.

---

## Context

The simulated system is a multi-tenant e-commerce application operating across several countries. Each tenant (e.g., `cambodia`, `slumberland`, etc.) has its own API entrypoint, headers, and context-specific behavior.

The test suite demonstrates how to:
- Authenticate per-tenant
- Maintain session headers
- Run realistic GraphQL flows tied to a specific region or account

---

## Contents

locust_graphql_demo/

├── locustfile.py # Main test definitions and task flow

├── users.json # Example user login data

├── utils/

│ ├── config.py # Per-tenant config mapping

│ └── graphql_loader.py # Utility for loading GraphQL queries from files

├── scenarios/ # Placeholder for future custom task flows

├── README.md # You're here

└── .gitignore

---

## Key Features

- **GraphQL Integration**: Uses real query structure and variables to simulate user interaction.
- **Authentication & Token Management**: Includes login flow and token-based session headers.
- **Per-Tenant Configuration**: Allows region-specific simulation using a dynamic config loader.
- **Response Validation**: Checks for HTTP status, GraphQL errors, and JSON integrity.
- **Task Composition**: Modular `@task`-based flows to simulate user journeys (e.g., club page access, product list, reward profiles, cart interaction).

---

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/karl5252/locust_graphql_demo.git
   cd locust_graphql_demo
2. Install dependencies (requires Python 3.8+):
   ```bash
   pip install -r requirements.txt
   Start the Locust web interface:
3. locust -f locustfile.py
   ```bash
   Open http://localhost:8089 in your browser and launch the test.
   
## Sample Tasks
* spam_product_list: Single query, repeated request for product data
* spam_profile_rewards: Repeated reward data query
* club_page_flow: Combined profile + product data
* outlet_change_flow: Complex flow simulating a full tenant-aware session

---

## Future Enhancements

To support growing tenant-specific complexity and reduce duplication, the test structure can be extended using the **Strategy Pattern**.

Each tenant (country/region) could implement its own behavior module, encapsulating:
- custom login logic,
- different GraphQL flows,
- region-specific headers or tokens.

This would allow:
- cleaner code separation,
- improved maintainability,
- removal of copy-paste variations of `locustfile.py`.

Suggested structure:
/tenants/
├── cambodia.py
├── slumberland.py
└── base_strategy.py


Each strategy can be injected dynamically via CLI (`--host`, `--tenant`) or environment variables.

---



## Disclaimer
This repository is a demonstration and not tied to any production system.
Query payloads and URLs have been fully sanitized. The project is meant to highlight testing strategy and execution using Locust with GraphQL APIs.