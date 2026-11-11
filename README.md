# StackForge 🚀
### Bridging the Gap Between Engineering Skills and Career Success.

**Live Application**: [https://stack-forge-xi.vercel.app](https://stack-forge-xi.vercel.app)  
**Backend API**: [https://stackforge-backend.onrender.com](https://stackforge-backend.onrender.com)

---

## 📌 Mission Statement
The modern Cloud and DevOps job market is intensely competitive. Candidates often struggle to demonstrate the specific, production-grade skills required by top-tier tech companies. **StackForge** leverages Artificial Intelligence to deconstruct job descriptions and provide a technical roadmap for building high-impact, portfolio-worthy projects.

## ✨ Core Features

### 🔍 Job Description Analyser
Deconstructs any job posting to identify mandatory skills, preferred tools, and "project gaps" in your current profile.

### 🎯 Strategic Project Recommender
Generates 3-5 specific project ideas tailored to your target role, ranked by their ROI for hiring managers.

### 🛠️ One-Click Implementation Blueprints
Provides complete technical blueprints—architecture designs, production-ready file structures, and exact CLI commands (Terraform, Docker, Kubectl)—with a single click.

### 🚀 Production-Grade Upgrader
Critiques existing work against a "Senior Engineer's Checklist" to move projects from student-grade to production-grade quality.

---

## 🛠️ Technical Architecture

### **Frontend**
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS (Dark Mode Optimized)
- **Authentication**: Supabase Auth (Google OAuth)
- **Deployment**: Vercel

### **Backend**
- **Framework**: Python FastAPI
- **AI Engine**: Google Gemini 1.5 Flash (Advanced Prompt Engineering)
- **Database**: Supabase (PostgreSQL)
- **Orchestration**: Render

### **DevOps & Security**
- **CI/CD**: GitHub Actions (Automated multi-stage pipelines)
- **Database Security**: Row Level Security (RLS) & PL/pgSQL Triggers
- **Monitoring**: IP-based rate limiting & Tiered Quotas

---

## 📂 Project Structure

```text
stackforge/
├── backend/            # FastAPI REST API & AI Service Logic
│   ├── routers/        # Feature-based API endpoints
│   ├── services/       # Core AI (Gemini) & Database logic
│   └── models/         # Pydantic schemas for request/response
├── frontend/           # Next.js 14 Web Application
│   ├── src/app/        # App Router pages and layouts
│   ├── components/     # Reusable React components
│   └── lib/            # API clients & state management
├── database/           # SQL schemas & migrations
├── .github/            # GitHub Actions CI/CD workflows
└── render.yaml         # Render deployment blueprint
```

---

## 🚀 Getting Started

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Dudubynatur3/StackForge.git
   ```

2. **Backend Setup**:
   - Install dependencies: `pip install -r backend/requirements.txt`
   - Configure `.env` with `GOOGLE_API_KEY`, `SUPABASE_URL`, and `SUPABASE_KEY`.
   - Run: `uvicorn backend.main:app --reload`

3. **Frontend Setup**:
   - Install dependencies: `cd frontend && npm install`
   - Configure `.env.local` with `NEXT_PUBLIC_API_URL` and Supabase keys.
   - Run: `npm run dev`

---

## 👨‍💻 Author
**Akintade** — Senior DevSecOps & Platform Engineer

Built with the vision of empowering Cloud Engineers to build better, faster, and smarter.


## Security and deployment (November 2026)

The API authenticates Supabase access tokens on the server and no longer trusts
a client-supplied `user_id`. AI endpoints enforce atomic, database-backed usage
limits. The frontend expects environment-provided Supabase public credentials,
while the backend requires a **server-only service-role key**.

**Before merging or deploying**, run the SQL migration and configure the
Render/Vercel environment variables as described in
[Security and deployment checklist](docs/SECURITY_DEPLOYMENT.md).

GitHub Actions validates the backend API tests, TypeScript, lint and production
frontend build on pull requests. External cloud services require separate smoke
testing. Do not merge until the migration and configuration checklist is complete.
