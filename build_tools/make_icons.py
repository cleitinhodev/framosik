"""Conversão determinística do PNG fornecido, sem redesenhar a marca."""
from pathlib import Path
from PIL import Image, ImageOps
import sys

def make_icons(source, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    image = Image.open(source).convert('RGBA')
    # A área útil tem alpha alto; margens transparentes não devem encolher o logo.
    box = image.getchannel('A').point(lambda a: 255 if a > 128 else 0).getbbox()
    if box:
        image = image.crop(box)
    master = Image.new('RGBA', (1024, 1024))
    fitted = ImageOps.contain(image, (960, 960), Image.Resampling.LANCZOS)
    master.alpha_composite(fitted, ((1024-fitted.width)//2, (1024-fitted.height)//2))
    for size in [16, 20, 24, 32, 40, 48, 64, 96, 128, 192, 256, 512, 1024]:
        master.resize((size, size), Image.Resampling.LANCZOS).save(output/f'framosik_{size}.png')
    master.save(output/'framosik.ico', sizes=[(n,n) for n in [16,24,32,48,64,128,256]])
    master.save(output/'framosik.icns', sizes=[(n,n) for n in [16,32,64,128,256,512,1024]])

if __name__ == '__main__':
    make_icons(sys.argv[1], sys.argv[2])
