# Repository Guidelines

`text-to-cad` is a monorepo that ships **agent skills for CAD** plus the `cadgen`
runtime they invoke, the CAD Viewer, and the docs site. The repository root *is*
the plugin package: `skills/` is the product, `models/` is the shared
manual-validation corpus, and everything else is the machinery that builds and
serves it.

Canonical version: `VERSION` (`0.7.19`). Every other version field and every
`cadgen==` pin is stamped from it — never hand-edit them.

---

## Architecture & Data Flow

The spine is `packages/cadgen`, a **PyPI distribution that ships alone**: Python
engine, generated-file support, CLI parsers, a warm build daemon, and a bundled
JS/React runtime (`cadgen/_runtime`, built not committed). Two framework-free JS
packages sit under it, and four apps consume them.

```
user prompt
  └─> skills/<name>/SKILL.md  ──(agent reads; routes to references/*.md)
        └─> python model.py  ──uvx --from cadgen==<VERSION>──
              ├─ authoring.py      @step/@dxf/@glb/@stl/@threemf decorators
              ├─ _internal/        generation pipeline, filetrace, surface extract
              ├─ store/            ~/.cache/cadgen  objects/ (content) + index/ (input)
              └─> artifacts        part.step + part.step.json sidecar
                    │
      ┌─────────────┴──────────────┐
      │                            │
cadgen viewer  (HTTP :3245)   cadgen mcp  (stdio JSON-RPC, agent hosts)
 apps/web  React+Vite               apps/mcp  single-file React page
      └──────────┬──────────────────┘
          @text-to-cad/ui  CadViewer  ──>  @text-to-cad/core  render pipeline
                    (packages/ui)                (packages/core)
```

Two entry doors only: `python model.py` (source) and the generated CLIs
(`cadgen <format> <verb>`, which take *documents* and compile from bytes, never
scripts). A skill script is a thin entrypoint — its parser and behaviour live in
`cadgen.cli`.

**Import direction is one-way and enforced:** apps → shared packages → never up.
`packages/core` never imports React/UI/app code; `packages/ui` never imports an
app; apps never import one another. `cadgen.viewer` and `cadgen.mcp` are leaves —
nothing outside them imports them.

### cadgen's design laws (`packages/cadgen/README.md`)

Read the README before touching generation, storage or CLIs. The load-bearing ones:

1. Generated files are fully readable from their own bytes + store objects alone.
2. `~/.cache/cadgen` holds **only derived** results — deletable, rebuildable.
3. One sidecar per artifact, describing only that artifact.
4. Written artifacts carry **zero metadata**; provenance rides the sidecar.
5. Writers are byte-deterministic; equal bytes mean reuse.
6. One surface, three faces: decorator declares, public function performs, CLI generated.
7. `python model.py` is the one source door.
8. No backwards compatibility — hard cutover, teaching errors, no shims.
10. Loud failure or correct output; never plausible-wrong output at exit 0.
15. The package ships alone: its markdown must read as if the repo is gone.
18. Caches sit around a model run, never inside it.
19. Nothing waits on the network once installed.

`packages/cadgen/STORE.md` is the store contract (wins over the README on any
disagreement). `SNAPSHOTS.md` documents display presets and `--debug` timings.

### Module map — `packages/cadgen/src/cadgen/`

| Module | Responsibility |
|---|---|
| `authoring.py` | `@step`/`@dxf`/`@stl`/`@glb`/`@threemf` decorators |
| `<format>.py` | Public namespaces (`step`, `dxf`, `stl`, `glb`, `threemf`, `urdf`, `srdf`, `sdf`) |
| `store/` | `build.py` build pipeline, `closure.py` file-trace deps, `gate.py` freshness, `gc.py`, `lazy.py`, `meshes.py`, `surfaces.py` |
| `daemon/` | Warm build pool: `broker.py`, `pool.py`, `jobs.py`, `server.py`, `worker.py`, `transport.py` (singleton lock) |
| `_internal/` | `generation.py`, `generation_runner.py`, `step_scene_*`, `surface_extract.py`, `cli_from_function.py`, `filetrace.py` |
| `viewer/` | CAD Viewer server: `main.py`, `http_app.py`, `backend.py`, `scanner.py`, `recents.py`, `build_progress.py` |
| `mcp/` | `server.py` (tools + launches), `protocol.py` (stdio JSON-RPC), `tunnel.py`, `ui.py` |
| `cli/` | Generated command shells, one per `<format> <verb>` |
| `_runtime/` | **Built, never committed**: `node/`, `browser/`, `viewer/`, `mcp/`, `native/` |

One daemon per *installation* (singleton lock on the socket), named after it —
that is why every skill command uses the same pinned `uvx` line. `CADGEN_DAEMON=0`
forces a transient executor per job for tests and CI.

---

## Key Directories

| Path | Purpose |
|---|---|
| `skills/` | 12 agent skills. `SKILL.md` + `references/*.md` + `scripts/`. The product. |
| `packages/cadgen/` | The Python distribution: engine, CLIs, daemon, viewer server, MCP server, bundled runtime |
| `packages/core/` | Framework-independent CAD/render/client code (`src/client`, `src/prompt`, `src/common`, `src/lib`, `bin/` Node builders) |
| `packages/ui/` | Shared React `FileViewer` + `CadViewer` + five renderers (`step`, `dxf`, `glb`, `mesh`, `robot`) |
| `apps/web/` | CAD Viewer client (React 19 + Vite). Backend is `cadgen viewer` |
| `apps/mcp/` | CAD app for MCP Apps hosts: tabs in Codex, cards in Claude Desktop. Server is `cadgen mcp` |
| `apps/docs/` | Documentation site (Next.js 16). Homepage copy in `src/lib/content.ts` |
| `apps/api/` | `api.texttocad.dev` — PyPI version feed + consented analytics. Not an npm workspace member |
| `models/` | Sample/durable CAD + robot-description fixtures. **Manual validation only** |
| `tests/` | `python/` (unittest suites, `global/` policy), `fixtures/`, `browser/` |
| `scripts/` | Durable repo commands: `bundle/`, `test/`, `release/`, `github-workflows/`, `install/`, `git-hooks/`, `build/`, `brand/`, `bench/` |
| `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `plugin.json`, `gemini-extension.json` | Agent plugin manifests, at the root by design |
| `docs/migrations/` | Manual migration playbooks (e.g. `migrating-0.4-to-0.5.md`) |

### Skills

Every skill is independent: no skill may import another skill, a `skills/` root
module, or a repository-root module, and none may add `skills/`, the repo root, or
a sibling skill directory to `sys.path`/`PYTHONPATH`/`NODE_PATH`.

Skills that use cadgen define both tools identically in their SKILL.md:

```
cadgen = uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.19 cadgen
python = uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.19 python
```

Do not add a `requirements.txt` naming cadgen, and do not vendor a browser or
Node runtime into a skill. Cadgen-free skills (do **not** add the dependency):
`bambu-labs`, `dfam-check`, `dfm`, `gcode`, `sendcutsend`, `step-parts`.

---

## Development Commands

```bash
# Python environment (POSIX; on WSL install inside the distro, never reuse a Windows .venv)
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements-dev.txt   # installs cadgen editable

# Node (only for the workflow you changed)
npm ci --workspace @text-to-cad/core                        # Python engine / core work
npm ci --workspace @text-to-cad/core --workspace @text-to-cad/ui --workspace @text-to-cad/web
npm run build:packages                                       # core, then ui — required before web/mcp/docs

# Packaged runtime (BUILT, gitignored, ships in the wheel)
scripts/bundle/bundle.sh
scripts/bundle/bundle.sh --check     # assert every required output + version metadata
```

Root npm scripts: `build:packages`, `build:web`, `build:mcp`, `build:docs`,
`dev:web`, `dev:docs`, `test` (= `scripts/test/test-js.sh`), `check:boundaries`.

Run the app: `npm run dev:web` (Vite) against a checkout backend, or the launcher
`cadgen viewer --host 127.0.0.1 --json --detach`. Reuse an existing instance; never
stop one you did not start.

Prefer `./.venv/bin/python` for CAD Python work.

---

## Runtime & Tooling Preferences

| Thing | Value | Where it is set |
|---|---|---|
| Package manager | **npm** (lockfileVersion 3) — not bun, not pnpm | `package-lock.json`, root `package.json` `allowScripts` |
| Node | **22** | `.github/actions/setup-deps`, `test.yml` |
| Python floor | `>=3.11` — and it lives *only* in `packages/cadgen/pyproject.toml` | every cadgen source is parsed against it |
| Skill launch python | `3.13` via `uvx --managed-python` | every `SKILL.md` pin |
| Editable install | `--editable ./packages/cadgen` via `requirements-dev.txt` | — |
| Lint/format | **eslint only in `apps/docs`** (`npm --prefix apps/docs run lint`). No prettier, ruff, black, flake8, or biome anywhere. Do not invent a lint command for other packages | `apps/docs/eslint.config.mjs` |
| Typecheck | `npm run typecheck -w @text-to-cad/core` (and ui/web/mcp) | per-package scripts |

One root lockfile. No nested lockfiles, no source aliases, no symlinked dependency
trees. Root workspaces consume **compiled** package exports.

`packages/cadgen/src/cadgen/_runtime/` is built, never committed — the whole
directory is gitignored and ships only inside the wheel. Never edit it; change the
source and rerun `scripts/bundle/bundle.sh`.

**Never let a symlink reach the tracked tree.** Installers disagree: the Skills
CLI dereferences, Claude Code preserves, Codex `plugin add` drops them silently.
Also: no Git LFS, no `.gitattributes` rule that rewrites files, every tracked file
under 5 MiB. All four are enforced by `scripts/github-workflows/check-builds.sh`.

Prefer path-targeted search and checks. Reserve `scripts/` for durable commands —
one-off helpers go in `tmp/` or `/tmp`. Never commit `.venv/`, `node_modules/`,
caches, `tmp/`, credentials, or generated CAD output.

---

## Code Conventions & Common Patterns

**One surface, three faces.** A feature declared in a `@step`-family decorator is
performed by a public function, and its CLI is *generated* from that function's
signature. Adding a verb means adding the public function; do not hand-write a
parser in a skill. Enforced by `tests/python/global/test_documented_commands.py`
and `test_cli_main_guards.py`.

**CLI stream contract:** stdout carries only the `RESULT`; everything else goes to
stderr. Every CLI module with `main()` needs a `__main__` guard.

**Closed vocabularies.** Unknown keys on a declaration surface are *teaching
errors*, not ignored fields. Loud failure beats plausible-wrong output.

**Injected capabilities, not environment sniffing.** Shared UI never discovers
Electron, browser globals, clipboard or storage — the host passes a `ViewerHost`
(`files`, `clipboard`, `promptContext`, `attachments`, `navigation`, `links`,
`environment`). App-specific surfaces go through *named additive slots*
(`fileActions`, `usage`, `fullSize`) in the contract in
`packages/ui/docs/viewer-host.md`. Renderers register via `defineFileRenderer`
and reject duplicate or ambiguous IDs.

**Capability registry, not format identity.** Ask what a format *can* do
(`packages/core/src/lib/renderCapabilities.js`), never what it *is*. Format-identity
checks are ratcheted to zero by `test_viewer_format_capability_policy.py`.

**Two sides of the store.** The *artifact side* is derived, disposable, content
addressed; the *code side* is input addressed. `~/.cache/cadgen` never holds
authored data. A sidecar is written only when something must read it.

**Cross-language contracts are mirrored and sync-tested.** Bump both sides or a
policy test fails: `lib/cadRefs.js` ↔ `cadgen/cad_ref_syntax.py`,
`common/kinematicsRuntime.js` ↔ `_internal/kinematics_resolve.py`,
`common/renderModule.js` ↔ `_internal/animation_source.py`, tessellation v4 ↔
`store/meshes.py`, `SURF_VERSION` across the boundary.

**Laws live in READMEs.** Each package README holds the boundaries and names the
one document that holds the mechanism — read the README, then follow that one
link. `packages/ui/docs/settings-ui.md` is **binding** for any settings control.
Docs that exist: `packages/core/docs/{render-pipeline,resource-ownership,tube-deformation,workspace-resources}.md`;
`packages/ui/docs/{viewer-host,settings-ui,render-types,render-mode,lod,cad-renderer,drawing,feature-detection,file-viewer,renderers,view-updates}.md`;
`apps/web/docs/{storage,backend,shell}.md`.

**The root README and the docs-site homepage** (`apps/docs/src/lib/content.ts`)
share structure, install message and commands — change them together. The README
says more.

**Python:** stdlib `unittest`, no pytest in the suites. Name every
`read_text`/`write_text` `encoding="utf-8"`. No source file carries a NUL byte.
No entry point re-execs to pin `PYTHONHASHSEED`.

---

## Important Files

| File | Why it matters |
|---|---|
| `VERSION` | The only canonical version. Everything else is stamped from it |
| `package.json` | npm workspace root; `build:packages` order (core → ui) is load-bearing |
| `requirements-dev.txt` | Editable cadgen + the native tracer's `ziglang` |
| `packages/cadgen/pyproject.toml` | `requires-python` floor and dependency pins |
| `packages/cadgen/README.md` | The design laws |
| `packages/cadgen/STORE.md` | The store contract (wins over the README) |
| `mcp.json`, `claude.mcp.json`, `codex.mcp.json`, `cursor.mcp.json`, `gemini-extension.json` | One per host; each carries `CADGEN_INSTALL_CHANNEL` |
| `.claude-plugin/marketplace.json` | The catalog lists the plugin at `./` |
| `scripts/release/sync-version.mjs` | Stamps every derived version and pin (`--check` fails on drift) |
| `scripts/release/check-version.sh` | Asserts every skill pins `cadgen==<VERSION>` |
| `scripts/github-workflows/select_checks.py` | The changed-path → CI-job table |
| `scripts/github-workflows/check-builds.sh` | The shipping contract (symlinks, LFS, 5 MiB, skill reach) |
| `CONTRIBUTING.md` | Full release lifecycle, CI, viewer workflow, iteration loop |
| `models/README.md` | Sample corpus layout — and the rule that tests never read it |

**Branches.** `main` is the only branch you develop on: it is the source tree,
what releases are cut from, and an installable plugin. Branch from it, PR against
it, never push it directly. `latest` and `claude-plugin` are install branches
written *only* by `Publish Release`; `build-test` is the rehearsal branch.

**Releases.** A PR that changes `VERSION` is a release; merging it publishes.
Never bump during normal work and never pick the bump yourself — if a request
does not name patch/minor/major/an exact version, ask. Either

```bash
gh workflow run release-prepare.yml --ref main -f bump=patch   # or minor|major, or -f set_version=X.Y.Z
```

or, on the branch that should carry it:

```bash
git fetch origin && git merge origin/main
scripts/release/bump-version.sh patch
```

---

## Testing & QA

Python is **stdlib `unittest`**, run through `scripts/test/unittest_files.py`
(one interpreter per file, isolated `CADGEN_CACHE_DIR`, daemon state dir and
socket, fail-closed when it collects nothing). JS uses **`node --test`** for units
and **vitest** only for React/jsdom component tests (`packages/ui`,
`apps/mcp`). Real Chromium via Playwright is reserved for WebGL.

```bash
scripts/test/test.sh                                              # everything: JS, API, Python, policy
scripts/test/test-python.sh --select cadgen|viewer|skills|all     # also --print-weights
scripts/test/test-js.sh --select core|ui|web|mcp|all
scripts/test/test-api.sh
scripts/test/test-docs.sh
scripts/test/test-global.sh
./.venv/bin/python -m unittest <changed test paths>               # targeted
```

**Test one contract at the cheapest level that exercises the real path** — unit or
jsdom first, real browser only for what needs it. Await the condition, never a
fixed sleep. A flaky test is fixed or deleted, never retried. CI time is a
budget: the `web` job stays within 7 minutes, and a change that lengthens any job
says what it costs and why in its PR.

**Automated tests are self-contained.** They must not read, enumerate, build or
import anything from `models/`, and must not depend on the developer's default
store. Generate the smallest fixture in a fresh temp dir (`tests/python/support/tmp_root.py`)
or commit a tiny fixture with the test. Enforced by
`tests/python/global/test_tests_are_self_contained.py`.

**Every test must run in CI.** Each test file is reached by a runner under
`scripts/test/`, every runner is called by a `test.yml` job on the changes that can
break it, and a collector that finds nothing fails the run. A test no CI job runs
is dead — wire it in or delete it. A test that reads a new kind of path gets a
rule in `scripts/github-workflows/select_checks.py`.

`tests/python/global/` is the enforced-laws layer: ~40 files, each one rule
(`test_package_boundaries.py`, `test_host_neutral_packages.py`,
`test_skill_self_containment.py`, `test_plugin_manifests.py`,
`test_cadgen_python_floor_syntax.py`, `test_release_gate.py`,
`test_python_test_runner_isolation.py`, …). Read the relevant one before adding a
structure that crosses a boundary.

`scripts/bench/` is manual only, never in CI, and its output goes to an ignored
`tmp/`. Only its pure helper units run in `test-js.sh`.

**Verify a real change by running it.** Launch the Viewer, exercise the changed
path, and observe the output before claiming it works. Test a skill or the plugin
in an agent app with

```bash
scripts/install/dev_install.py claude    # also: codex, cursor, grok, gemini, claude-desktop
```

Flags: `--uninstall`, `--no-build`, `--restart`, `--wheel`. One copy of the plugin
per app — the script refuses a duplicate install; uninstall the published plugin
before testing and reinstall it afterwards.
