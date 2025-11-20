# Create tenant first
curl -X POST http://localhost:8000/admin/tenants/acme

# Search via subdomain
curl http://acme.localhost:8000/search?q=john

# Or via header
curl -H "X-Tenant: acme" http://localhost:8000/search?q=john

# Or in dev
curl http://localhost:8000/search?q=john&tenant=acme


---

# 1. Start API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Create your first tenant
curl -X POST http://localhost:8000/admin/tenants/acme

# 3. Use it!
curl http://acme.localhost:8000/legal-persons
# or
curl -H "X-Tenant: acme" http://localhost:8000/search?q=john

curl -X POST http://acme.localhost:8000/legal_persons/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Holdings Ltd",
    "registration_number": "HRB-1001",
    "jurisdiction": "Germany",
    "incorporation_date": "2015-03-20",
    "status": "active"
  }'