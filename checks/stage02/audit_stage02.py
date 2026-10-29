"""Stage02 provenance, preservation, links and bounded textual/protocol checks.

No optimizer, historical scientific script, Git mutation or network call.
Semantic equivalence and naturalness remain the executor's separate review.
"""
import argparse
import ast
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import re
import subprocess

import pypdf
from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
BASE = "91ba65b40857b33912200a32efd1ba993f7c83a5"
EDITABLE = {"README.md", "REVIEW.md", "STATE.md", "scope/P00_ALIGNMENT.md",
            "scope/ACCELERATION_MAP.md", "scope/CANDIDATES.md", "sources/manifest.json",
            "sources/READING_LOG.md", "knowledge/METHODS.md", "knowledge/WRITING.md",
            "knowledge/EXPERIMENTS.md"}
NEW = {f"papers/{pid}/{name}.md" for pid in ("ACC03", "ACC04")
       for name in ("RESEARCH", "WRITING", "EXPERIMENTS")}
NEW |= {f"checks/stage02/{name}" for name in (
    "PROTOCOL.md", "DERIVATION.md", "RESULT.md", "config.json", "verify_smoothing.py",
    "results.json", "stdout.txt", "audit_stage02.py", "audit.json")}
NEW.add("reviews/STAGE02_EXECUTOR_CHECK.md")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(name):
    return (REPO/name).read_text(encoding="utf-8")


def segment(text, pid, side):
    if pid == "ACC03":
        a, b = f"<!-- SAME_FACTS_{side.upper()}_START -->", f"<!-- SAME_FACTS_{side.upper()}_END -->"
    else:
        a, b = f"<!-- controlled-rewrite-{side} -->", f"<!-- controlled-rewrite-{side}-end -->"
    assert text.count(a) == text.count(b) == 1
    return text.split(a)[1].split(b)[0].strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    args = parser.parse_args()
    package = args.package_root.resolve()
    assert not package.is_relative_to(REPO)
    git("merge-base", "--is-ancestor", BASE, "HEAD")
    assert git("branch", "--show-current").decode().strip() == "main"
    remote = git("remote", "get-url", "origin").decode().strip()
    assert remote in ("https://github.com/SummerTianYi/Optimization-Acceleration-Knowledge.git",
                      "git@github.com:SummerTianYi/Optimization-Acceleration-Knowledge.git")
    baseline = git("ls-tree", "-r", "--name-only", BASE).decode().splitlines()
    protected = []
    for name in baseline:
        if name not in EDITABLE:
            raw = (REPO/name).read_bytes()
            assert raw == git("show", f"{BASE}:{name}"), name
            protected.append(dict(path=name, sha256=digest(raw)))

    manifest = json.loads(read("sources/manifest.json"))
    old = json.loads(git("show", f"{BASE}:sources/manifest.json"))
    fields = ("id", "bytes", "sha256", "pages", "actual_pages", "title", "authors",
              "original_filename", "package_path")
    assert len(manifest["files"]) == len(old["files"]) == 8
    sources = []
    for now, then in zip(manifest["files"], old["files"]):
        assert all(now.get(f) == then.get(f) for f in fields), now["id"]
        if now["id"] in {"ACC05", "ACC06", "ACC06-ORIGINAL"}:
            assert now == then, now["id"]
        if now["id"] in {"P00", "ACC03", "ACC04"}:
            path = package/now["package_path"]
            raw = path.read_bytes()
            pages = len(PdfReader(path).pages)
            assert len(raw) == now["bytes"] and digest(raw) == now["sha256"]
            assert pages == now["pages"]
            sources.append(dict(id=now["id"], bytes=len(raw), sha256=digest(raw), pages=pages))

    facts = []
    for pid in ("ACC03", "ACC04"):
        text = read(f"papers/{pid}/WRITING.md")
        assert re.findall(r"\| S([1-4]) \|", text) == ["1", "2", "3", "4"]
        assert "事实校准" in text and "反向" in text and "英文练习" in text
        before, after = (segment(text, pid, side) for side in ("before", "after"))
        if pid == "ACC03":
            numbers = {"50", "500", "31.06", "49.90", "21.52", "23.74",
                       "909.60", "1305.98", "32.84", "32.87", "2.22", "0.03"}
            for version in (before, after):
                assert set(re.findall(r"\d+(?:\.\d+)?", version)) == numbers
                assert "PALM" in version and "GiPALM" in version and "SNR₁" in version
            assert Q("23.74")-Q("21.52") == Q("2.22")
            assert Q("32.87")-Q("32.84") == Q("0.03")
        else:
            for version in (before, after):
                for item in ("h̃与h", "κμ", "相同的g", "近似目标差不超过ε", "原目标差", "ε+2κμ", "L/μ", "μ/L", "求解精度应与μ一起安排"):
                    assert item in version, item
            assert "最优值有限" in text and "μ∈(0,1]" in text
        facts.append(dict(paper=pid, fact_ids=["S1", "S2", "S3", "S4"],
                          before_sha256=digest(before.encode()), after_sha256=digest(after.encode()),
                          textual_invariants="pass", semantic_naturalness="manual review, not proven by string checks"))

    e3, e4 = read("papers/ACC03/EXPERIMENTS.md"), read("papers/ACC04/EXPERIMENTS.md")
    for item in ("τ=5/12", "σ=1/2", "3×2=6", "2000", "无调参", "未执行", "residual", "预算耗尽"):
        assert item in e3, item
    for item in ("4配置×2初值=8", "F*=.1||a||₁=0.5", "L=1、κ=4", "无调参", "2000", "先做有效性检查", "未执行"):
        assert item in e4, item
    inertia = [Q(0), Q(".5"), Q(".8")]
    e3_units = list(product(inertia, [(0, 0), (2, -1)]))
    assert len(e3_units) == 6
    tau, sigma, lf, lg = Q(5,12), Q(1,2), Q(6,5), Q(1)
    assert 2*lf*tau == 2*lg*sigma == 1
    rho = []
    for alpha in inertia[1:]:
        assert alpha**2 < Q(2,3)
        m1, m2 = ((Q(3,2)+1/alpha**2)*ell/2 for ell in (lf, lg))
        lower = min(m1-Q(3,2)*lf, lf/alpha**2-m1, m2-Q(3,2)*lg, lg/alpha**2-m2)
        assert lower > 0
        rho.append(dict(inertia=str(alpha), descent_margin=str(lower)))
    a = [Q(x) for x in ("-1", "-.75", "-.5", "-.25", ".25", ".5", ".75", "1")]
    fstar = Q(1,10)*sum(abs(x) for x in a)
    assert len(a) == 8 and all(-2 <= x <= 2 for x in a) and fstar == Q(1,2)
    # |x-a|+.1|x| >= .1|a| + .9|x-a|: a is the exact coordinate minimizer.
    assert Q(1,10) < 1
    e4_count = len(list(product(["FISTA_s", "PG_s", "fixed_mu_FISTA", "fixed_mu_PG"], ["zero", "one"])))
    assert e4_count == 8

    result = json.loads(read("checks/stage02/results.json"))
    config_raw = (REPO/"checks/stage02/config.json").read_bytes()
    assert result["config"] == json.loads(config_raw)
    assert result["config_sha256"] == digest(config_raw)
    assert result["script_sha256"] == digest((REPO/"checks/stage02/verify_smoothing.py").read_bytes())
    assert result["passed"] and result["assertion_count"] == 62 and not result["performance_protocols_executed"]
    assert len(result["bias_grid"]) == 24 and len(result["fixed_parameter_pairs"]) == 9 and len(result["drift_cases"]) == 3
    moving, samepoint, control = result["drift_cases"]
    assert Q(moving["same_relation_lhs"]) > Q(moving["mixed_substitution_rhs"])
    assert moving["L_same"] == "2" and moving["L_mix"] == "8/15"
    assert samepoint["D_same"] == "0" and samepoint["L_mix"] == "1/7"
    assert control["mixed_substitution_valid"]
    stdout = json.loads(read("checks/stage02/stdout.txt"))
    assert stdout["passed"] and stdout["assertions"] == 62

    cand = read("scope/CANDIDATES.md")
    assert re.findall(r"^## (C\d)：", cand, re.M) == ["C1", "C2"]
    assert "第二批后收缩保留" in cand and "网络研究不以C1先通过为前提" in cand
    assert "下一条关键证据" in cand and "§2.1(1)" in cand and "§2.2(1)" in cand and "§2.3(2)" in cand and "§3.1" in cand

    paths = [p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.relative_to(REPO).parts
             and "__pycache__" not in p.relative_to(REPO).parts]
    links, artifacts = [], []
    audit_name = "checks/stage02/audit.json"
    for path in paths:
        name = path.relative_to(REPO).as_posix()
        assert name in set(baseline) | NEW, f"Unexpected file: {name}"
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        assert len(raw) < 300000 and b"\r" not in raw and not raw.startswith(b"\xef\xbb\xbf"), name
        assert not re.search(r"(?<![A-Za-z0-9])(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{24,})", text), name
        if path.suffix == ".json":
            json.loads(text)
        if path.suffix == ".py":
            ast.parse(text)
        if path.suffix == ".md":
            prose = re.sub(r"```[\s\S]*?```|`[^`\n]*`", "", text)
            for target in re.findall(r"\]\(([^)]+)\)", prose):
                target = target.strip("<>").split("#",1)[0]
                if not target or "://" in target:
                    continue
                resolved = (path.parent/target).resolve()
                assert resolved.is_relative_to(REPO), (name, target)
                assert resolved.is_file() or resolved == REPO/audit_name, (name, target)
                links.append(dict(source=name, target=resolved.relative_to(REPO).as_posix()))
        if name in (NEW | EDITABLE) and name != audit_name:
            artifacts.append(dict(path=name, sha256=digest(raw)))
    assert all((REPO/name).is_file() for name in NEW if name != audit_name)
    output = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  scope="provenance, protected bytes, links, text invariants, static protocol algebra; no optimizer",
                  command="python checks/stage02/audit_stage02.py --package-root <external handoff>",
                  manager_base=BASE, manager_base_is_ancestor=True, branch="main",
                  environment=dict(python=platform.python_version(), pypdf=pypdf.__version__, system=platform.system()),
                  source_identities=sources, all_manifest_identity_fields_preserved=True,
                  acc05_acc06_manifest_unchanged=True, protected_files=protected,
                  writing_checks=facts, e03_static=dict(planned_units=6, descent_margins=rho, tuning_runs=0),
                  e04_static=dict(planned_units=8, exact_fstar=str(fstar), tuning_runs=0),
                  v02_saved_output_and_hashes="pass; not rerun by this audit", candidate_count=2,
                  local_link_count=len(links), local_links=links,
                  inspected_files=len(paths), artifact_hashes=artifacts,
                  scientific_scripts_executed_by_audit=[], syntax_utf8_lf_credentials_allowlist="pass", passed=True)
    (REPO/audit_name).write_bytes((json.dumps(output, ensure_ascii=False, indent=2)+"\n").encode())
    print(json.dumps(dict(passed=True, sources=len(sources), protected=len(protected), fact_sets=len(facts),
                         planned_e03=6, planned_e04=8, links=len(links), files=len(paths), scientific_runs=0)))


if __name__ == "__main__":
    main()
