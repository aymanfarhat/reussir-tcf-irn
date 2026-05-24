# Frontend AGENTS.md

## Purpose

`frontend/` is the Nuxt 3 user-facing app for TCF IRN practice.

The browser calls Nuxt routes. Nuxt server routes proxy `/api/*` to Django with cookies and CSRF forwarding, so the browser does not need direct CORS access to Django.

## Commands

```bash
npm install
npm run dev
npm run build
npm run lint
```

## Structure

- `pages/`: route surfaces matching the original Django user flows.
- `components/`: reusable UI kit and feature components.
- `composables/`: session, API, timer, word count, recorder, scoring helpers.
- `server/api/[...path].ts`: generic BFF proxy to Django.
- `server/utils/djangoProxy.ts`: cookie/CSRF forwarding and snake_case/camelCase mapping.
- `assets/css/base.css`: Tailwind 4 theme tokens and shared component classes.

## UX Rules

- Preserve existing workflows and business behavior.
- Keep current color semantics:
  - indigo for oral/primary
  - emerald for written
  - amber for warnings
  - red for errors
  - lime for high scores
- Do not move grading, scoring, or selection logic into Vue.
- Keep task-local browser behavior in composables/components: timers, word counts, recording, question playback.
