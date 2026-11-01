"""Check the 04 delivery against its manager base. Needs git, gh and pypdf.

From the repository, pass --materials DIR, --bundle FILE and one --source-dir
DIR for each of the four outside-repository PDF directories. Prints JSON and
writes the same receipt next to this script. No historical experiment is run.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
BASE = "726224d05a300d15d77a97800ba6b8c73b186847"
SLUG = "SummerTianYi/Optimization-Acceleration-Knowledge"
CURRENT = {
    "README.md", "STATE.md", "REVIEW.md", "tasks/MASTER_PLAN.md",
    "scope/ACCELERATION_MAP.md", "scope/CANDIDATES.md", "scope/P00_ALIGNMENT.md",
    "scope/PROBLEM_EVIDENCE.md", "scope/DIRECTION_SHORTLIST_V2.md",
    "scope/RECENT_LITERATURE_MAP.md", "sources/RECENT_SEARCH_LOG.md",
    "sources/RECENT_SOURCES.json",
}
CHECKS = {f"checks/topic04/{n}" for n in
          ("audit.py", "audit_result.json", "fusion_geometry.py", "fusion_geometry_result.json")}


def run(*args):
    return subprocess.check_output(args, cwd=ROOT)


def doc(path):
    return (ROOT / path).read_text(encoding="utf-8")


def normalize(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s).lower() if c.isalnum())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--materials", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, action="append", required=True)
    args = parser.parse_args()
    failures = []

    def verify(ok, reason):
        if not ok:
            failures.append(reason)

    for path in [args.materials, args.bundle, *args.source_dir]:
        verify(not path.resolve().is_relative_to(ROOT), "input_inside_repo")
    meta = json.loads(run("gh", "repo", "view", SLUG, "--json", "nameWithOwner,isPrivate,defaultBranchRef"))
    verify(meta["nameWithOwner"] == SLUG and meta["isPrivate"] and meta["defaultBranchRef"]["name"] == "main", "target")
    verify(run("git", "remote", "get-url", "origin").decode().strip() == f"https://github.com/{SLUG}.git", "origin")
    verify(run("git", "branch", "--show-current").strip() == b"main", "local_branch")
    verify(subprocess.run(["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT).returncode == 0, "ancestry")
    backup = args.bundle.resolve()
    verify(subprocess.run(["git", "bundle", "verify", backup], cwd=ROOT, capture_output=True).returncode == 0, "bundle_verify")
    heads = run("git", "bundle", "list-heads", str(backup)).decode()
    verify("c0df5732da2ae72d16380824854ca26e147b27b0 refs/heads/main" in heads, "bundle_pre_sync_head")

    changed = set(run("git", "diff", "--name-only", BASE).decode().splitlines())
    changed.update(run("git", "ls-files", "--others", "--exclude-standard").decode().splitlines())
    verify(changed <= CURRENT | CHECKS, "changes_outside_delivery")
    old_paths = set(run("git", "ls-tree", "-r", "--name-only", BASE).decode().splitlines())
    protected = old_paths - CURRENT
    verify(not protected.intersection(changed), "protected_baseline_diff")

    materials = json.loads(doc("sources/manifest.json"))["files"]
    for item in materials:
        matches = list(args.materials.glob(item["id"] + "_*"))
        verify(len(matches) == 1, "material_path:" + item["id"])
        if len(matches) != 1:
            continue
        data = matches[0].read_bytes()
        verify(len(data) == item["bytes"] and hashlib.sha256(data).hexdigest() == item["sha256"], "material_identity:" + item["id"])
        if matches[0].suffix.lower() == ".pdf":
            verify(len(PdfReader(matches[0]).pages) == item["pages"], "material_pages:" + item["id"])

    reg_path = "sources/RECENT_SOURCES.json"
    old_records = json.loads(run("git", "show", BASE + ":" + reg_path))["records"]
    records = json.loads(doc(reg_path))["records"]
    ids = {r["id"] for r in records}
    verify(len(records) == len(ids) == 49, "registry")
    for old, new in zip(old_records, records):
        if old["id"] != "R06":
            verify(old == new, "history:" + old["id"])
        else:
            verify({k: v for k, v in old.items() if k != "reading_updates"}
                   == {k: v for k, v in new.items() if k != "reading_updates"}
                   and new["reading_updates"][:-1] == old.get("reading_updates", [])
                   and new["reading_updates"][-1]["stage"] == "TOPIC_FORMULATION_04", "R06_history")
    added = {r["id"] for r in records[len(old_records):]}
    verify(added == {f"R{i}" for i in range(41, 48)}, "added_sources")
    for rec in records:
        sid = rec["id"]
        paths = [d / (sid + ".pdf") for d in args.source_dir if (d / (sid + ".pdf")).is_file()]
        verify(len(paths) == 1, "source_path:" + sid)
        if not paths:
            continue
        raw = paths[0].read_bytes()
        pdf = PdfReader(paths[0])
        verify(rec["bytes"] == len(raw) and rec["sha256"] == hashlib.sha256(raw).hexdigest()
               and rec["pages"] == len(pdf.pages), "source_identity:" + sid)
        if sid in added:
            verify(normalize(rec["title"]) in normalize(" ".join(p.extract_text() or "" for p in pdf.pages[:2])), "title:" + sid)
            verify(rec["url"].endswith(rec["version"]), "version_url:" + sid)
        for reading in (rec, *rec.get("reading_updates", [])):
            pg = map(int, re.findall(r"\d+", reading["read_pdf_pages"]))
            verify(all(1 <= n <= len(pdf.pages) for n in pg), "reading_pages:" + sid)

    log = doc("sources/RECENT_SEARCH_LOG.md")
    queries = re.findall(r"^\|((?:Q\d{2}-[^|]+|T04-\d{2}))\|", log, re.M)
    old_log = run("git", "show", BASE + ":sources/RECENT_SEARCH_LOG.md").decode()
    old_query_rows = re.findall(r"^\|Q\d{2}-[^\n]+", old_log, re.M)
    verify(old_query_rows == re.findall(r"^\|Q\d{2}-[^\n]+", log, re.M), "historical_queries")
    # Previous derivations and the archived 16-row snapshot must survive in place.
    pool_path = "scope/PROBLEM_EVIDENCE.md"
    old_body = run("git", "show", BASE + ":" + pool_path).decode().split("## 筛选01历史论证", 1)[1]
    old_body = old_body.replace("## 完整问题池：有效线索、关闭主张和旧候选均保留", "## 03 验收时的问题池（历史快照）")
    verify(old_body.strip() in doc(pool_path), "historical_science_text")
    verify(len(queries) == len(set(queries)) == 80 and sum(q.startswith("T04-") for q in queries) == 17, "query_ids")
    pool = doc("scope/PROBLEM_EVIDENCE.md").split("## 04 复评与当前索引", 1)[1]
    expected = {"A0","A1","A2","B0","B1","B2","B3","B4","C0","C-R1","D0","D1","D2","D3","旧C1","旧C2"}
    rows = re.findall(r"^\|([^|]+)\|", pool, re.M)[2:]
    verify(set(rows) == expected and len(rows) == 16, "pool_reappraisal")
    cards = re.findall(r"^## T04-(\d) · (.+)$", doc("scope/DIRECTION_SHORTLIST_V2.md"), re.M)
    verify([n for n, _ in cards] == list("12345"), "card_ids")
    for name in ("README.md", "REVIEW.md", "STATE.md"):
        verify("选题体系重构与课题形成04完成，待Manager独立验收" in doc(name), "entry:" + name)

    links = 0
    scanned = (CURRENT | CHECKS) - {"checks/topic04/audit_result.json"}
    for rel in sorted(scanned):
        body = doc(rel)
        for pattern in (r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{30,}",
                        r"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----", r"(?i)[A-Z]:[/\\](?:Users|UserData|AppData)[/\\]"):
            verify(not re.search(pattern, body), "privacy:" + rel)
        if not rel.endswith(".md"):
            continue
        prose = re.sub(r"\x60\x60\x60[\s\S]*?\x60\x60\x60|\x60[^\x60\n]*\x60", "", body)
        for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", prose):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                continue
            target = ((ROOT / rel).parent / unquote(link.split("#")[0])).resolve()
            # The receipt itself is generated at the end of this check.
            verify(target.is_relative_to(ROOT) and (target.is_file() or target == Path(__file__).with_name("audit_result.json").resolve()), "link:" + rel + ":" + link)
            links += 1
        for sid in re.findall(r"(?<![\w-])(R\d{2}[A-Z]?)(?![\w-])", body):
            verify(sid in ids, "citation:" + sid)
    forbidden = {".pdf",".caj",".zip",".png",".jpeg",".jpg",".tif",".tiff",".key",".pem",".bundle"}
    for path in ROOT.rglob("*"):
        if ".git" not in path.parts and path.is_file():
            verify(path.suffix.lower() not in forbidden and not path.name.startswith(".env"), "forbidden_file")
    recorded = json.loads(doc("checks/topic04/fusion_geometry_result.json"))
    reproduced = json.loads(run(sys.executable, "checks/topic04/fusion_geometry.py"))
    verify(recorded == reproduced and recorded["two_columns"]["column_specific_squared_norm_lower_bound"] == "5/4", "finite_check")
    verify(subprocess.run(["git", "diff", "--check", BASE], cwd=ROOT).returncode == 0, "diff_whitespace")
    result = {"date": "2026-11-01", "baseline": BASE, "repository": meta, "pre_sync_head_verified": "c0df5732da2ae72d16380824854ca26e147b27b0",
              "protected_baseline_files": len(protected), "source_files": len(records), "new_pdf_titles": sorted(added),
              "material_ids": [m["id"] for m in materials], "query_strings": len(queries), "new_queries": 17,
              "historical_ids_reappraised": rows, "proposal_titles": dict(cards), "local_links_checked": links,
              "finite_check": "rational single-column fusion and two-column spectral-ball boundary",
              "scope": "File identities, scoped history, local links, current entries and privacy patterns. No performance or novelty test.",
              "failures": failures, "result": "FAIL" if failures else "PASS"}
    Path(__file__).with_name("audit_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8", newline="\n")
    print(json.dumps(result, ensure_ascii=False))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
