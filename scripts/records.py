#!/usr/bin/env python3
"""Read-only structural checks and TODO rendering; Python 3 standard library."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

STATES = ('todo', 'doing', 'blocked', 'paused', 'review', 'done', 'cancelled')
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]*$')


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('must be an ISO timestamp with timezone')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone is required')
    return result


def parse(text):
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise ValueError('missing front matter')
    try:
        end = lines.index('---', 1)
    except ValueError:
        raise ValueError('unclosed front matter') from None
    data = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        match = re.fullmatch(r'([a-z_]+):\s*(.+)', line)
        if not match:
            raise ValueError('expected key: JSON-value, not general YAML')
        key, raw = match.groups()
        if key in data:
            raise ValueError('duplicate metadata key: ' + key)
        data[key] = json.loads(raw)
    criteria = []
    sections = 0
    active = False
    fenced = False
    for line in lines[end + 1:]:
        if line.strip().startswith(('```', '~~~')):
            fenced = not fenced
            continue
        if fenced:
            continue
        if re.match(r'^#{1,2}\s', line):
            active = line.strip() == '## 验收清单'
            sections += int(active)
        if active:
            item = re.fullmatch(r'\s*[-*] \[([ xX])\] (\S.*)', line)
            if item:
                criteria.append((item[1].lower() == 'x', item[2]))
    if sections != 1:
        raise ValueError('expected exactly one ## 验收清单 section')
    return data, criteria


def inside(path, root):
    try:
        path.resolve().relative_to(root)
        return True
    except (ValueError, OSError, RuntimeError):
        return False


def audit(root, tasks_dir='management/tasks'):
    root = Path(root).resolve()
    result = {'scope': str(root), 'checked_at': datetime.now(timezone.utc).isoformat(),
              'task_count': 0, 'errors': [], 'warnings': [],
              'verification': 'Structure and local path existence only; not scientific or remote verification.'}
    errors, warnings = result['errors'], result['warnings']
    records = []
    if not root.is_dir():
        errors.append('project root is not a directory')
        return result, records
    relative = Path(tasks_dir)
    task_root = root / relative
    if relative.is_absolute() or '..' in relative.parts or not inside(task_root, root):
        errors.append('tasks directory must resolve within project root')
        return result, records
    if not task_root.is_dir():
        warnings.append('No task directory; project status is unknown.')
        return result, records
    # Never traverse symlink directories, including links inside the task tree.
    def discover(directory):
        for path in sorted(directory.iterdir()):
            if path.is_symlink():
                errors.append(str(path.relative_to(root)) + ': symlink task entry is not read')
            elif path.is_dir():
                yield from discover(path)
            elif path.suffix == '.md':
                yield path
    try:
        paths = list(discover(task_root))
    except OSError as exc:
        errors.append('Cannot enumerate task directory: ' + str(exc))
        return result, records
    for path in paths:
        label = path.relative_to(root).as_posix()
        if not inside(path, root):
            errors.append(label + ': path escapes project root')
            continue
        try:
            data, criteria = parse(path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            errors.append(label + ': ' + str(exc))
            continue
        record = {'path': label, 'data': data, 'criteria': criteria}
        records.append(record)
        def err(message):
            errors.append(label + ': ' + message)
        for key in ('id', 'type', 'project', 'title', 'status'):
            value = data.get(key)
            if not isinstance(value, str) or not value.strip() or '{{' in value:
                err(key + ' must be a non-placeholder string')
        if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
            err('schema_version must be 1')
        if data.get('type') != 'task':
            err('type must be task')
        task_id = data.get('id')
        if not isinstance(task_id, str) or not ID.fullmatch(task_id):
            err('invalid task ID')
        state = data.get('status')
        if state not in STATES:
            err('unsupported status')
        owner = data.get('owner')
        if 'owner' not in data or (owner is not None and
                (not isinstance(owner, str) or not owner.strip() or '{{' in owner)):
            err('owner must be null or a nonempty identifier')
        if state in ('doing', 'review', 'done') and not owner:
            err('doing/review/done requires an owner')
        parent = data.get('parent')
        if 'parent' not in data or (parent is not None and
                (not isinstance(parent, str) or not ID.fullmatch(parent))):
            err('parent must be null or a task ID')
        dates = {}
        for key in ('created_at', 'updated_at', 'verified_at'):
            if key == 'verified_at' and key in data and data[key] is None:
                continue
            try:
                dates[key] = timestamp(data.get(key))
            except ValueError as exc:
                err(key + ': ' + str(exc))
        if dates.get('created_at') and dates.get('updated_at'):
            if dates['updated_at'] < dates['created_at']:
                err('updated_at precedes created_at')
        if dates.get('verified_at') and dates.get('updated_at'):
            if dates['verified_at'] > dates['updated_at']:
                err('verified_at is later than updated_at')
            elif state == 'done' and dates['verified_at'] < dates['updated_at']:
                warnings.append(label + ': record changed after verification; review evidence freshness')
        for key in ('depends_on', 'links', 'evidence'):
            value = data.get(key)
            if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
                err(key + ' must be an array of nonempty strings')
            elif len(set(value)) != len(value):
                err(key + ' contains duplicates')
        if state == 'done':
            if not criteria or not all(checked for checked, _ in criteria):
                err('done requires nonempty, fully checked acceptance criteria')
            if not data.get('evidence') or not dates.get('verified_at'):
                err('done requires evidence and verified_at')
        for item in data.get('evidence', []) if isinstance(data.get('evidence'), list) else []:
            if not isinstance(item, str):
                continue
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', item):
                warnings.append(label + ': remote/URI evidence is unverified: ' + item)
                continue
            evidence = root / item.split('#', 1)[0]
            if not inside(evidence, root):
                warnings.append(label + ': external evidence not inspected: ' + item)
            elif not evidence.exists():
                err('missing local evidence: ' + item)
    by_id = {}
    for record in records:
        ident = record['data'].get('id')
        if not isinstance(ident, str):
            continue
        if ident in by_id:
            errors.append('duplicate task ID: ' + ident)
        by_id[ident] = record
    graph = {}
    for ident, record in by_id.items():
        deps = record['data'].get('depends_on', [])
        deps = [v for v in deps if isinstance(v, str)] if isinstance(deps, list) else []
        graph[ident] = deps
        for dep in deps:
            if dep not in by_id:
                errors.append(ident + ': unresolved dependency: ' + dep)
        parent = record['data'].get('parent')
        if isinstance(parent, str) and parent not in by_id:
            errors.append(ident + ': unresolved parent: ' + parent)
    # Iterative DFS avoids recursion limits on large research backlogs.
    for graph_name, edges in (('dependency', graph), ('parent', {
            ident: [r['data']['parent']] if isinstance(r['data'].get('parent'), str) else []
            for ident, r in by_id.items()})):
        visited = set()
        active = set()
        for start in edges:
            stack = [(start, False)]
            while stack:
                node, leaving = stack.pop()
                if leaving:
                    active.discard(node)
                    visited.add(node)
                elif node in active:
                    errors.append(graph_name + ' cycle involving: ' + node)
                elif node not in visited and node in edges:
                    active.add(node)
                    stack.append((node, True))
                    stack.extend((v, False) for v in reversed(edges[node]))
    result['task_count'] = len(records)
    if not paths:
        warnings.append('No task cards; project status is unknown.')
    return result, records


LOG_CANDIDATES = ('management/LOG.md', 'HANDOFF.md')


def audit_log(root, log_path=None):
    """Check rolling event-log lines: 时间｜事件｜变化｜证据｜下一步. Never edits."""
    root = Path(root).resolve()
    result = {'scope': str(root), 'checked_at': datetime.now(timezone.utc).isoformat(),
              'log': None, 'event_count': 0, 'last_event_at': None, 'errors': [], 'warnings': [],
              'verification': 'Line format only; not whether events happened or evidence is true.'}
    errors, warnings = result['errors'], result['warnings']
    if not root.is_dir():
        errors.append('project root is not a directory')
        return result
    candidates = (log_path,) if log_path else LOG_CANDIDATES
    for candidate in candidates:
        relative = Path(candidate)
        path = root / relative
        if relative.is_absolute() or '..' in relative.parts or not inside(path, root):
            errors.append('log path must resolve within project root')
            return result
        if path.is_symlink():
            errors.append(candidate + ': symlink log is not read')
            return result
        if path.is_file():
            break
    else:
        warnings.append('No event log found (' + ', '.join(candidates) + '); project status is unknown.')
        return result
    result['log'] = relative.as_posix()
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(result['log'] + ': ' + str(exc))
        return result
    latest = None
    fenced = False
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(('```', '~~~')):
            fenced = not fenced
            continue
        if fenced or '｜' not in stripped or stripped.startswith(('#', '`', '>')):
            continue
        fields = [f.strip() for f in re.sub(r'^[-*]\s+', '', stripped).split('｜')]
        where = result['log'] + ':' + str(number)
        try:
            when = timestamp(fields[0])
        except ValueError as exc:
            warnings.append(where + ': first field is not a timestamp (' + str(exc) + ')')
            continue
        result['event_count'] += 1
        if latest is None or when > latest:
            latest = when
        if len(fields) != 5:
            warnings.append(where + ': expected 5 fields, found ' + str(len(fields)))
        elif not all(fields[1:]):
            warnings.append(where + ': empty field; write 无 when there is no evidence or next step')
    if latest:
        result['last_event_at'] = latest.isoformat()
    elif not errors:
        warnings.append('Log has no parseable events; project status is unknown.')
    return result


def render_todo(result, records):
    if result['errors']:
        raise ValueError('Cannot generate TODO from invalid records')
    lines = ['# TODO（派生只读视图）', '', 'generated_at: ' + result['checked_at'], '',
             '状态源为任务卡；勾选不代表科学质量已被本工具验证。', '']
    for warning in result['warnings']:
        lines.extend(['> 未核验：' + warning, ''])
    for state in STATES:
        group = [r for r in records if r['data'].get('status') == state]
        if not group:
            continue
        lines.extend(['## ' + state, ''])
        for r in group:
            d = r['data']
            lines.append('- [' + ('x' if state == 'done' else ' ') + '] ' +
                         d['id'] + ' — ' + d['title'] + ' | owner=' + str(d['owner']) +
                         ' | source: `' + r['path'] + '`')
            for checked, criterion in r['criteria']:
                lines.append('  - [' + ('x' if checked else ' ') + '] ' + criterion)
        lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('audit', 'todo', 'log'))
    parser.add_argument('root')
    parser.add_argument('--tasks-dir', default='management/tasks')
    parser.add_argument('--log', help='event log path relative to root')
    args = parser.parse_args(argv)
    if args.command == 'log':
        result = audit_log(args.root, args.log)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result['errors'] else 0
    result, records = audit(args.root, args.tasks_dir)
    if args.command == 'audit' or result['errors']:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_todo(result, records))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
