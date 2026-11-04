# -*- coding: utf-8 -*-
"""v8：把每一页的可查证内容填满（提高单页信息密度）"""
import sys, copy
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
SRC = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7）.pptx"
DST = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v8）.pptx"
EMU = 914400
FONT = '微软雅黑'

prs = Presentation(SRC)
sl = list(prs.slides)


def find(idx, needle):
    for sh in sl[idx].shapes:
        if sh.has_text_frame and needle in sh.text_frame.text:
            return sh
    return None


def set_single(sh, text, size=None):
    """清空全部段落 → 单段，沿用首段 pPr + 首个 rPr"""
    txBody = sh.text_frame._txBody
    ps = txBody.findall(qn('a:p'))
    pPr = copy.deepcopy(ps[0].find(qn('a:pPr'))) if ps[0].find(qn('a:pPr')) is not None else None
    rPr = None
    for p in ps:
        r = p.find(qn('a:r'))
        if r is not None and r.find(qn('a:rPr')) is not None:
            rPr = copy.deepcopy(r.find(qn('a:rPr')))
            break
    for p in ps:
        txBody.remove(p)
    p = etree.SubElement(txBody, qn('a:p'))
    if pPr is not None:
        p.append(pPr)
    r = etree.SubElement(p, qn('a:r'))
    if rPr is not None:
        r.append(rPr)
    etree.SubElement(r, qn('a:t')).text = text
    if size:
        for pp in sh.text_frame.paragraphs:
            for rr in pp.runs:
                rr.font.size = Pt(size)


def rewrite(sh, lines):
    """多段重写，沿用首段 pPr + 首个 rPr"""
    txBody = sh.text_frame._txBody
    ps = txBody.findall(qn('a:p'))
    pPr = copy.deepcopy(ps[0].find(qn('a:pPr'))) if ps[0].find(qn('a:pPr')) is not None else None
    rPr = None
    for p in ps:
        r = p.find(qn('a:r'))
        if r is not None and r.find(qn('a:rPr')) is not None:
            rPr = copy.deepcopy(r.find(qn('a:rPr')))
            break
    for p in ps:
        txBody.remove(p)
    for t in lines:
        p = etree.SubElement(txBody, qn('a:p'))
        if pPr is not None:
            p.append(copy.deepcopy(pPr))
        r = etree.SubElement(p, qn('a:r'))
        if rPr is not None:
            r.append(copy.deepcopy(rPr))
        etree.SubElement(r, qn('a:t')).text = t


def add_line(slide, x, y, w, h, text, size=10, color='8A8378', bold=False):
    tb = slide.shapes.add_textbox(Emu(int(x * EMU)), Emu(int(y * EMU)),
                                  Emu(int(w * EMU)), Emu(int(h * EMU)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.name = FONT
    r.font.color.rgb = RGBColor.from_string(color)
    rPr = r._r.get_or_add_rPr()
    for tag in ('a:latin', 'a:ea'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)
    return tb


def _fade(nid, sid, delay=0):
    return (f'<p:par><p:cTn id="{nid}" presetID="10" presetClass="entr" presetSubtype="0" '
            f'fill="hold" grpId="0" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="{nid+1}" dur="1" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr>'
            f'<p:cTn id="{nid+2}" dur="550"/>'
            f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
            f'</p:childTnLst></p:cTn></p:par>')


def regen_timing(slide, base=13000):
    ids = [sh.shape_id for sh in slide.shapes][1:]   # 跳过背景
    nid, blocks = base, []
    for sid in ids:
        nid += 3
        blocks.append('<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                      f'<p:childTnLst>{_fade(nid, sid, 0)}</p:childTnLst></p:cTn></p:par>')
    xml = ('<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
           'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
           f'<p:tnLst><p:par><p:cTn id="{base-2}" dur="indefinite" restart="never" nodeType="tmRoot">'
           '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
           f'<p:cTn id="{base-1}" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
           '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
           '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
    sld = slide._element
    old = sld.find(qn('p:timing'))
    if old is not None:
        sld.remove(old)
    sld.append(etree.fromstring(xml))


N = 0
def done(msg):
    global N; N += 1
    print('  ✓', msg)


print('=== P08 她凭什么考出 699（4 卡加厚 + 字号 10→11.5） ===')
s = 7
for old, new in [
    ('新课先自己过一遍', '新课先自己过一遍，把看不懂的地方标出来，带着问题进课堂——听课时心里有靶心，效率比边听边想高得多。这个习惯，从初中一年级一直保持到高考前，一天都没断过。'),
    ('当天的知识点当天弄懂', '当天的知识点当天弄懂，绝不把问题留到第二天。实在弄不明白，第二天一早就去办公室问老师，问懂了才回教室。在她那里，问题从不过夜，疑点从不隔天。'),
    ('错题本按题型分类', '错题本按题型分类，错一次记一次，旁边注明错因：是概念不清，还是计算失误。考前不用翻课本，只翻这一本。三年下来，这样的本子她写满了厚厚一摞。'),
    ('每周回头过一遍', '每周日晚自习，把一周的错题和笔记从头过一遍，薄弱的地方单独挑出来再刷一遍。她说，重复是最笨也最稳的办法——难的不是方法，是每天都做到。'),
]:
    sh = find(s, old)
    if sh:
        set_single(sh, new, size=11.5); done(old[:8])

print('=== P09 捷报（3 卡加厚） ===')
s = 8
for old, new in [
    ('清华招生组的电话直接打进了那间平房', '2026 年 6 月 25 日凌晨，河南放榜。清华招生组的电话，直接打进了那间平房——彼时，父亲还在工地搬砖，供她读书。'),
    ('河南物理类 699 分，韩雅平被清华大学专业组', '河南物理类 699 分，她被清华大学专业组 101 正式录取，就读「卓越医师科学家」八年制——本博连读，一路读到博士。'),
    ('不和别人比吃穿', '她说："不和别人比吃穿，学生就该比学习。"母亲的病办了残疾证，家里享受低保——她比谁都清楚，钱该怎么花。'),
]:
    sh = find(s, old)
    if sh:
        set_single(sh, new); done(old[:10])

print('=== P11 托举（3 卡加厚） ===')
s = 10
for old, new in [
    ('学校把费用都免了', '高中三年，学校把能免的费用都免了，每学期还发奖学金。她算过，"花了一点，剩下的钱都给爸妈了。"那笔钱，成了家里的生活费。'),
    ('北京大学第一医院为这个家庭提供医疗帮助', '母亲患强直性脊柱炎多年，干不了重活。北京大学第一医院主动为这个家庭提供医疗帮助——那是这个家最需要的一次托举。'),
    ('整整资助了她十二年', '她六岁那年，浙江嘉善的顾虹阿姨看到她"想上学"的眼泪，从此开始一对一资助——从小学一年级，一直供到高中毕业。'),
]:
    sh = find(s, old)
    if sh:
        set_single(sh, new); done(old[:10])

print('=== P12 接力（3 卡加厚） ===')
s = 11
for old, new in [
    ('她已去清华报到', '八月底，她去清华报到。父亲申请了助学贷款，不给爱心捐款添负担——往后的路，要让她自己走下去。'),
    ('郏县实验高中开起', '郏县实验高中开起"向韩雅平学习"主题班会。屏幕那头，她在清华宿舍与学弟学妹隔空对话，讲了自己十二年的读书路。'),
    ('一场班会，几十双眼睛被点亮', '一场班会，几十双眼睛被点亮。微光正以这种方式，继续传下去——这堂课，还没有结束。'),
]:
    sh = find(s, old)
    if sh:
        set_single(sh, new); done(old[:10])

print('=== P10 他们眼中的她（加观察行 + 重建动画） ===')
s = 9
q = find(s, '以书为梯，扛起家的希望')
if q:
    q.top = Emu(int(6.48 * EMU))
    add_line(sl[s], 0.56, 6.96, 12.22, 0.40,
             '三位老师，说的其实是同一件事：她从不需要别人推着走。这份自律，从六年级一直带到了清华园。')
    regen_timing(sl[s]); done('新增观察行并重建 26 项淡入')

print('=== P14 陈新超人物页（补第三段，恢复信息密度） ===')
s = 13
sh = find(s, '她身高不足 1 米 6')
if sh:
    sh.height = Emu(int(2.80 * EMU))
    rewrite(sh, [
        '她身高不足 1 米 6，却能把 50 公斤的化肥咬牙扛上肩。一辆手动挡的二手货车，没有空调——夏天像蒸笼，冬天手脚冻得发硬。',
        '2012 年查出肝癌早期。她红着眼眶说出接下快递点的原因——"为了挣钱治病。"每月四针干扰素，为省注射费，她跟医生学会了给自己打针。',
        '她说，过去工作是为了挣钱治病；这几年，工作早已成了服务乡亲的责任。',
    ]); done('2 段 → 3 段')

print('=== P15 铁娘子的一天（6 格各补一句） ===')
s = 14
for old, new in [
    ('起床，喂鸡', '起床，喂鸡、给家人做早饭——这是一天里唯一属于她自己家的时间'),
    ('开上那辆没有空调', '开上那辆没有空调的二手货车出发——夏天像蒸笼，冬天手脚冻得发硬'),
    ('到县城分拨中心', '到县城分拨中心，分拣、扫码、装车——她常常比工作人员到得还早'),
    ('返回水源村快递点', '返回水源村快递点，卸货、分类、上架、通知取件——额头上的汗没干过'),
    ('骑三轮车', '骑三轮车，给行动不便的老人送货上门——子女寄回的年货，也一并捎到'),
    ('收车、对账', '收车、对账，一天才算忙完——运的不只是快递，更是远方家人的牵挂'),
]:
    sh = find(s, old)
    if sh:
        set_single(sh, new, size=10.5); done(old[:8])

print('=== P16 服务站（4 卡加厚 + 卡片04 改名） ===')
s = 15
for old, new in [
    ('教老人用手机缴费', '教老人用手机缴费、操作网购退货、替留守家庭寄东西。捎东西、指路、载人都是常事——副驾驶一个月至少 20 天不空着。'),
    ('村里的老人去趟县城不容易', '老人进城一趟不容易，她每天拖货回来顺路把菜捎上——"菜比昨天的新鲜，价格还便宜"。帮老人把干菜、腊鱼腊肉寄给外地子女，也是常事。'),
    ('太苦了，她也把快递点转让过', '太苦了，她也把快递点转让过——接手的人只撑了三天就喊"太辛苦了"退了回来。她算过账：从前取个快递，要坐 15 公里的车去镇上，来回十几块。'),
    ('2021 年网湖抗洪，她像男同志一样冲在前面', '2021 年网湖抗洪，她像男同志一样冲在前面：灌沙袋、堵漏点，夜里在堤上睡帐篷守夜。村里人居环境整治，志愿者里也总有她。'),
]:
    sh = find(s, old)
    if sh:
        set_single(sh, new); done(old[:10])
t = find(s, '04 · 示范点')
if t:
    set_single(t, '04 · 上一线'); done('卡片04 标题 示范点→上一线')

print('=== P17 1700+ 数据页（恢复被我误删的一行） ===')
s = 16
sh = find(s, '第一次开车')
if sh:
    sh.height = Emu(int(1.70 * EMU))
    rewrite(sh, [
        '一辆没空调的二手厢式货车 · 10 个村 · 2.3 万群众',
        '第一次开车，40 公里开了 2 个多小时，安全到家后放声大哭',
    ]); done('恢复「10 个村 · 2.3 万群众」行')

print('=== P19 她记得的名字（4 条各扩成两行） ===')
s = 18
for old, new in [
    ('周边十个村里', '周边十个村，谁家是独居老人、谁家有残障，姓名、电话、住址她全都记得。谁家老人每月要进城买药，都是搭她的顺风车——回程，她再帮着把药拎进家门。'),
    ('老人进城一趟不容易', '每天拖货回来顺路把菜捎上，谁家要猪肝、要猪心，她心里有数。村民柯节娇说，水果等重东西拿不动，她就挨家挨户送上门——今天送的鸡棚，好几十斤。'),
    ('每次进城买三四十个馒头', '每次进城，她都买上三四十个馒头，一路分送给村里的留守老人。子女从城里寄回的衣物、文具和年货，也是她拉回山村，再一件一件送到家门口。'),
    ('车上放着一个零钱盒', '车上常年放着一个零钱盒，装着一元硬币和纸币，专为转乘公交的乡亲准备。老人不会手机支付、急着用钱，她都先垫上——钱不多，可乡亲们心里踏实。'),
]:
    sh = find(s, old)
    if sh:
        set_single(sh, new); done(old[:8])

print('=== P20 主题页（两栏各补一句） ===')
s = 19
sh = find(s, '她扛起的不只是四百个包裹')
if sh:
    rewrite(sh, ['她扛起的不只是四百个包裹，', '是十个村、两万三千人的日常。', '抗洪她第一个上，环卫她第一个到。']); done('高山栏 2→3 行')
sh = find(s, '她攒下的不只是二十八张奖状')
if sh:
    rewrite(sh, ['她攒下的不只是二十八张奖状，', '是一间平房里不肯熄灭的灯。', '那盏灯，照着她走出平房，也照着身后的人。']); done('涓流栏 2→3 行')

print('=== P21 青马之问（3 卡加厚） ===')
s = 20
for old, new in [
    ('陈新超的每一次出发', '陈新超的每一次出发，先想的都是"乡亲们还需要我"。十年邮路、两万乡亲，她把"人民"两个字，走成了一条具体的路。'),
    ('韩雅平的错题本翻到卷边', '韩雅平的错题本翻到卷边，一道题弄不懂就不肯放过。所谓天赋，不过是把预习、消化、复盘这些小事，一天不落地做到底。'),
    ('顾虹资助她十二年', '我们问自己：如果有一天有能力了，会不会也伸手拉一把身后的人？这道题，他俩已经替我们答了一半。'),
]:
    sh = find(s, old)
    if sh:
        set_single(sh, new); done(old[:10])

prs.save(DST)
print(f'\n共 {N} 处修改，已保存：{DST}')
