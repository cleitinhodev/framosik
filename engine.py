"""Montagem incremental por translação ou escala + XY, sem preenchimento por IA.

Cada frame é registrado no último frame aceito; a transformação é acumulada
no espaço global. Máscaras distinguem pixels pretos de regiões inexistentes.
"""
from dataclasses import dataclass, asdict
import time
import cv2
import numpy as np
from media import Media


@dataclass
class Settings:
    first: int = 0
    last: int = 0
    step: int = 1
    scale: float = 1.0
    direction: str = 'free'
    blend: str = 'preserve'
    feather: int = 24
    confidence: float = 0.65
    min_overlap: float = 0.20
    max_megapixels: int = 24
    skip_failed: bool = False
    crop_left: int = 0
    crop_top: int = 0
    crop_right: int = 0
    crop_bottom: int = 0

    def validate(self, count, width, height):
        if not 0 <= self.first <= self.last < count:
            raise ValueError('O primeiro frame deve ser menor ou igual ao último, dentro do arquivo.')
        if self.step < 1 or not 0.1 <= self.scale <= 1:
            raise ValueError('Passo ou escala inválidos.')
        if self.direction not in {'free', 'vertical', 'horizontal', 'zoom'} or self.blend not in {'preserve', 'feather', 'average'}:
            raise ValueError('Modo de alinhamento/mesclagem inválido.')
        if not 0 <= self.confidence <= 1 or not 0.05 <= self.min_overlap <= .9:
            raise ValueError('Confiança/sobreposição inválida.')
        if not 1 <= self.max_megapixels <= 100 or not 1 <= self.feather <= 300:
            raise ValueError('Limite de imagem ou suavização inválidos.')
        margins = (self.crop_left, self.crop_top, self.crop_right, self.crop_bottom)
        if min(margins) < 0 or width-self.crop_left-self.crop_right < 32 or height-self.crop_top-self.crop_bottom < 32:
            raise ValueError('O recorte precisa deixar pelo menos 32 × 32 pixels.')


def prepare(rgba, cfg):
    h, w = rgba.shape[:2]
    out = rgba[cfg.crop_top:h-cfg.crop_bottom, cfg.crop_left:w-cfg.crop_right]
    if cfg.scale != 1:
        out = cv2.resize(out, None, fx=cfg.scale, fy=cfg.scale, interpolation=cv2.INTER_AREA)
    return np.ascontiguousarray(out)


def overlap_score(previous, current, dx, dy, minimum):
    """NCC da região realmente compartilhada; penaliza cortes e falsas matches."""
    h, w = previous.shape[:2]
    x0, y0, x1, y1 = max(0, dx), max(0, dy), min(w, dx+w), min(h, dy+h)
    if x1 <= x0 or y1 <= y0:
        return -1.0
    a = previous[y0:y1, x0:x1]
    b = current[y0-dy:y1-dy, x0-dx:x1-dx]
    mask = (a[..., 3] > 200) & (b[..., 3] > 200)
    if mask.sum() < h*w*minimum:
        return -1.0
    # Limita o custo da validação sem alterar os pixels exportados.
    stride = max(1, int(np.sqrt(mask.size/180000)))
    a, b, mask = a[::stride, ::stride], b[::stride, ::stride], mask[::stride, ::stride]
    a = cv2.cvtColor(a, cv2.COLOR_RGBA2GRAY)[mask].astype(np.float32)
    b = cv2.cvtColor(b, cv2.COLOR_RGBA2GRAY)[mask].astype(np.float32)
    if len(a) < 32:
        return -1.0
    error = float(np.mean(np.abs(a-b)))
    a -= a.mean()
    b -= b.mean()
    denom = float(np.linalg.norm(a)*np.linalg.norm(b))
    if denom < 1:
        return 1.0 if error < 1 else -1.0
    return float(np.dot(a, b)/denom)


def align(previous, current, cfg):
    if previous.shape != current.shape:
        raise ValueError('As dimensões dos frames mudaram dentro da cena.')
    if np.array_equal(previous, current):
        return 0, 0, 1.0, 'repetido'
    h, w = previous.shape[:2]
    ratio = min(1.0, 1100/max(h, w))
    size = (max(16, round(w*ratio)), max(16, round(h*ratio)))
    grays, masks = [], []
    for image in (previous, current):
        grays.append(cv2.resize(cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY), size))
        masks.append(cv2.resize((image[..., 3] > 200).astype('uint8')*255, size, interpolation=cv2.INTER_NEAREST))
    candidates = []
    sift = cv2.SIFT_create(nfeatures=2500, contrastThreshold=0.02)
    ka, da = sift.detectAndCompute(grays[0], masks[0])
    kb, db = sift.detectAndCompute(grays[1], masks[1])
    if da is not None and db is not None and len(da) >= 4 and len(db) >= 4:
        pairs = cv2.BFMatcher().knnMatch(db, da, k=2)
        good = [p[0] for p in pairs if len(p) == 2 and p[0].distance < .72*p[1].distance]
        if len(good) >= 5:
            src = np.float32([kb[m.queryIdx].pt for m in good])
            dst = np.float32([ka[m.trainIdx].pt for m in good])
            # RANSAC elimina correspondências inconsistentes. Apenas a translação
            # dos inliers é utilizada: este protótipo NÃO deforma o desenho.
            _, inliers = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2.5)
            if inliers is not None and inliers.sum() >= 5:
                delta = (dst-src)[inliers.ravel().astype(bool)]
                median = np.median(delta, axis=0)
                consistent = np.linalg.norm(delta-median, axis=1) <= 3
                if consistent.sum() >= 5:
                    shift = np.median(delta[consistent], axis=0)/ratio
                    candidates.append((*shift, 'detalhes SIFT'))
    # Alternativa útil quando há poucos cantos/detalhes na ilustração.
    window = cv2.createHanningWindow(size, cv2.CV_32F)
    shift, response = cv2.phaseCorrelate(grays[1].astype('float32'), grays[0].astype('float32'), window)
    if response > .08 and np.isfinite(shift).all():
        candidates.append((shift[0]/ratio, shift[1]/ratio, 'correlação'))
    best = (0, 0, -1.0, 'sem correspondência')
    for dx, dy, method in candidates:
        dx, dy = round(dx), round(dy)
        if cfg.direction == 'vertical':
            if abs(dx) > max(4, w*.02):
                continue
            dx = 0
        elif cfg.direction == 'horizontal':
            if abs(dy) > max(4, h*.02):
                continue
            dy = 0
        # Busca local de 1 px evita borrão por arredondamento no detector reduzido.
        for ox in ([0] if cfg.direction == 'vertical' else [-1, 0, 1]):
            for oy in ([0] if cfg.direction == 'horizontal' else [-1, 0, 1]):
                x, y = dx+ox, dy+oy
                score = overlap_score(previous, current, x, y, cfg.min_overlap)
                if score > best[2]:
                    best = (x, y, score, method)
    return best


def align_zoom(previous, current, cfg):
    """Fit uniform scale + XY, current -> last accepted frame (no perspective)."""
    identity = np.eye(3, dtype=np.float64)
    if previous.shape != current.shape:
        raise ValueError('As dimensões dos frames mudaram dentro da cena.')
    if np.array_equal(previous, current):
        return identity, 1.0, 'repetido'
    h, w = previous.shape[:2]
    ratio = min(1.0, 1100/max(h, w))
    size = (max(16, round(w*ratio)), max(16, round(h*ratio)))
    detector = cv2.SIFT_create(nfeatures=4000, contrastThreshold=.015)
    features = []
    for image in (previous, current):
        gray = cv2.resize(cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY), size)
        mask = cv2.resize((image[..., 3] > 200).astype('uint8')*255, size,
                          interpolation=cv2.INTER_NEAREST)
        features.append(detector.detectAndCompute(gray, mask))
    (ka, da), (kb, db) = features
    failed = (identity, -1.0, 'zoom sem correspondência')
    if da is None or db is None or min(len(da), len(db)) < 8:
        return failed
    pairs = cv2.BFMatcher().knnMatch(db, da, k=2)
    good = [a for a, *rest in pairs if rest and a.distance < .72*rest[0].distance]
    if len(good) < 8:
        return failed
    src = np.float64([kb[m.queryIdx].pt for m in good])/ratio
    dst = np.float64([ka[m.trainIdx].pt for m in good])/ratio
    model, inliers = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC,
                                                ransacReprojThreshold=2.5/ratio)
    if model is None or inliers is None or inliers.sum() < max(8, len(good)*.35):
        return failed
    # Reject rotation, then refit only scale/translation on the RANSAC consensus.
    if abs(np.degrees(np.arctan2(model[1, 0], model[0, 0]))) > 2:
        return failed
    src, dst = src[inliers.ravel().astype(bool)], dst[inliers.ravel().astype(bool)]
    if np.ptp(src, axis=0).min() < min(h, w)*.12:
        return failed
    a, b = src-src.mean(axis=0), dst-dst.mean(axis=0)
    scale = float(np.sum(a*b)/max(np.sum(a*a), 1e-9))
    offset = dst.mean(axis=0)-scale*src.mean(axis=0)
    if not .5 <= scale <= 2 or np.median(np.linalg.norm(src*scale+offset-dst, axis=1)) > 3/ratio:
        return failed
    matrix = np.array([[scale, 0, offset[0]], [0, scale, offset[1]], [0, 0, 1.]])
    warped = cv2.warpAffine(current, matrix[:2], (w, h), flags=cv2.INTER_LINEAR)
    score = overlap_score(previous, warped, 0, 0, cfg.min_overlap)
    return matrix, score, 'escala + XY (SIFT)'


class Canvas:
    def __init__(self, image, cfg):
        self.cfg = cfg
        self._check(image.shape[1], image.shape[0])
        self.image = image.copy()
        self.seams = np.zeros(image.shape[:2], np.uint8)
        self.x = self.y = 0

    def _check(self, w, h):
        if w*h > self.cfg.max_megapixels*1_000_000 or max(w, h) > 60000:
            raise ValueError('Limite de tamanho atingido. Reduza a escala ou o intervalo de frames.')

    def add_transformed(self, frame, matrix):
        """Warp each original frame once; bound the allocation before warping."""
        if not np.isfinite(matrix).all() or not .05 <= matrix[0, 0] <= 20:
            raise ValueError('Escala acumulada fora do limite seguro. Reduza o intervalo.')
        h, w = frame.shape[:2]
        corners = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]]) @ matrix.T
        left, top = np.floor(corners[:, :2].min(axis=0)).astype(int)
        right, bottom = np.ceil(corners[:, :2].max(axis=0)).astype(int)
        ch, cw = self.image.shape[:2]
        self._check(max(self.x+cw, right)-min(self.x, left),
                    max(self.y+ch, bottom)-min(self.y, top))
        local = matrix[:2].copy()
        local[:, 2] -= [left, top]
        # Premultiplied alpha prevents dark fringes at transparent edges.
        pixels = frame.astype(np.float32)/255
        pixels[..., :3] *= pixels[..., 3:4]
        warped = cv2.warpAffine(pixels, local, (right-left, bottom-top), flags=cv2.INTER_LINEAR)
        np.divide(warped[..., :3], warped[..., 3:4], out=warped[..., :3],
                  where=warped[..., 3:4] > 0)
        self.add(np.clip(np.rint(warped*255), 0, 255).astype(np.uint8), int(left), int(top))

    def add(self, frame, x, y):
        h, w = frame.shape[:2]
        ch, cw = self.image.shape[:2]
        left, top = min(self.x, x), min(self.y, y)
        right, bottom = max(self.x+cw, x+w), max(self.y+ch, y+h)
        self._check(right-left, bottom-top)
        if (left, top, right, bottom) != (self.x, self.y, self.x+cw, self.y+ch):
            enlarged = np.zeros((bottom-top, right-left, 4), np.uint8)
            enlarged[self.y-top:self.y-top+ch, self.x-left:self.x-left+cw] = self.image
            expanded_seams = np.zeros(enlarged.shape[:2], np.uint8)
            expanded_seams[self.y-top:self.y-top+ch, self.x-left:self.x-left+cw] = self.seams
            self.seams = expanded_seams
            self.image, self.x, self.y = enlarged, left, top
        roi = self.image[y-self.y:y-self.y+h, x-self.x:x-self.x+w]
        valid = frame[..., 3] > 0
        old = roi[..., 3] > 0
        fresh, overlap = valid & ~old, valid & old
        if fresh.any() and overlap.any():
            mask = self.seams[y-self.y:y-self.y+h, x-self.x:x-self.x+w]
            near_new = cv2.dilate(fresh.astype(np.uint8), np.ones((5, 5), np.uint8))
            mask[overlap & (near_new > 0)] = 255
        if self.cfg.direction == 'zoom':
            # A warped edge may cover only part of a pixel. Prefer a later
            # observation with better coverage, even in preserve mode.
            better = overlap & (frame[..., 3] > roi[..., 3])
            roi[better] = frame[better]
            overlap &= frame[..., 3] == roi[..., 3]
        if self.cfg.blend == 'average':
            roi[overlap, :3] = ((roi[overlap, :3].astype('uint16') + frame[overlap, :3])/2).astype('uint8')
            roi[overlap, 3] = np.maximum(roi[overlap, 3], frame[overlap, 3])
        elif self.cfg.blend == 'feather' and fresh.any():
            # Fade apenas junto à nova área. Regiões antigas distantes são preservadas.
            distance = cv2.distanceTransform((~fresh).astype('uint8'), cv2.DIST_L2, 3)
            weight = np.clip(1-distance/self.cfg.feather, 0, 1)
            active = overlap & (weight > 0)
            alpha = weight[active, None]
            roi[active, :3] = np.rint(roi[active, :3]*(1-alpha)+frame[active, :3]*alpha).astype('uint8')
        roi[fresh] = frame[fresh]


@dataclass
class Result:
    image: np.ndarray
    report: dict
    seams: np.ndarray = None


def stitch(path, cfg, progress=lambda *_: None, preview=lambda *_: None, cancelled=lambda: False):
    started = time.monotonic()
    with Media(path) as media:
        cfg.validate(media.count, media.width, media.height)
        indices = list(range(cfg.first, cfg.last+1, cfg.step))
        if indices[-1] != cfg.last:
            indices.append(cfg.last)
        first, _ = media.frame(indices[0])
        previous = prepare(first, cfg)
        canvas = Canvas(previous, cfg)
        x = y = 0
        transform = np.eye(3, dtype=np.float64)
        accepted, rejected = [indices[0]+1], []
        records = []
        status, reason = 'concluído', ''
        preview(thumbnail(canvas.image).copy())
        last_preview = 0.0
        for ordinal, index in enumerate(indices[1:], 2):
            if cancelled():
                status, reason = 'cancelado', 'Montagem parcial conservada.'
                break
            raw, _ = media.frame(index)
            current = prepare(raw, cfg)
            if cfg.direction == 'zoom':
                relative, confidence, method = align_zoom(previous, current, cfg)
                dx, dy = float(relative[0, 2]), float(relative[1, 2])
            else:
                dx, dy, confidence, method = align(previous, current, cfg)
                relative = np.array([[1., 0, dx], [0, 1., dy], [0, 0, 1.]])
            record = dict(frame=index+1, dx=dx, dy=dy, confidence=round(confidence, 4), method=method)
            if confidence < cfg.confidence:
                rejected.append(index+1)
                record['accepted'] = False
                records.append(record)
                progress(ordinal, len(indices), record)
                if not cfg.skip_failed:
                    status = 'interrompido'
                    reason = f'Frame {index+1} não alinhado. Reduza o passo, ajuste o recorte ou revise o fim da cena.'
                    break
                continue  # A referência continua sendo o último frame ACEITO.
            try:
                candidate = transform @ relative
                if cfg.direction == 'zoom':
                    canvas.add_transformed(current, candidate)
                else:
                    canvas.add(current, x+dx, y+dy)
            except ValueError as error:
                status, reason = 'interrompido', str(error)
                break
            transform = candidate
            x, y = float(transform[0, 2]), float(transform[1, 2])
            if cfg.direction != 'zoom':
                x, y = round(x), round(y)
            previous = current
            accepted.append(index+1)
            record.update(accepted=True, global_x=x, global_y=y,
                          relative_scale=float(relative[0, 0]), global_scale=float(transform[0, 0]),
                          transform=transform.tolist())
            records.append(record)
            progress(ordinal, len(indices), record)
            if time.monotonic()-last_preview > .4:
                preview(thumbnail(canvas.image).copy())
                last_preview = time.monotonic()
        report = dict(status=status, reason=reason, settings=asdict(cfg), accepted=accepted, rejected=rejected,
                      width=canvas.image.shape[1], height=canvas.image.shape[0],
                      seconds=round(time.monotonic()-started, 2), frames=records)
        return Result(canvas.image, report, canvas.seams)


def thumbnail(image, limit=1400):
    scale = min(1, limit/max(image.shape[:2]))
    if scale < 1:
        return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return image.copy()


def finish_image(image, seams, smooth, color):
    """Filter opaque seam neighborhoods in strips to bound temporary memory."""
    if not (smooth or color) or seams is None:
        return image
    output = image.copy()
    for top in range(0, len(image), 128):
        bottom = min(len(image), top + 128)
        start, stop = max(0, top - 4), min(len(image), bottom + 4)
        mask = seams[start:stop]
        if not mask.any():
            continue
        rgba = image[start:stop]
        strength = cv2.GaussianBlur(mask, (5, 5), 1)
        opaque = cv2.erode(rgba[..., 3], np.ones((5, 5), np.uint8)) == 255
        weight = (strength * (1.0 / 255) * opaque).astype(np.float32)[..., None]
        rgb = np.ascontiguousarray(rgba[..., :3])
        mixed = rgb.astype(np.float32)
        if color:
            median = cv2.medianBlur(rgb, 3)
            mixed += (median - mixed) * weight * (color / 100)
        if smooth:
            soft = cv2.bilateralFilter(rgb, 5, 24, 2)
            mixed += (soft - mixed) * weight * (smooth / 100)
        output[top:bottom, :, :3] = np.rint(mixed[top-start:bottom-start]).astype(np.uint8)
    return output
