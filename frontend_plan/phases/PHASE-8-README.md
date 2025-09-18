# Phase 8 — Walkthroughs & Sharing (Next.js / React Translation)

## Purpose

Create collaboration tooling that turns scenarios, triggers, and evidence into guided narratives. Analysts curate walkthroughs highlighting key timesteps, triggers, and findings; colleagues can replay them with synchronized timeline, map, network, and analytics panels. Provide export options for sharing insights outside the platform.

## Inputs

**From Phase 7:**
- Trigger metadata (names, descriptions, expected actions) accessible via `useTriggerDraft`
- Timeline controller with ability to jump to specific timesteps and load cached states
- Evidence rail diff utilities and chart/map/network synchronization primitives

**Backend Dependencies:**
- `POST /api/walkthroughs` / `GET /api/walkthroughs` (if existing; otherwise plan for backend addition)
- Scenario snapshot endpoints (`/states/{t}`) already used in prior phases
- Optional export endpoints (PDF generation) if server-managed

## Deliverables

```
frontend/
├── app/(workspace)/walkthroughs/page.tsx                 # Lists walkthroughs, create button
├── app/(workspace)/walkthroughs/WalkthroughBuilder.tsx   # Client wizard for assembling walkthroughs
├── app/(workspace)/walkthroughs/WalkthroughPlayer.tsx    # Presentation mode for replaying narratives
├── app/(workspace)/walkthroughs/components/
│   ├── StepEditor.tsx                                    # Define individual walkthrough steps
│   ├── NarrativeSidebar.tsx                              # Markdown editor for commentary (using TipTap/MDX)
│   ├── PlaybackControls.tsx                              # Controls for stepping through narrative
│   ├── ExportMenu.tsx                                    # Options for PDF/JSON/Share link
│   └── AudienceSettings.tsx                              # Permissions, collaborators, annotations settings
├── app/(workspace)/walkthroughs/hooks/
│   ├── useWalkthroughDraft.ts                           # Zustand store for walkthrough steps
│   ├── useStepBindings.ts                                # Syncs step metadata with timeline/map/network
│   ├── useExportWalkthrough.ts                           # Generates export payloads (PDF/JSON)
│   └── useCollaboration.ts                               # Presence indicators, comments (if enabled)
├── app/(workspace)/walkthroughs/utils/
│   ├── stepSchema.ts                                     # Zod schema mapping to backend model
│   ├── markdownTemplates.ts                              # Example narrative structures
│   └── shareLinks.ts                                     # Generate signed links for read-only view
└── docs/PHASE-8-README.md
```

## Implementation Checklist

### Walkthrough Builder
- [ ] Multi-step editor allowing authors to select timesteps, add annotations, attach triggers/events, and include media (images/video embeds)
- [ ] Step metadata includes: title, description (Markdown), linked triggers, evidence items, spotlighted countries/indicators
- [ ] Provide preview pane showing how step will look in player mode
- [ ] Support reordering steps via drag-and-drop; duplicate step functionality
- [ ] Autosave drafts using `useWalkthroughDraft`; integrate with scenario builder autosave when relevant

### Timeline & Visualization Sync
- [ ] `useStepBindings` ensures each step stores timeline position, selected countries, active layers
- [ ] When playing walkthrough, timeline controller navigates to stored timestep, map and network highlight stored selections, charts load appropriate indicators
- [ ] Provide "snapshot" capture button to populate step fields based on current workspace configuration
- [ ] Allow step to optionally include comparison range (e.g., highlight delta between timesteps) using diff utilities

### Collaboration & Sharing
- [ ] Audience settings specifying visibility (private, team, link-only)
- [ ] Support collaborator mentions/comments within steps (optional for future iteration; at minimum store placeholder)
- [ ] Generate shareable read-only link (signed token) to view walkthrough in player mode without edit access
- [ ] Export options: PDF (via `react-pdf` or server), JSON (structured data), PNG snapshots of key panels (using existing screenshot utilities)

### Walkthrough Player
- [ ] Fullscreen presentation mode with progress indicator, list of steps, and commentary panel
- [ ] Keyboard navigation (`←/→`, space) and remote pointer mode for collaborative sessions
- [ ] Option to auto-play with configurable delay per step
- [ ] Provide "Explain" overlay summarizing triggers/actions referenced in step
- [ ] Ensure player gracefully handles missing data (e.g., step referencing trigger removed later)

### UX & Accessibility
- [ ] Markdown editor accessible with toolbar shortcuts and raw text editing fallback
- [ ] Provide transcripts for any embedded media; ensure exported PDFs maintain contrast + alt text
- [ ] Walkthrough list view displays tags, author, last updated, scenario association
- [ ] Notification system to alert collaborators when walkthrough updated/published

### Testing
- [ ] Unit tests for `stepSchema` ensuring valid payload generation
- [ ] Tests for `useStepBindings` verifying timeline/map/chart sync
- [ ] Component tests for builder (add step, snapshot, reorder) and player (playback, keyboard navigation)
- [ ] Playwright scenario: create walkthrough, add steps referencing triggers, play in presentation mode

## Validation Tests

### Functional
- [ ] Playing walkthrough accurately replays stored state (timeline, map, network, charts)
- [ ] Exported JSON/PDF contains steps with correct metadata and commentary
- [ ] Share link opens player in read-only mode with proper permissions

### Accessibility
- [ ] Player mode supports keyboard navigation and screen reader announcements for each step
- [ ] Markdown content rendered with semantic elements; headings/lists accessible
- [ ] Exported documents meet color contrast and include alt text for images

### Performance
- [ ] Loading walkthrough with 50 steps <2s using lazy loading of heavy assets (maps, charts)
- [ ] Playback transitions remain >50 FPS when switching steps
- [ ] Export operations run asynchronously with progress indicators

## API Integration Notes

- Coordinate with backend for walkthrough storage model; until available, support local JSON export/import as fallback
- Ensure share links integrate with authentication (e.g., token appended, validated via backend route handler)
- Use server actions for publish/unpublish to enforce permissions and audit trails

## Handoff Memo → Phase 9

**What’s Complete:**
- Collaborative storytelling workflow built atop simulation timeline and triggers
- Export/share infrastructure for distributing insights outside SlashRun
- Player synchronized with map, network, time-series, and evidence rail components

**Up Next (Phase 9):**
- Performance, accessibility, and polish enhancements across the app
- Introduce workers, virtualization tweaks, and QA automation per cross-phase architecture
- Finalize theming, micro-interactions, and responsiveness for production readiness

**Integration Notes:**
- Capture performance metrics during playback to inform Phase 9 optimization
- Ensure analytics/logging capture walkthrough usage for future insights
- Maintain typed interfaces for walkthroughs to reuse in export/analytics modules
