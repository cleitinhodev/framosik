"""Gera uma ilustração de teste própria, com movimento vertical conhecido."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    im = Image.new('RGB', (480, 1080), '#131b2e')
    d = ImageDraw.Draw(im)
    # Elementos distintos ajudam a verificar o alinhamento de cada região.
    rng = np.random.default_rng(41)
    for i in range(100):
        x, y = map(int, [rng.integers(10, 470), rng.integers(20, 1060)])
        r = int(rng.integers(1, 4))
        d.ellipse((x-r, y-r, x+r, y+r), fill='#54648c')
    for y in range(20, 1080, 80):
        d.line((12, y, 34, y), fill='#8294c9', width=2)
        d.text((38, y-5), str(y), fill='#8294c9')
    # Mascote geométrico de demonstração: a cena é estática.
    d.rounded_rectangle((174, 360, 220, 880), 18, fill='#8293f9', outline='#c8d2ff', width=4)
    d.rounded_rectangle((260, 360, 306, 880), 18, fill='#8293f9', outline='#c8d2ff', width=4)
    d.rounded_rectangle((135, 855, 224, 915), 18, fill='#48cdbb', outline='#affff0', width=4)
    d.rounded_rectangle((257, 855, 345, 915), 18, fill='#48cdbb', outline='#affff0', width=4)
    d.rounded_rectangle((115, 330, 165, 610), 20, fill='#5868bf', outline='#c8d2ff', width=4)
    d.rounded_rectangle((315, 330, 365, 610), 20, fill='#5868bf', outline='#c8d2ff', width=4)
    d.rounded_rectangle((155, 310, 325, 575), 25, fill='#a0adff', outline='#d7deff', width=4)
    d.rounded_rectangle((185, 360, 295, 465), 14, fill='#253354')
    d.line((206, 400, 229, 425, 278, 380), fill='#74f4cd', width=8)
    d.rounded_rectangle((150, 155, 330, 290), 40, fill='#a0adff', outline='#e2e6ff', width=4)
    d.rounded_rectangle((172, 190, 308, 250), 16, fill='#253354')
    d.ellipse((193, 208, 212, 227), fill='#74f4cd')
    d.ellipse((267, 208, 286, 227), fill='#74f4cd')
    d.line((240, 154, 240, 121), fill='#a0adff', width=5)
    d.ellipse((231, 103, 249, 121), fill='#74f4cd')
    d.text((177, 50), 'FRAME MOSAIC', fill='#e3e7ff', stroke_width=1)
    d.text((130, 985), 'CENA DE TESTE / PAN VERTICAL', fill='#c8d2ff')
    d.text((145, 1010), '480 x 1080 / 37 FRAMES', fill='#8294c9')
    # Uma paleta global evita diferenças de cor entre frames de GIF.
    indexed = im.quantize(colors=128)
    frames = [indexed.crop((0, y, 480, y+360)) for y in range(720, -1, -20)]
    frames[0].save(folder/'demo_vertical.gif', save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=False)
    indexed.convert('RGBA').save(folder/'resultado_esperado.png')

if __name__ == '__main__':
    create(Path(__file__).resolve().parents[1]/'examples')
