# PriceYard Frontend — Stage 18

React + TypeScript public/user MVP for PriceYard.

## Local development

1. Start the FastAPI backend on `http://127.0.0.1:8000`.
2. From `frontend/` run:

```bash
npm install
npm run dev
```

The Vite development server proxies `/api/*` to the local FastAPI backend. This keeps Stage 18 local integration simple without changing production CORS policy before the deployment/security stages.

## Production build

```bash
npm run build
```

For deployment, set `VITE_API_URL` to the deployed FastAPI base URL. Production CORS/origin configuration is handled in the approved deployment/security stages.

## Stage 18 boundary

This frontend contains only public/user MVP pages. Admin management pages are Stage 19 and are intentionally not included here.
