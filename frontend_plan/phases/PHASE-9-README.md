# Phase 9 — Performance & Polish (Next.js / React Translation)

## Purpose

Finalize the SlashRun frontend for production by optimizing performance, accessibility, and reliability. Address bottlenecks surfaced in prior phases, implement worker-based computations, tighten lint/test automation, and ensure the Gotham aesthetic is refined across devices.

## Inputs

**From Phase 8:**
- Full feature set implemented (timeline, evidence rail, map, network, time-series, builder, triggers, walkthroughs)
- Usage telemetry/performance data collected during walkthrough playback and heavy simulations

**Cross-Phase Considerations:**
- Component library coverage (Storybook), testing infrastructure, lint rules
- Design tokens and theming from Phase 0/1

## Deliverables

```
frontend/
├── performance/
│   ├── profiler-report.md                    # Findings from React Profiler/Chrome DevTools
│   ├── optimization-plan.md                  # Prioritized fixes
│   └── benchmarks/                           # Scripts + results for FPS/memory benchmarks
├── workers/
│   ├── diffWorker.ts                         # Offloads JSON diff calculations
│   ├── networkMetricsWorker.ts               # Centrality/clustering computations
│   └── forecastWorker.ts                     # Time-series forecasting calculations
├── app/(workspace)/_providers/
│   └── WorkerProvider.tsx                    # Manages worker pool + message passing
├── scripts/
│   ├── lighthouse.mjs                        # Automated Lighthouse runs
│   ├── accessibility-check.mjs               # Axe/Pally CLI integration
│   └── bundle-analyze.mjs                    # Uses Next.js analyze output
├── .github/workflows/frontend-ci.yml         # CI pipeline for lint/test/build/storybook/playwright
├── docs/PHASE-9-README.md
```

## Implementation Checklist

### Performance Optimization
- [ ] Profile timeline scrubbing, map overlays, network simulation, and time-series rendering using React Profiler and Chrome DevTools
- [ ] Move heavy computations to Web Workers (diffs, network metrics, forecasting)
- [ ] Implement memoization and virtualization improvements (e.g., evidence rail virtualization tuning, chart data memoization)
- [ ] Optimize bundle size: code-split rarely used modules (builder, walkthroughs) via dynamic import
- [ ] Ensure Next.js image optimization used for icons/screenshots; prefetch critical fonts with `next/font`
- [ ] Use `React.Suspense` boundaries to stream large data visualizations while preserving shell responsiveness

### Accessibility
- [ ] Run automated Axe/Pally audits across key pages (workspace, builder, player)
- [ ] Manual screen reader testing (NVDA/VoiceOver) verifying announcements for timeline, map, network, and charts
- [ ] Ensure keyboard trap prevention, skip links, focus outlines consistent across components
- [ ] Provide alt text for exported media, ensure color contrast meets WCAG AA in all states
- [ ] Update documentation describing accessibility patterns and compliance results

### Reliability & QA
- [ ] Expand unit/integration test coverage to >90% for critical modules (timeline controller, map hooks, network interactions)
- [ ] Harden error boundaries with user-friendly fallbacks and logging to telemetry service
- [ ] Implement retry/backoff policies for WebSocket reconnects and API fetch failures
- [ ] Add offline/slow-network indicators and gracefully degrade visualizations when data missing
- [ ] Verify autosave, drafts, and localStorage usage handle quota/full scenarios gracefully

### Tooling & CI/CD
- [ ] Configure GitHub Actions workflow running: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, `pnpm storybook:ci`, `pnpm playwright test`, `pnpm lighthouse`
- [ ] Integrate bundle analyzer into CI with threshold enforcement (e.g., < 800KB per route)
- [ ] Set up visual regression (Chromatic or Loki) as optional gating check
- [ ] Add pre-commit hooks via Husky + lint-staged for formatting/testing on staged files
- [ ] Document deployment process (Vercel or containerized) including environment variables for API base URLs

### UX Polish
- [ ] Refine Gotham theme: ensure consistent spacing, elevation, subtle glows, and motion durations
- [ ] Add micro-interactions (Framer Motion) for panel transitions, button presses, timeline scrubbing feedback
- [ ] Ensure responsive behavior on tablets/laptops (minimum width 1280px, degrade gracefully down to 1024px)
- [ ] Provide loading skeletons for all async panels, unify spinner styles
- [ ] Localize UI strings (prepare for i18n) using Next.js `appDir` localization primitives

### Documentation
- [ ] Update Storybook with final component states, usage notes, and accessibility annotations
- [ ] Produce `profiler-report.md` summarizing findings and improvements
- [ ] Update onboarding docs for developers (architecture overview, coding standards, test commands)
- [ ] Create runbooks for common operations (clearing caches, refreshing tokens, diagnosing WebSocket issues)

### Testing
- [ ] Regression run of entire Playwright suite after optimizations
- [ ] Lighthouse performance target: LCP < 2.5s, TBT < 200ms, Performance score ≥ 90 on workbench route
- [ ] Accessibility score ≥ 95 on major flows (login, workbench, builder, walkthrough player)
- [ ] Memory leak testing via Chrome Performance (no unbounded growth during 10-minute simulation playback)

## Validation Tests

### Functional
- [ ] All major flows (auth → workbench → timeline/map/network/charts → builder → triggers → walkthrough) execute without console errors or regressions
- [ ] Worker fallbacks: if worker unsupported, gracefully fallback to main thread with warning
- [ ] Offline mode: limited functionality (view cached states, read walkthroughs) with clear messaging

### Performance
- [ ] Timeline scrubbing remains smooth (≥55 FPS) with caches warmed and 1k timesteps
- [ ] Map + network combined overlays maintain ≥40 FPS during playback
- [ ] Time-series panel rendering stays under 16ms per frame for 5 charts × 1k points each (post-optimization)

### Accessibility & UX
- [ ] Screen reader announcement coverage validated for all interactive components
- [ ] Keyboard-only users can access entire workflow without pointer
- [ ] Micro-interactions respect reduced-motion preferences (CSS `prefers-reduced-motion`)

## API Integration Notes

- Monitor API request rates during performance testing to ensure backend can handle load; coordinate caching strategies if needed
- Consider server-provided aggregated endpoints to reduce client computation (if repeated transformations remain heavy)
- Ensure telemetry/logging data forwarded to backend observability stack (if configured)

## Handoff / Launch Checklist

- [ ] All docs updated, Storybook published, CI pipeline green
- [ ] Performance budget and accessibility reports shared with stakeholders
- [ ] Launch runbook prepared (rollback plan, monitoring alerts configured)
- [ ] Post-launch review plan defined (metrics, user feedback sessions)
