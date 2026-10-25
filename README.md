# HCM Lite — README

**A web-based Human Capital Management system for a real HR team, with an AI assistant that answers only from data your team actually entered.**

There is **no seed data and no dummy data**. A fresh install starts empty: the Admin sets up the company, HR registers employees, and every number on every dashboard comes from what people did in the app.

| | |
|---|---|
| **Team** | 4 people — 2 backend, 2 frontend |
| **Event** | Saylani Hackathon — 24 Oct 2026, Zaitoon Ashraf IT Park |
| **Scope** | 25 functionalities across 9 modules |
| **Live demo** | `<add your hosted URL here>` |
| **Demo video** | `<add link here>` |

---

## Table of contents

1. [What it does](#1-what-it-does)
2. [Tech stack](#2-tech-stack)
3. [Repository layout](#3-repository-layout)
4. [Prerequisites](#4-prerequisites)
5. [Run it locally in under 10 minutes](#5-run-it-locally-in-under-10-minutes)
6. [Environment variables](#6-environment-variables)
7. [Creating the first Admin](#7-creating-the-first-admin)
8. [Setting the AI key](#8-setting-the-ai-key)
9. [Roles and access](#9-roles-and-access)
10. [Business rules implemented](#10-business-rules-implemented)
11. [API overview](#11-api-overview)
12. [Tests](#12-tests)
13. [What is done](#13-what-is-done)
14. [What is not done / known limitations](#14-what-is-not-done--known-limitations)
15. [5-minute demo script](#15-5-minute-demo-script)
16. [Troubleshooting](#16-troubleshooting)

---

## 1. What it does

Three roles, each with its own menu, data scope and dashboard:

- **Admin** — company setup, office hours / grace / weekend / office location + radius, departments, designations, leave types and quotas, holidays, create & deactivate HR/employee logins, view everything, **finalize payroll (the only role that can lock a month)**, audit log, announcements, company-wide AI assistant.
- **HR** — register employees (this creates their login with a temporary password), edit details, CSV import/export, salary structures, daily attendance board, approve attendance corrections, approve/reject leave with a comment, prepare the monthly payroll draft, HR dashboard, announcements, AI assistant scoped to HR data.
- **Employee** — web check-in/check-out, own attendance calendar, request a correction, apply/cancel leave, see balance, download own payslips, edit own phone & address, personal dashboard, AI assistant scoped to **own data only** and to company policy.

Everything is enforced **server-side**. Hiding a button is not a permission.

---

## 2. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | **React 18 + Vite**, React Router, Tailwind CSS, Recharts | Fast dev loop, responsive from 375 px, easy charts |
| Backend | **Node 20 + Express**, layered as `routes → services → data` | Rules live in services, so REST and AI tools share the same code |
| Database | **MongoDB 7 + Mongoose** | Flexible modelling for settings, runs, audit logs |
| Auth | **JWT** (access token) + **bcrypt** password hashing | Role + data-scope guard on every request |
| Validation | **Zod** schemas on every write endpoint | Also used to validate AI tool JSON output |
| PDF | **pdfkit** server-side payslip rendering | Payslip download per employee |
| AI | Any hosted LLM with **tool calling** — OpenAI-compatible API (OpenAI / Groq free tier / Together) | Provider is swappable via env vars |
| Tests | **Vitest** (unit: services, rules) + **Supertest** (API/RBAC) | Rules are pure functions, easy to test |
| Deploy | Backend on Render/Railway, frontend on Vercel/Netlify, DB on MongoDB Atlas | Free-tier friendly |

Nothing is locked in — any DB or framework was allowed by the brief; this is the combination we shipped.

---

## 3. Repository layout

```
hcm-lite/
├── server/
│   ├── src/
│   │   ├── config/            env, db connection, constants
│   │   ├── models/            User, Employee, Department, Designation,
│   │   │                      LeaveType, LeaveRequest, Attendance,
│   │   │                      PayrollRun, Payslip, Setting, Holiday,
│   │   │                      Announcement, Notification, AuditLog, AiLog
│   │   ├── middleware/        auth (JWT), rbac + data-scope guard,
│   │   │                      validate(zod), rateLimit, errorHandler
│   │   ├── routes/            one router per module (M1–M9)
│   │   ├── services/          business rules — the only place rules live
│   │   │                      attendance.service.js, leave.service.js,
│   │   │                      payroll.service.js, analytics.service.js, ...
│   │   ├── ai/                tools.js (tool definitions + implementations),
│   │   │                      chat.js (LLM call, guardrails, ai_logs),
│   │   │                      prompts.js (policy system prompt)
│   │   ├── utils/             dates, workingDays, haversine, tax, csv
│   │   └── app.js / server.js
│   └── tests/
├── client/
│   └── src/
│       ├── pages/             admin/ hr/ employee/ auth/ setup/
│       ├── components/        tables, charts, forms, ai/ChatPanel
│       ├── api/               typed fetch wrappers
│       └── context/           auth, role menus, filters
├── docker-compose.yml         mongo + server + client for local run
├── .env.example
└── README.md
```

---

## 4. Prerequisites

- **Node.js 20+** and npm
- **MongoDB 7** — either local (`mongod`) or a free MongoDB Atlas cluster
- An **LLM API key** with tool-calling support (optional to boot the app; required for the AI features). A free tier is enough.
- *(Optional)* Docker + Docker Compose

---

## 5. Run it locally in under 10 minutes

### Option A — Docker Compose (fastest)

```bash
git clone <your-repo-url> hcm-lite
cd hcm-lite
cp .env.example .env          # then edit the values (see §6)
docker compose up --build
```

- Frontend → `http://localhost:5173`
- API → `http://localhost:4000/api`
- Mongo → `localhost:27017`

### Option B — Manual

```bash
# 1. install
git clone <your-repo-url> hcm-lite
cd hcm-lite
npm --prefix server install
npm --prefix client install

# 2. configure
cp .env.example server/.env
cp .env.example client/.env
# edit server/.env  (MONGODB_URI, JWT_SECRET, ADMIN_*, AI_API_KEY)

# 3. make sure MongoDB is running
#    local:  mongod --dbpath ./data
#    atlas:  set MONGODB_URI to your connection string

# 4. start both
npm --prefix server run dev      # http://localhost:4000
npm --prefix client run dev      # http://localhost:5173
```

Open `http://localhost:5173`. On a **fresh database** you are redirected to the first-run setup screen (§7).

### Production build

```bash
npm --prefix client run build     # outputs client/dist
npm --prefix server start         # serves API; serve client/dist via nginx/Vercel
```

> **Judges:** after cloning, the only required edits are `MONGODB_URI`, `JWT_SECRET`, and (optionally) `ADMIN_EMAIL` / `ADMIN_PASSWORD`. The app boots and works with the AI features disabled.

---

## 6. Environment variables

Copy `.env.example` → `server/.env` and fill in:

```ini
# ---- server ----
NODE_ENV=development
PORT=4000
CLIENT_ORIGIN=http://localhost:5173

# ---- database ----
MONGODB_URI=mongodb://127.0.0.1:27017/hcm_lite
# or: mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/hcm_lite

# ---- auth ----
JWT_SECRET=change-me-to-a-long-random-string
JWT_EXPIRES_IN=8h

# ---- first-run admin (optional, see §7) ----
ADMIN_EMAIL=admin@company.com
ADMIN_PASSWORD=Admin@12345
ADMIN_NAME=Company Admin

# ---- AI assistant (optional, see §8) ----
AI_API_KEY=
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
AI_TIMEOUT_MS=15000
AI_RATE_LIMIT_PER_HOUR=20
```

```ini
# ---- client/.env ----
VITE_API_BASE_URL=http://localhost:4000/api
```

> 🔒 **`AI_API_KEY` lives only in the backend env.** The browser never talks to the LLM provider — all AI calls go through `POST /api/ai/chat` on our server.

---

## 7. Creating the first Admin

A fresh install has **no users**. There are two supported paths — pick one.

### Path 1 — First-run setup screen (default)

1. Start the server against an **empty** database.
2. Open the web app. It detects `users.count === 0` and redirects to `/setup`.
3. Enter the **company name** and the **Admin account** (name, email, password).
4. Submit → the setup endpoint creates the company settings and the first Admin user, then logs you in.
5. The setup route **locks itself** permanently once an Admin exists.

### Path 2 — Environment variables (CI / hosted / scripted)

Set these before the first boot:

```ini
ADMIN_EMAIL=admin@company.com
ADMIN_PASSWORD=Admin@12345
ADMIN_NAME=Company Admin
```

On startup, if no Admin user exists, the server creates one from these values. The setup screen is then skipped. **Change the password after first login.**

### After the Admin exists

1. Admin → **Users** → **Create HR login** (email + temporary password, or an invite).
2. HR logs in, changes the password on first sign-in, then registers employees.
3. **HR registering an employee creates that employee's login** with a **temporary password** that **must be changed on first sign-in** (`must_change_password` flag → forced redirect to `/change-password`).

> To reset everything during a demo, drop the database (`mongosh hcm_lite --eval "db.dropDatabase()"`) and restart the server.

---

## 8. Setting the AI key

The AI assistant uses any hosted LLM with **tool calling** through an OpenAI-compatible API. A free tier is sufficient.

1. Get a key from your provider — e.g. OpenAI, **Groq** (free tier), or Together.
2. Put it in **`server/.env` only**:

   ```ini
   AI_API_KEY=sk-...
   AI_BASE_URL=https://api.openai.com/v1     # e.g. https://api.groq.com/openai/v1
   AI_MODEL=gpt-4o-mini                       # e.g. llama-3.3-70b-versatile on Groq
   AI_TIMEOUT_MS=15000
   AI_RATE_LIMIT_PER_HOUR=20
   ```

3. Restart the server. The chat panel shows a friendly "assistant unavailable" state until the key is set — **the rest of the app is fully functional without it**.

### How the assistant is wired (and guarded)

- `POST /api/ai/chat` → server builds the message list → LLM picks a tool → **server executes the tool with the caller's role and data scope** → LLM writes the answer → response carries an **"AI-generated"** label.
- Tools: `get_headcount`, `get_attendance_summary`, `get_late_comers`, `get_leave_summary`, `get_my_leave_balance`, `get_payroll_summary`, `search_employees`.
- Tools are **thin wrappers over the same services** used by the REST API — so AI answers always match the dashboards.
- The model **never touches the database directly** and **never saves data on its own**. Structured JSON output (smart leave, summaries) is validated with Zod; on failure we retry **once**, then fall back to the normal form.
- **15 s timeout**, friendly fallback message, **20 requests per user per hour**, and every call is written to `ai_logs` (user, tool, tokens, latency, outcome).

**Smart leave** (Employee): *"I need next Monday and Tuesday off for my sister's wedding"* → server returns `{ type, start, end, reason }` → the **leave form is pre-filled** → the user reviews and confirms. The AI does not submit anything.

**Policy Q&A**: the rules from §10 are in the system prompt; the model answers only from them or says it does not know.

---

## 9. Roles and access

| Capability | Admin | HR | Employee |
|---|---|---|---|
| First-run company setup | Manage | — | — |
| Company settings (hours, grace, weekend, location, radius) | Manage | View | — |
| Departments, designations, leave types/quotas, holidays | Manage | View | — |
| Create HR logins, deactivate/reset logins | Manage | — | — |
| Register employee (creates login) / edit details | View | Manage | Own phone & address |
| Employee directory & Employee 360 | All | All | Own |
| CSV import (dry run) / export | — | Manage | — |
| Check in / check out (web) | — | Own | Own |
| Attendance calendar / daily board | All | All | Own |
| Attendance correction | View | Approve | Request |
| Apply / cancel leave, see balance | — | Own | Own |
| Approve / reject leave with comment | View | Approve | — |
| Salary structure | View | Manage | — |
| Monthly payroll draft | View | Manage | — |
| **Finalize payroll (locks the month)** | **Manage** | — | — |
| Payslips + PDF | All | All | Own |
| Dashboards / KPIs / trends | Company | HR | Personal |
| AI assistant scope | All data | HR data | Own data + policy |
| AI dashboard summary | Yes | Yes | — |
| Announcements | Post | Post | Read |
| In-app notifications | Own | Own | Own |
| Audit log | View | — | — |

Guard is a single middleware: `authenticate` → `authorize(...roles)` → `scopeToUser` (Employees are always filtered to `employee_id = req.user.employeeId`). The AI tool layer reuses the same guard.

---

## 10. Business rules implemented

These are in `server/src/services/*` and covered by unit tests.

**M1 Auth** — JWT login, bcrypt hashing, role + data-scope check on every API. Employees can only read rows with their own `employee_id`.

**M2 Setup** — Office start **09:00**, grace **15 min**, half day under **5 h**, weekend **Sat–Sun**, office location + radius (default **150 m**). Stored as settings and applied to **new records only**.

**M4 Attendance** — Server stamps the time (never the client). One record per employee per day; second check-in returns **409**. **Late after 09:15**. `half_day` under 5 h. `absent` when there is no record and no approved leave. `missing_checkout` when there is no checkout.

**M5 Leave** — Working days only (weekends and holidays skipped). Quotas: **annual 14, sick 8, casual 10, unpaid unlimited**. Overlapping request or over-balance → **422**. Approval inbox for HR with comment.

**M6 Payroll** — `gross = 1.5 × basic` (HRA 40%, medical 10%). `per_day = gross ÷ working_days`; deduct absent + unpaid + `0.5 × half_days`. Joiners/leavers prorated. Tax slab on `gross × 12` (illustrative):

| Annual gross | Tax |
|---|---|
| 0 – 600,000 | 0 |
| 600,001 – 1,200,000 | 5% |
| 1,200,001 – 2,400,000 | 30,000 + 15% |
| 2,400,001 – 3,600,000 | 210,000 + 25% |
| above 3,600,000 | 510,000 + 35% |

Admin finalizes; **finalized runs are locked** (further edits return 409). Payslip PDF per employee.

**M7 Dashboards** — All numbers computed **server-side via DB aggregation**, filterable by **date range and department**. Metrics per the brief: headcount, attrition, attendance rate, late %, absenteeism, leave utilization, payroll cost, average salary.

**M9 Comms & Audit** — Announcements on all dashboards, in-app notifications, audit log with **actor, action, entity, before/after JSON**. Audit entries are **append-only** (no update/delete endpoints).

**M3 Employees** — Server-side search, filters, paging. CSV import has a **dry run** returning `row + field + reason`; checks required fields, unique code/email, valid email, known department, ISO dates, salary > 0.

---

## 11. API overview

Base: `http://localhost:4000/api`

| Module | Endpoints (abridged) |
|---|---|
| M1 Auth | `POST /auth/setup`, `POST /auth/login`, `POST /auth/change-password`, `GET /auth/me`, `POST /auth/logout` |
| M2 Setup | `GET/PUT /settings`, `CRUD /departments`, `/designations`, `/leave-types`, `/holidays`, `POST /users/hr` |
| M3 Employees | `GET /employees` (search/filter/page), `GET /employees/:id`, `POST /employees`, `PATCH /employees/:id`, `POST /employees/import?dryRun=true`, `GET /employees/export.csv` |
| M4 Attendance | `POST /attendance/check-in`, `POST /attendance/check-out`, `GET /attendance` (board/calendar), `POST /attendance/corrections`, `POST /attendance/corrections/:id/approve|reject` |
| M5 Leave | `GET /leave/types`, `GET /leave/balance`, `POST /leave`, `POST /leave/:id/cancel`, `GET /leave/inbox`, `POST /leave/:id/approve|reject` |
| M6 Payroll | `GET/PUT /employees/:id/salary`, `POST /payroll/runs`, `GET /payroll/runs/:id`, `POST /payroll/runs/:id/finalize` (Admin), `GET /payslips`, `GET /payslips/:id.pdf` |
| M7 Analytics | `GET /analytics/admin`, `GET /analytics/hr`, `GET /analytics/me` — all accept `?from=&to=&department=` |
| M8 AI | `POST /ai/chat`, `POST /ai/summarize`, `POST /ai/smart-leave` |
| M9 Comms | `GET/POST /announcements`, `GET /notifications`, `POST /notifications/:id/read`, `GET /audit-logs` (Admin) |

All responses are JSON; errors are `{ error: { code, message, details? } }`.

---

## 12. Tests

```bash
npm --prefix server test          # unit + API tests
npm --prefix server test -- --coverage
```

Covered by tests:

- Attendance status rules (late, half_day, absent, missing_checkout, duplicate 409)
- Leave working-day counting, overlap and over-balance 422
- Payroll gross/deduction/tax slab and proration
- RBAC: Employee cannot read another employee's rows; HR cannot finalize payroll; finalized run is locked
- CSV dry-run error report shape
- AI tool JSON validation + one-retry fallback

---

## 13. What is done

**All 25 core functionalities are implemented end to end.** Specifically:

- ✅ First-run setup (company + Admin), or Admin from env vars
- ✅ JWT login/logout/change-password with **forced password change on first sign-in** for HR-created employees
- ✅ Server-side role + data-scope guard on every endpoint, including AI tools
- ✅ Company settings (office hours, grace, weekend, location + radius), departments, designations, leave types/quotas, holidays
- ✅ Admin can create HR logins, deactivate/reset logins
- ✅ Employee registration (creates login), edit details, directory with server-side search/filters/paging, Employee 360
- ✅ CSV import with **dry-run error report** and CSV export
- ✅ Web check-in/check-out with server-stamped time, one record per day, 409 on double check-in
- ✅ Attendance calendar, daily board, correction request + HR approval
- ✅ Leave apply/cancel, balance, overlap + holiday checks, HR approval with comment
- ✅ Salary structures, monthly payroll draft (HR), **finalize + lock (Admin)**, payslip **PDF download**
- ✅ Admin / HR / Employee dashboards with server-aggregated KPIs, trends, filters by date range and department
- ✅ **AI assistant** with the 7 tools, role-scoped answers, "AI-generated" label, `ai_logs`, 20 req/hr limit, 15 s timeout, graceful fallback
- ✅ **AI dashboard summary** (3–5 insight bullets from the current KPI JSON)
- ✅ **Smart leave** (sentence → pre-filled form, user confirms)
- ✅ **Policy Q&A** restricted to the §10 rules
- ✅ Announcements, in-app notifications (leave decisions, payslips), **append-only audit log** with before/after JSON
- ✅ Responsive UI from 375 px, loading / empty / error states
- ✅ Seed-free: dashboards and AI answers match exactly the records created during judging

### Bonus features we shipped

- ✅ **Camera + geofence attendance** — browser `getUserMedia` + face detection (`@vladmandic/face-api`) + Geolocation API; server computes distance (Haversine) and decides; GPS accuracy worse than 100 m rejected; result stored, **no photo stored**; source = `camera`.
- ✅ **Late penalty rule** — 3 lates in a month = 0.5 day deduction, applied in the payroll run.
- ⚠️ **Roman Urdu understanding** — prompt-level only (the model usually understands it), **not** a validated/guaranteed feature.

---

## 14. What is not done / known limitations

Being explicit so nobody is surprised during judging:

- ❌ **No mobile app.** The web app is required and is what we shipped. Camera attendance runs **in the browser** on a laptop/phone, which covers the bonus, but there is no React Native / Expo build.
- ❌ **No face-to-enrolled-face matching and no liveness/blink check.** We detect that **exactly one face** is present in the frame (reject zero or more than one) but we do not store face descriptors or verify identity. This is the "extra bonus" tier we did not implement.
- ❌ **No attrition risk score** and **no absence anomaly flags** (bonus items).
- ❌ **No dark mode** and **no PWA / offline** support.
- ⚠️ **Single company instance.** Multi-tenancy is not modelled — one deployment = one company.
- ⚠️ **Payroll tax slabs are illustrative**, exactly as in the brief. They are not a statutory payroll engine, and there is no multi-currency, no EOBI/social-security, no loans/advances, no bonus/increment cycles.
- ⚠️ **No email delivery.** Temporary passwords, leave decisions and payslip notifications are shown in-app; nothing is emailed or SMS'd (no SMTP/SMS provider configured).
- ⚠️ **No refresh-token rotation.** A single short-lived JWT (`JWT_EXPIRES_IN`); logout is client-side token discard.
- ⚠️ **Announcements** are company-wide only — no department targeting, no scheduling.
- ⚠️ **Audit log** covers create/update/approve/finalize on the main modules; read actions are not logged.
- ⚠️ **CSV import** validates and reports per row, but is limited to the documented columns; no mapping UI for arbitrary CSV headers.
- ⚠️ **CSV export** is employees only (not attendance/leave/payroll).
- ⚠️ **AI features degrade gracefully** if `AI_API_KEY` is missing, but they need network access to the provider; there is no local/offline model.
- ⚠️ **No automated E2E browser tests** (Playwright/Cypress) — coverage is unit + API level.

---

## 15. 5-minute demo script

1. **Fresh install** → `/setup`: Admin enters company name, office hours 09:00, grace 15 min, office location + 150 m radius, creates a department and leave types, creates an **HR login**.
2. **HR** registers 2–3 employees → one employee signs in, **changes the temporary password**, and **checks in** (web).
3. **Employee** types *"I need next Monday and Tuesday off for my sister's wedding"* → **smart leave** pre-fills the form → employee confirms → **HR approves** with a comment.
4. **HR** opens the dashboard → **Summarize** (AI insight bullets) → asks the assistant *"Who is on leave this month?"* → creates the **monthly payroll draft**. **Admin finalizes** it (month locked).
5. **Employee** downloads the **payslip PDF** and asks *"What is my colleague's salary?"* → **politely refused**. **Admin** opens the **audit log** to show every action from the demo.

---

## 16. Troubleshooting

| Symptom | Fix |
|---|---|
| Setup screen does not appear | A user already exists. Drop the DB or use a fresh `MONGODB_URI`. |
| `401` on every request | `JWT_SECRET` missing/changed between restarts — log in again. |
| AI panel says "assistant unavailable" | `AI_API_KEY` not set, wrong `AI_BASE_URL`/`AI_MODEL`, or provider unreachable. The rest of the app still works. |
| AI answers don't match dashboards | Stale filters — both the dashboard and the AI use the **same** service layer; refresh the filter (date range + department). |
| Payroll run cannot be edited | It was **finalized by Admin** — this is intentional; finalized runs are locked. |
| Camera check-in rejected | No face / more than one face / outside office radius / GPS accuracy worse than 100 m. Fall back to an **HR correction**. |
| CSV import shows errors | Use the **dry run** report — it gives `row + field + reason` for each rejected row. |

---

## License

Built for the Saylani Hackathon (24 Oct 2026). MIT — do what you like with it.
