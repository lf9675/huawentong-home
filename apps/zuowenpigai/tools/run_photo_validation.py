"""Run the real OCR + independent language audit on a private photo manifest.

Usage: python tools/run_photo_validation.py /private/manifest.json --out /private/results
Manifest: {"essays":[{"id":"sample_a","pages":[{"path":"photo.jpg","rotation":0}]}]}
Credentials: ZHIPU_API_KEY, DEEPSEEK_API_KEY. Outputs and photos must stay private.
No test results are fabricated when credentials or a remote service are absent.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from image_input import normalize_image, layout_envelope
from layout_locator import build_layout_locators
from annotation_core import build_ledger, ledger_pages
from language_audit import audit_language, openai_call
from image_review_render import build_image_review_html


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('manifest');parser.add_argument('--out',required=True)
    args=parser.parse_args();dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    missing=[n for n in ('ZHIPU_API_KEY','DEEPSEEK_API_KEY') if not os.environ.get(n)]
    if missing:
        result={'status':'not_run','reason':'Missing service credentials','missing_names':missing}
        (dest/'run-status.json').write_text(json.dumps(result,indent=2))
        print(json.dumps(result));return 2
    import requests
    from openai import OpenAI
    manifest=json.loads(Path(args.manifest).read_text())
    client=OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'],base_url='https://api.deepseek.com',timeout=90,max_retries=0)
    statuses=[]
    for essay in manifest['essays']:
        # File names are local, derived only from safe manifest ids.
        ident=''.join(c for c in essay['id'] if c.isalnum() or c in '_-')
        if not ident:raise ValueError('Invalid essay id')
        images,texts,layouts=[],[],[]
        try:
            for page in essay['pages']:
                image=normalize_image(Path(page['path']).read_bytes(),page.get('rotation',0));images.append(image)
                r=requests.post(os.environ.get('ZHIPU_BASE_URL','https://open.bigmodel.cn').rstrip('/')+'/api/paas/v4/layout_parsing',
                    headers={'Authorization':'Bearer '+os.environ['ZHIPU_API_KEY']},timeout=120,
                    json={'model':'glm-ocr','file':'data:image/jpeg;base64,'+base64.b64encode(image).decode()})
                r.raise_for_status();response=r.json()
                if not response.get('md_results'):raise ValueError('OCR returned no text')
                texts.append(response['md_results']);layouts.append(layout_envelope(response))
            audit=audit_language(texts,openai_call(client,os.environ.get('LANGUAGE_AUDIT_MODEL','deepseek-v4-flash')))
            ledger=build_ledger({'language_audit':audit},texts,[[l] for l in build_layout_locators(layouts,len(images))])
            result={'status':'complete' if audit['complete'] else 'partial','source':'live_api',
                    'texts':texts,'audit':audit,'ledger':ledger,'accuracy':'not_scored_without_independent_reference'}
            (dest/(ident+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
            pages=ledger_pages(ledger,len(images))
            for i,p in enumerate(pages):p.update(img_b64=base64.b64encode(images[i]).decode(),mime='image/jpeg',para_cards=[])
            (dest/(ident+'.html')).write_text(build_image_review_html(pages,{'title':'Live API output（真实接口结果，待教师核对）'}))
            statuses.append({'id':ident,'status':result['status']})
        except Exception as exc:
            statuses.append({'id':ident,'status':'failed','error_type':type(exc).__name__})
    (dest/'run-status.json').write_text(json.dumps(statuses,indent=2))
    print(json.dumps(statuses));return 0 if all(s['status']=='complete' for s in statuses) else 1


if __name__=='__main__':raise SystemExit(main())
