# === 1. Create 3 Legal Persons ===
curl -X POST http://localhost:8000/legal_persons \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Holdings Ltd",
    "registration_number": "HRB-1001",
    "jurisdiction": "Germany",
    "incorporation_date": "2015-03-20",
    "status": "active"
  }' | jq .

curl -X POST http://localhost:8000/legal_persons \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Beta Investments SARL",
    "registration_number": "RCS-B123456",
    "jurisdiction": "Luxembourg",
    "incorporation_date": "2018-07-10"
  }' | jq .

curl -X POST http://localhost:8000/legal_persons \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gamma Tech LLC",
    "registration_number": "12345678",
    "jurisdiction": "Delaware, USA",
    "incorporation_date": "2021-01-15"
  }' | jq .


# === 2. Create 3 Natural Persons ===
curl -X POST http://localhost:8000/natural_persons \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Elon",
    "last_name": "Musk",
    "nationality": "South African",
    "date_of_birth": "1971-06-28",
    "tax_id": "TAX-001"
  }' | jq .

curl -X POST http://localhost:8000/natural_persons \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Sundar",
    "last_name": "Pichai",
    "nationality": "Indian",
    "date_of_birth": "1972-06-10",
    "tax_id": "TAX-002"
  }' | jq .

curl -X POST http://localhost:8000/natural_persons \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Satya",
    "last_name": "Nadella",
    "nationality": "Indian",
    "date_of_birth": "1967-08-19",
    "tax_id": "TAX-003"
  }' | jq .


# === 3. Create some realistic connections (shareholders, directors, etc.) ===
# Elon Musk is 100% shareholder of Acme Holdings
curl -X POST http://localhost:8000/graph/connections \
  -H "Content-Type: application/json" \
  -d '{
    "from_type": "natural",
    "from_id": 1,
    "to_type": "legal",
    "to_id": 1,
    "relation": "shareholder",
    "share_percentage": "100"
  }' | jq .

# Acme Holdings owns 75% of Beta Investments
curl -X POST http://localhost:8000/graph/connections \
  -H "Content-Type: application/json" \
  -d '{
    "from_type": "legal",
    "from_id": 1,
    "to_type": "legal",
    "to_id": 2,
    "relation": "shareholder",
    "share_percentage": "75"
  }' | jq .

# Sundar Pichai is director of Gamma Tech
curl -X POST http://localhost:8000/graph/connections \
  -H "Content-Type: application/json" \
  -d '{
    "from_type": "natural",
    "from_id": 2,
    "to_type": "legal",
    "to_id": 3,
    "relation": "director"
  }' | jq .

# Satya Nadella is 25% shareholder of Beta Investments
curl -X POST http://localhost:8000/graph/connections \
  -H "Content-Type: application/json" \
  -d '{
    "from_type": "natural",
    "from_id": 3,
    "to_type": "legal",
    "to_id": 2,
    "relation": "shareholder",
    "share_percentage": "25"
  }' | jq .



  # See all connections from Elon Musk (natural person id=1)
curl http://localhost:8000/graph/natural/1 | jq .

# See all connections from Acme Holdings (legal person id=1)
curl http://localhost:8000/graph/legal/1 | jq .

# See who owns Beta Investments (legal id=2)
curl http://localhost:8000/graph/legal/2 | jq .