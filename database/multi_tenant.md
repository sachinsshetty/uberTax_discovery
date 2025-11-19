# Create tenant first
curl -X POST http://localhost:8000/admin/tenants/acme

# Search via subdomain
curl http://acme.localhost:8000/search?q=john

# Or via header
curl -H "X-Tenant: acme" http://localhost:8000/search?q=john

# Or in dev
curl http://localhost:8000/search?q=john&tenant=acme
