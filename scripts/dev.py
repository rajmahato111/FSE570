#!/usr/bin/env python3
"""
Developer utility scripts for the Autonomous OSINT Investigation Swarm.

Subcommands
-----------
  check-env         Validate .env and verify all raw cache files are present.
  pull-entity       Pull / refresh all raw data sources for one entity.
  run-tests         Run the full pytest suite and print a pass/fail summary.
  bench-pipeline    Time the full pipeline for all 5 registered entities.
  demo-batch        [PLACEHOLDER] Batch-investigate multiple entities and export a combined report.

Usage
-----
  python scripts/dev.py check-env
  python scripts/dev.py pull-entity --entity-id tesla_inc_cik_0001318605
  python scripts/dev.py run-tests
  python scripts/dev.py bench-pipeline
  python scripts/dev.py demo-batch          # placeholder — not yet implemented
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")


# ---------------------------------------------------------------------------
# 1. check-env
# ---------------------------------------------------------------------------

def cmd_check_env(args: argparse.Namespace) -> None:
    """Validate .env variables and confirm all raw cache files exist."""
    print("=== check-env ===\n")
    ok = True

    # --- env vars ---
    required_vars = {
        "SEC_USER_AGENT": "Required for SEC EDGAR fair-use header (e.g. 'First Last email@domain.com')",
        "GROQ_API_KEY":   "Required for LLM planner, action policy, stop policy, reflexion, narrative",
    }
    print("Environment variables:")
    for var, desc in required_vars.items():
        val = os.environ.get(var, "")
        if val:
            masked = val[:6] + "…" if len(val) > 6 else val
            print(f"  [OK]  {var} = {masked}")
        else:
            print(f"  [MISSING]  {var}  — {desc}")
            ok = False

    # --- raw cache files ---
    print("\nRaw cache files:")
    expected: list[tuple[Path, str]] = [
        (ROOT / "data/raw/ofac/sdn.xml",                           "OFAC SDN list"),
        (ROOT / "data/raw/sec/CIK0001318605.json",                 "SEC — Tesla"),
        (ROOT / "data/raw/sec/CIK0000037996.json",                 "SEC — Ford"),
        (ROOT / "data/raw/sec/CIK0000012927.json",                 "SEC — Boeing"),
        (ROOT / "data/raw/sec/CIK0001652044.json",                 "SEC — Alphabet"),
        (ROOT / "data/raw/sec/CIK0000019617.json",                 "SEC — JPMorgan"),
        (ROOT / "data/raw/gdelt/news_tesla.json",                  "GDELT — Tesla"),
        (ROOT / "data/raw/gdelt/news_ford_motor.json",             "GDELT — Ford"),
        (ROOT / "data/raw/gdelt/news_the_boeing.json",             "GDELT — Boeing"),
        (ROOT / "data/raw/gdelt/news_alphabet.json",               "GDELT — Alphabet"),
        (ROOT / "data/raw/gdelt/news_jpmorgan_chase.json",         "GDELT — JPMorgan"),
        (ROOT / "data/raw/courtlistener/cases_tesla.json",         "CourtListener — Tesla"),
        (ROOT / "data/raw/courtlistener/cases_ford.json",          "CourtListener — Ford"),
        (ROOT / "data/raw/courtlistener/cases_boeing.json",        "CourtListener — Boeing"),
        (ROOT / "data/raw/courtlistener/cases_alphabet.json",      "CourtListener — Alphabet"),
        (ROOT / "data/raw/courtlistener/cases_jpmorgan_chase.json","CourtListener — JPMorgan"),
    ]
    for path, label in expected:
        if path.exists():
            size_kb = path.stat().st_size // 1024
            print(f"  [OK]  {label:<36} {size_kb:>6} KB  ({path.relative_to(ROOT)})")
        else:
            print(f"  [MISSING]  {label:<36}  ({path.relative_to(ROOT)})")
            ok = False

    print()
    if ok:
        print("All checks passed.")
    else:
        print("Some checks failed — see [MISSING] items above.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# 2. pull-entity
# ---------------------------------------------------------------------------

def cmd_pull_entity(args: argparse.Namespace) -> None:
    """Pull / refresh all raw data sources for one entity."""
    print(f"=== pull-entity: {args.entity_id} ===\n")

    from agents.lead_agent.entity_resolution.resolver import ENTITY_REGISTRY
    registry_map = {e.entity_id: e for e in ENTITY_REGISTRY}
    entity = registry_map.get(args.entity_id)
    if not entity:
        raise SystemExit(
            f"Unknown entity_id: {args.entity_id!r}\n"
            f"Available: {list(registry_map.keys())}"
        )

    cik = entity.identifiers.get("cik", "")
    steps: list[tuple[str, list[str]]] = [
        (
            "SEC EDGAR submissions",
            [sys.executable, str(ROOT / "scripts/pull_sec_submissions.py"), "--cik", cik],
        ),
        (
            "GDELT adverse media",
            [sys.executable, str(ROOT / "scripts/pull_gdelt_news.py"), "--entity-id", args.entity_id],
        ),
        (
            "CourtListener dockets",
            [sys.executable, str(ROOT / "scripts/pull_courtlistener.py"),
             "--entity-id", args.entity_id, "--name", entity.name],
        ),
        (
            "OFAC SDN list (shared)",
            [sys.executable, str(ROOT / "scripts/pull_ofac_sdn.py")],
        ),
    ]

    for label, cmd in steps:
        print(f"  Pulling {label} …")
        t0 = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.perf_counter() - t0
        if result.returncode == 0:
            print(f"  [OK]  {label} ({elapsed:.1f}s)")
        else:
            print(f"  [FAIL]  {label}")
            if result.stderr:
                print(result.stderr.strip())
            sys.exit(result.returncode)

    print(f"\nAll sources pulled for {entity.name}.")
    print(f"Next step: python scripts/build_evidence.py --entity-id {args.entity_id}")


# ---------------------------------------------------------------------------
# 3. run-tests
# ---------------------------------------------------------------------------

def cmd_run_tests(args: argparse.Namespace) -> None:
    """Run the full pytest suite and print a pass/fail summary."""
    print("=== run-tests ===\n")

    pytest_args = [sys.executable, "-m", "pytest", "tests/unit", "-v", "--tb=short"]
    if args.fast:
        pytest_args += ["-x"]
    if args.k:
        pytest_args += ["-k", args.k]

    t0 = time.perf_counter()
    result = subprocess.run(pytest_args, cwd=ROOT)
    elapsed = time.perf_counter() - t0

    print(f"\nCompleted in {elapsed:.1f}s — exit code {result.returncode}")
    sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# 4. bench-pipeline
# ---------------------------------------------------------------------------

def cmd_bench_pipeline(args: argparse.Namespace) -> None:
    """Time the full pipeline for all 5 registered entities and print a table."""
    print("=== bench-pipeline ===\n")

    from agents.lead_agent import LeadAgent
    from agents.lead_agent.entity_resolution.resolver import ENTITY_REGISTRY

    data_root = ROOT / "data"
    results: list[tuple[str, int, float, str]] = []

    for entity in ENTITY_REGISTRY:
        query = f"Investigate {entity.name} for money laundering"
        print(f"  Running: {query} …", end="", flush=True)
        try:
            t0 = time.perf_counter()
            agent = LeadAgent(data_root=data_root)
            ctx = agent.run(query)
            elapsed = time.perf_counter() - t0
            findings = len(ctx.get_all_findings())
            print(f" {findings} findings in {elapsed:.2f}s")
            results.append((entity.name, findings, elapsed, "OK"))
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            print(f" ERROR in {elapsed:.2f}s — {exc}")
            results.append((entity.name, 0, elapsed, f"ERROR: {exc}"))

    print()
    print(f"{'Entity':<30} {'Findings':>9} {'Time':>8}  Status")
    print("-" * 62)
    for name, findings, elapsed, status in results:
        print(f"  {name:<28} {findings:>9} {elapsed:>7.2f}s  {status}")

    ok_results = [(f, t) for _, f, t, s in results if s == "OK"]
    if ok_results:
        avg_findings = sum(f for f, _ in ok_results) / len(ok_results)
        avg_time = sum(t for _, t in ok_results) / len(ok_results)
        print("-" * 62)
        print(f"  {'Average':<28} {avg_findings:>9.0f} {avg_time:>7.2f}s")


# ---------------------------------------------------------------------------
# 5. demo-batch  [PLACEHOLDER]
# ---------------------------------------------------------------------------

def cmd_demo_batch(args: argparse.Namespace) -> None:
    """
    [PLACEHOLDER — not yet implemented]

    Intended behaviour:
      - Accept a list of entity names or IDs via --entities (or default to all 5)
      - Run the full pipeline for each, in parallel (ThreadPoolExecutor)
      - Aggregate all findings into a single combined JSON/CSV report
      - Write output to data/processed/batch_<timestamp>/combined_report.json
      - Print a summary table identical to bench-pipeline, plus a citation-rate column

    To implement:
      1. Import app.pipeline.run_investigation (the full pipeline function)
      2. Use concurrent.futures.ThreadPoolExecutor(max_workers=3) for parallelism
      3. Collect InvestigationResult objects and merge their .evidence lists
      4. Write the merged output via output_layer.report_builder
    """
    print("[PLACEHOLDER]  demo-batch is not yet implemented.")
    print("See the docstring in cmd_demo_batch() for the intended design.")
    sys.exit(0)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dev.py",
        description="Developer utilities for the OSINT Investigation Swarm.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # check-env
    sub.add_parser("check-env", help="Validate .env and raw cache files.")

    # pull-entity
    p_pull = sub.add_parser("pull-entity", help="Pull all data sources for one entity.")
    p_pull.add_argument(
        "--entity-id", required=True,
        help="e.g. tesla_inc_cik_0001318605",
    )

    # run-tests
    p_test = sub.add_parser("run-tests", help="Run pytest suite.")
    p_test.add_argument("--fast", action="store_true", help="Stop on first failure (-x).")
    p_test.add_argument("--k", metavar="EXPR", default="", help="pytest -k filter expression.")

    # bench-pipeline
    sub.add_parser("bench-pipeline", help="Benchmark full pipeline across all 5 entities.")

    # demo-batch (placeholder)
    sub.add_parser("demo-batch", help="[PLACEHOLDER] Batch-investigate and export combined report.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "check-env":     cmd_check_env,
        "pull-entity":   cmd_pull_entity,
        "run-tests":     cmd_run_tests,
        "bench-pipeline": cmd_bench_pipeline,
        "demo-batch":    cmd_demo_batch,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
