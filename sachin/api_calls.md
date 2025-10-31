curl -X 'POST' \
  'http://localhost/api/clients/natural-query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"user_query":"news from germany","table_name":"regulatory_feed"}

'

{
  "results": [
    {
      "id": 1,
      "date": "Nov 5, 2025",
      "country": "Germany",
      "content": "Bundesrat approves amendments to the Digital Services Act (DSA) implementation, mandating AI-driven content moderation tools for platforms with over 1 million EU users; compliance deadline set for March 2026."
    }
  ]
}
---

curl -X 'POST' \
  'http://localhost/api/clients/natural-query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '
{"user_query":"companies from croatia","table_name":"client_profiles"}
'

{
  "results": [
    {
      "company_name": "Split Hospitality Group j.d.o.o."
    },
    {
      "company_name": "Adriatic Solutions d.o.o."
    },
    {
      "company_name": "Zagreb Eco Solutions d.o.o."
    }
  ]
}

---




{"user_query":"companies from croatia","table_name":"client_profiles"}


{"user_query":"news from germany","table_name":"regulatory_feed"}

