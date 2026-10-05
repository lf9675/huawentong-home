import io
import json
import unittest
from unittest.mock import patch
from PIL import Image
from annotation_core import (build_ledger, source_version, unique_span, ledger_pages,
                             apply_overrides, valid_rects)
from layout_locator import LayoutLocator, build_layout_locators
from image_input import normalize_image, layout_envelope, sync_corrected_pages
from language_audit import audit_language, chunks
from row_locator import RowLocator
from image_review_render import build_image_review_html


def layout(text, chars=False):
    item=dict(index=0,label='text',content=text,bbox_2d=[.1,.2,.9,.3])
    if chars:
        w=.8/len(text)
        item['char_boxes']=[dict(text=c,bbox_2d=[.1+i*w,.2,.1+(i+1)*w,.3]) for i,c in enumerate(text)]
    return LayoutLocator([item])


def feedback(para, quote, fix='修改', **extra):
    return {'paragraph_feedback':[{'original_text':para,'red_issues':[dict(original=quote,improved=fix,**extra)]}]}


class AnnotationTests(unittest.TestCase):
    def test_duplicate_not_first(self):
        text='他低着头。年低考试。'
        self.assertIsNone(unique_span(text,'低')[0])
        self.assertEqual(unique_span(text,'低','年','考试')[0],(6,7))

    def test_bad_anchor_no_fallback(self):
        self.assertIsNone(layout('他低着头。年低考试。')._find('低','错误','错误'))

    def test_paragraph_scopes_repeated_word(self):
        text='他低着头。年低考试。'
        a=build_ledger(feedback('年低考试。','低'),[text],[[layout(text,True)]])[0]
        self.assertEqual(a['source_span'],(6,7))
        self.assertEqual(a['status'],'located')

    def test_missing_quote_retained(self):
        a=build_ledger(feedback('原文。','不存在'),['原文。'])[0]
        self.assertEqual(a['status'],'unlocated')
        self.assertEqual(ledger_pages([a],1)[0]['issues'][0]['quote'],'不存在')

    def test_regional_bbox_is_not_character(self):
        a=build_ledger(feedback('甲乙丙','乙'),['甲乙丙'],[[layout('甲乙丙')]])[0]
        self.assertEqual(a['status'],'approximate')
        self.assertEqual(a['locations'][0]['rects'],[[10.,20.,80.,10.]])

    def test_provider_chars_precise(self):
        a=build_ledger(feedback('甲乙丙','乙'),['甲乙丙'],[[layout('甲乙丙',True)]])[0]
        self.assertEqual(a['status'],'located')
        self.assertAlmostEqual(a['locations'][0]['rects'][0][0],36.6667,places=3)

    def test_cross_page_split(self):
        a=build_ledger(feedback('今天我到公园。','我到公园'),['今天我到','公园。'],
                       [[layout('今天我到',True)],[layout('公园。',True)]])[0]
        self.assertEqual(a['status'],'located')
        self.assertEqual([l['page'] for l in a['locations']],[0,1])

    def test_partial_cross_page_not_claimed_complete(self):
        a=build_ledger(feedback('今天我到公园。','我到公园'),['今天我到','公园。'],
                       [[layout('今天我到',True)],[]])[0]
        self.assertEqual(a['status'],'unlocated')

    def test_cloud_pixel_metadata(self):
        response={'data_info':{'pages':[{'width':1000,'height':2000}]},'layout_details':[[
            {'index':0,'label':'text','content':'原文','bbox_2d':[100,400,900,500]}]]}
        loc=build_layout_locators([layout_envelope(response)],1)[0]
        self.assertEqual(loc.locate('原文'),[[10.,20.,80.,5.]])

    def test_bad_pixel_geometry_preserves_issue(self):
        loc=build_layout_locators([{'elements':[{'label':'text','content':'原文','bbox_2d':[10,20,30,40]}],
                                    'coordinate_space':'pixel'}],1)
        self.assertEqual(loc,[None])

    def test_edit_sync_only_invalidates_changed_page(self):
        state={'ocr_pages':['甲','乙'],'ocr_layout_pages':['a','b'],'ocr_text':'旧'}
        sync_corrected_pages(state,['甲','丙'])
        self.assertEqual(state['ocr_layout_pages'],['a',None])
        self.assertEqual(state['ocr_text'],'甲\n丙')

    def test_same_word_different_locations_retained(self):
        t='我更着他，他更着我。'
        fb={'paragraph_feedback':[{'original_text':t,'red_issues':[
            {'original':'更','improved':'跟','anchor_left':'我','anchor_right':'着他'},
            {'original':'更','improved':'跟','anchor_left':'他','anchor_right':'着我'}]}]}
        self.assertEqual(len(build_ledger(fb,[t])),2)

    def test_supplementary_annotations_not_dropped(self):
        fb=feedback('甲乙丙','甲');fb['annotations']=[{'quote':'乙','fix':'另一个修改'}]
        self.assertEqual(len(build_ledger(fb,['甲乙丙'])),2)

    def test_uncertain_not_declared_correct_error(self):
        pages=['原文'];fb={'language_audit':{'issues':[{'quote':'原','fix':'源','uncertain':True}]}}
        a=build_ledger(fb,pages,[[layout('原文',True)]])[0]
        self.assertEqual(a['status'],'uncertain')

    def test_stale_spans_refused(self):
        a=build_ledger({'annotations':[{'quote':'乙','source_span':[0,1],'source_version':source_version(['甲'])}]},['乙'])[0]
        self.assertEqual(a['reason'],'text_changed')

    def test_manual_position_persists_without_changing_grade(self):
        fb=feedback('原文','原');fb['scores']={'total':40}
        ledger=build_ledger(fb,['原文']);a=ledger[0]
        edit={'source_version':source_version(['原文']),'items':[{'id':a['id'],'locations':[{'page':0,'rects':[[10,20,5,5]]}]}]}
        result=apply_overrides(ledger,edit,1,source_version(['原文']))
        self.assertEqual(result[0]['status'],'manual');self.assertEqual(fb['scores']['total'],40)

    def test_out_of_bounds_and_nan_refused(self):
        self.assertFalse(valid_rects([[90,20,30,10]]));self.assertFalse(valid_rects([[float('nan'),1,2,3]]))

    def test_stale_override_refused(self):
        ledger=build_ledger(feedback('原文','原'),['原文'])
        result=apply_overrides(ledger,{'source_version':'old','items':[{'id':ledger[0]['id'],'dismissed':True}]},1,'new')
        self.assertEqual(result[0]['status'],'unlocated')

    def test_pdf_and_web_share_payload(self):
        from image_review_page import _build_pages
        fb=feedback('原文','原')
        pages,n=_build_pages(fb,[None],[''],['image/jpeg'],['原文'],layout_locs=[layout('原文')])
        self.assertEqual(len(pages[0]['issues']),1)
        self.assertEqual(pages[0]['hotspots'][0]['mark'],'region')

    def test_slot_mismatch_has_no_fake_character_box(self):
        loc=RowLocator(dict(width=100,height=100,texts=['甲乙丙丁戊'],rows=[[20,30]],
                       slots=[[[10,20],[30,40],[50,60],[70,80]]],pitch=20))
        self.assertEqual(loc.locate_source('甲乙丙丁戊',4,5)['precision'],'region')

    def test_image_rotation_one_coordinate_space(self):
        b=io.BytesIO();Image.new('RGB',(1600,1250),'white').save(b,'JPEG')
        out=normalize_image(b.getvalue(),270)
        self.assertEqual(Image.open(io.BytesIO(out)).size,(1250,1600))

    def test_json_script_injection_escaped(self):
        text='</script><script>alert(1)</script>'
        html=build_image_review_html([],{'title':text})
        self.assertNotIn(text,html)
        self.assertIn('\\u003c/script',html)


class AuditTests(unittest.TestCase):
    def test_success_and_cache(self):
        cache={};calls=[]
        def call(*args):
            calls.append(1);return json.dumps({'complete':True,'issues':[{'quote':'更','fix':'跟','anchor_left':'我','anchor_right':'着','uncertain':False}]})
        a=audit_language(['我更着老师。'],call,cache)
        b=audit_language(['我更着老师。'],call,cache)
        self.assertTrue(a['complete']);self.assertEqual(len(calls),1);self.assertEqual(a,b)
        self.assertEqual(a['issues'][0]['source_span'],[1,2])

    def test_failure_is_not_success(self):
        def fail(*args):raise RuntimeError('unavailable')
        a=audit_language(['原文'],fail)
        self.assertFalse(a['complete']);self.assertEqual(a['jobs'][0]['status'],'failed')

    def test_partial_invalid_output_not_accepted(self):
        a=audit_language(['原文'],lambda *args:'{"complete":true,"issues":[{}]}')
        self.assertFalse(a['complete'])

    def test_failed_chunks_retry_only(self):
        cache={};calls=[]
        def first(*args):
            calls.append(1)
            if len(calls)>1:raise RuntimeError()
            return '{"complete":true,"issues":[]}'
        a=audit_language(['甲'*900],first,cache)
        self.assertFalse(a['complete'])
        calls.clear()
        b=audit_language(['甲'*900],lambda *args:(calls.append(1) or '{"complete":true,"issues":[]}'),cache)
        self.assertTrue(b['complete']);self.assertEqual(len(calls),1)

    def test_chunks_cover_whole_source(self):
        cs=chunks(['甲'*1400]);covered=set()
        for c in cs:covered.update(range(c['start'],c['end']))
        self.assertEqual(len(covered),1400)

    def test_unmatched_finding_retained_uncertain(self):
        a=audit_language(['原文'],lambda *args:'{"complete":true,"issues":[{"quote":"别的字","fix":"改","uncertain":false}]}')
        self.assertTrue(a['issues'][0]['uncertain'])
        self.assertEqual(len(build_ledger({'language_audit':a},['原文'])),1)


if __name__=='__main__':unittest.main()
