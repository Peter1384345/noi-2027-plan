# -*- coding: utf-8 -*-
"""v11：以真原版 15 页为基线，动画特效零改动，只在页面内添加内容（两人均衡，陈新超略多）"""
import sys, shutil, copy
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')
BASE = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58"
SRC = r"D:/桌面/总文件夹/资料整合/微光成炬-星火自有燎原时.pptx"
DST = BASE + r"/微光成炬-星火自有燎原时（终版·v11）.pptx"
shutil.copyfile(SRC, DST)

prs = Presentation(DST)
sl = list(prs.slides)
EMU = 914400


def box(slide, sid):
    return next(sh for sh in slide.shapes if sh.shape_id == sid)


def append_run(sh, text):
    """在段落末尾追加一句，复用该段最后一个 run 的字符样式"""
    p = sh.text_frame.paragraphs[0]._p
    runs = p.findall(qn('a:r'))
    rPr = runs[-1].find(qn('a:rPr'))
    r = etree.SubElement(p, qn('a:r'))
    if rPr is not None:
        r.append(copy.deepcopy(rPr))
    etree.SubElement(r, qn('a:t')).text = text


def add_caption(slide, x, y, w, text, size=9.75):
    """新增小注脚（金色 E8C87A，微软雅黑，与原版注脚同色系）"""
    tb = slide.shapes.add_textbox(Emu(int(x * EMU)), Emu(int(y * EMU)),
                                  Emu(int(w * EMU)), Emu(int(0.22 * EMU)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]._p
    r = etree.SubElement(p, qn('a:r'))
    rPr = etree.SubElement(r, qn('a:rPr'))
    rPr.set('lang', 'zh-CN'); rPr.set('sz', str(int(size * 100))); rPr.set('spc', '150')
    fill = etree.SubElement(rPr, qn('a:solidFill'))
    clr = etree.SubElement(fill, qn('a:srgbClr')); clr.set('val', 'E8C87A')
    for tag, face in (('a:latin', '微软雅黑'), ('a:ea', '微软雅黑')):
        el = etree.SubElement(rPr, qn(tag)); el.set('typeface', face)
    etree.SubElement(r, qn('a:t')).text = text


# ---------- 韩雅平（2 处，适度） ----------
# 1. P06 人物页：补奖学金去向与助学贷款
s6 = sl[5]
b223 = box(s6, 223)
tx = b223.text_frame._txBody
p_blank = etree.fromstring(
    '<a:p xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:r><a:t> </a:t></a:r></a:p>')
tx.append(p_blank)
p_new = copy.deepcopy(tx.findall(qn('a:p'))[0])   # 复用段0样式
for r in p_new.findall(qn('a:r')):
    p_new.remove(r)
r = etree.SubElement(p_new, qn('a:r'))
src_r = tx.findall(qn('a:p'))[0].find(qn('a:r'))
if src_r is not None and src_r.find(qn('a:rPr')) is not None:
    r.append(copy.deepcopy(src_r.find(qn('a:rPr'))))
etree.SubElement(r, qn('a:t')).text = (
    '学校免了学费还发奖学金，"花了一点，剩下的钱都给爸妈了"；'
    '父亲申请了助学贷款，不给爱心捐款添负担。')
tx.append(p_new)
print('P06 人物页：+1 段（奖学金去向 / 助学贷款）')

# 2. P07 699 页：底部右上加一行后续影响
s7 = sl[6]
add_caption(s7, 8.20, 6.83, 4.40, '九月，郏县实验高中开起「向韩雅平学习」主题班会')
print('P07 699 页：+1 注脚（主题班会）')

# ---------- 陈新超（4 处，略多） ----------
s10 = sl[9]
append_run(box(s10, 44), '副驾驶一个月至少 20 天不空着。')
append_run(box(s10, 48), '顺路还帮老人买药、捎上子女寄回的衣物年货。')
append_run(box(s10, 52), '退回来第三天，她照常清晨 5 点出车。')
print('P10 服务站：3 张卡各 +1 句')

s11 = sl[10]
add_caption(s11, 7.75, 6.83, 3.60, '五年 20 多万公里，绕赤道 5 圈')
print('P11 1700+ 页：+1 注脚（20 多万公里）')

prs.save(DST)
print('已保存 v11（原版 15 页结构 / 动画特效零改动）')
