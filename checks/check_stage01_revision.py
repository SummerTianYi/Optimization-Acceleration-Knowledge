"""Bounded revision audit. No optimizer or historical scientific script is run.

Requires pypdf. Supply --package-root for the original handoff outside Git.
Semantic equivalence and naturalness require the separate human review record.
"""
import argparse
import ast
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import re
import subprocess

from pypdf import PdfReader
import pypdf

BASE = "e53d9271e89b832a6996e2eff225be94416e547f"
REPO = Path(__file__).resolve().parents[1]
EDITABLE = {
    "AGENTS.md", "README.md", "REVIEW.md", "STATE.md",
    "knowledge/EXPERIMENTS.md", "knowledge/METHODS.md", "knowledge/WRITING.md",
    "papers/ACC01/EXPERIMENTS.md", "papers/ACC01/WRITING.md",
    "papers/ACC02/EXPERIMENTS.md", "papers/ACC02/WRITING.md",
    "scope/ACCELERATION_MAP.md", "scope/CANDIDATES.md",
    "sources/READING_LOG.md", "sources/manifest.json",
}
NEW_FILES = {"checks/check_stage01_revision.py", "checks/results/stage01_revision_audit.json",
             "reviews/STAGE01_REVISION_EXECUTOR_CHECK.md"}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(name):
    return (REPO / name).read_text(encoding="utf-8")


def rewrite(text, side):
    return text.split(f"<!-- controlled-rewrite-{side} -->", 1)[1].split(
        f"<!-- controlled-rewrite-{side}-end -->", 1)[0].strip().removeprefix("> ")


def select_c(rows, budget):
    """Decision-table check: None denotes failure, not an optimization run."""
    if not any(any(cost is not None for cost in costs) for costs in rows.values()):
        return None
    return min(rows, key=lambda c: (
        -sum(cost is not None for cost in rows[c]),
        sum(budget if cost is None else cost for cost in rows[c]), c))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    package = parser.parse_args().package_root.resolve()
    assert not package.is_relative_to(REPO), "Originals must stay outside Git"
    git("merge-base", "--is-ancestor", BASE, "HEAD")
    baseline = git("ls-tree", "-r", "--name-only", BASE).decode().splitlines()
    protected = []
    for name in baseline:
        if name not in EDITABLE:
            raw = (REPO / name).read_bytes()
            assert raw == git("show", f"{BASE}:{name}"), name
            protected.append({"path": name, "sha256": digest(raw)})
    manifest = json.loads(read("sources/manifest.json"))
    old_manifest = json.loads(git("show", f"{BASE}:sources/manifest.json"))
    identity_fields = ("id", "bytes", "sha256", "pages", "actual_pages", "title",
                       "authors", "original_filename", "package_path")
    assert len(manifest["files"]) == len(old_manifest["files"]) == 8
    sources = []
    for current, old in zip(manifest["files"], old_manifest["files"]):
        assert all(current.get(key) == old.get(key) for key in identity_fields)
        if current["id"] in {"P00", "ACC01", "ACC02"}:
            path = package / current["package_path"]
            raw = path.read_bytes()
            assert len(raw) == current["bytes"] and digest(raw) == current["sha256"]
            pages = len(PdfReader(path).pages)
            assert pages == current["actual_pages"]
            sources.append({"id": current["id"], "sha256": digest(raw), "bytes": len(raw), "pages": pages})

    a, b = read("papers/ACC01/WRITING.md"), read("papers/ACC02/WRITING.md")
    formulas = ["x[k+1]=W x[k]−α y[k]+β(x[k]−x[k−1])", "y[k+1]=W y[k]+g[k+1]−g[k]"]
    condition = ("Let f be convex and L-smooth on a real Hilbert space, with a nonempty "
                 "set of minimizers, and consider (6) initialized with x₀=y₀ under Hypothesis 2.1.")
    facts = []
    for pid, text, prefix in (("ACC01", a, "A"), ("ACC02", b, "B")):
        assert re.findall(rf"\| ({prefix}\d) \|", text) == [f"{prefix}{i}" for i in range(1, 5)]
        assert "事实校准示例" in text and "自然性反向审查" in text
        before, after = rewrite(text, "before"), rewrite(text, "after")
        for version in (before, after):
            if pid == "ACC01":
                for invariant in formulas + ["全局目标是m个局部目标的平均", "每个局部目标又是其p_i个样本函数的平均",
                                            "通信网络无向连通", "W是与该网络相关的双随机权重矩阵"]:
                    assert invariant in version, (pid, invariant)
            else:
                assert version.startswith(condition)
                for invariant in ("function values and gradients at consecutive iterates", "next step size without a line search",
                                  "objective gap", "o(k⁻²)", "both iterate sequences converge weakly to the same minimizer"):
                    assert invariant in version.lower(), invariant
        facts.append({"paper": pid, "fact_ids": [f"{prefix}{i}" for i in range(1, 5)],
                      "before_sha256": digest(before.encode()), "after_sha256": digest(after.encode()),
                      "invariant_text_checks": "pass", "semantic_and_naturalness_review": "manual; see executor review"})
    assert "摘要 PDF6/印I" in a
    e1, e2 = read("papers/ACC01/EXPERIMENTS.md"), read("papers/ACC02/EXPERIMENTS.md")
    old_e1 = git("show", f"{BASE}:papers/ACC01/EXPERIMENTS.md").decode()
    assert e1.split("## 原报告", 1)[1].split("## 迁移设计 E01", 1)[0] == old_e1.split(
        "## 原报告", 1)[1].split("## 迁移设计 E01", 1)[0]
    old_e2 = git("show", f"{BASE}:papers/ACC02/EXPERIMENTS.md").decode()
    assert e2.split("## 迁移设计 E03", 1)[1].split("修订自查：", 1)[0].rstrip() == old_e2.split(
        "## 迁移设计 E03", 1)[1].split("实验自查：", 1)[0].rstrip()

    # Planned configuration keys only: no generated data, f/g evaluations or trajectories.
    cs = [Fraction(x) for x in re.search(r"c∈\{([^}]+)\}", e1)[1].split(",")]
    train = [int(x) for x in re.search(r"训练种子为\{([^}]+)\}", e1)[1].split(",")]
    test = [int(x) for x in re.search(r"测试为\{([^}]+)\}", e1)[1].split(",")]
    betas = [Fraction(x) for x in re.search(r"4个β∈\{([^}]+)\}", e1)[1].split(",")]
    assert len(cs) == len(set(cs)) == 5 and set(train).isdisjoint(test)
    graphs = ["J", "lazy_ring"]
    main_train = set(product(["HB", "SAGA", "FGT"], graphs, cs, train))
    ablation = set(product(graphs, test, [Fraction(0), Fraction(".05")]))
    sensitivity = set(product(graphs, cs, betas, train))
    reused = {key for key in sensitivity if key[2] in {0, Fraction(".05")}}
    assert (len(main_train), 3*len(graphs)*len(test), len(ablation), len(sensitivity), len(reused)) == (90, 42, 28, 120, 60)
    for invariant in ("Lf=max_i,h λ_max(Hᵢₕ)", "μ=λ_min(H)", "α=c/Lf", "HB固定β=0.05", "GT-SAGA及FGT固定β=0",
                      "平均惩罚梯度成本升序", "仍平手选较小c", "所有c均零成功", "下一轮将超B时停止"):
        assert invariant in e1, invariant
    budget, c0, c1 = 10**6, cs[0], cs[1]
    cases = [
        ("success_count_first", {c0: [1, None, None], c1: [budget-1, budget-1, None]}, c1),
        ("penalty_cost_second", {c0: [100, 100, None], c1: [90, 90, None]}, c1),
        ("smaller_c_tie", {c1: [100, None, None], c0: [100, None, None]}, c0),
        ("all_failed_no_configuration", {c: [None]*3 for c in cs}, None),
    ]
    decisions = []
    for label, rows, expected in cases:
        selected = select_c(rows, budget)
        assert selected == expected, label
        decisions.append({"case": label, "synthetic_costs": {str(c): v for c, v in rows.items()},
                          "expected": str(expected), "actual": str(selected), "passed": True})
    m = beta = gamma = Fraction(1, 2)
    t0 = Fraction(2)
    lhs, rhs = (1+beta)*gamma/2, (2*(t0-1)+m)/(2*t0+m)
    assert lhs == Fraction(3, 8) and rhs == Fraction(5, 9) and lhs <= rhs
    assert len(set(product([100, 10000], ["positive", "semidefinite"], ["ACC02", "GD", "NAG", "NAG_backtracking"]))) == 16
    for invariant in ("m=0.5,t₀=2,β=0.5,γ=0.5", "η=ω=0.5", "不调参", "r_k=(f(q_k)−f*)/max(1,|f(x₀)−f*|)",
                      "N_f+N_grad≤200000", "不降低、不重置", "每外轮至多100个候选", "ℓ←2ℓ",
                      "f(z)≤f(v_k)+〈g,z−v_k〉+(ℓ/2)||z−v_k||²",
                      "v_{k+1}=z_{k+1}+((t_k−1)/t_{k+1})(z_{k+1}−z_k)", "惯性只在接受后更新一次"):
        assert invariant in e2, invariant
    assert "未执行" in e1 and "未执行" in e2
    candidates = read("scope/CANDIDATES.md")
    assert re.findall(r"^## (C\d)：", candidates, re.M) == ["C1", "C2"]
    for invariant in ("可选的集中凸前置", "潜在联系，未直接覆盖", "等待ACC03/ACC04",
                      "网络研究不以C1先通过为前提", "默认由Manager下达ACC03/ACC04完整蒸馏"):
        assert invariant in candidates, invariant

    paths = [p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.relative_to(REPO).parts]
    links = []
    for path in paths:
        name = path.relative_to(REPO).as_posix()
        assert name in set(baseline) | NEW_FILES, f"Unexpected file: {name}"
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        assert len(raw) < 300000 and b"\r\n" not in raw, name
        assert not re.search(r"(?<![A-Za-z0-9])(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{24,})", text), name
        if path.suffix == ".json":
            json.loads(text)
        if path.suffix == ".py":
            ast.parse(text)
        if path.suffix == ".md":
            prose = re.sub(r"```[\s\S]*?```|`[^`\n]*`", "", text)
            for target in re.findall(r"\]\(([^)]+)\)", prose):
                target = target.strip("<>").split("#", 1)[0]
                if not target or "://" in target:
                    continue
                resolved = (path.parent / target).resolve()
                assert resolved.is_relative_to(REPO) and resolved.is_file(), (name, target)
                links.append({"from": name, "to": resolved.relative_to(REPO).as_posix()})
    assert all((REPO / name).is_file() for name in NEW_FILES)
    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Engineering, textual invariants and decision tables only; no scientific experiment or independent acceptance",
        "command": "python checks/check_stage01_revision.py --package-root <external-handoff-directory>",
        "environment": {"python": platform.python_version(), "pypdf": pypdf.__version__, "system": platform.system()},
        "manager_base": BASE, "manager_base_is_ancestor": True, "original_identities_checked": sources,
        "all_eight_manifest_identities_preserved": True, "protected_files_equal_manager_base": protected,
        "original_acc01_experiment_audit_and_e03_preserved": True, "writing_invariants": facts,
        "e01_planned_counts": {"main_training": 90, "per_method_training": 30, "main_testing": 42,
                               "ablation": 28, "sensitivity": 120, "reused_training": 60, "additional_sensitivity": 60},
        "synthetic_selection_cases_not_experiments": decisions,
        "e02_static_checks": {"parameter_lhs": str(lhs), "parameter_rhs": str(rhs), "planned_performance_units": 16,
                               "backtracking_retry_limit": 100, "oracle_budget": 200000},
        "candidate_count": 2, "local_link_count": len(links), "local_links": links,
        "inspected_file_count": len(paths), "file_allowlist_utf8_lf_syntax_credentials": "pass",
        "scientific_scripts_executed": [], "passed": True,
    }
    (REPO / "checks/results/stage01_revision_audit.json").write_bytes((json.dumps(result, ensure_ascii=False, indent=2)+"\n").encode())
    print(json.dumps({"passed": True, "sources": len(sources), "protected_files": len(protected), "fact_sets": len(facts),
                      "synthetic_selection_cases": len(decisions), "local_links": len(links), "files": len(paths), "scientific_runs": 0}))


if __name__ == "__main__":
    main()
