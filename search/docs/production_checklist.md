Production Rollout Checklist

A production rollout for Discovery should follow a clear checklist across data, infra, API, security, and
operational readiness.[1][2]

## Data, indexing, and ingestion
- Corpus frozen and verified (sources, repos, wikis, PDFs) defined for initial rollout, with data
owners sign‑off.[3][4]
- Automated ingestion pipeline configured for full build and incremental updates
(new/changed/deleted docs), with at least one successful full re‑index in staging.[1][4][5]
- Embedding model, BM25/full‑text engine, and vector database chosen, provisioned, and sized;
index version tagged and documented for rollback.[1][6][4]
## Application and API readiness
- FastAPI service refactored to use proper dependency injection, async DB and vector‑store
clients, and connection pooling.[7][8][9]
- Core endpoints (ingest, search, health, metrics) covered by automated tests with acceptable
pass rate and basic load test (e.g., P95 latency and error rate within defined SLOs) in
staging.[1][7][3]
- Configuration externalized (env / config files), with separate configs for dev, staging, and prod
and documented bootstrap procedure. [6][7]
## Security, privacy, and access control
- Authentication (API keys/JWT/OIDC) enforced on all non‑health endpoints; CORS and TLS
configured at the ingress/load balancer.[7][10][11]
- Authorization and multi‑tenancy rules implemented and tested (project/tenant scoping of
queries, indices, and ingestion), including negative tests to prove isolation.[12][13][4]
- Secrets (DB, vector store, embedding provider keys) stored in a secret manager or env vars;
no secrets in code or repo; security review completed for initial scope. [1][10]
## Observability and quality monitoring
- Structured logging (with request IDs) enabled; logs shipped to centralized storage (e.g.,
ELK/Cloud logs) and searchable by correlation ID.[1][7][14]
- Metrics and dashboards set up for query latency, error rates, queue depths, index sizes,
embedding throughput and failures, with alerting on critical thresholds.[1][15][14]
- Retrieval quality evaluation in place (e.g., small labeled set or click/accept tracking), with a
simple dashboard for precision@k / MRR and a process to review low‑quality queries.[16][17][2]

## Deployment, scaling, and failure handling
- Service containerized and deployed with a multi‑worker ASGI stack behind a load balancer;
liveness and readiness probes configured and passing.[1][7][14]
- Horizontal scaling tested (scale out workers / pods) and basic load test run to identify
bottlenecks (embedding model, DB, vector store) with mitigation plan (batching, caching, or
capacity increase).[1][15][18]
- Graceful shutdown and zero‑ or low‑downtime deployment validated (draining, readiness
gates, rollback path if new release fails health checks). [7][14]

## Governance, rollout plan, and support
- CI/CD pipeline wired to staging and prod with gated promotions (tests and smoke checks
required to deploy to prod).[1][6][9]
- Rollout strategy defined: internal beta or small traffic percentage first, explicit SLOs (latency,
availability, relevance) and criteria for expanding to 100% traffic.[1][2][19]
- Runbook and on‑call basics prepared: how to rotate keys, pause ingestion, rebuild indexes,
rollback a model/index version, and handle incident types (data leak, relevance regression,
outage).[1][12][4]
Citations:
[1] How do I deploy semantic search in a production ...
https://milvus.io/ai-quick-reference/how-do-i-deploy-semantic-search-in-a-production-environme
nt
[2] To build a roadmap for semantic search implementation ...
https://milvus.io/ai-quick-reference/how-do-i-build-a-roadmap-for-semantic-search-implementati
on
[3] How To Build A Rag Pipeline https://www.multimodal.dev/post/how-to-build-a-rag-pipeline
[4] The Production-Ready RAG Pipeline: An Engineering ...
https://activewizards.com/blog/the-production-ready-rag-pipeline-an-engineering-checklist
[5] Cheatsheet for Production-Ready Advanced RAG
https://www.thecloudgirl.dev/blog/this-is-your-playbook-for-production-readynbsp-advanced-rag
[6] Building a Semantic Search Engine from Scratch
https://www.hakia.com/tech-insights/build-semantic-search-engine/
[7] FastAPI production deployment best practices
https://render.com/articles/fastapi-production-deployment-best-practices
[8] FastAPI Best Practices: A Condensed Guide with Examples
https://dev.to/devasservice/fastapi-best-practices-a-condensed-guide-with-examples-3pa5
[9] Deployment https://fastapi.tiangolo.com/deployment/
[10] Deployment checklist for FastAPI: security, observability ...
https://www.linkedin.com/posts/igor-benav_fastroai-the-ultimate-ai-development-stack-activity-7
381720108496441344-LNmx
[11] The FastAPI Pre-Deployment Checklist You Actually Need
https://fastro.ai/blog/fastapi-deployment-checklist
[12] Production Deployment Challenges for an Enterprise RAG ...
https://www.linkedin.com/pulse/production-deployment-challenges-enterprise-rag-pradeep-kuma
r-k1mqc
[13] Making RAG Production-Ready: Overcoming Common Challenges
https://www.konverso.ai/en/blog/what-is-rag
[14] FastAPI Docker Best Practices | Better Stack Community
https://betterstack.com/community/guides/scaling-python/fastapi-docker-best-practices/
[15] Building Production-Ready Semantic Search Applications
https://aws.amazon.com/awstv/watch/5f480d62227/
[16] The Power of Semantic Search: Turn Every Query Into a ...
https://bix-tech.com/the-power-of-semantic-search-turn-every-query-into-a-great-customer-expe
rience/
[17] Understanding RAG Pipelines: Architecture, Challenges, and Best ...
https://www.getmaxim.ai/articles/understanding-rag-pipelines-architecture-challenges-and-best-
practices/
[18] Boosting search relevance: Automatic semantic enrichment ...
https://aws.amazon.com/blogs/big-data/boosting-search-relevance-automatic-semantic-enrichm
ent-in-amazon-opensearch-serverless/
[19] How to Build a RAG Pipeline: A Step-by-Step Guide
https://www.meilisearch.com/blog/how-to-build-a-rag-pipepline
[20] Understanding the semantic search roll out plan
https://support.zendesk.com/hc/en-us/articles/6675063083418-Understanding-the-semantic-sea
rch-roll-out-plan
[21] AI introduction checklist - your guide to successfully ...
https://ambersearch.de/en/ai-introduction-checklist/
[22] What is semantic search? How it works, use cases & more
https://www.meilisearch.com/blog/semantic-search
[23] How AI semantic search with LLMs is redefining enterprise ...
https://pretius.com/blog/ai-semantic-search-with-llm
[24] Semantic Search With Cohere and PostgreSQL in 10 Minutes
https://www.tigerdata.com/blog/semantic-search-with-cohere-and-postgresql-in-10-minutes
[25] 15 FastAPI Best Practices For Production https://www.youtube.com/watch?v=kmJz8w5ij8Y
[26] How to get RAG to behave in production: a checklist
https://www.linkedin.com/posts/mohitsinghal-software-architect_how-easy-do-you-think-getting-t
his-simple-activity-7366560057368506370-rQjn
[27] How to deploy semantic search model to production?
https://www.reddit.com/r/learnmachinelearning/comments/v4pdtj/how_to_deploy_semantic_search_model_to_production/