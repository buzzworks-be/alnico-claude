"""What kind of file a path is, for every script that bins by lines of code.

One definition, imported by all of them. Until 2026-09-02 each script carried
its own copy of these patterns and they had drifted: `spec/` was a test
directory in one and a documentation directory in another; `.txt` was
documentation in some and code in the rest; fixtures and snapshots were noise
only in the newest scripts; and R-003's extractor counted code by an extension
allowlist where R-011's counted anything not test, doc or noise — on one
history the first binned 131 landings where the second binned 248, so the
same landing sat in different size bands under two rules that had borrowed
each other's floors on the argument that they were comparable.

The order of tests is the definition, and it is deliberate:

  noise  vendored, generated, lockfiles, minified, binary, fixtures, snapshots
         — nothing a reader reads or a test covers.
  doc    by extension first, wherever it lives (a README inside tests/ is a
         document), then by directory (docs/, adr/, decisions/, rfcs/,
         design/) whatever the extension.
  test   by directory (tests/, spec/, e2e/ …) or by name (test_x, x_test,
         x.spec, conftest).
  code   everything else. Configuration — YAML, JSON, TOML — counts as code
         here, which the rules already carry as an exemption ("a dependency
         bump or configuration change classed as code by path heuristics").
         Excluding it would move landings between bands and invalidate the
         sweep the bands were set on; adding a config class is a future
         change and needs its own re-sweep.

`spec` and `specs` directories are TEST directories: a specification document
inside one is caught by its extension first, and what remains is the JS and
Ruby convention.

Scripts that ask a different question — which documents are specifications
(R-002), how heavy a document is to read (S-6), whether documentation still
describes the code (R-005) — keep their own patterns; those are not "what is a
line of code" and unifying them here would be a category error.
"""

import re

NOISE_RE = re.compile(
    r"(^|/)(vendor|vendored|node_modules|third[-_]party|dist|build|generated|__snapshots__|snapshots?|fixtures?)(/)"
    r"|(lock|\.lock)$|package-lock\.json$|yarn\.lock$|pnpm-lock\.yaml$|poetry\.lock$"
    r"|go\.sum$|Cargo\.lock$|composer\.lock$|Gemfile\.lock$"
    r"|\.min\.(js|css)$|\.(svg|png|jpg|jpeg|gif|ico|pdf|woff2?|snap)$", re.I)

DOC_EXT_RE = re.compile(r"\.(md|rst|adoc|txt)$", re.I)
DOC_DIR_RE = re.compile(r"(^|/)(docs?|adr|adrs|decisions|rfcs?|design)(/|$)", re.I)

# A directory whose NAME ENDS in test or tests is a test directory too — a
# repository that keeps its suite under <name>test/ read as wholly untested
# until 2026-09-07, when a full read of R-027's candidates on one history found
# two "untested" landings whose test fixtures sat in exactly such a directory.
# `latest/` is the one common directory name that ends that way and is not a
# suite; it is excluded by name.
TEST_RE = re.compile(
    r"(^|/)(tests?|__tests__|spec|specs|e2e|it|testing|benches|benchmarks?)(/)"
    r"|(^|/)(?!latest/)[a-z0-9_-]*tests?(/)"
    r"|(^|/)test_[^/]+$|_test\.[^/.]+$|\.test\.[^/.]+$|\.spec\.[^/.]+$"
    r"|Test[s]?\.[^/.]+$|_spec\.[^/.]+$|conftest\.py$", re.I)

# Tests that do not live in a test FILE. Rust's dominant convention puts unit
# tests in the source file under #[cfg(test)]; several other languages have a
# marker that is visible in the added lines of a diff.
INLINE_TEST_RE = re.compile(
    r"#\[\s*cfg\s*\(\s*test\s*\)\s*\]"
    r"|#\[\s*(tokio::|async_std::|rstest|test_case)?\s*test"
    r"|^\+\s*(async\s+)?def\s+test_"
    r"|@Test\b|\[\s*(Fact|Theory|Test|TestMethod)\s*\]"
    r"|^\+\s*(describe|it|test)\s*\("
    r"|^\+\s*func\s+Test[A-Z]", re.M)

# A commit whose committer is the hosting platform is a squashed or rebased
# branch landing: one pull request, one landing, whatever its neighbours are.
FORGE_COMMITTERS = {
    "noreply@github.com", "noreply@gitlab.com", "noreply@gitea.io", "noreply@codeberg.org",
}

# For scripts whose DOC_RE was one pattern: doc by extension or by directory.
DOC_RE = re.compile(DOC_DIR_RE.pattern + "|" + DOC_EXT_RE.pattern, re.I)


def kind(path):
    """'noise', 'doc', 'test' or 'code' — see the module docstring for the order."""
    if NOISE_RE.search(path):
        return "noise"
    if DOC_EXT_RE.search(path):
        return "doc"
    if TEST_RE.search(path):
        return "test"
    if DOC_DIR_RE.search(path):
        return "doc"
    return "code"


def is_forge(committer_email):
    return (committer_email or "").strip().lower() in FORGE_COMMITTERS
