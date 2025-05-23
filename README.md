# Vue3 + FastAPI + Keycloak

It's required to create .dockercontainer/.env file with the following content:

```env
KEYCLOAK_URL=https://keycloak.example.com/
KEYCLOAK_REALM=EXAMPLE_REALM
KEYCLOAK_CLIENT_ID=EXAMPLE_CLIENT_ID
KEYCLOAK_REALM_ADMIN_ROLE=WG_COMMAND_ADMIN
DATABASE_URI=postgres://user:password@db:5432/db
```