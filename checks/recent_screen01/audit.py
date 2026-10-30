"""Stage-specific provenance/history/link checks; not scientific validation.

python checks/recent_screen01/audit.py --source-dir <outside-Git download directory>
Requires pypdf, git and authenticated gh. Does not rerun scientific experiments.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote
from pypdf import PdfReader

BASE = 'bf294849d4908a2fb4dc5078c39c428581efc8b2'
REPO = Path(__file__).resolve().parents[2]


def run(*args):
    return subprocess.check_output(args, cwd=REPO)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, required=True)
    args = parser.parse_args()
    assert not args.source_dir.resolve().is_relative_to(REPO), 'Fulltexts must be outside Git'
    failures = []
    branch = run('git','branch','--show-current').decode().strip()
    if branch != 'main': failures.append('branch_not_main')
    ancestry = subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=REPO).returncode == 0
    if not ancestry: failures.append('manager_commit_not_ancestor')
    remote = run('git','remote','get-url','origin').decode().strip()
    if remote != 'https://github.com/SummerTianYi/Optimization-Acceleration-Knowledge.git':
        failures.append('unexpected_origin')
    remote_info = json.loads(run('gh','repo','view','SummerTianYi/Optimization-Acceleration-Knowledge',
                               '--json','nameWithOwner,isPrivate,defaultBranchRef,url'))
    if not remote_info['isPrivate'] or remote_info['defaultBranchRef']['name'] != 'main':
        failures.append('remote_private_or_main')

    base_paths=run('git','ls-tree','-r','--name-only',BASE).decode().splitlines()
    protected=[p for p in base_paths if p.startswith(('papers/','checks/','reviews/','sources/'))
               or p in ['scope/P00_ALIGNMENT.md','tasks/MASTER_PLAN.md','tasks/STAGE01_REVISION.md',
                        'tasks/STAGE02.md','tasks/STAGE03.md']]
    protected_hashes={}
    for rel in protected:
        original=run('git','rev-parse',BASE+':'+rel).decode().strip()
        file=REPO/rel
        current=run('git','hash-object',rel).decode().strip() if file.is_file() else None
        protected_hashes[rel]=original
        if current != original: failures.append('protected_content_changed:'+rel)

    registry=json.loads((REPO/'sources/RECENT_SOURCES.json').read_text(encoding='utf-8'))
    source_results=[]
    ids=set()
    for item in registry['records']:
        sid=item['id']
        if sid in ids: failures.append('duplicate_source:'+sid)
        ids.add(sid)
        pdf=args.source_dir/(sid+'.pdf')
        data=pdf.read_bytes()
        digest=hashlib.sha256(data).hexdigest()
        pages=len(PdfReader(pdf).pages)
        ok=digest==item['sha256'] and len(data)==item['bytes'] and pages==item['pages']
        if not ok: failures.append('source_identity:'+sid)
        nums=[int(n) for n in re.findall(r'\d+',item['read_pdf_pages'])]
        if any(n<1 or n>pages for n in nums): failures.append('reading_page_out_of_range:'+sid)
        source_results.append({'id':sid,'sha256':digest,'pages':pages,'identity_matches':ok})

    changed=set(run('git','diff','--name-only',BASE).decode().splitlines())
    changed.update(run('git','ls-files','--others','--exclude-standard').decode().splitlines())
    # Create only this generated report placeholder so links to the report resolve on first run.
    out=Path(__file__).with_name('audit_result.json')
    if not out.exists(): out.write_text('{}\n',encoding='utf-8')
    local_links=0
    sensitive=[]
    patterns=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),
              re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),
              re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
              re.compile(r'(?i)[A-Z]:[/\\](?:Users|UserData|AppData)[/\\]')]
    for rel in sorted(changed):
        p=REPO/rel
        if not p.is_file() or p.suffix not in ('.md','.json','.py'): continue
        body=p.read_text(encoding='utf-8')
        if any(regex.search(body) for regex in patterns): sensitive.append(rel)
        if p.suffix=='.md':
            for dest in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',body):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',dest) or dest.startswith('#'): continue
                target=unquote(dest.split('#',1)[0].strip('<>'))
                if target:
                    local_links+=1
                    resolved=(p.parent/target).resolve()
                    if not resolved.is_relative_to(REPO) or not resolved.exists():
                        failures.append('local_link:'+rel+':'+target)
            for sid in re.findall(r'\bR\d{2}A?\b',body):
                if sid not in ids: failures.append('unknown_source_id:'+rel+':'+sid)
    if sensitive: failures.append('sensitive_pattern_in_changed_files')
    forbidden=[]
    for p in REPO.rglob('*'):
        if '.git' in p.parts or not p.is_file(): continue
        if p.suffix.lower() in {'.pdf','.caj','.zip','.png','.jpg','.jpeg','.pem','.key'} or p.name.startswith('.env'):
            forbidden.append(p.relative_to(REPO).as_posix())
    if forbidden: failures.append('forbidden_repository_files')
    log=(REPO/'sources/RECENT_SEARCH_LOG.md').read_text(encoding='utf-8')
    query_count=len(re.findall(r'^\|Q\d{2}-[^|]+\|',log,re.M))
    if query_count != 46: failures.append('query_ledger_count')
    pool=(REPO/'scope/PROBLEM_EVIDENCE.md').read_text(encoding='utf-8')
    pool_table=pool.split('## 完整问题池',1)[1]
    pool_rows=re.findall(r'^\|(?:[ABCD][0-9]|C-R1|旧C[12])\|',pool_table,re.M)
    if len(pool_rows)!=16: failures.append('problem_pool_count')
    state=(REPO/'STATE.md').read_text(encoding='utf-8')
    review=(REPO/'REVIEW.md').read_text(encoding='utf-8')
    for name,body in [('STATE',state),('REVIEW',review)]:
        if '待Manager' not in body or '导师' not in body or 'STAGE03' not in body:
            failures.append('current_status_entry:'+name)
    task=(REPO/'tasks/RECENT_LITERATURE_SCREEN_01.md').read_text(encoding='utf-8')
    if '通常2—3个实质不同方向' in task: failures.append('superseded_quota_remains_active')
    outputs=json.loads((Path(__file__).with_name('results.json')).read_text(encoding='utf-8'))
    if outputs.get('kind') != 'algebra_and_cost_accounting_only' or outputs.get('assertions')!='passed':
        failures.append('decision_check_output_status')
    diff_check=subprocess.run(['git','diff','--check'],cwd=REPO,capture_output=True,text=True)
    if diff_check.returncode: failures.append('git_diff_check')
    result={'date':'2026-10-31','baseline':BASE,'branch':branch,
            'manager_ancestor':ancestry,'remote':remote_info,
            'protected_files_count':len(protected),'protected_git_blob_ids':protected_hashes,
            'source_documents':source_results,'query_strings':query_count,
            'problem_pool_rows':len(pool_rows),'local_links_checked':local_links,
            'changed_files_checked':sorted(changed),'sensitive_file_flags':sensitive,
            'forbidden_files':forbidden,'failures':failures,
            'scope':'Identity, local links, state markers, privacy patterns and history only; mathematical judgments require independent review.',
            'result':'PASS' if not failures else 'FAIL'}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['result','protected_files_count','query_strings','problem_pool_rows','local_links_checked','failures']},ensure_ascii=False))
    if failures: raise SystemExit(1)


if __name__=='__main__':
    main()
