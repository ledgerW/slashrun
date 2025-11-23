# New Feature - Feature Development Workflow

⚠️ **PREREQUISITE: Get-Started Workflow Must Be Complete**

This workflow guides you through adding new features to an existing production application. Use this after completing the get-started workflow (Phases 0-9) when you need to add functionality to the system.

---

## 🎯 Workflow Execution Requirements

### 1. Prerequisites

Before starting this workflow, verify:

- [ ] Get-started workflow (Phases 0-9) **100% complete**
- [ ] SYSTEM_REFERENCE.md exists with current architecture
- [ ] PROJECT_REQUIREMENTS.md documents existing features
- [ ] INTEGRATION_CHECKLIST.md shows all systems validated
- [ ] All three services running (Supabase, Next.js, Agent Service if applicable)
- [ ] No outstanding bugs or incomplete features

**Cannot start new feature development until existing system is stable and documented.**

### 2. Phase Execution Pattern: Non-Linear Based on Feature Type

Unlike get-started, new-feature workflow is **non-linear**. Execute only phases relevant to your feature:

```
new-feature.md (Review feature type)
    ↓
Classify Feature Type
    ↓
Execute Only Relevant Phases
    ↓
new-feature.md (Final verification)
```

**Phase Selection Guide:**

| Feature Type | Phases Required |
|--------------|----------------|
| UI-Only Feature (new page/component) | 0, 2, 5 |
| Data Feature (new database entity) | 0, 1, 2, 4, 5 |
| AI Feature (new agent capability) | 0, 3, 4, 5 |
| Complex Feature (all services) | 0, 1, 2, 3, 4, 5 |
| Configuration Change | 0, relevant phase, 5 |

### 3. Feature Complexity Assessment

**Simple Feature** (1-2 days)
- Single service impacted
- No new database entities
- Uses existing patterns
- Examples: New dashboard widget, export function, theme customization

**Moderate Feature** (3-5 days)
- 2 services impacted
- May add database entities
- Some new patterns
- Examples: User preferences system, notification center, search functionality

**Complex Feature** (1-2 weeks)
- All services impacted
- Multiple database entities
- New integration patterns
- Examples: Collaboration features, real-time sync, advanced AI workflows

### 4. Quality Standards

Every feature must maintain:
- ✅ Existing patterns and conventions
- ✅ RLS policies on all new tables
- ✅ Proper error handling with user feedback
- ✅ Loading states on async operations
- ✅ TypeScript strict mode compliance
- ✅ Documentation updates
- ✅ Integration testing
- ✅ No breaking changes to existing features

### 5. Documentation First Approach

Before writing code:
1. Review SYSTEM_REFERENCE.md for architecture
2. Check PROJECT_REQUIREMENTS.md for existing features
3. Identify integration points
4. Plan database changes
5. Design UI mockups
6. Document expected behavior

**Create FEATURE_PLAN.md before implementation.**

---

## 📋 Workflow Phases

### Phase 0: Feature Discovery & Planning [MANDATORY]
**📄 [Full Guide: phase-0-feature-discovery.md](.clinefiles/workflows/new-feature-phases/phase-0-feature-discovery.md)**

**Purpose:** Thoroughly plan the feature before implementation

**Key Outputs:**
- FEATURE_PLAN.md with complete requirements
- Feature classification (Simple/Moderate/Complex)
- Service impact analysis
- Database schema design (if needed)
- UI mockups/wireframes
- Integration point identification

**Cannot proceed without approved feature plan.**

---

### Phase 1: Database Schema Updates [IF NEEDED]
**📄 [Full Guide: phase-1-database-updates.md](.clinefiles/workflows/new-feature-phases/phase-1-database-updates.md)**

**Execute if feature requires:**
- New database tables
- New columns in existing tables
- New relationships between entities
- Updated RLS policies
- New seed data patterns

**Skip if:** Feature is UI-only or uses existing data structures

**Key Tasks:**
- Create migrations following naming conventions
- Add RLS policies for new tables
- Update relationships
- Test data isolation
- Update DATABASE_SCHEMA.md

---

### Phase 2: Next.js Frontend Implementation [IF NEEDED]
**📄 [Full Guide: phase-2-frontend-implementation.md](.clinefiles/workflows/new-feature-phases/phase-2-frontend-implementation.md)**

**Execute if feature requires:**
- New pages or routes
- New UI components
- Form additions
- Navigation updates
- Client-side logic

**Skip if:** Feature is backend-only

**Key Tasks:**
- Create components following shadcn/ui patterns
- Implement forms with validation
- Add navigation items
- Implement loading/error states
- Follow existing UI conventions

---

### Phase 3: Agent Service Integration [IF NEEDED]
**📄 [Full Guide: phase-3-agent-integration.md](.clinefiles/workflows/new-feature-phases/phase-3-agent-integration.md)**

**Critical References:**
- `.clinefiles/langchain/patterns/middleware-centric.md` - **REQUIRED** - Middleware composition pattern
- `.clinefiles/langchain/patterns/middleware-tools.md` - Tools organization
- `.clinefiles/tavily/capabilities-and-integration.md` - Web search integration (if needed)

**Execute if feature requires:**
- New agent tools
- Web search/data extraction capabilities
- Updated prompts/system messages
- New middleware capabilities
- Memory/state changes
- Streaming updates

**Skip if:** Feature doesn't involve AI

**Key Tasks:**
- Create tools using @tool decorator
- Add via ToolsMiddleware (middleware-centric pattern)
- Update tool guidance (tools_prompt.py) with {tools_list} placeholder
- Add Tavily integration if web search needed
- Test in LangGraph Studio
- Integrate with frontend
- Update agent documentation

---

### Phase 4: Integration & End-to-End Testing [MANDATORY IF MULTIPLE PHASES]
**📄 [Full Guide: phase-4-integration-testing.md](.clinefiles/workflows/new-feature-phases/phase-4-integration-testing.md)**

**Execute:** When feature touches 2+ services

**Skip if:** Single-service UI-only feature

**Key Tasks:**
- Test all integration points
- Verify data flows correctly
- Check RLS policies work
- Performance testing
- Security validation
- User acceptance testing

---

### Phase 5: Documentation & System Update [MANDATORY]
**📄 [Full Guide: phase-5-documentation-update.md](.clinefiles/workflows/new-feature-phases/phase-5-documentation-update.md)**

**Always execute:** Every feature requires documentation

**Key Tasks:**
- Update SYSTEM_REFERENCE.md
- Update PROJECT_REQUIREMENTS.md
- Update API documentation
- Create feature user guide
- Update troubleshooting guide
- Final verification checklist

---

## ✅ Feature Development Checklist

### Pre-Development
- [ ] Feature requirements clearly defined
- [ ] FEATURE_PLAN.md created and reviewed
- [ ] Feature complexity assessed
- [ ] Required phases identified
- [ ] Existing patterns reviewed in codebase
- [ ] Integration points identified

### Development (Phase-Specific)
- [ ] Database migrations created (if Phase 1)
- [ ] RLS policies added/updated (if Phase 1)
- [ ] UI components implemented (if Phase 2)
- [ ] Forms validated (if Phase 2)
- [ ] Agent tools added (if Phase 3)
- [ ] Streaming tested (if Phase 3)

### Integration Testing (If Multiple Phases)
- [ ] Database → Frontend tested
- [ ] Frontend → Agent Service tested
- [ ] Agent → Database tested
- [ ] RLS policies validated
- [ ] Performance acceptable
- [ ] Security validated

### Documentation
- [ ] SYSTEM_REFERENCE.md updated
- [ ] PROJECT_REQUIREMENTS.md updated
- [ ] Feature documentation created
- [ ] API docs updated (if applicable)
- [ ] Troubleshooting guide updated

### Final Verification
- [ ] Feature works as specified
- [ ] No existing features broken
- [ ] Loading states present
- [ ] Error handling comprehensive
- [ ] User feedback clear
- [ ] Code follows project conventions
- [ ] Tests passing (if applicable)

---

## 🔄 Common Feature Patterns

### Pattern 1: Add New Dashboard Page

**Phases:** 0, 2, 5 (Simple)

**Steps:**
1. Create page in `app/dashboard/new-feature/page.tsx`
2. Add navigation item to sidebar
3. Fetch and display data
4. Update documentation

**Example:** Analytics dashboard, reports page, settings section

---

### Pattern 2: Add New Database Entity with CRUD

**Phases:** 0, 1, 2, 4, 5 (Moderate)

**Steps:**
1. Create migration for new table
2. Add RLS policies
3. Create list/detail/create/edit pages
4. Add form components
5. Test integration
6. Update documentation

**Example:** New resource type, user preferences, notification system

---

### Pattern 3: Add New Agent Capability

**Phases:** 0, 3, 4, 5 (Moderate)

**Steps:**
1. Design tool functionality
2. Implement @tool function
3. Add to agent tools list
4. Test in LangGraph Studio
5. Integrate with frontend
6. Update documentation

**Example:** New research capability, data analysis tool, external API integration

---

### Pattern 4: Add Real-Time Feature

**Phases:** 0, 1, 2, 4, 5 (Complex)

**Steps:**
1. Set up database triggers (Phase 1)
2. Configure Realtime subscription (Phase 2)
3. Implement client-side updates (Phase 2)
4. Test multi-user scenarios (Phase 4)
5. Update documentation (Phase 5)

**Example:** Live collaboration, activity feeds, presence indicators

---

### Pattern 5: Add User Preference/Setting

**Phases:** 0, 1, 2, 5 (Simple to Moderate)

**Steps:**
1. Add column to profiles or create preferences table
2. Create settings form
3. Save/load preference
4. Apply preference throughout app
5. Update documentation

**Example:** Theme preferences, notification settings, display options

---

## 🚨 Common Pitfalls to Avoid

### Pitfall 1: Starting Code Before Planning
**Problem:** Rushing into implementation without understanding impact
**Solution:** Always complete Phase 0 with FEATURE_PLAN.md first

### Pitfall 2: Breaking Existing Patterns
**Problem:** Introducing new patterns when existing ones work
**Solution:** Review SYSTEM_REFERENCE.md and match existing code

### Pitfall 3: Forgetting RLS Policies
**Problem:** New tables without security policies
**Solution:** Every new table needs RLS policies in Phase 1

### Pitfall 4: Skipping Integration Testing
**Problem:** Feature works in isolation but breaks integration
**Solution:** Always test integration points (Phase 4)

### Pitfall 5: Poor Documentation
**Problem:** Future developers can't understand the feature
**Solution:** Comprehensive updates in Phase 5

### Pitfall 6: Not Testing User Isolation
**Problem:** Data leaks between users
**Solution:** Test with 2 users, verify RLS works

### Pitfall 7: Ignoring Loading States
**Problem:** Poor user experience during async operations
**Solution:** Add loading states for all async actions

### Pitfall 8: Breaking Existing Features
**Problem:** New feature causes regressions
**Solution:** Test existing features still work after changes

---

## 📊 Progress Tracking

### Update WORKFLOW_CHECKPOINT.md

After each phase completion:

```markdown
## Current Feature: [Feature Name]

### Feature Status
- Status: In Progress
- Started: [Date]
- Complexity: Moderate
- Phases Required: 0, 1, 2, 4, 5

### Completed Phases
- [x] Phase 0: Feature Discovery - FEATURE_PLAN.md created
- [x] Phase 1: Database Updates - Migration created, RLS policies added
- [ ] Phase 2: Frontend Implementation - In progress
- [ ] Phase 4: Integration Testing
- [ ] Phase 5: Documentation Update

### Key Decisions
- Using existing user preferences pattern
- Adding to dashboard sidebar
- No agent integration needed

### Issues Encountered
- RLS policy needed adjustment for junction table
- Resolved by adding policy for both sides of relationship
```

---

## 🎯 Feature Completion Criteria

Before marking feature complete:

### Functionality
- [ ] Feature works exactly as specified in FEATURE_PLAN.md
- [ ] All user scenarios tested and working
- [ ] Edge cases handled gracefully
- [ ] Error messages clear and helpful

### Quality
- [ ] Code follows project conventions
- [ ] TypeScript types correct
- [ ] No console errors or warnings
- [ ] Performance acceptable
- [ ] Security validated

### Integration
- [ ] No existing features broken
- [ ] All integration points tested
- [ ] RLS policies working correctly
- [ ] Data isolation verified

### Documentation
- [ ] SYSTEM_REFERENCE.md updated
- [ ] PROJECT_REQUIREMENTS.md updated
- [ ] Feature documentation complete
- [ ] Code comments where needed

### User Experience
- [ ] Loading states implemented
- [ ] Empty states handled
- [ ] Error states managed
- [ ] Success feedback provided
- [ ] Navigation intuitive

---

## 📚 Next Steps After Feature Completion

1. **User Testing** - Have users test the feature
2. **Gather Feedback** - Document improvement ideas
3. **Monitor Performance** - Watch for issues in production
4. **Plan Iterations** - Identify enhancements for v2
5. **Start Next Feature** - Return to Phase 0 for next feature

---

## 🔄 Workflow Version

**Version:** 1.0
**Last Updated:** 2025-01-11
**Compatible with:** get-started workflow v1.0
**Requires:** Completed get-started Phases 0-9

---

## 📖 Additional Resources

- **get-started.md** - Initial application setup workflow
- **SYSTEM_REFERENCE.md** - Current system architecture
- **PROJECT_REQUIREMENTS.md** - Existing features and entities
- **INTEGRATION_CHECKLIST.md** - Integration validation patterns
- **.clinefiles/guide-index.md** - Development patterns and guides
