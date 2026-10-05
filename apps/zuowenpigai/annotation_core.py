"""Lossless annotation ledger. Text identity and geometry are separate decisions.

All spans are half-open offsets in whitespace-normalised source text. An issue
never disappears because its text or geometry could not be resolved.
"""
import hashlib
import json
import math


def norm(text):
    return ''.join(str(text or '').split())


def source_version(pages):
    return hashlib.sha256(json.dumps(pages, ensure_ascii=False).encode()).hexdigest()


def occurrences(text, quote):
    if not quote:
        return []
    out, start = [], 0
    while True:
        at = text.find(quote, start)
        if at < 0:
            return out
        out.append(at)
        start = at + 1


def unique_span(text, quote, left='', right='', lo=0, hi=None):
    """Never discard a supplied anchor; repeated candidates are ambiguous."""
    quote, left, right = norm(quote), norm(left), norm(right)
    hi = len(text) if hi is None else hi
    candidates = [lo + p for p in occurrences(text[lo:hi], quote)]
    if left:
        candidates = [p for p in candidates if text[max(0, p-len(left)):p] == left]
    if right:
        candidates = [p for p in candidates if text[p+len(quote):p+len(quote)+len(right)] == right]
    if len(candidates) == 1:
        return (candidates[0], candidates[0] + len(quote)), ''
    return None, 'ambiguous_text' if len(candidates) > 1 else 'text_not_found'


def collect_issues(feedback):
    out = []
    for pi, para in enumerate(feedback.get('paragraph_feedback') or []):
        for field, default in [('red_issues', '语言问题'), ('green_issues', '表达建议')]:
            for item in para.get(field) or []:
                out.append(dict(item, para_idx=pi, quote=item.get('original', ''),
                                category=item.get('type') or default,
                                fix=item.get('improved') or item.get('suggestion', ''),
                                why=item.get('explanation') or item.get('issue_detail', ''),
                                kind='error' if field == 'red_issues' else 'suggestion'))
    # Preserve supplementary/legacy annotations even when paragraph issues exist.
    for item in feedback.get('annotations') or []:
        out.append(dict(item, quote=item.get('quote') or item.get('original', ''),
                        kind='praise' if item.get('action') == 'praise' else 'error'))
    for item in (feedback.get('language_audit') or {}).get('issues', []):
        out.append(dict(item, kind='uncertain' if item.get('uncertain') else 'error'))
    return out


def valid_rects(rects):
    if not isinstance(rects, list) or not rects or len(rects) > 100:
        return False
    return all(isinstance(r, (list, tuple)) and len(r) == 4
               and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                       and math.isfinite(v) for v in r)
               and r[0] >= 0 and r[1] >= 0 and r[2] > 0 and r[3] > 0
               and r[0]+r[2] <= 100.001 and r[1]+r[3] <= 100.001 for r in rects)


REASONS = {
    'ambiguous_text': 'More than one match（重复原文）',
    'text_not_found': 'Check transcription（核对原文）',
    'paragraph_not_found': 'Check paragraph（段落待核对）',
    'no_geometry': 'Position needed（待定位）',
    'text_changed': 'Text changed（原文已更改）',
    'region_only': 'Line / region only（范围待确认）',
    'recognition_uncertain': 'Check handwriting（字迹待核对）',
}


def build_ledger(feedback, page_texts, locators=None):
    texts = [norm(p) for p in page_texts]
    full = ''.join(texts)
    bounds = [0]
    for t in texts:
        bounds.append(bounds[-1]+len(t))
    version = source_version(page_texts)
    paras = feedback.get('paragraph_feedback') or []
    windows = []
    for p in paras:
        span, _ = unique_span(full, p.get('original_text', ''))
        windows.append(span)
    ledger, seen = [], set()
    for a in collect_issues(feedback):
        quote = norm(a.get('quote'))
        pi = a.get('para_idx')
        span, reason = None, ''
        explicit = a.get('source_span')
        if explicit is not None:
            if (a.get('source_version') == version and isinstance(explicit, (list, tuple))
                    and len(explicit) == 2 and all(type(v) is int for v in explicit)
                    and 0 <= explicit[0] < explicit[1] <= len(full)
                    and full[explicit[0]:explicit[1]] == quote):
                span = tuple(explicit)
            else:
                reason = 'text_changed'
        elif pi is not None and (pi >= len(windows) or windows[pi] is None):
            reason = 'paragraph_not_found'
        else:
            lo, hi = windows[pi] if pi is not None else (0, len(full))
            span, reason = unique_span(full, quote, a.get('anchor_left', a.get('a_left', '')),
                                       a.get('anchor_right', a.get('a_right', '')), lo, hi)
        cat = a.get('category') or a.get('type') or '语言问题'
        # Same physical occurrence once; different occurrences remain independent.
        key = (span, quote, norm(a.get('fix')), a.get('kind')) if span else (
            pi, quote, norm(a.get('fix')), a.get('anchor_left'), a.get('anchor_right'), a.get('kind'))
        if key in seen:
            continue
        seen.add(key)
        ident = hashlib.sha256(json.dumps([version, key], ensure_ascii=False).encode()).hexdigest()[:16]
        issue = dict(id=ident, n=len(ledger)+1, quote=a.get('quote', ''), cat=cat,
                     fix=a.get('fix') or a.get('suggestion', ''),
                     why=a.get('why') or a.get('comment') or a.get('explanation', ''),
                     kind=a.get('kind', 'error'), source_span=span, source_version=version,
                     status='unlocated', reason=reason, locations=[], para_idx=pi)
        if span:
            expected_parts, parts = 0, []
            precise = True
            for page, txt in enumerate(texts):
                start, end = max(span[0], bounds[page]), min(span[1], bounds[page+1])
                if start >= end:
                    continue
                expected_parts += 1
                local_start, local_end = start-bounds[page], end-bounds[page]
                result = None
                for locator in ((locators or [])[page] if locators and page < len(locators) else []):
                    if locator is None:
                        continue
                    # Resolve exact source context first; never use fuzzy substring guesses.
                    candidate = locator.locate_source(txt, local_start, local_end)
                    if candidate and valid_rects(candidate.get('rects')):
                        if result is None or candidate.get('precision') == 'character':
                            result = candidate
                        if candidate.get('precision') == 'character':
                            break
                if result:
                    precise = precise and result.get('precision') == 'character'
                    parts.append(dict(page=page, rects=result['rects']))
            issue['locations'] = parts
            issue['status'] = ('located' if precise else 'approximate') if len(parts) == expected_parts else 'unlocated'
            issue['reason'] = '' if issue['status'] == 'located' else ('region_only' if issue['status'] == 'approximate' else 'no_geometry')
        if issue['kind'] == 'uncertain':
            issue['status'], issue['reason'] = 'uncertain', 'recognition_uncertain'
        issue['reason_text'] = REASONS.get(issue['reason'], '')
        ledger.append(issue)
    return ledger


def apply_overrides(ledger, overrides, page_count, version):
    """Server-side validation; geometry edits never alter grades or source text."""
    by_id = {a['id']: a for a in ledger}
    if not isinstance(overrides, dict) or overrides.get('source_version') != version:
        return ledger
    edits = overrides.get('items')
    if not isinstance(edits, list):
        return ledger
    for edit in edits[:1000]:
        if not isinstance(edit, dict):
            continue
        a = by_id.get(edit.get('id'))
        if a is None and str(edit.get('id', '')).startswith('manual_'):
            a = dict(id=edit['id'], n=len(ledger)+1, quote='', cat='教师批注', fix='', why='',
                     kind='error', locations=[], status='unlocated', reason='no_geometry',
                     source_version=version, source_span=None, para_idx=None)
            ledger.append(a)
            by_id[a['id']] = a
        if a is None:
            continue
        if edit.get('dismissed') is True:
            a.update(status='dismissed', locations=[], reason='', reason_text='Cancelled（已取消）')
            continue
        locations = edit.get('locations')
        if (isinstance(locations, list) and locations and len(locations) <= page_count
                and all(isinstance(p, dict) and type(p.get('page')) is int
                        and 0 <= p['page'] < page_count and valid_rects(p.get('rects')) for p in locations)):
            a.update(locations=locations, status='manual', reason='', reason_text='Teacher positioned（人工定位）')
        for field in ('quote', 'fix', 'why'):
            if isinstance(edit.get(field), str):
                a[field] = edit[field][:2000]
    return ledger


def ledger_pages(ledger, page_count):
    pages = [dict(hotspots=[], issues=[]) for _ in range(page_count)]
    for a in ledger:
        home = a['locations'][0]['page'] if a['locations'] else 0
        pages[home]['issues'].append(a)
        if a['status'] == 'dismissed':
            continue
        for loc in a['locations']:
            precise = a['status'] in ('located', 'manual')
            good = a['kind'] == 'praise'
            pages[loc['page']]['hotspots'].append(dict(a, rects=loc['rects'], good=good,
                mark=('wavy' if good else ('circle' if len(norm(a['quote'])) <= 5 else 'line')) if precise else 'region'))
    return pages
