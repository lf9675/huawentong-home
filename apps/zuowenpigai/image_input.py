"""One oriented image is used for OCR, browser display and PDF export."""
from io import BytesIO
from PIL import Image, ImageOps


def normalize_image(data, rotation=0, max_bytes=9*1024*1024):
    with Image.open(BytesIO(data)) as source:
        im = ImageOps.exif_transpose(source).convert('RGB')
        if rotation:
            im = im.rotate(-rotation, expand=True)
        for _ in range(6):
            for quality in (94, 85, 70):
                buf = BytesIO()
                im.save(buf, 'JPEG', quality=quality)
                if buf.tell() <= max_bytes:
                    return buf.getvalue()
            im = im.resize((max(1, im.width*3//4), max(1, im.height*3//4)))
    raise ValueError('Image remains too large; upload a smaller image.')


def layout_envelope(response):
    pages = (response.get('data_info') or {}).get('pages') or []
    size = pages[0] if pages else {}
    return {'elements': response.get('layout_details') or [],
            'width': size.get('width'), 'height': size.get('height'),
            'coordinate_space': 'pixel'}


def sync_corrected_pages(state, pages):
    previous = state.get('ocr_pages') or []
    layouts = list(state.get('ocr_layout_pages') or [])
    # Retain unchanged page geometry; discard only the edited page's stale data.
    state['ocr_layout_pages'] = [layouts[i] if i < len(layouts) and i < len(previous)
                                and previous[i] == p else None for i, p in enumerate(pages)]
    state['ocr_pages'] = list(pages)
    state['ocr_text'] = '\n'.join(pages)
    return state['ocr_text']
