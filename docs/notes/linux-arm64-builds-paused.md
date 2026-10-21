# Linux ARM64 build checkpoint

Status: paused at the user's request on 2026-10-21. The current branch is
`feat/linux-port`, currently at commit
`30dd7d9e09d2e569804000f6cbb4d6db2152a5b4`. The worktree is clean. The
containers were rechecked on 2026-10-21: both exited with code 137 and
`OOMKilled=false` at 19:48:21 UTC. No Gentoo or Guix build process is active.

Do not count either target as supported or tested yet. The distro matrix still
marks both native package lifecycles as `unverified`.

## Gentoo ARM64

- Docker container: `jarvis-gentoo-aarch64` (`gentoo/stage3:latest`, ARM64 under
  QEMU); preserve it, do not remove it.
- Build command at pause: `sh scripts/build-package.sh --target gentoo
  --arch aarch64 --output /out` from `/src`.
- `emerge --onlydeps` was compiling Node.js 26.12.0. The retained build log
  ends at Ninja `[101/3417]` in ICU. A read-only copy is available at
  `/tmp/jarvis-gentoo-aarch64-nodejs-build.log`.
- Portage log inside the container:
  `/tmp/tmp.o7uf6mIw3M/tmp/portage/net-libs/nodejs-26.12.0/temp/build.log`.
- `/out` is the host bind mount `/tmp/jarvis-gentoo-aarch64/out`.
- `/out` contained no package artifacts at the last check. `/src` is a
  read-only bind mount of this worktree.

## Guix ARM64

- Docker container: `jarvis-guix-rust190-seccomp`; preserve it, do not remove it.
- Serial fallback command at pause:
  `guix build --fallback --cores=1 --max-jobs=1 --system=aarch64-linux -f
  ./jarvis.scm > build-serial.log 2>&1` from `/src`.
- The host bind-mounted `build-serial.log` ends at oneDNN `[74%]`,
  compiling `rnn_utils.cpp.o`. The expected `/src/build.log` is absent from
  the host mount. The container exited 137 with `OOMKilled=false`; no package
  lifecycle or install smoke completed.
- `/src` is the host bind mount `/tmp/jarvis-guix-eval.y9LJB2`.
- The original non-serial `guix build` process was also present in the
  container; check its log and exit marker before resuming.

## Resume procedure

The containers are exited, not removed, so their writable layers and
bind-mounted outputs/logs are preserved. `docker start` alone only restarts
each container's configured idle command; it will not resume either terminated
build process. The Guix container's `/src` is a temporary source snapshot from
the earlier build, while Gentoo's `/src` points at this worktree. On resume,
inspect the retained logs and outputs, then prepare the build inputs from the
current branch before re-running. The original builds do not promise
incremental recovery from the exact compiler object; verify package-manager
and build-system state before deciding whether to resume or restart a phase.

The user asked that current work continue only on distro targets already marked
complete in `docs/notes/linux-matrix.json`; keep these two ARM64 targets paused
until that scope changes.
