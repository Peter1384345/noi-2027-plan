# -*- coding: utf-8 -*-
"""v10-3：把特效视频插入 P04 / P11（章节页背景层），设置自动播放 + 循环"""
import sys, os, subprocess
from pptx import Presentation
from pptx.util import Emu
from lxml import etree
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
FF = r"C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
BASE = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58"
F = BASE + r"/微光成炬-星火自有燎原时（终版·v10）.pptx"
FX = BASE + r"/work/fx"
EMU = 914400

prs = Presentation(F)
sl = list(prs.slides)


def poster(video, tag):
    out = os.path.join(FX, f'poster_{tag}.jpg')
    subprocess.run([FF, '-y', '-i', video, '-vframes', '1', out],
                   capture_output=True)
    return out


def add_autoplay(slide, spid):
    """在 mainSeq 起始处插入 delay=0 的媒体节点：进入页面即播、循环"""
    sld = slide._element
    tim = sld.find(qn('p:timing'))
    cts = [int(e.get('id')) for e in tim.iter(qn('p:cTn')) if e.get('id')]
    base = max(cts) + 10
    mainSeq = None
    for ctn in tim.iter(qn('p:cTn')):
        if ctn.get('nodeType') == 'mainSeq':
            mainSeq = ctn
            break
    child = mainSeq.find(qn('p:childTnLst'))
    xml = (
        f'<p:par xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        f'<p:cTn id="{base}" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:video>'
        f'<p:cMediaNode vol="80000" showWhenStopped="0" numSld="1">'
        f'<p:cTn id="{base+1}" fill="hold" display="0" repeatCount="indefinite">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
        f'<p:endCondLst><p:cond evt="onStopAudio" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:endCondLst>'
        f'</p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
        f'</p:cMediaNode></p:video></p:childTnLst></p:cTn></p:par>')
    child.insert(0, etree.fromstring(xml))
    print(f'  自动播放/循环节点已写入（spid={spid}, cTn={base}）')


def insert_bg_video(slide, video, tag):
    p = poster(video, tag)
    movie = slide.shapes.add_movie(video, Emu(0), Emu(0),
                                   Emu(int(13.333 * EMU)), Emu(int(7.5 * EMU)),
                                   poster_frame_image=p, mime_type='video/mp4')
    sp = movie._element
    spTree = sld_spTree = slide._element.find(qn('p:cSld')).find(qn('p:spTree'))
    spTree.remove(sp)
    # 插到 index 1：背景矩形之上、所有文字/图片之下
    kids = [k for k in spTree if k.tag in (qn('p:sp'), qn('p:pic'), qn('p:graphicFrame'), qn('p:grpSp'))]
    if kids:
        kids[0].addnext(sp)
    else:
        spTree.append(sp)
    print(f'  视频已插入背景层：{os.path.basename(video)}  spid={movie.shape_id}')
    return movie.shape_id


# P04 = PART 01 寒门筑梦（新序号）
sid1 = insert_bg_video(sl[3], os.path.join(FX, 'fx_part01.mp4'), 'p04')
add_autoplay(sl[3], sid1)

# P11 = PART 02 高山邮路
sid2 = insert_bg_video(sl[10], os.path.join(FX, 'fx_part02.mp4'), 'p11')
add_autoplay(sl[10], sid2)

prs.save(F)
print('已保存 v10（含 2 段特效视频）')
