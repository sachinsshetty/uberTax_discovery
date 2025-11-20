API Server for Company Registry

- Steps for Implementation
    - Create Postgres DB
        - Done
    - Create Tables
        - Done
    - Insert Values in DB
        - [curl command](../docs/database-upgrade/curl_commands.md)
    - Create fastpi server
        - Done
    - Connect fastapi and postgres Container
        - Done
    - Build ER Cascade / Connection graph

    - Test endpoints for connection graph

    - Test - 
    - Test Migration
    - Run 3 version of migrations

-- 

- Run Server
```bash
docker build -t dwani/ubertax-register -f Dockerfile .

docker compose -f docker-compose.yml up -d
```

-- 
Multi tenant

```bash
docker build -t dwani/ubertax-register-multi -f Dockerfile .

docker compose -f multi-tenant-compose.yml up -d
```


-- 


![multi-tenant](../docs/database-upgrade/multi-tenant.png "multi-tenant")


---

- Steps for Migration

    - Daily Database snapshots 

    - Datbase backup before any migration 


    - Copy production to staging and run migration to test changes 


    - Use alembic for python or Liquibase for xml based 


    - Utilise postgres containers and test containers for Database related changes

-----
