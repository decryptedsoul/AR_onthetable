# Deploy the prototype with Vercel and Neon

This guide is specific to [AR_onthetable](https://github.com/decryptedsoul/AR_onthetable). Last checked: 7 November 2026.

You will create **two Vercel projects from the same repository** and **one Neon database project**. React stays on Vercel's static hosting; FastAPI runs as a Vercel Function; Neon stores the database. No Python-to-JavaScript rewrite is required.

The repository includes the Vercel configuration files shown below and serverless database handling. No cloud resources, credentials, migrations against Neon, or live deployments have been created or verified locally. The account setup and deployment steps remain manual.

## 1. What runs where

| Component | Provider | Repository root directory |
| --- | --- | --- |
| Intro, Menu, Preview, photos and sample model | Vercel project `ar-onthetable-web` | `coconut-grove/frontend` |
| FastAPI routes and database access | Vercel project `ar-onthetable-api` | `coconut-grove/backend` |
| PostgreSQL tables and menu records | Neon | No repository build |

The project names are suggestions. Use the actual URLs Vercel assigns, which may differ from the names shown here.

Browser flow: **React on Vercel → FastAPI on Vercel → PostgreSQL on Neon**. The browser receives an API URL, never a database password.

Vercel supports both [Vite](https://vercel.com/docs/frameworks/frontend/vite) and [FastAPI](https://vercel.com/docs/frameworks/backend/fastapi). Separate projects let us deploy the existing application without adopting Vercel's multi-service configuration.

## 2. Prerequisites

- GitHub access to the repository, and Vercel and Neon accounts.
- A local checkout containing the latest application code.
- Node.js 22.12+ and Python 3.11+; this project was tested with Node 24 and Python 3.13.
- Keep both services within their free allowances. Vercel Hobby is for personal, non-commercial projects; reassess before the site becomes the restaurant's operating brand website. See [Vercel Hobby](https://vercel.com/docs/plans/hobby) and [Neon pricing](https://neon.com/pricing).

Use provider subdomains initially. Buying a custom domain is optional and separate from hosting.

## 3. Create the Neon database

1. Sign in to [Neon](https://console.neon.tech/).
2. Create a project on the Free plan, for example `ar-onthetable`.
3. Choose an available region near the region you will use for Vercel's API functions. Keeping them close reduces database latency.
4. Create a branch named `prototype` from the initial branch. Use this branch for the public prototype; keep future testing branches separate.
5. Open **Connect** and select the `prototype` branch, its database and its role.
6. Copy two PostgreSQL connection strings into your password manager:
   - **Pooled**: for the deployed API. Its hostname normally contains `-pooler`.
   - **Direct / pooling disabled**: for the initial migration and administrative work.

Retain the TLS parameters supplied by Neon, including `sslmode=require`. Preserve any additional supplied parameters and URL-encoded password characters.

Our app uses SQLAlchemy with **psycopg 3**. It accepts Neon's standard `postgresql://` and `postgres://` URLs directly and selects the installed driver without changing credentials or TLS parameters. You can also use the explicit SQLAlchemy format:

```text
postgresql://...       becomes       postgresql+psycopg://...
```

Illustrative shape only; these values are not usable credentials:

```text
postgresql+psycopg://ROLE:ENCODED_PASSWORD@HOST/DATABASE?sslmode=require
```

Do not put either string in React source, a `VITE_` variable, a committed file or a chat message. See [SQLAlchemy with Neon](https://neon.com/docs/guides/sqlalchemy) and [connection pooling](https://neon.com/docs/connect/connection-pooling).

## 4. Create the tables and import the menu

Run this once against the chosen Neon branch from your computer, before the first backend deployment. Database creation does not create our application tables automatically.

Open PowerShell at the repository root:

```powershell
Set-Location ./coconut-grove/backend

# Skip creating the environment if .venv already exists.
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

# Paste the DIRECT Neon URL at the hidden prompt, without surrounding quotes.
# It is held in this terminal's environment rather than written into a file.
$env:DATABASE_URL = [System.Net.NetworkCredential]::new(
    '', (Read-Host 'Paste the DIRECT Neon connection URL' -AsSecureString)
).Password -replace '^postgres(?:ql)?://', 'postgresql+psycopg://'

.\.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Migration failed; stop here.' }

.\.venv\Scripts\python.exe -m app.import_menu
if ($LASTEXITCODE -ne 0) { throw 'Menu import failed; stop here.' }

.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic check

Remove-Item Env:DATABASE_URL
```

The current migration head is `0002_menu_sources`. The importer should report that the published reference was imported. In Neon's SQL Editor, select the same branch/database and run:

```sql
SELECT COUNT(*) AS published_dishes
FROM dishes
WHERE restaurant_id = 'coconut-grove' AND published = true;
```

An unchanged initial import should return **166**. The importer also retains six hidden legacy sample dishes, so counting every row in `dishes` gives a different result.

The import preserves existing sourced records rather than overwriting staff edits. Repeat it only when appropriate; it is not an ongoing synchronization with the source website. The source prices remain reference prices.

If an error stops the commands, clear `Env:DATABASE_URL` manually or close the terminal. Do not print its value while troubleshooting. Local Python does not automatically load `.env` files in this project.

## 5. Check the included deployment configuration

The following files are included locally. Commit and push the deployment preparation before using the GitHub flow, and confirm the files appear on the branch Vercel will build. Neither file contains secrets.

### Frontend: `coconut-grove/frontend/vercel.json`

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    { "source": "/menu", "destination": "/index.html" },
    { "source": "/preview", "destination": "/index.html" }
  ]
}
```

The explicit rewrites support refreshes and direct links to our two client routes. Assets keep their normal paths. The root URL already serves `index.html`.

### Backend: `coconut-grove/backend/vercel.json`

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "fastapi",
  "functions": {
    "app/main.py": { "maxDuration": 60 }
  }
}
```

`app/main.py` is the existing supported FastAPI entry point. Runtime dependencies come from `requirements.txt`. A 60-second cap is a conservative prototype setting, not an expectation that menu requests should take that long.

Do not add a frontend build or `uvicorn --port ...` start command to the backend project. Vercel invokes the ASGI application itself. Do not run migrations in function startup or every request.

## 6. Deploy the FastAPI project on Vercel

1. In [Vercel](https://vercel.com/), choose **Add New → Project** and import `decryptedsoul/AR_onthetable`.
2. Name the project, for example `ar-onthetable-api`.
3. Set **Root Directory** to `coconut-grove/backend`.
4. Confirm the framework is **FastAPI**. Keep the default dependency installation and framework build behavior. Do not set `dist` as its output directory.
5. Under environment variables, add the following for the **Production** environment:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | The **pooled** Neon URL, beginning with `postgresql+psycopg://` |
| `CORS_ORIGINS` | Leave unset until the frontend's assigned URL is known |

6. Deploy and copy the assigned production URL. Below, `https://YOUR-API.vercel.app` means that actual URL.
7. Open these URLs directly:

```text
https://YOUR-API.vercel.app/api/health
https://YOUR-API.vercel.app/api/ready
https://YOUR-API.vercel.app/api/v1/restaurants/coconut-grove/menu?limit=1
```

Expected results: health returns `{"status":"ok"}`, readiness returns `{"status":"ready"}`, and the menu returns JSON including `total: 166` for the unchanged initial catalog.

The backend's `/` URL can return 404: this deployment does not contain the React build. Test the API paths above. API documentation is at `/docs`.

Use a production API URL accessible to site visitors. If Vercel Deployment Protection redirects API calls to a sign-in page, review protection settings for this public prototype deployment. Do not embed protection-bypass secrets in browser code. Keep protected preview deployments separate.

## 7. Deploy the React project on Vercel

1. Add another Vercel project from the **same GitHub repository**.
2. Name it, for example `ar-onthetable-web`.
3. Set **Root Directory** to `coconut-grove/frontend`.
4. Confirm these settings:

| Setting | Value |
| --- | --- |
| Framework | Vite |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Node.js | 24.x, matching the tested local version |

5. Add these **Production** environment variables:

| Variable | Value |
| --- | --- |
| `VITE_API_BASE_URL` | `https://YOUR-API.vercel.app` using the actual backend URL; no `/api` suffix |
| `VITE_RESTAURANT_ID` | `coconut-grove` |

6. Deploy and copy the frontend's assigned URL.

Do not set `DATABASE_URL` on this frontend project. `API_PROXY_TARGET` is only for the local Vite development server; it does not configure production routing.

Vite embeds `VITE_` values during the build. Changing them requires a new frontend deployment.

## 8. Allow the frontend to call FastAPI

Return to the **backend** Vercel project and set:

```text
CORS_ORIGINS=https://YOUR-WEB.vercel.app
```

Use the exact frontend origin, without a trailing slash, path or quotation marks. Redeploy the backend to apply it. Environment-variable edits do not change an already deployed function.

If needed, the app supports multiple explicit origins separated by commas:

```text
https://YOUR-WEB.vercel.app,https://YOUR-STAGING-WEB.vercel.app
```

This setting does not support wildcard subdomains. A changing Vercel preview URL must be explicitly allowed, or you can use a stable staging deployment. CORS controls browser access; it is not authentication. The current API intentionally exposes read-only public catalog endpoints.

Vercel calls the live environment **Production** even though this remains our personal prototype.

## 9. Check the deployed site

- Open `/`, `/menu` and `/preview` on the **frontend** URL. Refresh each directly.
- Search for `smoky`, use a category filter, move between menu pages, save a dish and reopen its details.
- Confirm real menu requests go to the deployed API, not `localhost`.
- Check browser Network/Console panels for failed requests or CORS messages.
- Confirm the avocado loads, rotates, zooms and resets. Its model URL should be on the frontend host.
- Open the public frontend URL in Safari on a compatible iPhone and Chrome on a compatible Android phone. Test supported AR placement over HTTPS, including permission denial and returning to 3D.
- Confirm missing dish models, recipes, timing and portion information remain labeled as pending.
- Confirm the review form remains a local demo, with no claim that reviews are published.

The public URL supplies the secure context needed by browser AR. HTTPS does not guarantee device AR support or validate actual serving size. See [model-viewer AR requirements](https://modelviewer.dev/examples/augmentedreality/).

## 10. Common problems

| Symptom | Check |
| --- | --- |
| Backend reports that Vercel requires a PostgreSQL `DATABASE_URL` | Add the pooled Neon URL to the backend's correct deployment environment and redeploy. SQLite is only the local default; the Vercel deployment rejects it. |
| Driver error mentioning `psycopg2` | Deploy the latest backend: standard PostgreSQL URLs now select psycopg 3. The explicit `postgresql+psycopg://` format also works. |
| `/api/health` works but `/api/ready` returns 503 | Confirm Neon credentials, TLS, correct branch and completed migrations; check backend logs. |
| Menu request is 200 but `total` is zero | Run `app.import_menu` against the same branch/database used by the backend. |
| Menu reports a network error while direct API URLs work | Check exact CORS origin, production deployment access and the frontend's API URL. |
| API response is HTML or a Vercel sign-in screen | Check the hostname, deployment protection and project root settings. |
| Refreshing `/menu` or `/preview` returns 404 | Confirm the frontend `vercel.json` exists inside the configured frontend root and was deployed. |
| Browser still requests the previous backend URL | Update `VITE_API_BASE_URL` and rebuild/redeploy the frontend. |
| Credentials appear correct but database connection fails | Preserve Neon TLS parameters and password encoding; use the pooled hostname for runtime. Never paste credentials into an issue. |
| First request is slower after inactivity | Function initialization and Neon compute wake-up can add latency; test again and inspect logs. |
| Favorite dishes are missing on another phone | Favorites currently live in that browser's local storage; accounts and synchronization are not implemented. |

## 11. Updates and future growth

Normal source pushes can trigger both linked Vercel projects. Database migrations are a separate release step: test them on an isolated Neon branch, apply the approved migration once, then verify the API deployment. Do not put migrations or menu import into every preview build.

For Vercel Preview environments, use a separate Neon branch and its connection URL rather than automatically sharing the public prototype database. Configure the frontend preview's API URL and the backend preview's allowed origin together.

Keep the pooled database URL on the backend. On Vercel, the engine uses SQLAlchemy `NullPool`: closing a request's database session releases its client connection instead of retaining it in a frozen function. Neon's pooled endpoint handles server-side reuse. The PostgreSQL connection attempt has a 10-second timeout. Local and traditional server deployments retain application pooling. Watch connection counts and database capacity during load testing. Store future uploads in object storage, rather than in function-local files or PostgreSQL blobs by default.

Watch Vercel function CPU, memory, invocation and bandwidth usage, and Neon compute/storage/transfer usage. Free allowances can be exhausted. Check current dashboards and [Vercel function limits](https://vercel.com/docs/functions/limitations) before making capacity commitments.

The deployed prototype will not gain unimplemented features automatically. Approved restaurant models, measured portions, verified reviews, accounts, staff publishing and live kitchen integrations remain future work. PostgreSQL execution on your Neon branch and native phone AR require verification during this setup.
