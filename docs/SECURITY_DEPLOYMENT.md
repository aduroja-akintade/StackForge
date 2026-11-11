# StackForge security and deployment checklist

This change is deliberately **not deployed automatically** from the repair branch.
Apply the SQL migration before merging the PR, otherwise protected routes will
return HTTP 503 when quota storage is unavailable.

## 1. Database migration (required, before backend deployment)

In your Supabase project, open the SQL Editor and run
`database/migrations/20261111_security_quota.sql`.

It creates the `api_usage` table and an atomic, service-role-only
`consume_api_quota` RPC, restricts public profile reads to the owner,
and prevents authenticated browser users from granting themselves `tier=pro`.

The existing user/analysis/project tables remain in place. Make a
database backup first. Never run an unreviewed migration against a live project.

## 2. Render backend secrets

Set these environment variables for the `stackforge-backend` service:

| Variable | Value |
|---|---|
| `GOOGLE_API_KEY` | Server-only Gemini API key |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | **Server-only** Supabase service_role secret |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of exact trusted frontends, e.g. `https://stack-forge-xi.vercel.app` |
| `GEMINI_MODEL` | Optional, defaults to `gemini-flash-lite-latest` |

Do **not** use a public anon key as the server service-role key. The previous
`SUPABASE_KEY` variable is no longer read by the hardened API.

## 3. Vercel frontend environment variables

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public anon/publishable key, **not** service_role |
| `NEXT_PUBLIC_API_URL` | Backend URL, e.g. `https://stackforge-backend.onrender.com` |

Vercel must rebuild the frontend after setting these variables. This is a
public browser key; it is intentionally different from the backend secret.

Set Supabase Auth's Google OAuth provider and permitted redirect URL
`https://stack-forge-xi.vercel.app/auth/callback` (plus any custom domain).

## 4. Verify before merging

Run from the repository root:

```bash
python -m pip install -r backend/requirements-dev.txt
python -m pytest -q backend/tests
python -m compileall -q backend
cd frontend
npm ci
npx tsc --noEmit
npm run lint
npm run build
```

For the Docker variant, build from **repository root**:

```bash
docker build -f backend/Dockerfile -t stackforge-backend .
```

Smoke tests after deployment:

1. `GET /health` returns HTTP 200 with `{"status":"ok"}`.
2. `GET /analyse/history` without a token returns HTTP 401.
3. Google sign-in succeeds, and authenticated analysis and history requests succeed.
4. A different client's `user_id` cannot be supplied or used to fetch history.
5. Free-tier analysis accepts up to 3 requests per UTC day and then returns 429.
6. Pro tier should be checked with a genuine server-controlled tier assignment.
7. Test failed Gemini responses, expired sessions, and browser CORS origins.
8. Check Render/Vercel logs for any errors; verify no service-role key leaks.

## Operational notes

- Each accepted API request consumes a quota unit **before** its AI call. A failed
  model call still consumes quota, prioritizing cost protection.
- Free-tier quotas: analyse 3/day, implement 3/month, recommend 10/day,
  upgrade 10/day. Pro-tier accounts bypass these limits.
- Render `autoDeploy: true` handles pushes to the configured production branch.
  The old webhook deploy workflow was removed to prevent duplicate deployments.
- The old Terraform GCP workflow targeted an absent `infrastructure/gcp`
  directory and included invalid shell syntax, so it was removed.
- GitHub Actions now checks Python compilation, API regression tests,
  TypeScript, ESLint, and the Next.js production build.
- CI cannot verify live services, OAuth configuration, DNS, cloud billing,
  or database migrations. Complete the smoke tests above before production use.
