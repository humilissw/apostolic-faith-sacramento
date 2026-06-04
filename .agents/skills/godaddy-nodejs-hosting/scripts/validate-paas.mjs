#!/usr/bin/env node
/**
 * Node.js Hosting deploy contract validator.
 * Usage: node validate-paas.mjs <project-dir> [--strict]
 * Exit: 0 pass, 1 errors, 2 warnings only
 */

import { readFileSync, existsSync, readdirSync, statSync, lstatSync } from 'fs';
import { sep } from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const RUNTIME_PACKAGES = [
  'express',
  'fastify',
  'koa',
  'hono',
  '@hono/node-server',
  'next',
  'nuxt',
  '@nestjs/core',
  '@remix-run/serve',
  'remix-serve',
];

const BUILD_REQUIRED = [
  { match: (deps) => deps.next, name: 'next', hint: 'next build' },
  { match: (deps) => deps.nuxt, name: 'nuxt', hint: 'nuxt build' },
  {
    match: (deps) =>
      deps['@remix-run/node'] || deps['@remix-run/react'] || deps.remix,
    name: 'remix',
    hint: 'remix build',
  },
  { match: (deps) => deps['@nestjs/core'], name: 'nestjs', hint: 'nest build' },
  { match: (deps) => deps.vite, name: 'vite', hint: 'vite build' },
  {
    match: (deps) => deps['react-scripts'],
    name: 'react-scripts',
    hint: 'react-scripts build',
  },
];

const KNOWN_START_COMMANDS = new Set([
  'next',
  'nuxt',
  'remix-serve',
  'nest',
  'node',
  'npm',
  'npx',
  'pnpm',
  'yarn',
]);

const SKIP_DIRS = new Set([
  'node_modules',
  'dist',
  'build',
  '.next',
  '.output',
  '.git',
  'coverage',
]);

const DB_ENV_VARS = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'];

const MYSQL_CLIENT_PACKAGES = [
  'mysql2',
  'sequelize',
  'knex',
  'typeorm',
  'mariadb',
];

const errors = [];
const warnings = [];

function clearResults() {
  errors.length = 0;
  warnings.length = 0;
}

function err(id, message) {
  errors.push({ id, message });
}

function warn(id, message) {
  warnings.push({ id, message });
}

function readJson(filePath) {
  try {
    return JSON.parse(readFileSync(filePath, 'utf8'));
  } catch (e) {
    err('E001', `Invalid JSON: ${filePath} (${e.message})`);
    return null;
  }
}

function allDeps(pkg) {
  return { ...pkg.dependencies, ...pkg.devDependencies, ...pkg.peerDependencies };
}

/** Split a start script into tokens (respects single/double quotes). */
function tokenizeStartScript(script) {
  const tokens = [];
  const re = /'([^']*)'|"([^"]*)"|(\S+)/g;
  let m;
  while ((m = re.exec(script)) !== null) {
    tokens.push(m[1] ?? m[2] ?? m[3]);
  }
  return tokens;
}

/**
 * Parse `node ...` start scripts. Plain `node <file>` is verified. Any Node flags -> unverified (W003).
 * @returns {{ kind: 'entry', path: string } | { kind: 'node-unverified' } | { kind: 'not-node' }}
 */
export function parseNodeStart(startScript) {
  const trimmed = startScript.trim();
  const tokens = tokenizeStartScript(trimmed);
  if (tokens[0] !== 'node') return { kind: 'not-node' };

  const args = tokens.slice(1);
  if (args.some((t) => t.startsWith('-'))) {
    return { kind: 'node-unverified' };
  }

  const entry = args[0];
  return entry ? { kind: 'entry', path: entry } : { kind: 'node-unverified' };
}

/** Reject absolute paths and `..` segments (e.g. from package.json start script). */
function isSafeRelativePath(rel) {
  if (typeof rel !== 'string' || rel.length === 0 || rel.includes('\0')) {
    return false;
  }
  if (rel.startsWith('/') || rel.startsWith('\\')) return false;
  if (/^[A-Za-z]:[\\/]/.test(rel)) return false;
  return !rel.split(/[/\\]/).includes('..');
}

function projectRootPrefix(projectRoot) {
  return projectRoot.endsWith(sep) ? projectRoot : projectRoot + sep;
}

/** `projectRoot` must be absolute (from canonicalProjectDir). */
function isUnderProjectRoot(projectRoot, target) {
  if (target === projectRoot) return true;
  return target.startsWith(projectRootPrefix(projectRoot));
}

/** Append safe relative segments to an absolute base (no path.join / path.resolve). */
function appendPath(base, ...parts) {
  let target = base.endsWith(sep) ? base.slice(0, -1) : base;
  for (const part of parts) {
    if (!isSafeRelativePath(part)) return null;
    const normalized = part.split(/[/\\]/).filter(Boolean).join(sep);
    target = target + sep + normalized;
  }
  return target;
}

/** Build a path under project root; return null if outside root. */
function pathUnderProjectRoot(projectRoot, ...segments) {
  const target = appendPath(projectRoot, ...segments);
  if (!target || !isUnderProjectRoot(projectRoot, target)) return null;
  return target;
}

function isSafeDirEntry(name) {
  return (
    name.length > 0 &&
    name !== '.' &&
    name !== '..' &&
    !name.includes('\0') &&
    !name.includes('/') &&
    !name.includes('\\')
  );
}

function appendDirEntry(dir, name) {
  return dir.endsWith(sep) ? dir + name : dir + sep + name;
}

function findEntryFile(projectRoot, entry) {
  if (!isSafeRelativePath(entry)) return null;
  const candidates = [
    entry,
    `${entry}.js`,
    `${entry}.mjs`,
    `${entry}.cjs`,
  ];
  for (const c of candidates) {
    if (!isSafeRelativePath(c)) continue;
    const p = pathUnderProjectRoot(projectRoot, c);
    if (p && existsSync(p)) return p;
  }
  return null;
}

function validateStartScript(projectRoot, startScript) {
  const first = startScript.split(/\s+/)[0];
  const parsed = parseNodeStart(startScript);

  if (parsed.kind === 'entry') {
    if (!findEntryFile(projectRoot, parsed.path)) {
      err('E003', `Start script entry file not found: ${parsed.path}`);
    }
    return;
  }

  if (parsed.kind === 'node-unverified') {
    warn('W003', `Could not verify start script entry: ${startScript}`);
    return;
  }

  if (KNOWN_START_COMMANDS.has(first)) {
    return;
  }

  if (first.startsWith('.')) {
    if (!findEntryFile(projectRoot, first)) {
      err('E003', `Start script entry file not found: ${first}`);
    }
    return;
  }

  warn('W003', `Could not verify start script target: ${startScript}`);
}

function needsBuild(deps) {
  return BUILD_REQUIRED.filter((r) => r.match(deps));
}

function checkBuildScript(pkg, deps) {
  if (pkg.scripts?.build?.trim()) return;
  const required = needsBuild(deps);
  if (required.length > 0) {
    const names = required.map((r) => r.name).join(', ');
    const hints = required.map((r) => r.hint).join(', ');
    err(
      'E005',
      `Missing scripts.build (required for ${names}; e.g. ${hints})`,
    );
  } else {
    err(
      'E005',
      'Missing or empty scripts.build (use "echo build" if nothing needs compiling)',
    );
  }
}

function checkPackageMetadata(pkg, projectRoot) {
  if (!pkg.name || !String(pkg.name).trim()) {
    err('E007', 'Missing or empty package.json "name"');
  }
  if (!pkg.version || !String(pkg.version).trim()) {
    err('E007', 'Missing or empty package.json "version"');
  }
  const main = pkg.main;
  if (!main || !String(main).trim()) {
    err('E008', 'Missing or empty package.json "main"');
    return;
  }
  const mainRel = String(main).trim();
  if (!isSafeRelativePath(mainRel)) {
    err('E008', 'package.json "main" must be a safe relative path');
    return;
  }
  const mainPath = pathUnderProjectRoot(projectRoot, mainRel);
  if (!mainPath || !existsSync(mainPath)) {
    err('E008', `package.json "main" file not found: ${mainRel}`);
  }
}

function checkUploadHygiene(projectRoot) {
  const nm = pathUnderProjectRoot(projectRoot, 'node_modules');
  if (nm && existsSync(nm)) {
    warn(
      'W004',
      'node_modules present — exclude from deployment (zip or Git); platform runs install',
    );
  }
}

export function envVarReferencedInContent(content, varName) {
  const patterns = [
    new RegExp(`process\\.env\\.${varName}\\b`),
    new RegExp(`process\\.env\\?\\.${varName}\\b`),
    new RegExp(`process\\.env\\[\\s*['"]${varName}['"]\\s*\\]`),
  ];
  if (patterns.some((re) => re.test(content))) return true;
  return new RegExp(`\\b${varName}\\b[^=]*=\\s*process\\.env`).test(content);
}

function envVarReferencedInFiles(files, varName) {
  for (const file of files) {
    let content;
    try {
      content = readFileSync(file, 'utf8');
    } catch {
      continue;
    }
    if (envVarReferencedInContent(content, varName)) return true;
  }
  return false;
}

function usesMysqlFromPrisma(projectRoot) {
  const schemaPath = pathUnderProjectRoot(projectRoot, 'prisma', 'schema.prisma');
  if (!schemaPath || !existsSync(schemaPath)) return false;
  try {
    const schema = readFileSync(schemaPath, 'utf8');
    return /provider\s*=\s*["']mysql["']/i.test(schema);
  } catch {
    return false;
  }
}

export function usesDatabase(deps, projectRoot) {
  if (MYSQL_CLIENT_PACKAGES.some((name) => deps[name])) return true;
  return usesMysqlFromPrisma(projectRoot);
}

function checkDatabaseConfig(projectRoot, pkg) {
  const deps = allDeps(pkg);
  if (!usesDatabase(deps, projectRoot)) return;

  const runtimeDeps = pkg.dependencies || {};
  if (!runtimeDeps.mysql2) {
    if (deps.mysql2) {
      err('E009', 'mysql2 is only in devDependencies — move to dependencies for production');
    } else {
      err('E009', 'Database client detected — add mysql2 to dependencies for platform MySQL');
    }
  }

  const files = walkSourceFiles(projectRoot);
  for (const varName of DB_ENV_VARS) {
    if (!envVarReferencedInFiles(files, varName)) {
      err(
        'E010',
        `Managed MySQL requires process.env.${varName} (set by platform when DB is enabled)`,
      );
    }
  }
}

function checkRuntimeDeps(pkg) {
  const deps = pkg.dependencies || {};
  const devDeps = pkg.devDependencies || {};
  for (const name of RUNTIME_PACKAGES) {
    if (devDeps[name] && !deps[name]) {
      err('E006', `Runtime package "${name}" is only in devDependencies`);
    }
  }
}

function walkSourceFiles(projectRoot, dir = projectRoot, files = []) {
  const rootPrefix = projectRootPrefix(projectRoot);
  if (!existsSync(dir)) return files;
  for (const name of readdirSync(dir)) {
    if (SKIP_DIRS.has(name) || !isSafeDirEntry(name)) continue;
    const p = appendDirEntry(dir, name);
    if (p !== projectRoot && !p.startsWith(rootPrefix)) continue;
    let st;
    try {
      st = lstatSync(p);
    } catch {
      continue;
    }
    if (st.isSymbolicLink()) continue;
    if (st.isDirectory()) {
      walkSourceFiles(projectRoot, p, files);
    } else if (/\.(js|mjs|cjs|ts|tsx|jsx)$/.test(name)) {
      files.push(p);
    }
  }
  return files;
}

const HARDCODED_PORT_PATTERNS = [
  /\.listen\s*\(\s*['"]?\d{2,5}/,
  /\.listen\s*\(\s*\{\s*[^}]*\bport\s*:\s*['"]?\d{2,5}/,
  /createServer\s*\([^)]*\)\s*\.listen\s*\(\s*['"]?\d{2,5}/,
];

function checkHardcodedPorts(projectRoot) {
  const rootPrefix = projectRootPrefix(projectRoot);
  const files = walkSourceFiles(projectRoot);
  for (const file of files) {
    let content;
    try {
      content = readFileSync(file, 'utf8');
    } catch {
      continue;
    }
    for (const re of HARDCODED_PORT_PATTERNS) {
      if (re.test(content)) {
        const rel = file.startsWith(rootPrefix) ? file.slice(rootPrefix.length) : file;
        err('E004', `Possible hardcoded port in ${rel} — use process.env.PORT`);
        break;
      }
    }
  }
}

function validateProject(projectRoot) {
  const pkgPath = pathUnderProjectRoot(projectRoot, 'package.json');
  if (!pkgPath || !existsSync(pkgPath)) {
    err('E001', 'Missing root package.json');
    return;
  }

  const pkg = readJson(pkgPath);
  if (!pkg) return;

  checkPackageMetadata(pkg, projectRoot);

  const start = pkg.scripts?.start;
  if (!start || !String(start).trim()) {
    err('E002', 'Missing or empty scripts.start');
  } else {
    validateStartScript(projectRoot, String(start).trim());
  }

  const deps = allDeps(pkg);
  checkBuildScript(pkg, deps);
  checkRuntimeDeps(pkg);
  checkHardcodedPorts(projectRoot);
  checkDatabaseConfig(projectRoot, pkg);

  const envPath = pathUnderProjectRoot(projectRoot, '.env');
  if (envPath && existsSync(envPath)) {
    warn('W001', '.env file present — do not upload secrets');
  }

  if (!pkg.engines?.node) {
    warn('W002', 'Missing engines.node (optional but recommended)');
  }

  checkUploadHygiene(projectRoot);
}

/** Canonical absolute project root from CLI path (file URL, not path.resolve). */
export function canonicalProjectDir(input) {
  if (typeof input !== 'string' || input.length === 0 || input.includes('\0')) {
    return null;
  }
  let dirUrl;
  try {
    const cwdUrl = pathToFileURL(process.cwd());
    if (!cwdUrl.pathname.endsWith('/')) {
      cwdUrl.pathname += '/';
    }
    dirUrl = new URL(input, cwdUrl);
  } catch {
    return null;
  }
  if (dirUrl.protocol !== 'file:') return null;
  let dir;
  try {
    dir = fileURLToPath(dirUrl);
  } catch {
    return null;
  }
  try {
    if (!statSync(dir).isDirectory()) return null;
  } catch {
    return null;
  }
  return dir;
}

function printResults() {
  for (const e of errors) {
    console.error(`ERROR [${e.id}]: ${e.message}`);
  }
  for (const w of warnings) {
    console.warn(`WARN  [${w.id}]: ${w.message}`);
  }
}

function validationResult(exitCode) {
  return { exitCode, errors: [...errors], warnings: [...warnings] };
}

/**
 * Run validation. `args` like process.argv slice(2): [<project-dir>] [--strict]
 * @returns { exitCode, errors, warnings } — errors/warnings are snapshots, safe to retain across runs
 */
export function runValidation(args) {
  clearResults();
  const strict = args.includes('--strict');
  const paths = args.filter((a) => !a.startsWith('--'));

  if (paths.length === 0) {
    return validationResult(1);
  }

  const projectRoot = canonicalProjectDir(paths[0]);
  if (!projectRoot) {
    return validationResult(1);
  }

  validateProject(projectRoot);

  if (errors.length > 0) return validationResult(1);
  if (warnings.length > 0 && strict) return validationResult(1);
  if (warnings.length > 0) return validationResult(2);
  return validationResult(0);
}

const cliEntry = fileURLToPath(import.meta.url);
const isCliEntry =
  process.argv[1] &&
  (process.argv[1] === cliEntry ||
    fileURLToPath(pathToFileURL(process.argv[1])) === cliEntry);

if (isCliEntry) {
  const args = process.argv.slice(2);
  const paths = args.filter((a) => !a.startsWith('--'));

  if (paths.length === 0) {
    console.error('Usage: node validate-paas.mjs <project-dir> [--strict]');
    process.exit(1);
  }

  const projectRoot = canonicalProjectDir(paths[0]);
  if (!projectRoot) {
    console.error(`Directory not found or not a directory: ${paths[0]}`);
    process.exit(1);
  }

  console.log(`Validating: ${projectRoot}`);
  const { exitCode } = runValidation(args);
  printResults();

  if (exitCode === 0) {
    console.log('OK — ready for Node.js Hosting upload checks.');
  }
  process.exit(exitCode);
}
