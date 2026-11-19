#!/usr/bin/env python3
"""Idempotent GitHub Projects V2 / issues bootstrapper. Uses authenticated GitHub CLI.

Default mode is read-only, --apply requires an explicit repository confirmation.
No code from the target repository is modified by this program.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

PRIORITIES = {'P0', 'P1', 'P2', 'P3'}
KEY_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]{1,79}$')
REPO_RE = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
MARKER = '<!-- github-project-orchestrator:key={key} -->'
COLORS = {'P0':'B60205', 'P1':'D93F0B', 'P2':'FBCA04', 'P3':'0E8A16'}

class SetupError(Exception):
    pass


def validate_date(value, path):
    if value in ('', None):
        return None
    try:
        parsed = dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        raise SetupError(f'{path}: expected ISO date YYYY-MM-DD') from None
    if parsed.isoformat() != value:
        raise SetupError(f'{path}: expected YYYY-MM-DD')
    return value


def validate(raw):
    if not isinstance(raw, dict) or raw.get('schema_version') != 1:
        raise SetupError('schema_version must be 1')
    repo = raw.get('repository')
    if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
        raise SetupError('repository must be OWNER/REPO')
    project = raw.get('project')
    if not isinstance(project, dict) or not str(project.get('title', '')).strip():
        raise SetupError('project.title is required')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', str(project.get('owner', repo.split('/')[0]))):
        raise SetupError('project.owner must be a valid GitHub login')
    milestones = raw.get('milestones', [])
    issues = raw.get('issues', [])
    if not isinstance(milestones, list) or not isinstance(issues, list):
        raise SetupError('milestones and issues must be arrays')
    ms_keys = set()
    ms_titles = set()
    for m in milestones:
        if not isinstance(m, dict) or not KEY_RE.fullmatch(str(m.get('key', ''))):
            raise SetupError('every milestone needs a unique stable key')
        if m['key'] in ms_keys or not m.get('title') or m['title'] in ms_titles:
            raise SetupError(f'duplicate or empty milestone: {m}')
        ms_keys.add(m['key']); ms_titles.add(m['title'])
        validate_date(m.get('due_on'), f'milestone {m["key"]} due_on')
    issue_keys, issue_titles = set(), set()
    for i in issues:
        if not isinstance(i, dict) or not KEY_RE.fullmatch(str(i.get('key', ''))):
            raise SetupError('each issue needs a stable key (2-80 letters/digits/_/-)')
        if i['key'] in issue_keys or not i.get('title') or i['title'] in issue_titles:
            raise SetupError(f'duplicate issue key/title: {i}')
        issue_keys.add(i['key']); issue_titles.add(i['title'])
        if i.get('priority', 'P2') not in PRIORITIES:
            raise SetupError(f'issue {i["key"]}: invalid priority')
        if i.get('kind', 'task') not in ('epic', 'task'):
            raise SetupError(f'issue {i["key"]}: kind must be epic or task')
        if i.get('milestone') is not None and i['milestone'] not in ms_keys:
            raise SetupError(f'issue {i["key"]}: unknown milestone')
        validate_date(i.get('start_date'), f'issue {i["key"]} start_date')
        validate_date(i.get('target_date'), f'issue {i["key"]} target_date')
        if i.get('start_date') and i.get('target_date') and i['start_date'] > i['target_date']:
            raise SetupError(f'issue {i["key"]}: start_date after target_date')
        if i.get('blocked_by', []) and not isinstance(i['blocked_by'], list):
            raise SetupError(f'issue {i["key"]}: blocked_by must be a list')
    for i in issues:
        if i.get('parent') is not None and i['parent'] not in issue_keys:
            raise SetupError(f'issue {i["key"]}: parent key not found')
        if i.get('parent') == i['key']:
            raise SetupError(f'issue {i["key"]} cannot parent itself')
        for b in i.get('blocked_by', []):
            if b not in issue_keys or b == i['key']:
                raise SetupError(f'issue {i["key"]}: invalid blocker {b}')
    def cycle_check(relation):
        graph = {i['key']: ([i[relation]] if relation == 'parent' and i.get(relation) else i.get(relation, [])) for i in issues}
        visiting, visited = set(), set()
        def visit(k):
            if k in visiting:
                raise SetupError(f'cycle detected in {relation}: {k}')
            if k in visited:
                return
            visiting.add(k)
            for n in graph[k]: visit(n)
            visiting.remove(k); visited.add(k)
        for k in graph: visit(k)
    cycle_check('parent'); cycle_check('blocked_by')
    return raw


def run(*args, data=None, json_result=False, allow_failure=False):
    command = ['gh', *map(str, args)]
    if data is not None and args and args[0] == 'api':
        command.extend(['--input', '-'])
    p = subprocess.run(command, input=(json.dumps(data) if data is not None else None),
                       text=True, capture_output=True, check=False)
    if p.returncode != 0:
        if allow_failure:
            return None
        raise SetupError('GitHub CLI command failed: ' + ' '.join(command) + '\n' + p.stderr.strip())
    if json_result:
        try:
            return json.loads(p.stdout)
        except json.JSONDecodeError:
            raise SetupError('Expected JSON from ' + ' '.join(command)) from None
    return p.stdout.strip()


def issues_state(repo):
    data = run('issue', 'list', '--repo', repo, '--state', 'all', '--limit', '1000',
               '--json', 'number,title,body,url,milestone,labels', json_result=True)
    if not isinstance(data, list):
        raise SetupError('Unexpected gh issue list schema')
    if len(data) >= 1000:
        raise SetupError('>=1000 issues found: pagination required; stop to prevent duplicates')
    return data


def milestones_state(repo):
    pages = run('api', '--method', 'GET', '--paginate', '--slurp',
                f'repos/{repo}/milestones?state=all&per_page=100', json_result=True)
    if not isinstance(pages, list):
        raise SetupError('Unexpected milestones schema')
    return [x for page in pages for x in page]


def project_state(owner):
    raw = run('project', 'list', '--owner', owner, '--limit', '1000', '--format', 'json', json_result=True)
    return raw.get('projects', [])


def fields_state(number, owner):
    raw = run('project', 'field-list', number, '--owner', owner, '--limit', '200',
              '--format', 'json', json_result=True)
    return raw.get('fields', [])


def items_state(number, owner):
    raw = run('project', 'item-list', number, '--owner', owner, '--limit', '2000',
              '--format', 'json', json_result=True)
    items = raw.get('items', [])
    if len(items) >= 2000:
        raise SetupError('Project item limit reached; stop to avoid duplicates')
    return items


def desired_body(issue):
    body = str(issue.get('body') or '').strip()
    if not body:
        body = ('## Outcome\nExplain the deliverable.\n\n## Acceptance criteria\n'
                '- [ ] Work verified and evidence linked\n\n## Tests / evidence\nTo be defined during triage.')
    return body + '\n\n' + MARKER.format(key=issue['key']) + '\n'


def find_issue(existing, issue):
    marker = MARKER.format(key=issue['key'])
    by_key = [x for x in existing if marker in (x.get('body') or '')]
    if len(by_key) > 1:
        raise SetupError(f'Nonunique managed issue key {issue["key"]}')
    if by_key:
        return by_key[0], 'managed'
    by_title = [x for x in existing if x.get('title') == issue['title']]
    if len(by_title) > 1:
        raise SetupError(f'Multiple issues share title {issue["title"]}')
    return (by_title[0], 'matched-title') if by_title else (None, 'new')


def notice(action, dry):
    print(('PLAN ' if dry else 'DONE ') + action)


def execute(plan, apply=False, with_views=False):
    repo = plan['repository']
    owner = plan['project'].get('owner') or repo.split('/')[0]
    title = plan['project']['title']
    dry = not apply
    now = dt.datetime.now(ZoneInfo('Europe/Rome')).isoformat(timespec='seconds')
    print(f'GitHub Project Orchestrator | {now} | repo={repo} | mode={"APPLY" if apply else "READ ONLY"}')
    if shutil.which('gh') is None:
        raise SetupError('GitHub CLI (gh) is required for connected dry runs and apply. Run check-only first.')
    run('auth', 'status')
    ps = project_state(owner)
    matches = [p for p in ps if p.get('title') == title]
    if len(matches) > 1:
        raise SetupError('Several projects have same title; resolve ambiguity')
    project = matches[0] if matches else None
    new_project = project is None
    existing_issues = issues_state(repo)
    ms = {x['title']:x for x in milestones_state(repo)}
    try:
        labels = run('label','list','--repo',repo,'--limit','1000','--json','name',json_result=True)
    except SetupError:
        labels = []
    label_set = {v['name'] for v in labels}
    if len(labels) >= 1000:
        raise SetupError('Label list hit 1000; cannot guarantee duplicate-safe sync')
    if new_project:
        notice(f'create Project V2 {owner}/{title}', dry)
        if apply:
            project = run('project','create','--owner',owner,'--title',title,'--format','json',json_result=True)
            run('project','link',project['number'],'--owner',owner,'--repo',repo)
            if plan['project'].get('description'):
                run('project','edit',project['number'],'--owner',owner,
                    '--description',plan['project']['description'])
            if plan['project'].get('visibility'):
                run('project','edit',project['number'],'--owner',owner,
                    '--visibility',plan['project']['visibility'])
    else:
        notice(f'reuse existing Project V2 #{project["number"]}: {title}', dry)
    for p in ('P0','P1','P2','P3'):
        label = 'priority:'+p
        if label not in label_set:
            notice('create label '+label, dry)
            if apply:
                run('label','create',label,'--repo',repo,'--color',COLORS[p],
                    '--description','Managed priority '+p)
    for kind in ('epic', 'task'):
        label = 'type:'+kind
        if label not in label_set:
            notice('create label '+label, dry)
            if apply:
                run('label','create',label,'--repo',repo,'--color','1D76DB',
                    '--description','Project work type '+kind)
    for m in plan['milestones']:
        if m['title'] not in ms:
            notice('create milestone '+m['title'], dry)
            if apply:
                data={'title':m['title'], 'description':m.get('description','')}
                if m.get('due_on'):
                    # Due dates are approved planning proposals in the supplied plan.
                    data['due_on']=m['due_on']+'T23:59:00Z'
                run('api','--method','POST',f'repos/{repo}/milestones',data=data)
    number = project.get('number') if project else None
    if number:
        fields = {f['name']:f for f in fields_state(number, owner)}
    else:
        fields = {}
    field_defs=[('Priority','SINGLE_SELECT','P0,P1,P2,P3'),
                ('Start date','DATE',None),('Target date','DATE',None)]
    for name,kind,opts in field_defs:
        if name not in fields:
            notice('create Project field '+name+' ('+kind+')', dry)
            if apply:
                args=['project','field-create',number,'--owner',owner,
                      '--name',name,'--data-type',kind]
                if opts:
                    args+=['--single-select-options',opts]
                run(*args)
    # Re-check existing Priority configuration: never overwrite incompatible human option sets.
    if apply:
        refreshed = {f['name']: f for f in fields_state(number, owner)}
    else:
        refreshed = fields
    pri_field = refreshed.get('Priority', {})
    pri_opts = {o.get('name') for o in pri_field.get('options', [])} if pri_field else set()
    priority_ready = bool(pri_opts) and PRIORITIES.issubset(pri_opts)
    if apply and not priority_ready:
        print('REVIEW: Priority field options unverified/incompatible; skip Project Priority edits; priority labels remain.', file=sys.stderr)
    issues_by_key={}
    provenance={}
    for i in plan['issues']:
        existing, why = find_issue(existing_issues,i)
        if existing:
            issues_by_key[i['key']]=existing['number']
            provenance[i['key']]=why
            notice('reuse issue '+str(existing['number'])+' '+i['key']+' ['+why+']',dry)
        else:
            notice('create '+i.get('kind','task')+' '+i['key']+': '+i['title'],dry)
            if apply:
                args=['issue','create','--repo',repo,'--title',i['title'],
                      '--body',desired_body(i), '--label','priority:'+i.get('priority','P2'),
                      '--label','type:'+i.get('kind','task')]
                mkey=i.get('milestone')
                if mkey:
                    mtitle=next(x['title'] for x in plan['milestones'] if x['key']==mkey)
                    args+=['--milestone',mtitle]
                url=run(*args)
                match=re.search(r'/issues/(\d+)\s*$',url)
                if not match:
                    raise SetupError('Issue created but cannot parse number: '+url)
                issues_by_key[i['key']]=int(match.group(1))
                provenance[i['key']]='created'
    # Relationships: do not mutate unrelated existing issues matched by title.
    for i in plan['issues']:
        if i.get('parent'):
            notice(f'set parent {i["key"]} -> {i["parent"]}', dry)
            if apply and provenance[i['key']] in ('created', 'managed'):
                detail = run('issue','view',str(issues_by_key[i['key']]),'--repo',repo,
                             '--json','parent',json_result=True)
                parent = detail.get('parent') or {}
                current_parent = parent.get('number')
                desired_parent = issues_by_key[i['parent']]
                if current_parent is None:
                    run('issue','edit',str(issues_by_key[i['key']]),'--repo',repo,
                        '--parent',str(desired_parent))
                elif current_parent != desired_parent:
                    print(f'REVIEW parent conflict for {i["key"]}: current #{current_parent}, desired #{desired_parent}; preserved', file=sys.stderr)
            elif apply and provenance[i['key']] == 'matched-title':
                print('REVIEW parent for matched-title issue '+i['key']+' (preserved)', file=sys.stderr)
        for b in i.get('blocked_by', []):
            notice(f'link dependency {i["key"]} blocked by {b}', dry)
            if apply and provenance[i['key']] == 'created':
                run('issue','edit',str(issues_by_key[i['key']]),'--repo',repo,
                    '--add-blocked-by',str(issues_by_key[b]))
            elif apply and provenance[i['key']] == 'managed':
                detail=run('issue','view',str(issues_by_key[i['key']]),'--repo',repo,
                           '--json','blockedBy', json_result=True)
                blocked={x.get('number') for x in detail.get('blockedBy', [])}
                if issues_by_key[b] not in blocked:
                    run('issue','edit',str(issues_by_key[i['key']]),'--repo',repo,
                        '--add-blocked-by',str(issues_by_key[b]))
            elif apply:
                print('REVIEW dependency for matched-title issue '+i['key']+' (preserved)', file=sys.stderr)
    # Add issues to actual Projects board, set fields only for newly added items.
    existing_urls=set()
    if number:
        items=items_state(number,owner)
        for item in items:
            content=item.get('content') or {}
            if content.get('url'): existing_urls.add(content['url'])
    for i in plan['issues']:
        if not apply:
            notice('add/link Project item and fields '+i['key'],True)
            continue
        url=f'https://github.com/{repo}/issues/{issues_by_key[i["key"]]}'
        if url not in existing_urls:
            notice('add Project item '+i['key'],False)
            run('project','item-add',number,'--owner',owner,'--url',url)
            existing_urls.add(url)
            if priority_ready:
                run('project','item-edit',number,'--owner',owner,'--url',url,
                    '--field','Priority','--value',i.get('priority','P2'))
            for property_name, field_name in (('start_date','Start date'),('target_date','Target date')):
                if i.get(property_name):
                    run('project','item-edit',number,'--owner',owner,'--url',url,
                        '--field',field_name,'--date',i[property_name])
        else:
            notice('preserve existing Project item '+i['key'],False)
    if with_views:
        if not new_project:
            print('REVIEW: views not automatically added to an existing Project (avoid duplicates)')
        else:
            for name, layout in [('Backlog','table'),('Execution Board','board'),('Roadmap','roadmap')]:
                notice('create Project view '+name+' ('+layout+')',dry)
            if apply:
                user=run('api',f'users/{owner}',json_result=True)
                if user.get('type') == 'Organization':
                    endpoint=f'orgs/{owner}/projectsV2/{number}/views'
                else:
                    endpoint=f'users/{user["id"]}/projectsV2/{number}/views'
                for name, layout in [('Backlog','table'),('Execution Board','board'),('Roadmap','roadmap')]:
                    try:
                        run('api','--method','POST',endpoint,
                            data={'name':name,'layout':layout})
                    except SetupError as ex:
                        print(f'VIEW WARNING: {name} not verified: {ex}', file=sys.stderr)
    print('RESULT: '+('dry-run complete; no writes' if dry else 'apply complete; verify project URL and GitHub relationships'))
    if apply:
        print(f'Project: https://github.com/users/{owner}/projects/{number} (organization projects may use /orgs/{owner})')
    print('NOTE: Project built-in workflows and scheduled Actions require separate enablement and verification.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan',required=True,type=Path)
    ap.add_argument('--check-only',action='store_true',help='Validate JSON plan offline, no gh needed')
    ap.add_argument('--apply',action='store_true',help='Create/update GitHub objects (default is read-only)')
    ap.add_argument('--confirm',default='',help='Must exactly equal OWNER/REPO with --apply')
    ap.add_argument('--with-views',action='store_true',help='Attempt REST API board/table/roadmap view creation on new project only')
    args=ap.parse_args()
    try:
        raw=json.loads(args.plan.read_text(encoding='utf-8'))
        plan=validate(raw)
        if args.check_only:
            print('VALID '+plan['repository']+': '
                  +str(len(plan.get('milestones',[])))+' milestones, '
                  +str(len(plan.get('issues',[])))+' issues')
            return 0
        if args.apply and args.confirm != plan['repository']:
            raise SetupError('Refusing --apply without --confirm '+plan['repository'])
        execute(plan,apply=args.apply,with_views=args.with_views)
        return 0
    except (SetupError,FileNotFoundError,PermissionError,json.JSONDecodeError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr)
        return 2

if __name__=='__main__':
    sys.exit(main())