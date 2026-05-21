# Architecutre of the projejct

Starlette App -> FastAPI -> SQLAlchemy (ORM) -> PostgreSQL

**Why FastAPI?**

The decision to choose FastAPI was made because it is a very fast and lightweight framework. 
There was no need to create an admin panel for the project, so Django was not used.
It is a modern framework, and it supports async and concurrency very well. 
Every view is async, and every request is handled by a worker.

