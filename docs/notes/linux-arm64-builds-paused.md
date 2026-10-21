# Linux ARM64 build checkpoint

Status: paused at the user's request on 2026-10-21. The current branch is
`feat/linux-port`, commit `50369e2a75df3c2afeceb43b203212eb14f2b21f`.
The worktree was clean when the builds were paused.

Do not count either target as supported or tested yet. The distro matrix still
marks both native package lifecycles as `unverified`.

## Gentoo ARM64

- Docker container: `jarvis-gentoo-aarch64` (`gentoo/stage3:latest`, ARM64 under
  QEMU); preserve it, do not remove it.
- Build command running at pause: `sh scripts/build-package.sh --target gentoo
  --arch aarch64 --output /out` from `/src`.
- `emerge --onlydeps` was compiling Node.js 26.12.0. Ninja had reached
  approximately `[83/3417]` in ICU. No failure or OOM was observed.
- Portage log inside the container:
  `/tmp/tmp.o7uf6mIw3M/tmp/portage/net-libs/nodejs-26.12.0/temp/build.log`.
- `/out` is the host bind mount `/tmp/jarvis-gentoo-aarch64/out`.
- `/src` is the read-only bind mount of this worktree.

## Guix ARM64

- Docker container: `jarvis-guix-rust190-seccomp`; preserve it, do not remove it.
- Serial fallback command running at pause:
  `guix build --fallback --cores=1 --max-jobs=1 --system=aarch64-linux -f
  ./jarvis.scm > build-serial.log 2>&1` from `/src`.
- Build was compiling oneDNN at `[74%]`; the serial log had advanced from
  `ref_rnn.cpp.o` to `rnn_utils.cpp.o`. No failure or OOM was observed.
- Logs in the container: `/src/build-serial.log` and `/src/build.log`.
- `/src` is the host bind mount `/tmp/jarvis-guix-eval.y9LJB2`.
- The original non-serial `guix build` process was also present in the
  container; check its log and exit marker before resuming.

## Resume procedure

The containers are stopped, not removed, so their writable layers and the
bind-mounted build outputs/logs are preserved. `docker start` alone will only
restart each container's configured idle command; it will not resume the
terminated `docker exec` build process. Inspect the retained logs and outputs,
then re-run the build commands above when ARM64 work is explicitly resumed.
The original builds do not promise incremental recovery from the exact compiler
object; verify package-manager and build-system state before deciding whether
to resume or restart a phase.

The user asked that current work continue only on distro targets already marked
complete in `docs/notes/linux-matrix.json`; keep these two ARM64 targets paused
until that scope changes.
