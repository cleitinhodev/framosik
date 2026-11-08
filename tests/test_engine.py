import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cv2
import numpy as np
import pytest
from PIL import Image
from engine import Settings, align, Canvas, stitch
from media import Media


def drawing(width=440, height=850):
    rng = np.random.default_rng(82)
    image = np.full((height, width, 4), (225, 221, 245, 255), np.uint8)
    for i in range(120):
        x, y = rng.integers(10, width-10), rng.integers(10, height-10)
        color = tuple(int(c) for c in rng.integers(20, 210, 3))+(255,)
        cv2.circle(image, (int(x), int(y)), int(rng.integers(4, 24)), color, -1)
    for y in range(50, height, 95):
        cv2.putText(image, f'FRAME MOSAIC {y}', (15, y), cv2.FONT_HERSHEY_SIMPLEX, .65, (20, 30, 65, 255), 2)
    return image


@pytest.mark.parametrize('direction', ['free', 'vertical'])
def test_vertical_reconstruction(direction):
    full = drawing()
    cfg = Settings(direction=direction)
    last = full[500:800]
    canvas = Canvas(last, cfg)
    position = 0
    for top in [450, 400, 350, 300, 250, 200, 150, 100, 50, 0]:
        current = full[top:top+300]
        dx, dy, score, _ = align(last, current, cfg)
        assert (dx, dy) == (0, -50)
        assert score > .99
        position += dy
        canvas.add(current, 0, position)
        last = current
    assert np.array_equal(canvas.image, full[:800])


def test_horizontal_and_diagonal():
    full = drawing(900, 900)
    for dx, dy in [(40, 0), (-30, 25), (20, -30)]:
        previous = full[100:450, 100:500]
        current = full[100+dy:450+dy, 100+dx:500+dx]
        x, y, score, _ = align(previous, current, Settings())
        assert (x, y) == (dx, dy)
        assert score > .99


def test_scene_cut_and_duplicate():
    a = drawing()[:300]
    rng = np.random.default_rng(33)
    b = rng.integers(0, 256, a.shape, np.uint8)
    b[..., 3] = 255
    assert align(a, b, Settings())[2] < .65
    assert align(a, a.copy(), Settings())[:3] == (0, 0, 1.0)


@pytest.mark.parametrize('mode', ['preserve', 'feather', 'average'])
def test_blends_preserve_black_and_alpha(mode):
    first = np.zeros((60, 60, 4), np.uint8)
    first[..., 3] = 255
    second = np.full((60, 60, 4), 255, np.uint8)
    c = Canvas(first, Settings(blend=mode))
    c.add(second, 0, 30)
    assert c.image.shape == (90, 60, 4)
    assert (c.image[:30, :, :3] == 0).all()
    assert (c.image[60:] == 255).all()
    assert (c.image[..., 3] == 255).all()
    if mode == 'preserve':
        assert (c.image[:60, :, :3] == 0).all()


def test_gif_pipeline_and_range(tmp_path):
    full = drawing()
    frames = [Image.fromarray(full[y:y+300]) for y in range(0, 201, 40)]
    path = tmp_path/'cena_á.gif'
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=80, loop=0)
    with Media(path) as media:
        assert media.count == 6
        assert media.frame(3)[0].shape == (300, 440, 4)
    result = stitch(path, Settings(first=1, last=5, step=3))
    assert result.report['accepted'] == [2, 5, 6]
    assert result.image.shape == (460, 440, 4)
    result = stitch(path, Settings(first=0, last=5), cancelled=lambda: True)
    assert result.report['status'] == 'cancelado'
    assert len(result.report['accepted']) == 1


def test_video_pipeline(tmp_path):
    path = tmp_path/'pan.avi'
    full = drawing()
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'MJPG'), 25, (440, 300))
    assert writer.isOpened()
    for y in range(0, 201, 40):
        writer.write(cv2.cvtColor(full[y:y+300], cv2.COLOR_RGBA2BGR))
    writer.release()
    result = stitch(path, Settings(first=0, last=5, blend='feather'))
    assert len(result.report['accepted']) == 6
    assert result.image.shape == (500, 440, 4)


def test_invalid_settings_and_memory_guard():
    with pytest.raises(ValueError):
        Settings(first=5, last=1).validate(10, 100, 100)
    with pytest.raises(ValueError):
        Settings(crop_top=80).validate(10, 100, 100)
    with pytest.raises(ValueError):
        Canvas(np.zeros((1100, 1100, 4), np.uint8), Settings(max_megapixels=1))


def test_transparent_pixels_stay_transparent():
    image = np.zeros((50, 50, 4), np.uint8)
    image[10:40, 10:40] = (0, 0, 0, 255)
    canvas = Canvas(image, Settings())
    canvas.add(image, 20, 20)
    assert canvas.image[0, 0, 3] == 0
    assert canvas.image[15, 15, 3] == 255


def test_rejected_frame_does_not_move_reference(tmp_path):
    full = drawing()
    rng = np.random.default_rng(11)
    bad = rng.integers(0, 256, (300, 440, 4), np.uint8)
    bad[..., 3] = 255
    frames = [Image.fromarray(a) for a in [full[:300], full[40:340], bad, full[80:380]]]
    path = tmp_path/'cut.gif'
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=80)
    stopped = stitch(path, Settings(first=0, last=3))
    assert stopped.report['status'] == 'interrompido'
    assert stopped.report['accepted'] == [1, 2]
    skipped = stitch(path, Settings(first=0, last=3, skip_failed=True))
    assert skipped.report['accepted'] == [1, 2, 4]
    assert skipped.report['rejected'] == [3]
    assert skipped.image.shape[:2] == (380, 440)


def test_crop_and_resolution(tmp_path):
    full = drawing()
    frames = [Image.fromarray(full[y:y+300]) for y in [0, 40, 80]]
    path = tmp_path/'crop.gif'
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=80)
    result = stitch(path, Settings(first=0, last=2, scale=.5, crop_left=20, crop_right=20, crop_top=20, crop_bottom=20))
    assert result.image.shape[:2] == (170, 200)
    assert len(result.report['accepted']) == 3
