"""Accessible photo + complete issue ledger, with optional teacher editing.

All model/student text enters textContent, never HTML. Edits are returned to the
server by the component bridge; this renderer never changes scores.
"""
import json
from pathlib import Path


def build_image_review_html(pages, top_issue, score_text='', editable=False, source_version=''):
    template = Path(__file__).with_name('review_component').joinpath('review.html').read_text(encoding='utf-8')
    data = json.dumps(dict(pages=pages, top=top_issue, score=score_text,
                          editable=editable, source_version=source_version), ensure_ascii=False)
    # Keep raw student/model strings from terminating the JSON script element.
    data = data.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return template.replace('__REVIEW_DATA__', data)


build_image_review_html_multi = build_image_review_html
