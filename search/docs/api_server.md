Run locally:
```bash
uvicorn api:app --reload
```
Then:

```bash
curl -X POST http://localhost:8000/ingest \
-H "Content-Type: application/json" \
-d '{"title":"Nia intro","content":"Nia is an indexing service.\n\nIt builds multiple indexes."}'
curl "http://localhost:8000/search?q=indexes"
```
## 2. Suggested next steps
- Swap paragraph chunker with fixed‑size or code‑aware chunkers for real repos.
- Persist documents/chunks to a DB instead of keeping them only in memory, and rebuild
`NiaIndex` from storage on startup