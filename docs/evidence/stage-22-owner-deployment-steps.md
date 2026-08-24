# Stage 22 Owner Deployment Steps

Deployment order:

1. Pull and verify the deployment-preparation commit.
2. Create the Render FastAPI Web Service.
3. Verify the backend health URL.
4. Create the Render React Static Site using the backend URL.
5. Add the React Router rewrite.
6. Add the final frontend URL to backend `CORS_ORIGINS`.
7. Run the complete production verification checklist.

Exact dashboard values are provided interactively during owner deployment so generated Render URLs can be inserted safely. Never publish or paste `DATABASE_URL` or `JWT_SECRET` into chat or GitHub.
