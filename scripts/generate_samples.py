from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out = Path(__file__).parent.parent / 'static' / 'samples'
out.mkdir(parents=True, exist_ok=True)

def make_label(path, brand, abv, net, warning):
    img = Image.new('RGB', (800,1200), 'white')
    d = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype('arial.ttf', 48)
        f2 = ImageFont.truetype('arial.ttf', 28)
    except Exception:
        f1 = ImageFont.load_default()
        f2 = ImageFont.load_default()

    d.text((40,40), brand, fill='black', font=f1)
    d.text((40,140), f'ABV: {abv}', fill='black', font=f2)
    d.text((40,190), f'Net: {net}', fill='black', font=f2)
    d.multiline_text((40,260), warning, fill='black', font=f2)
    img.save(path)

if __name__ == '__main__':
    warning = ("""GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy
because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.""")
    make_label(out / 'sample1.png', 'OLD TOM DISTILLERY', '45% Alc./Vol. (90 Proof)', '750 mL', warning)
    make_label(out / 'sample2.png', "STONE'S THROW", '40% Alc./Vol.', '750 mL', warning)
    print('Samples written to', out)
