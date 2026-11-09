"""Convert the supplied PNG/ICO without redrawing or changing its framing."""
from pathlib import Path
from PIL import Image
import shutil
import sys


def make_icons(source, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    original = Image.open(source)
    image = original.convert('RGBA')  # Pillow selects the largest ICO layer.
    for size in [16, 20, 24, 32, 40, 48, 64, 96, 128, 192, 256, 512, 1024]:
        layer = (original.ico.getimage((size, size)).convert('RGBA')
                 if original.format == 'ICO' and (size, size) in original.ico.sizes()
                 else image.resize((size, size), Image.Resampling.LANCZOS))
        layer.save(output/f'framosik_{size}.png')
    if original.format == 'ICO':
        shutil.copyfile(source, output/'framosik.ico')
    else:
        image.save(output/'framosik.ico', sizes=[(n,n) for n in [16,24,32,48,64,128,256]])
    image.resize((1024,1024), Image.Resampling.LANCZOS).save(output/'framosik.icns')

if __name__ == '__main__':
    make_icons(sys.argv[1], sys.argv[2])
