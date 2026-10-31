"""Validation03 provenance, links, current state and history audit; no science rerun.

Run with three --source-dir options for the reused and new outside-Git PDFs,
and --bundle for the pre-sync backup. Requires pypdf, git and authenticated gh.
The report contains source identities, not private machine paths.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import unquote

from pypdf import PdfReader


BASE = "92fe7219ade0314a0f6dff61c25e81864005f17f"
REPO = Path(__file__).resolve().parents[2]
ALLOWED = {
    "README.md", "REVIEW.md", "STATE.md", "knowledge/METHODS.md",
    "scope/DIRECTION_SHORTLIST_V2.md", "scope/PROBLEM_EVIDENCE.md",
    "scope/RECENT_LITERATURE_MAP.md", "scope/RECENT_RESEARCH_STRATEGY.md",
    "sources/RECENT_SEARCH_LOG.md", "sources/RECENT_SOURCES.json",
}
STAGE = "checks/validation03/"


def run(*args):
    return subprocess.check_output(args, cwd=REPO)


def normalized(value):
    return "".join(c.lower() for c in unicodedata.normalize("NFKD", value)
                   if c.isalnum())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", action="append", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args()
    failures = []

    def check(condition, message):
        if not condition:
            failures.append(message)

    for path in [*args.source_dir, args.bundle]:
        check(not path.resolve().is_relative_to(REPO), "input_inside_git")
    branch = run("git", "branch", "--show-current").decode().strip()
    check(branch == "main", "branch")
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", BASE, "HEAD"],
                              cwd=REPO, capture_output=True).returncode == 0
    check(ancestor, "manager_ancestor")
    remote = run("git", "remote", "get-url", "origin").decode().strip()
    check(remote == "https://github.com/SummerTianYi/Optimization-Acceleration-Knowledge.git",
          "origin")
    info = json.loads(run("gh", "repo", "view",
                         "SummerTianYi/Optimization-Acceleration-Knowledge",
                         "--json", "nameWithOwner,isPrivate,defaultBranchRef,url"))
    check(info["isPrivate"] and info["defaultBranchRef"]["name"] == "main",
          "private_main")
    bundle = subprocess.run(["git", "bundle", "verify", str(args.bundle.resolve())],
                            cwd=REPO, capture_output=True)
    check(bundle.returncode == 0, "backup_bundle")

    # Protect every baseline file except the explicit current-stage edit surface.
    baseline_paths = run("git", "ls-tree", "-r", "--name-only", BASE).decode().splitlines()
    protected = {}
    for rel in baseline_paths:
        if rel in ALLOWED:
            continue
        original = run("git", "rev-parse", BASE + ":" + rel).decode().strip()
        protected[rel] = original
        check((REPO / rel).is_file(), "protected_missing:" + rel)
        if (REPO / rel).is_file():
            current = run("git", "hash-object", rel).decode().strip()
            check(original == current, "protected_changed:" + rel)

    output = Path(__file__).with_name("audit_result.json")
    if not output.exists():
        output.write_text("{}\n", encoding="utf-8", newline="\n")
    changed = set(run("git", "diff", "--name-only", BASE).decode().splitlines())
    changed.update(run("git", "ls-files", "--others", "--exclude-standard").decode().splitlines())
    check(all(p in ALLOWED or p.startswith(STAGE) for p in changed), "unexpected_edit")

    registry = json.loads((REPO / "sources/RECENT_SOURCES.json").read_text(encoding="utf-8"))
    old_registry = json.loads(run("git", "show", BASE + ":sources/RECENT_SOURCES.json"))
    records = registry["records"]
    by_id = {r["id"]: r for r in records}
    check(len(records) == len(by_id) == 42, "source_count_or_duplicate")
    check([r["id"] for r in records[:len(old_registry["records"])]] == [r["id"] for r in old_registry["records"]],
          "source_order_history")
    for old in old_registry["records"]:
        new = by_id.get(old["id"], {})
        check(all(new.get(k) == v for k, v in old.items() if k != "reading_updates"),
              "old_metadata:" + old["id"])
        old_reads = old.get("reading_updates", [])
        new_reads = new.get("reading_updates", [])
        check(new_reads[:len(old_reads)] == old_reads, "old_reading_history:" + old["id"])
        check(all(item["stage"] == "CANDIDATE_VALIDATION_03" for item in new_reads[len(old_reads):]),
              "new_reading_stage:" + old["id"])
        check(set(new) - set(old) <= {"reading_updates"}, "unexpected_metadata:" + old["id"])
    increments = sum(item["stage"] == "CANDIDATE_VALIDATION_03"
                     for r in records for item in r.get("reading_updates", []))
    check(increments == 6, "incremental_reading_count")
    check(by_id["R38"]["read_pdf_pages"] == "1–4,9"
          and by_id["R39"]["reading_status"] == "navigation_only_superseded_version"
          and by_id["R40"]["version"] == "2509.07580v2"
          and by_id["R40"]["related_record"] == "R39", "new_source_scope")
    check(by_id["R25S"]["reading_status"] == "downloaded_not_read"
          and not by_id["R25S"]["read_pdf_pages"], "supplement_reading_status")
    check("R36" not in by_id, "excluded_wrong_title")

    source_results = []
    for item in records:
        sid = item["id"]
        found = [directory / (sid + ".pdf") for directory in args.source_dir
                 if (directory / (sid + ".pdf")).is_file()]
        check(bool(found), "source_missing:" + sid)
        if not found:
            continue
        data = found[0].read_bytes()
        reader = PdfReader(found[0])
        digest = hashlib.sha256(data).hexdigest()
        identity = (digest == item["sha256"] and len(data) == item["bytes"]
                    and len(reader.pages) == item["pages"])
        check(identity, "source_identity:" + sid)
        for reading in [item, *item.get("reading_updates", [])]:
            numbers = [int(n) for n in re.findall(r"\d+", reading["read_pdf_pages"])]
            check(all(1 <= n <= len(reader.pages) for n in numbers), "page_range:" + sid)
        check(item["url"].startswith("https://") and item["metadata_url"].startswith("https://"),
              "source_url:" + sid)
        title_match = None
        if sid not in {r["id"] for r in old_registry["records"]}:
            head = normalized(" ".join(page.extract_text() or "" for page in reader.pages[:2]))
            title = item["title"].removeprefix("Supplement: ")
            title_match = normalized(title) in head
            check(title_match, "new_source_title:" + sid)
        source_results.append({"id": sid, "sha256": digest, "bytes": len(data),
                               "pages": len(reader.pages), "identity_matches": identity,
                               "new_title_matches_first_two_pages": title_match})

    log = (REPO / "sources/RECENT_SEARCH_LOG.md").read_text(encoding="utf-8")
    old_log = run("git", "show", BASE + ":sources/RECENT_SEARCH_LOG.md").decode("utf-8")
    check(old_log.split("\n", 1)[1].strip() in log, "old_search_log_not_preserved")
    query_ids = re.findall(r"^\|(Q\d{2}-[^|]+)\|", log, re.M)
    check(len(query_ids) == len(set(query_ids)) == 63, "query_ledger")
    pool = (REPO / "scope/PROBLEM_EVIDENCE.md").read_text(encoding="utf-8")
    old_pool = run("git", "show", BASE + ":scope/PROBLEM_EVIDENCE.md").decode("utf-8")
    old_argument = old_pool.split("## 筛选01历史论证", 1)[1].split("## 完整问题池", 1)[0].strip()
    new_argument = pool.split("## 筛选01历史论证", 1)[1].split("## 验证03增量", 1)[0].strip()
    check(old_argument == new_argument, "screen01_02_argument_history")
    rows = re.findall(r"^\|([ABCD][0-9]|C-R1|旧C[12])\|([^|]+)\|",
                      pool.split("## 完整问题池", 1)[1], re.M)
    expected = {"A1": "方法线索", "B1": "方法线索", "A2": "方法线索",
                "B2": "方法线索", "C-R1": "潜在候选", "D1": "学习实施线索",
                "B3": "问题线索", "D2": "问题线索", "D3": "问题线索",
                "A0": "关闭", "B0": "关闭", "B4": "关闭", "C0": "关闭", "D0": "关闭",
                "旧C1": "历史潜在候选", "旧C2": "历史潜在候选"}
    check(len(rows) == 16 and set(dict(rows)) == set(expected), "pool_ids")
    check(all(status.startswith(expected[sid]) for sid, status in rows), "pool_tiers")
    for rel in ["STATE.md", "REVIEW.md", "README.md"]:
        body = (REPO / rel).read_text(encoding="utf-8")
        check("待Manager独立验收" in body and "导师" in body and "STAGE03" in body,
              "current_entry:" + rel)
    shortlist = (REPO / "scope/DIRECTION_SHORTLIST_V2.md").read_text(encoding="utf-8")
    check("0项候选课题、1项潜在候选、8项线索、5条关闭主张、2项历史处置" in shortlist,
          "shortlist_counts")

    links = 0
    sensitive = []
    patterns = [r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{30,}",
                r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
                r"(?i)[A-Z]:[/\\](?:Users|UserData|AppData)[/\\]"]
    for rel in sorted(changed):
        path = REPO / rel
        if not path.is_file() or path.suffix not in {".md", ".json", ".py"}:
            continue
        text = path.read_text(encoding="utf-8")
        if any(re.search(pattern, text) for pattern in patterns):
            sensitive.append(rel)
        if path.suffix != ".md":
            continue
        # Mathematical expressions in code spans are not Markdown links.
        link_text = re.sub(r"```[\s\S]*?```|`[^`\n]*`", "", text)
        for dest in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", link_text):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", dest) or dest.startswith("#"):
                continue
            target = unquote(dest.split("#", 1)[0].strip("<>"))
            if target:
                links += 1
                resolved = (path.parent / target).resolve()
                check(resolved.is_relative_to(REPO) and resolved.is_file(), "link:" + rel + ":" + target)
        for sid in re.findall(r"\bR\d{2}[A-Z]?\b", text):
            check(sid in by_id, "source_id:" + rel + ":" + sid)
    check(not sensitive, "sensitive_pattern")
    forbidden = []
    for path in REPO.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if (path.suffix.lower() in {".pdf", ".caj", ".zip", ".png", ".jpg", ".jpeg",
                                    ".tif", ".tiff", ".pem", ".key"}
                or path.name.startswith(".env")):
            forbidden.append(path.relative_to(REPO).as_posix())
    check(not forbidden, "forbidden_files")
    a2 = json.loads(Path(__file__).with_name("a2_results.json").read_text(encoding="utf-8"))
    cb = json.loads(Path(__file__).with_name("cr1_b1_results.json").read_text(encoding="utf-8"))
    check(a2["kind"] == "finite_one_step_relation_not_performance"
          and a2["assertions"] == "passed" and len(a2["cases"]) == 2, "a2_output_scope")
    check(a2["cases"][1]["raw_mix_exact"][1] == "131/119"
          and a2["cases"][1]["projection_mean_drift"] != 0, "a2_boundary")
    check(all(c["lemma_lhs"] <= c["lemma_rhs"] and
              c["mix_envelope"] <= c["mix_envelope_upper"] and
              c["next_envelope"] <= c["descent_upper"] and
              c["projection_envelope_nonincrease"] for c in a2["cases"]), "a2_recorded_relations")
    check(cb["kind"] == "closed_form_relation_checks_not_performance"
          and cb["assertions"] == "passed" and len(cb["CR1"]["steps"]) == 3
          and len(cb["B1"]["cases"]) == 3, "cr1_b1_output_scope")
    check(sum(float(c["uncontrolled_cross"]) > 0 for c in cb["CR1"]["steps"]) == 2,
          "cr1_positive_cross")
    check(all(float(c["true_original_FW_gap"]) > 1 for c in cb["B1"]["cases"]),
          "b1_true_gap")
    diff = subprocess.run(["git", "diff", "--check"], cwd=REPO, capture_output=True)
    check(diff.returncode == 0, "diff_whitespace")
    check_files = {}
    for name in ["a2_relation.py", "a2_results.json", "cr1_b1_relations.py", "cr1_b1_results.json",
                 "A2_RELATION.md", "C_R1_RELATION.md", "A1_COVERAGE.md", "B1_RELATION.md",
                 "D3_QUALIFICATION.md", "audit.py"]:
        check_files[name] = hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()

    result = {
        "date": "2026-10-31", "baseline": BASE, "branch": branch, "manager_ancestor": ancestor,
        "remote": info, "pre_sync_bundle_verified": bundle.returncode == 0,
        "protected_files_count": len(protected), "protected_git_blob_ids": protected,
        "old_source_metadata_preserved": not any("metadata:" in f for f in failures),
        "source_documents": source_results, "new_records": 3, "new_distinct_works": 2, "new_core_readings": 2,
        "old_version_navigation_only": 1,
        "unread_supplements": 1, "incremental_readings": increments,
        "query_strings": len(query_ids), "new_query_strings": 0,
        "problem_pool_rows": len(rows), "tiers": {"candidate": 0, "potential": 1,
            "lead": 8, "closed_claim": 5, "historical": 2},
        "local_links_checked": links, "changed_files_checked": sorted(changed),
        "check_file_sha256": check_files, "sensitive_file_flags": sensitive,
        "forbidden_files": forbidden, "failures": failures,
        "scope": "File identities, new titles, local links, state, privacy patterns and history. "
                 "Original PDFs remain outside Git. No old science scripts rerun; no performance "
                 "or theorem validation. External source access is recorded in the search log.",
        "result": "PASS" if not failures else "FAIL",
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ["result", "protected_files_count", "query_strings",
                                           "problem_pool_rows", "local_links_checked", "failures"]},
                     ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
