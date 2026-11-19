import importlib.util
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / 'scripts' / 'github_project_sync.py'
PLAN_PATH = Path(__file__).resolve().parents[1] / 'examples' / 'project-plan.example.json'
spec = importlib.util.spec_from_file_location('gpo', MODULE_PATH)
gpo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gpo)

class FakeGh:
    def __init__(self):
        self.project = None
        self.milestones = []
        self.fields = []
        self.issues = []
        self.items = []
        self.labels = []
        self.links = []
        self.blockers = {}
        self.actions = []

    def __call__(self, *args, **kw):
        self.actions.append((' '.join(str(x) for x in args), kw.get('data')))
        args = list(args)
        if args[:2] == ['auth', 'status']:
            return ''
        if args[:2] == ['project', 'list']:
            return {'projects':[self.project] if self.project else []}
        if args[:2] == ['project', 'create']:
            self.project = {'number':7, 'title':args[args.index('--title')+1]}
            return self.project
        if args[:2] == ['project', 'field-list']:
            return {'fields':self.fields}
        if args[:2] == ['project', 'field-create']:
            self.fields.append({'name':args[args.index('--name')+1], 'options':[{'name':n} for n in ['P0','P1','P2','P3']] if args[args.index('--name')+1]=='Priority' else []})
            return ''
        if args[:2] == ['project', 'item-list']:
            return {'items':self.items}
        if args[:2] == ['project', 'item-add']:
            url=args[args.index('--url')+1]
            self.items.append({'content':{'url':url}})
            return ''
        if args[:2] == ['project', 'item-edit'] or args[:2] == ['project', 'edit'] or args[:2] == ['project', 'link']:
            return ''
        if args[:2] == ['issue', 'list']:
            return self.issues
        if args[:2] == ['issue', 'create']:
            num=100+len(self.issues)
            title=args[args.index('--title')+1]
            body=args[args.index('--body')+1]
            url=f'https://github.com/OWNER/REPOSITORY/issues/{num}'
            self.issues.append({'number':num,'title':title,'body':body,'url':url})
            return url
        if args[:2] == ['issue', 'edit']:
            num=int(args[2])
            if '--add-blocked-by' in args:
                self.blockers.setdefault(num,set()).add(int(args[args.index('--add-blocked-by')+1]))
            if '--parent' in args:
                self.links.append(('parent',num,int(args[args.index('--parent')+1])))
            return ''
        if args[:2] == ['issue', 'view']:
            num=int(args[2])
            parent=next(({'number':p} for _,child,p in self.links if child==num), None)
            nums=sorted(self.blockers.get(num,set()))
            return {'blockedBy':{'nodes':[{'number':n} for n in nums], 'totalCount':len(nums)}, 'parent':parent}
        if args[:2] == ['label', 'list']:
            return [{'name':x} for x in self.labels]
        if args[:2] == ['label', 'create']:
            self.labels.append(args[2])
            return ''
        if args[0] == 'api' and '--paginate' in args:
            return [self.milestones]
        if args[0] == 'api' and '--method' in args and 'POST' in args:
            self.milestones.append(kw['data'])
            return ''
        raise AssertionError(('Unexpected gh command',args,kw))

class Tests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads(PLAN_PATH.read_text())
        gpo.validate(self.plan)

    def test_valid_plan(self):
        self.assertEqual(len(self.plan['issues']),3)

    def test_cyclic_dependencies(self):
        self.plan['issues'][1]['blocked_by']=['release-gate']
        with self.assertRaisesRegex(gpo.SetupError,'cycle'):
            gpo.validate(self.plan)

    def test_invalid_date(self):
        self.plan['issues'][1]['target_date']='2026-99-31'
        with self.assertRaisesRegex(gpo.SetupError,'ISO date'):
            gpo.validate(self.plan)

    def test_run_gh_api_json_via_stdin(self):
        from subprocess import CompletedProcess
        with patch.object(gpo.subprocess,'run', return_value=CompletedProcess([],0,'{}','')) as sub:
            gpo.run('api','--method','POST','repos/OWNER/REPO/milestones',data={'title':'A'})
            call=sub.call_args
            self.assertEqual(call.args[0][-2:],['--input','-'])
            self.assertEqual(json.loads(call.kwargs['input']),{'title':'A'})

    def test_dry_run_has_no_mutations(self):
        fake=FakeGh()
        with patch.object(gpo,'run',fake),patch.object(gpo.shutil,'which',return_value='/usr/bin/gh'),redirect_stdout(io.StringIO()):
            gpo.execute(self.plan,apply=False)
        self.assertFalse(any(x[0].startswith(('issue create','project create','label create','project field-create')) for x in fake.actions))
        self.assertIsNone(fake.project)

    def test_recover_interrupted_parent_link_on_managed_issue(self):
        fake=FakeGh()
        with patch.object(gpo,'run',fake),patch.object(gpo.shutil,'which',return_value='/usr/bin/gh'),redirect_stdout(io.StringIO()):
            gpo.execute(self.plan,apply=True)
            fake.links=[]  # Simulate an interrupted apply or externally missing parent edges.
            gpo.execute(self.plan,apply=True)
        self.assertIn(('parent',101,100),fake.links)
        self.assertIn(('parent',102,100),fake.links)
        self.assertEqual(len(fake.issues),3)

    def test_native_relationship_connection_shape(self):
        self.assertEqual(gpo.linked_issue_numbers(
            {'blockedBy': {'nodes': [{'number': 4}, {'number': 9}], 'totalCount': 2}},
            'blockedBy'), {4, 9})

    def test_refuse_truncated_relationships(self):
        with self.assertRaisesRegex(gpo.SetupError, 'incomplete'):
            gpo.linked_issue_numbers(
                {'blockedBy': {'nodes': [{'number': 4}], 'totalCount': 60}},
                'blockedBy')

    def test_refuse_missing_relationships(self):
        with self.assertRaisesRegex(gpo.SetupError, 'not returned'):
            gpo.linked_issue_numbers({}, 'blockedBy')

    def test_apply_twice_is_idempotent_and_links(self):
        fake=FakeGh()
        with patch.object(gpo,'run',fake),patch.object(gpo.shutil,'which',return_value='/usr/bin/gh'),redirect_stdout(io.StringIO()):
            gpo.execute(self.plan,apply=True)
            first_count=len(fake.actions)
            gpo.execute(self.plan,apply=True)
        self.assertEqual(len(fake.issues),3)
        self.assertEqual(len(fake.items),3)
        self.assertEqual(len(fake.milestones),2)
        # Example plan has no dates, so only Priority is created (date fields are opt-in).
        self.assertEqual([f['name'] for f in fake.fields],['Priority'])
        self.assertEqual(len(fake.labels),6)
        self.assertIn(('parent',101,100),fake.links)
        self.assertIn(('parent',102,100),fake.links)
        self.assertIn(101, fake.blockers[102])
        second_actions=[x[0] for x in fake.actions[first_count:]]
        self.assertFalse(any(x.startswith(('issue create','project create','project item-add','project field-create','label create')) for x in second_actions), second_actions)

    def test_explicit_null_parent_is_valid(self):
        self.plan['issues'][0]['parent']=None
        self.plan['issues'][0]['blocked_by']=None
        gpo.validate(self.plan)

    def test_reuses_equivalent_existing_label(self):
        fake=FakeGh()
        fake.labels=['type: epic','Priority: P1']
        with patch.object(gpo,'run',fake),patch.object(gpo.shutil,'which',return_value='/usr/bin/gh'),redirect_stdout(io.StringIO()):
            gpo.execute(self.plan,apply=True)
        self.assertNotIn('type:epic',fake.labels)
        self.assertNotIn('priority:P1',fake.labels)
        epic_create=next(a for a,_ in fake.actions if a.startswith('issue create') and 'baseline-epic' in a)
        self.assertIn('--label type: epic',epic_create)

    def test_date_fields_created_only_when_plan_has_dates(self):
        self.plan['issues'][1]['target_date']='2026-12-01'
        fake=FakeGh()
        with patch.object(gpo,'run',fake),patch.object(gpo.shutil,'which',return_value='/usr/bin/gh'),redirect_stdout(io.StringIO()):
            gpo.execute(self.plan,apply=True)
        self.assertEqual(sorted(f['name'] for f in fake.fields),['Priority','Start date','Target date'])

    def test_dry_run_flags_skipped_links_on_matched_title_issues(self):
        fake=FakeGh()
        fake.issues=[{'number':5,'title':i['title'],'body':'','url':f'https://github.com/OWNER/REPOSITORY/issues/{5+n}'}
                     for n,i in enumerate(self.plan['issues'])]
        for n,x in enumerate(fake.issues): x['number']=5+n
        out=io.StringIO()
        with patch.object(gpo,'run',fake),patch.object(gpo.shutil,'which',return_value='/usr/bin/gh'),redirect_stdout(out):
            gpo.execute(self.plan,apply=False)
        text=out.getvalue()
        self.assertIn('SKIP set parent test-audit -> baseline-epic (matched-title',text)
        self.assertNotIn('PLAN set parent test-audit',text)

if __name__ == '__main__':
    unittest.main()