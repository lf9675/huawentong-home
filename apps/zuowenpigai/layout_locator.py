"""OCR region coordinates are not character coordinates.

Only provider-supplied character boxes permit exact marks. Regional OCR is
shown as a clearly labelled region until a teacher confirms the position.
"""
from annotation_core import norm, unique_span


def _elements(value):
    if not isinstance(value, list):
        return []
    return [e for group in value for e in (group if isinstance(group, list) else [group])
            if isinstance(e, dict)]


def _box(item, width=0, height=0, coordinate_space='legacy'):
    b = item.get('bbox_2d')
    if not isinstance(b, (list, tuple)) or len(b) != 4:
        return None
    try:
        x1,y1,x2,y2 = map(float,b)
        import math
        if not all(math.isfinite(v) for v in (x1,y1,x2,y2)):
            return None
        space = item.get('coordinate_space', coordinate_space)
        if space == 'pixel' or (space == 'legacy' and max(b) > 1.5):
            w,h = float(width or item.get('width') or 0),float(height or item.get('height') or 0)
            if w <= 0 or h <= 0:
                return None
            x1,x2,y1,y2 = x1/w,x2/w,y1/h,y2/h
        elif space == 'normalized_1000':
            x1,y1,x2,y2 = [v/1000 for v in (x1,y1,x2,y2)]
        if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
            return None
        return x1,y1,x2,y2
    except (TypeError,ValueError):
        return None


def _rect(box):
    x1,y1,x2,y2=box
    return [round(x1*100,4),round(y1*100,4),round((x2-x1)*100,4),round((y2-y1)*100,4)]


class LayoutLocator:
    def __init__(self, page_layout):
        meta = page_layout if isinstance(page_layout,dict) else {}
        self.fragments=[]
        self.full=''
        for item in sorted(_elements(meta.get('elements',page_layout)),key=lambda e:e.get('index',0)):
            if item.get('label') not in ('text','formula','doc_title','paragraph_title'):
                continue
            text=norm(item.get('content'))
            box=_box(item,meta.get('width'),meta.get('height'),meta.get('coordinate_space','legacy'))
            # Retain text without geometry so offsets do not drift.
            if not text:
                continue
            chars=item.get('char_boxes') or []
            char_boxes=[]
            if isinstance(chars,list) and norm(''.join(str(c.get('text','')) for c in chars if isinstance(c,dict)))==text:
                for c in chars:
                    cb=_box(c,meta.get('width'),meta.get('height'),meta.get('coordinate_space','legacy'))
                    if cb is None or len(norm(c.get('text'))) != 1:
                        char_boxes=[]
                        break
                    char_boxes.append(cb)
            self.fragments.append(dict(start=len(self.full),end=len(self.full)+len(text),box=box,chars=char_boxes,text=text))
            self.full+=text
        self.reliable=bool(self.fragments) and any(f['box'] or f['chars'] for f in self.fragments)

    def locate_source(self, source, start, end):
        source=norm(source)
        if self.full==source:
            span=(start,end)
        else:
            span,_=unique_span(self.full,source[start:end],source[max(0,start-6):start],source[end:end+6])
        if span is None:
            return None
        rects=[]
        precise=True
        covered=0
        for f in self.fragments:
            lo,hi=max(span[0],f['start']),min(span[1],f['end'])
            if lo>=hi:
                continue
            if f['chars']:
                boxes=f['chars'][lo-f['start']:hi-f['start']]
                # Preserve per-character geometry; cross-line spans stay separate.
                rects.extend(_rect(b) for b in boxes)
            elif f['box']:
                rects.append(_rect(f['box']))
                precise=False
            else:
                return None
            covered+=hi-lo
        if covered != end-start:
            return None
        return {'rects':rects,'precision':'character' if precise else 'region'}

    def _find(self,quote,a_left='',a_right=''):
        span,_=unique_span(self.full,quote,a_left,a_right)
        return span[0] if span else None

    def locate(self,quote,a_left='',a_right=''):
        start=self._find(quote,a_left,a_right)
        result=self.locate_source(self.full,start,start+len(norm(quote))) if start is not None else None
        return result['rects'] if result else []


def build_layout_locators(layout_pages,expected_pages):
    pages=layout_pages if isinstance(layout_pages,list) else []
    out=[]
    for i in range(expected_pages):
        try:
            ll=LayoutLocator(pages[i]) if i<len(pages) else None
            out.append(ll if ll and ll.reliable else None)
        except (TypeError,ValueError,KeyError):
            out.append(None)
    return out
