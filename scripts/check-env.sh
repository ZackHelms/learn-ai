#!/usr/bin/env bash
#
# Preflight for the learn-ai course.
#
# Run this BEFORE pulling any models. A 5 GB download that dies two thirds of
# the way through because the disk was full is a miserable way to find out the
# disk was full.
#
# Exit codes:
#   0  good to go (warnings may still have been printed)
#   1  something is wrong that will stop you making progress
#
# Usage: bash scripts/check-env.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROSTER="$REPO_ROOT/models/roster.yaml"

# --- output helpers -------------------------------------------------------

if [ -t 1 ]; then
  RED=$'\033[31m'; YELLOW=$'\033[33m'; GREEN=$'\033[32m'
  BOLD=$'\033[1m'; DIM=$'\033[2m'; RESET=$'\033[0m'
else
  RED=''; YELLOW=''; GREEN=''; BOLD=''; DIM=''; RESET=''
fi

FAILURES=0
WARNINGS=0

ok()   { printf '  %s✓%s %s\n' "$GREEN" "$RESET" "$1"; }
warn() { printf '  %s!%s %s\n' "$YELLOW" "$RESET" "$1"; WARNINGS=$((WARNINGS + 1)); }
bad()  { printf '  %s✗%s %s\n' "$RED" "$RESET" "$1"; FAILURES=$((FAILURES + 1)); }
note() { printf '    %s%s%s\n' "$DIM" "$1" "$RESET"; }
head_() { printf '\n%s%s%s\n' "$BOLD" "$1" "$RESET"; }

# --- budget, read from the roster so there is one source of truth ---------
# roster.yaml stores these as plain "key: value" lines under `budget:`.

read_budget() {
  # $1 = key name; prints the integer value, or nothing if unparseable.
  sed -n '/^budget:/,/^[a-z_]*:/p' "$ROSTER" 2>/dev/null |
    grep -E "^[[:space:]]+$1:" |
    head -1 |
    sed -E 's/.*:[[:space:]]*([0-9]+).*/\1/'
}

NEED_RAM_GB="$(read_budget total_ram_gb)"
NEED_DISK_GB="$(read_budget disk_gb)"
: "${NEED_RAM_GB:=16}"
: "${NEED_DISK_GB:=20}"

printf '%slearn-ai environment check%s\n' "$BOLD" "$RESET"
note "budget from models/roster.yaml: ${NEED_RAM_GB} GB RAM, ${NEED_DISK_GB} GB disk"

# --- platform -------------------------------------------------------------

head_ "Platform"

UNAME_S="$(uname -s)"
ARCH="$(uname -m)"

if [ "$UNAME_S" != "Linux" ]; then
  warn "Not Linux (found: $UNAME_S)."
  note "This course is written and tested against Ubuntu 24.04+."
  note "On macOS, prefer a NATIVE Ollama install over a Linux VM -- see"
  note "modules/00-overview/README.md, 'If you are on a Mac'."
else
  if [ -r /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    case "${ID:-}" in
      ubuntu)
        MAJOR="${VERSION_ID%%.*}"
        if [ "${MAJOR:-0}" -ge 24 ] 2>/dev/null; then
          ok "Ubuntu ${VERSION_ID} (reference platform)"
        else
          bad "Ubuntu ${VERSION_ID} is older than the 24.04 minimum."
          note "Commands here assume 24.04+. Older releases ship a Python too"
          note "old for some of the tooling and lack current Ollama packaging."
        fi
        ;;
      debian) ok "Debian ${VERSION_ID:-?} (close enough; commands should work)" ;;
      *)      warn "Linux, but not Ubuntu (${PRETTY_NAME:-unknown})."
              note "Should mostly work. Package install steps may differ." ;;
    esac
  else
    warn "Linux, but /etc/os-release is missing; cannot identify the distro."
  fi

  if grep -qiE '(microsoft|wsl)' /proc/version 2>/dev/null; then
    ok "Running under WSL2"
    note "WSL2 caps guest RAM by default. If the RAM check below fails but"
    note "your Windows box has plenty, set memory= in %USERPROFILE%\\.wslconfig"
    note "and run 'wsl --shutdown' to apply it."
  fi
fi

ok "Architecture: $ARCH"

# --- CPU ------------------------------------------------------------------

head_ "CPU"

CORES="$(nproc 2>/dev/null || echo 0)"
if [ "$CORES" -ge 4 ]; then
  ok "$CORES cores"
elif [ "$CORES" -gt 0 ]; then
  warn "$CORES cores. Workable, but generation will be slow."
else
  warn "Could not determine core count."
fi
if [ "$CORES" -lt 8 ] && [ "$CORES" -gt 0 ]; then
  note "Most published tokens/sec figures assume 8+ cores. Yours will be lower."
  note "That is fine -- record what YOU get in the module's FIELD-NOTES.md."
fi

if [ -r /proc/cpuinfo ]; then
  CPUFLAGS="$(grep -m1 '^flags' /proc/cpuinfo 2>/dev/null || echo '')"
  HAS_AVX2=0
  case "$CPUFLAGS" in *" avx2 "*) HAS_AVX2=1 ;; esac

  if [ "$HAS_AVX2" -eq 1 ]; then
    ok "AVX2 available"
    case "$CPUFLAGS" in
      *" avx512f "*) ok "AVX-512 available (quantized inference will benefit)" ;;
    esac
    case "$CPUFLAGS" in
      *" avx512_vnni "*|*" avx_vnni "*) ok "VNNI available (helps int8/int4 matmul)" ;;
    esac
  elif [ "$ARCH" = "x86_64" ]; then
    # This is the Apple Silicon footgun: an amd64 image on an ARM host runs
    # under emulation, which strips modern vector extensions and is
    # catastrophically slow. It presents as "local models are useless".
    bad "x86_64 CPU with no AVX2. This is almost certainly EMULATION."
    note "If you are on an Apple Silicon Mac running an amd64 Linux image,"
    note "you are inside QEMU and inference will be ~10-100x slower than real."
    note "Fix: use an arm64/aarch64 image, or run Ollama natively on macOS."
  fi
fi

# --- memory ---------------------------------------------------------------

head_ "Memory"

if [ -r /proc/meminfo ]; then
  TOTAL_KB="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
  AVAIL_KB="$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)"
  TOTAL_GB=$((TOTAL_KB / 1024 / 1024))
  AVAIL_GB=$((AVAIL_KB / 1024 / 1024))

  # Allow 1 GB of slack: a "16 GB" machine reports ~15 GB to the OS.
  if [ "$((TOTAL_GB + 1))" -ge "$NEED_RAM_GB" ]; then
    ok "${TOTAL_GB} GB total, ${AVAIL_GB} GB available now"
  else
    bad "${TOTAL_GB} GB total; the course assumes ~${NEED_RAM_GB} GB."
    note "You can still do most of the course -- stick to rungs 0-2 and skip"
    note "the 8B baseline. Edit models/roster.yaml to drop what will not fit."
  fi

  if [ "$AVAIL_GB" -lt 6 ]; then
    warn "Only ${AVAIL_GB} GB free right now. Close some tabs before benchmarking."
  fi
else
  warn "Cannot read /proc/meminfo; skipping the memory check."
fi

# --- disk -----------------------------------------------------------------

head_ "Disk"

# Models land in ~/.ollama by default, which may be on a different filesystem
# than the repo. Check where the models actually go.
OLLAMA_DIR="${OLLAMA_MODELS:-$HOME/.ollama}"
CHECK_DIR="$OLLAMA_DIR"
while [ ! -d "$CHECK_DIR" ] && [ "$CHECK_DIR" != "/" ]; do
  CHECK_DIR="$(dirname "$CHECK_DIR")"
done

FREE_GB="$(df -BG --output=avail "$CHECK_DIR" 2>/dev/null | tail -1 | tr -dc '0-9')"
if [ -n "$FREE_GB" ]; then
  if [ "$FREE_GB" -ge "$NEED_DISK_GB" ]; then
    ok "${FREE_GB} GB free on the filesystem holding $OLLAMA_DIR"
  else
    bad "${FREE_GB} GB free where models are stored; need ~${NEED_DISK_GB} GB."
    note "Models go to \$OLLAMA_MODELS (default ~/.ollama). Point that at a"
    note "roomier disk, or pull fewer models from models/roster.yaml."
  fi
else
  warn "Could not determine free disk space for $OLLAMA_DIR."
fi

# --- tooling --------------------------------------------------------------

head_ "Tooling"

if command -v ollama >/dev/null 2>&1; then
  ok "ollama installed ($(ollama --version 2>&1 | head -1))"
  if curl -fsS --max-time 3 http://localhost:11434/api/version >/dev/null 2>&1; then
    ok "ollama service responding on :11434"
  else
    bad "ollama is installed but not responding on http://localhost:11434"
    note "Start it with:  ollama serve    (or: sudo systemctl start ollama)"
  fi
else
  bad "ollama not installed -- module 1 walks you through this."
fi

if command -v uv >/dev/null 2>&1; then
  ok "uv installed ($(uv --version 2>&1 | head -1))"
else
  warn "uv not installed. The Python exercises use it."
  note "Install:  curl -LsSf https://astral.sh/uv/install.sh | sh"
  note "Ubuntu 24.04 marks its system Python as externally managed (PEP 668),"
  note "so a bare 'pip install' will refuse to run. uv sidesteps that."
fi

for cmd in curl jq git; do
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "$cmd installed"
  else
    warn "$cmd not installed (sudo apt install $cmd)"
  fi
done

# --- verdict --------------------------------------------------------------

printf '\n'
if [ "$FAILURES" -gt 0 ]; then
  printf '%s%d blocking issue(s)%s' "$RED" "$FAILURES" "$RESET"
  [ "$WARNINGS" -gt 0 ] && printf ', %d warning(s)' "$WARNINGS"
  printf '. Fix the ✗ items above before continuing.\n'
  exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
  printf '%sReady%s, with %d warning(s). Read them, then carry on.\n' \
    "$GREEN" "$RESET" "$WARNINGS"
else
  printf '%sReady.%s Next: modules/01-local-model-lab/README.md\n' "$GREEN" "$RESET"
fi
exit 0
