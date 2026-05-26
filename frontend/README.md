# Docquery — Frontend

React 19 + Vite frontend for Docquery.

**Live:** https://docquery-app.netlify.app
**Backend:** https://github.com/harshgolani/docquery/tree/main/backend

## Stack

- React 19
- Vite
- react-markdown (answer rendering)
- Pure CSS (no component library)

## Run locally

```bash
npm install
npm run dev
```

Requires backend running at `http://localhost:8000`. Update `API` constant in `src/App.jsx` to switch between local and production backend.

## Structure

```
src/
├── App.jsx          # Root component, all state management
├── App.css          # All styles
└── components/
    ├── Sidebar.jsx  # Document list + upload
    ├── Chat.jsx     # Chat interface + input
    └── Message.jsx  # Single message with sources
```
