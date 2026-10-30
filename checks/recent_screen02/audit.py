"""Stage02 provenance, links, current state and history audit; no science rerun.

Run with two --source-dir options for the existing and new outside-Git PDFs,
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


BASE = "f440b2f6d5fd52b785d0de6a85edbe61eb767609"
REPO = Path(__file__).resolve().parents[2]
ALLOWED = {
    "README.md", "REVIEW.md", "STATE.md", "knowledge/METHODS.md",
    "scope/DIRECTION_SHORTLIST_V2.md", "scope/PROBLEM_EVIDENCE.md",
    "scope/RECENT_LITERATURE_MAP.md", "scope/RECENT_RESEARCH_STRATEGY.md",
    "sources/RECENT_SEARCH_LOG.md", "sources/RECENT_SOURCES.json",
}
STAGE = "checks/recent_screen02/"


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
    check(len(records) == len(by_id) == 39, "source_count_or_duplicate")
    check([r["id"] for r in records[:25]] == [r["id"] for r in old_registry["records"]],
          "source_order_history")
    for old in old_registry["records"]:
        new = by_id.get(old["id"], {})
        check(all(new.get(k) == v for k, v in old.items()), "old_metadata:" + old["id"])
        check(set(new) - set(old) <= {"reading_updates"}, "unexpected_metadata:" + old["id"])
    check(sum(bool(r.get("reading_updates")) for r in records) == 8, "incremental_reading_count")
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
    old_argument = old_pool.split("## B1：", 1)[1].split("## 完整问题池", 1)[0].strip()
    new_argument = pool.split("## B1：", 1)[1].split("## 补齐02增量", 1)[0].strip()
    check(old_argument == new_argument, "screen01_argument_history")
    rows = re.findall(r"^\|([ABCD][0-9]|C-R1|旧C[12])\|([^|]+)\|",
                      pool.split("## 完整问题池", 1)[1], re.M)
    expected = {"A1": "潜在候选", "B1": "潜在候选", "A2": "潜在候选",
                "B2": "方法线索", "C-R1": "候选课题", "D1": "学习实施线索",
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
    check("1项候选课题、3项潜在候选、5项线索、5条关闭主张、2项历史处置" in shortlist,
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
        for dest in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
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
    scientific_output = json.loads(Path(__file__).with_name("results.json").read_text(encoding="utf-8"))
    check(scientific_output["kind"] == "algebra_and_cost_accounting_only"
          and scientific_output["assertions"] == "passed", "decision_output")
    diff = subprocess.run(["git", "diff", "--check"], cwd=REPO, capture_output=True)
    check(diff.returncode == 0, "diff_whitespace")
    check_files = {}
    for name in ["decision_checks.py", "results.json", "DERIVATION.md", "audit.py"]:
        check_files[name] = hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()

    result = {
        "date": "2026-10-31", "baseline": BASE, "branch": branch, "manager_ancestor": ancestor,
        "remote": info, "pre_sync_bundle_verified": bundle.returncode == 0,
        "protected_files_count": len(protected), "protected_git_blob_ids": protected,
        "old_source_metadata_preserved": not any("metadata:" in f for f in failures),
        "source_documents": source_results, "new_records": 14, "new_targeted_readings": 13,
        "unread_supplements": 1, "old_incremental_readings": 8,
        "query_strings": len(query_ids), "new_query_strings": 17,
        "problem_pool_rows": len(rows), "tiers": {"candidate": 1, "potential": 3,
            "lead": 5, "closed_claim": 5, "historical": 2},
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
