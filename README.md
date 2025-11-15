# AI-Native Application Template

A comprehensive template for building production-ready AI-native applications with an opinionated infrastructure stack and workflow-driven development.

## 🎯 What Is This Template?

This template provides a complete foundation for building modern AI-native applications with:

- **Opinionated Stack:** Next.js + Supabase + LangChain - battle-tested technologies
- **Workflow-Driven Development:** Step-by-step guides in `.clinerules/workflows/`
- **Production Patterns:** Best practices built-in from day one
- **AI-First Architecture:** Designed for agentic and generative capabilities
- **Comprehensive Documentation:** Detailed guides for every aspect

## 🏗️ Template Structure

```
template-repo/
├── .clinerules/              # Workflow guides and best practices
│   ├── workflows/           # Development workflows (get-started, new-feature)
│   ├── langchain/          # LangChain patterns and guides
│   ├── supabase/           # Supabase patterns and guides
│   └── ui/                 # UI patterns and component guides
├── .gitignore.template     # User .gitignore (tracks service folders)
├── .gitignore             # Template dev .gitignore (ignores service folders)
├── .env.example            # Template environment variables
└── README.md              # This file

# Created by workflows (not in template):
├── nextjs_/                 # Next.js application service
├── supabase_/              # Supabase database service
├── langchain_/             # LangChain AI service (Phase 8)
└── project/                # AI assistant progress tracking
    ├── services/          # Service-specific docs
    ├── decisions/         # Architecture decisions
    └── WORKFLOW_CHECKPOINT.md
```

## 📚 Core Services

### nextjs_/
Frontend application built with:
- Next.js 16 with App Router
- TypeScript (strict mode)
- Tailwind CSS v3
- shadcn/ui components
- Supabase Auth & Realtime

### supabase_/
Backend services including:
- PostgreSQL database
- Row Level Security (RLS)
- Authentication system
- Real-time subscriptions
- File storage (optional)

### langchain_/
AI agent service featuring:
- LangChain/LangGraph framework
- Middleware-centric architecture
- LangSmith deployment platform
- Automatic memory management
- Production patterns

## 🚀 Quick Start

### Prerequisites

**Required:**
- Node.js 18+ and npm
- Python 3.11+
- Docker Desktop (for Supabase)
- Supabase CLI
- Git

**For AI Service:**
- uv package manager (`pip install uv`)
- OpenAI or Anthropic API key
- LangSmith account

### Installation

1. **Clone or use this template:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Initialize your project's .gitignore:**
   ```bash
   # Copy the template .gitignore for your project
   cp .gitignore.template .gitignore
   ```
   
   **Important:** The template repository uses `.gitignore` to exclude service folders during template development. When you start a new project, you need to replace it with `.gitignore.template`, which properly tracks service folders while ignoring only build artifacts and environment files.

3. **Start your first workflow:**
   ```bash
   # Open in your preferred IDE
   code .
   
   # Review the get-started workflow
   cat .clinerules/workflows/get-started.md
   ```

3. **Follow the workflow phases:**
   The template includes comprehensive workflows that guide you step-by-step through building your application. See "Using the Workflows" section below.

## 📖 Using the Workflows

This template includes two main workflows:

### Get-Started Workflow
**Purpose:** Building a new AI-native application from scratch

**Phases:**
1. **Discovery** - Define your application requirements
2. **Supabase Setup** - Database, auth, and RLS
3. **Next.js Setup** - Frontend application
4. **Marketing & UI** - Landing page and dashboard
5. **CRUD Implementation** - Full data operations
6. **User Management** - Profiles and settings
7. **Advanced Features** - ReactFlow, realtime, etc.
8. **Polish & Docs** - Production-ready polish
9. **AI Service** - LangChain agent integration
10. **System Review** - Final validation

**Start here:** `.clinerules/workflows/get-started.md`

### New-Feature Workflow
**Purpose:** Adding features to existing applications

**Phases:**
1. **Feature Discovery** - Planning and requirements
2. **Database Updates** - Schema changes (if needed)
3. **Frontend Implementation** - UI components (if needed)
4. **Agent Integration** - AI capabilities (if needed)
5. **Integration Testing** - End-to-end validation
6. **Documentation** - Update docs (always required)

**Start here:** `.clinerules/workflows/new-feature.md`

## 🤖 Working with AI Coding Assistants

This template is optimized for AI-powered development:

### Plan Mode vs Act Mode
- **Plan Mode:** Gather information, discuss approach, create detailed plans
- **Act Mode:** Execute changes, write code, modify files

### Workflow Integration
1. Start in Plan Mode to review workflow phase
2. AI assistant reads relevant guides from `.clinerules/`
3. Switch to Act Mode for implementation
4. AI follows step-by-step instructions
5. Return to Plan Mode for next phase planning

### Progress Tracking
The AI assistant creates a `project/` folder during development to track:
- **WORKFLOW_CHECKPOINT.md** - Overall progress through phases
- **project/services/** - Service-specific implementation notes
- **project/decisions/** - Architecture decision records

This folder is created during development and specific to your project, not part of the template.

## 🎨 Key Features

### Built-In Best Practices
- ✅ TypeScript strict mode throughout
- ✅ Comprehensive error handling
- ✅ Loading states on all async operations
- ✅ Toast notifications for user feedback
- ✅ Row Level Security on all tables
- ✅ Middleware-centric agent architecture

### Production-Ready Patterns
- ✅ Environment variable management
- ✅ Authentication with SSR support
- ✅ Database migrations and seeding
- ✅ Real-time subscriptions
- ✅ AI agent streaming responses
- ✅ Comprehensive documentation

### Developer Experience
- ✅ Hot reload in development
- ✅ Local Supabase with Docker
- ✅ LangGraph Studio for agent testing
- ✅ shadcn/ui component library
- ✅ Detailed troubleshooting guides

## 📚 Documentation Structure

### Template Documentation (.clinerules/)
**Never modify these files** - they are reusable workflow templates:
- Workflow guides for development processes
- Pattern guides for implementation
- Best practices and conventions
- Troubleshooting references

### Project Documentation (project/)
**Created by AI assistant during development:**
- The workflow creates this folder to track progress
- Documents your specific implementation decisions
- Records architecture choices and service-specific notes
- Not part of the template - unique to each project

## 🔧 Environment Configuration

Copy `.env.example` to create your environment files:

```bash
# For Next.js
cp .env.example nextjs_/.env.local

# For LangChain (created in Phase 8)
cp .env.example langchain_/.env
```

Required variables:
- `NEXT_PUBLIC_SUPABASE_URL` - From `supabase start`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - From `supabase start`
- `NEXT_PUBLIC_AGENT_API_URL` - LangChain service URL
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - LLM provider

## 🎯 Development Workflow

### Starting Development

1. **Start Supabase:**
   ```bash
   cd supabase_
   supabase start
   ```

2. **Start Next.js:**
   ```bash
   cd nextjs_
   npm install
   npm run dev
   ```

3. **Start AI Service (Phase 8+):**
   ```bash
   cd langchain_
   langgraph dev
   ```

### Common Commands

**Supabase:**
```bash
supabase start          # Start local instance
supabase stop           # Stop local instance
supabase db reset       # Reset and rerun migrations
supabase db diff        # Generate migration from changes
```

**Next.js:**
```bash
npm run dev            # Development server
npm run build          # Production build
npm run lint           # Run linter
```

**LangChain:**
```bash
uv add <package>       # Add Python package (NOT pip!)
langgraph dev          # Start dev server with Studio
langgraph push         # Deploy to LangSmith
```

## 📖 Learning Resources

### Essential Reading
Before starting, familiarize yourself with:
1. `.clinerules/workflows/get-started.md` - Main workflow anchor
2. `.clinerules/guide-index.md` - Complete guide catalog

### Key Guides by Topic

**Authentication:**
- `.clinerules/supabase/auth-for-nextjs.md` - **CRITICAL** SSR patterns

**Database:**
- `.clinerules/supabase/database/create_migrations.md` - Migration patterns
- `.clinerules/supabase/database/create_rls_policies.md` - Security policies

**AI Agents:**
- `.clinerules/langchain/patterns/middleware-centric.md` - **CRITICAL** agent architecture
- `.clinerules/langchain/core/short-term-memory.md` - Thread memory
- `.clinerules/langchain/core/long-term-memory.md` - Persistent storage

**UI Components:**
- `.clinerules/ui/shadcn-components.md` - Component catalog
- `.clinerules/ui/shadcn-blocks.md` - Pre-built patterns

## 🚢 Deployment

> **⚠️ COMING SOON:** Comprehensive deployment guides and CI/CD pipelines are currently in development. Manual deployment is supported via the platforms below.

### Next.js Frontend
**Recommended:** Vercel
```bash
# Connect repo to Vercel
vercel

# Set environment variables in Vercel dashboard
# Deploy
vercel --prod
```

### Supabase Database
**Recommended:** Supabase Cloud
```bash
# Create project in Supabase dashboard
# Link local to cloud
supabase link --project-ref <your-ref>

# Push migrations
supabase db push
```

### LangChain Service
**Recommended:** LangSmith Platform
```bash
# Push to LangSmith
langgraph push

# Configure in LangSmith dashboard
# Monitor in production
```

### CI/CD Automation
> **⚠️ COMING SOON:** Automated deployment pipelines, testing workflows, and infrastructure-as-code configurations.

## 🐛 Troubleshooting

### Common Issues

**"Supabase won't start"**
- Ensure Docker Desktop is running
- Check ports 54321-54325 are not in use
- Try `supabase stop` then `supabase start`

**"Next.js auth not working"**
- Verify `NEXT_PUBLIC_SUPABASE_ANON_KEY` (not PUBLISHABLE_KEY)
- Check Supabase client files use getAll/setAll cookies
- Review `.clinerules/supabase/auth-for-nextjs.md`

**"Agent memory not persisting"**
- Confirm using `thread_id` parameter
- Verify NOT manually instantiating PostgresSaver
- Check `.clinerules/langchain/core/short-term-memory.md`

**"Python dependencies failing"**
- Always use `uv add`, never `pip install`
- Check Python version is 3.11+
- Review `.clinerules/langchain/langsmith/local-development.md`

### Getting Help

1. **Check relevant guide in `.clinerules/`**
2. **Review phase-specific troubleshooting**
3. **Search workflow checkpoint for similar issues**
4. **Consult official documentation:**
   - Next.js: https://nextjs.org/docs
   - Supabase: https://supabase.com/docs
   - LangChain: https://python.langchain.com/

## 🤝 Contributing

This template is designed to be customized for your project. However, if you discover improvements to the workflow templates:

1. Document the improvement
2. Test thoroughly
3. Update relevant `.clinerules/` guides
4. Share with the community

## 📄 License

[Your License Here]

## 🎉 Getting Started

Ready to build your AI-native application?

1. **Read:** `.clinerules/workflows/get-started.md`
2. **Prepare:** Install prerequisites above
3. **Begin:** Follow Phase 0 - Application Discovery
4. **Build:** Execute phases systematically
5. **Deploy:** Ship your production-ready app

The workflow guides you every step of the way. Happy building! 🚀

---

**Questions?** Review `.clinerules/guide-index.md` for a complete catalog of available guides and patterns.
