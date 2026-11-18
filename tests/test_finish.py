import numpy as np
from engine import finish_image


def test_local_retreatment_preserves_alpha_and_unmarked_pixels():
    im = np.full((260, 18, 4), 120, np.uint8)
    im[..., 3] = 255
    im[:, 9, :3] = 130
    seams = np.zeros(im.shape[:2], np.uint8)
    seams[:, 9] = 255
    im[80, 9, 3] = 0
    for smooth, color in [(60, 0), (0, 60)]:
        result = finish_image(im, seams, smooth, color)
        assert result[128, 9, 0] < 130
        assert result[128, 9, 0] == result[127, 9, 0]
        assert np.array_equal(im[..., 3], result[..., 3])
        assert np.array_equal(im[:, :5], result[:, :5])
        assert np.array_equal(im[80, 9], result[80, 9])
    assert finish_image(im, seams, 0, 0) is im
