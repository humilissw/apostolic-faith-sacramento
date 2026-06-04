# Troubleshooting — Node.js Hosting skill

Map symptoms to [contract.md](contract.md) rules and validator IDs.

| Symptom | Contract | Validator | Fix |
|---------|----------|-----------|-----|
| Deploy fails immediately | C2, C4 | E001, E002, E007, E008 | Complete `package.json`; add `main`, `build`, `start` |
| App won't start locally | C4 | E003 | Fix `start` path; ensure `main` file exists |
| Port / connection errors on platform | C5, C6 | E004 | Replace `listen(3000)`; use `host: '0.0.0.0'` for Fastify |
| `Cannot find module` in production | deps | E006 | Move packages from `devDependencies` to `dependencies` |
| Build step skipped / stale assets | C3 | E005 | Add `scripts.build` (real command or `echo build`) |
| Next/Nuxt/Remix blank or old UI | C3 | E005 | Use framework `build`; run install → build → start locally |
| Upload too large | C10 | W004 | Remove `node_modules`, caches from zip |
| Secrets leaked | C8 | W001 | Remove `.env` from upload; use hosting UI for env vars |
| Monorepo upload fails | C1 | — | Upload single package folder only |
| External API unreachable | C11 | — | Use HTTP/HTTPS (80/443) only |
| Database connection fails | C12 | E009, E010 | Use platform MySQL: all five `DB_*` from `process.env`, `mysql2` in `dependencies`; not remote :3306 |

## Validator exit codes

| Code | Meaning |
|------|---------|
| 0 | Pass |
| 1 | Errors — must fix before upload |
| 2 | Warnings only (`--strict` treats warnings as errors) |
