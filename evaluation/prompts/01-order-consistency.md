# Prompt 1: Order Consistency

Use the DDIA system design skill to review this design:

We are building an order service. Users can place orders, cancel orders, and view order history. Inventory is stored in another service. The proposal uses a relational database for orders, Redis for order status caching, and asynchronous events to update inventory. Review the design for consistency risks, failure modes, and verification steps.
