"""Export unchanged existing comic rectangles for normal-flow iPad images."""
from pathlib import Path
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / 'du/textbook/2hcl/unit1/ba-ai-shuo-chu-lai'
source = (LESSON / 'content.js').read_text()
lesson = json.loads(source.split('window.LESSON=', 1)[1].split(';\nwindow.DATA', 1)[0])
for n, (x, y, width, height) in enumerate(lesson['panelRects'], 1):
    sheet = (n - 1) // 10 + 1
    original = Image.open(LESSON / f'assets/comic{sheet}.png')
    panel = original.crop((x, y, x + width, y + height))
    target = LESSON / lesson['panelImages'][n - 1]
    target.parent.mkdir(exist_ok=True, parents=True)
    panel.save(target, optimize=True)
    assert Image.open(target).tobytes() == panel.tobytes()
print(f"Exported {len(lesson['panelRects'])} unchanged comic panels.")
