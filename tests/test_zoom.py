import numpy as np
import cv2
import pytest
from PIL import Image
from engine import Settings, align_zoom, Canvas, stitch
from test_engine import drawing


def scene_frames():
    full = drawing(900, 900)
    # Increasing field of view: zoom out with a small diagonal pan.
    boxes = [(250, 240, 320), (220, 205, 400), (180, 165, 500)]
    frames = [cv2.resize(full[y:y+n, x:x+n], (320,320)) for x,y,n in boxes]
    return frames, boxes


def test_scale_and_translation_in_both_directions():
    frames, boxes = scene_frames()
    for a,b,i,j in [(frames[0],frames[1],0,1),(frames[1],frames[0],1,0)]:
        m, score, _ = align_zoom(a,b,Settings(direction='zoom'))
        x,y,n=boxes[i]; xx,yy,nn=boxes[j]
        expected = np.array([[nn/n,0,(xx-x)*320/n],[0,nn/n,(yy-y)*320/n],[0,0,1]])
        assert score > .85
        assert np.allclose(m,expected,atol=.65)


@pytest.mark.parametrize('blend',['preserve','feather','average'])
def test_zoom_chain(tmp_path, blend):
    frames,_=scene_frames()
    path=tmp_path/'zoom.gif'
    ims=[Image.fromarray(f) for f in frames]
    ims[0].save(path,save_all=True,append_images=ims[1:],duration=100)
    result=stitch(path,Settings(last=2,direction='zoom',blend=blend))
    assert result.report['accepted']==[1,2,3]
    assert abs(result.report['frames'][-1]['global_scale']-500/320)<.02
    assert 498 <= result.image.shape[0] <= 503
    assert 498 <= result.image.shape[1] <= 503
    assert np.isfinite(result.image).all()


def test_zoom_cut_skip_cancel_and_memory(tmp_path):
    frames,_=scene_frames()
    rng=np.random.default_rng(4)
    bad=rng.integers(0,256,frames[0].shape,np.uint8);bad[...,3]=255
    assert align_zoom(frames[0],bad,Settings(direction='zoom'))[1]<.65
    ims=[Image.fromarray(f) for f in [frames[0],bad,frames[1]]]
    path=tmp_path/'cut.gif';ims[0].save(path,save_all=True,append_images=ims[1:])
    result=stitch(path,Settings(last=2,direction='zoom',skip_failed=True))
    assert result.report['accepted']==[1,3]
    assert result.report['rejected']==[2]
    assert abs(result.report['frames'][-1]['global_scale']-1.25)<.02
    assert stitch(path,Settings(last=2,direction='zoom'),cancelled=lambda:True).report['status']=='cancelado'
    canvas=Canvas(frames[0],Settings(max_megapixels=1))
    with pytest.raises(ValueError): canvas.add_transformed(frames[1],np.diag([10.,10.,1.]))
    assert canvas.image.shape==frames[0].shape


def test_zoom_transparency_has_no_black_fringe():
    im=np.zeros((64,64,4),np.uint8);im[10:50,10:50]=(250,100,50,255)
    canvas=Canvas(np.zeros_like(im),Settings())
    canvas.add_transformed(im,np.array([[1.23,0,-5.4],[0,1.23,4.6],[0,0,1.]]))
    valid=canvas.image[...,3]>0
    assert np.all(canvas.image[valid,:3]==(250,100,50))
