# Frontend

Modern frontend learning with **React 18 + TypeScript + Vite**, tested with
**Vitest + React Testing Library**.

## Planned structure

```
frontend/
├── react-app/            # the main Vite app (scaffolded when code lands)
│   ├── src/
│   │   ├── components/       # reusable UI components
│   │   ├── hooks/            # custom hooks
│   │   ├── state/            # state management (Context / Zustand / Redux Toolkit)
│   │   ├── api/              # API clients, data fetching (fetch / axios / react-query)
│   │   ├── pages/           # route-level components
│   │   └── types/           # shared TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── components/           # notes on component patterns
├── state-management/     # notes: local vs global state, when to reach for a library
├── api-integration/      # notes: fetching, caching, error/loading states
└── architecture/         # notes: folder structure, module boundaries, scaling a FE app
```

## Scaffold the app (when ready)

```bash
cd frontend
npm create vite@latest react-app -- --template react-ts
cd react-app
npm install
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
npm run dev
```

## Topics
- TypeScript essentials for React
- Components, props, composition
- Hooks (`useState`, `useEffect`, `useMemo`, custom hooks)
- State management options and trade-offs
- Data fetching and API integration
- Accessibility (target WCAG 2.2 AA)
- Testing with Vitest + RTL

## Status
Skeleton / documentation. The Vite app is scaffolded when frontend code work begins.
