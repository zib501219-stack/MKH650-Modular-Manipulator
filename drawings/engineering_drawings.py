"""GB/ISO-style bilingual engineering drawings for the four resume projects.

The drawings are generated from the same confirmed parameter baselines as the
parametric STEP assemblies. Dimensions marked REF/参考 are layout assumptions;
fit and manufacturing dimensions are explicitly identified in notes.
"""
from __future__ import annotations
import math
from pathlib import Path
import ezdxf
import build123d as b3d
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

BLACK=7; RED=1; YELLOW=2; GREEN=3; CYAN=4; BLUE=5; MAGENTA=6

def setup(sheet='A3', title_cn='', title_en='', number='', material='见BOM / SEE BOM', scale='1:2'):
    doc=ezdxf.new('R2013', setup=True); doc.units=units.MM
    for name,color,lt in [('BORDER',BLACK,'CONTINUOUS'),('OBJECT',BLACK,'CONTINUOUS'),('HIDDEN',BLUE,'DASHED'),('CENTER',RED,'CENTER'),('DIM',CYAN,'CONTINUOUS'),('TEXT',BLACK,'CONTINUOUS'),('HATCH',GREEN,'CONTINUOUS'),('BOM',BLACK,'CONTINUOUS')]:
        if name not in doc.layers: doc.layers.add(name,color=color,linetype=lt)
    if 'CJK' not in doc.styles: doc.styles.add('CJK',font='simhei.ttf')
    m=doc.modelspace(); w,h=(594,420) if sheet=='A2' else (420,297)
    frame(m,w,h); title_block(m,w,h,title_cn,title_en,number,material,scale,sheet)
    return doc,m,w,h

def L(m,a,b,layer='OBJECT',lw=25): m.add_line(a,b,dxfattribs={'layer':layer,'lineweight':lw})
def PL(m,pts,closed=False,layer='OBJECT',lw=25): m.add_lwpolyline(pts,close=closed,dxfattribs={'layer':layer,'lineweight':lw})
def C(m,c,r,layer='OBJECT',lw=25): m.add_circle(c,r,dxfattribs={'layer':layer,'lineweight':lw})
def A(m,c,r,s,e,layer='OBJECT',lw=25): m.add_arc(c,r,s,e,dxfattribs={'layer':layer,'lineweight':lw})
def T(m,p,text,h=3.2,layer='TEXT',align='LEFT'):
    e=m.add_text(str(text),height=h,dxfattribs={'layer':layer,'style':'CJK'})
    e.set_placement(
        p,
        align={
            'LEFT': TextEntityAlignment.LEFT,
            'CENTER': TextEntityAlignment.MIDDLE_CENTER,
            'RIGHT': TextEntityAlignment.RIGHT,
        }.get(align, TextEntityAlignment.LEFT),
    )
    return e

def frame(m,w,h):
    PL(m,[(10,10),(w-10,10),(w-10,h-10),(10,h-10)],True,'BORDER',50)
    PL(m,[(15,15),(w-15,15),(w-15,h-15),(15,h-15)],True,'BORDER',25)
    for x,ch in ((w/4,'1'),(w/2,'2'),(3*w/4,'3')): T(m,(x,h-12),ch,3,'TEXT','CENTER')
    for y,ch in ((h/3,'A'),(2*h/3,'B')): T(m,(12,y),ch,3,'TEXT','CENTER'); T(m,(w-12,y),ch,3,'TEXT','CENTER')

def title_block(m,w,h,cn,en,no,mat,scale,sheet):
    x0,y0=w-195,15; x1,y1=w-15,70
    PL(m,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],True,'BORDER',35)
    for y in (y0+12,y0+24,y0+38): L(m,(x0,y),(x1,y),'BORDER')
    for x in (x0+35,x0+110,x0+145): L(m,(x,y0),(x,y0+24),'BORDER')
    T(m,(x0+4,y0+43),cn,5,'TEXT'); T(m,(x0+4,y0+34),en,3.5,'TEXT')
    T(m,(x0+3,y0+15),'图号/DWG NO.',2.6); T(m,(x0+38,y0+15),no,3)
    T(m,(x0+113,y0+15),'比例/SCALE',2.6); T(m,(x0+148,y0+15),scale,3)
    T(m,(x0+3,y0+4),'材料/MAT.',2.6); T(m,(x0+38,y0+4),mat,2.8)
    T(m,(x0+113,y0+4),'图幅/SHEET',2.6); T(m,(x0+148,y0+4),sheet,3)
    T(m,(x0+4,y0+27),'设计/DESIGN: ZIBIN LIU    日期/DATE: 2026-07-16    版本/REV: A',2.7)

def arrow(m,p,ang,layer='DIM'):
    s=2.5; a=math.radians(ang); pts=[]
    for da in (150,-150): pts.append((p[0]+s*math.cos(a+math.radians(da)),p[1]+s*math.sin(a+math.radians(da))))
    PL(m,[p,pts[0],pts[1]],True,layer,18)

def dim_h(m,x1,x2,y_obj,y_dim,text):
    L(m,(x1,y_obj),(x1,y_dim),'DIM',18); L(m,(x2,y_obj),(x2,y_dim),'DIM',18); L(m,(x1,y_dim),(x2,y_dim),'DIM',18)
    arrow(m,(x1,y_dim),0); arrow(m,(x2,y_dim),180); T(m,((x1+x2)/2,y_dim+2),text,3,'DIM','CENTER')

def dim_v(m,y1,y2,x_obj,x_dim,text):
    L(m,(x_obj,y1),(x_dim,y1),'DIM',18); L(m,(x_obj,y2),(x_dim,y2),'DIM',18); L(m,(x_dim,y1),(x_dim,y2),'DIM',18)
    arrow(m,(x_dim,y1),90); arrow(m,(x_dim,y2),-90); T(m,(x_dim+2,(y1+y2)/2),text,3,'DIM')

def center(m,c,rx=8,ry=None):
    ry=rx if ry is None else ry; L(m,(c[0]-rx,c[1]),(c[0]+rx,c[1]),'CENTER',18); L(m,(c[0],c[1]-ry),(c[0],c[1]+ry),'CENTER',18)

def leader(m,p1,p2,text): L(m,p1,p2,'DIM',18); arrow(m,p1,math.degrees(math.atan2(p2[1]-p1[1],p2[0]-p1[0]))+180); T(m,(p2[0]+2,p2[1]+2),text,3,'DIM')
def balloon(m,p,n): C(m,p,6,'BOM',25); T(m,p,str(n),3.5,'BOM','CENTER')

def notes(m,x,y,lines):
    T(m,(x,y),'技术要求 / TECHNICAL REQUIREMENTS',4,'TEXT')
    for i,s in enumerate(lines,1): T(m,(x,y-i*6),f'{i}. {s}',2.8,'TEXT')

def bom(m,x,y,rows,width=155):
    rh=7; cols=[12,58,15,35,35]; total=sum(cols)
    T(m,(x,y+5),'明细栏 / BILL OF MATERIALS',3.5,'BOM')
    for r in range(len(rows)+2): L(m,(x,y-rh*r),(x+total,y-rh*r),'BOM',18)
    xx=x
    for c in cols: L(m,(xx,y),(xx,y-rh*(len(rows)+1)),'BOM',18); xx+=c
    L(m,(x+total,y),(x+total,y-rh*(len(rows)+1)),'BOM',18)
    headers=['序号','名称/NAME','数量','材料/MAT.','备注/NOTE']
    xx=x
    for i,h in enumerate(headers): T(m,(xx+cols[i]/2,y-rh/2),h,2.3,'BOM','CENTER'); xx+=cols[i]
    for ri,row in enumerate(rows,1):
        xx=x
        for ci,val in enumerate(row): T(m,(xx+cols[ci]/2,y-rh*(ri+.5)),val,2.1,'BOM','CENTER'); xx+=cols[ci]

def first_angle_symbol(m,x,y):
    A(m,(x,y),7,90,270,'TEXT'); A(m,(x+14,y),4,90,270,'TEXT'); A(m,(x+14,y),7,-90,90,'TEXT'); L(m,(x,y-7),(x+14,y-7),'TEXT'); L(m,(x,y+7),(x+14,y+7),'TEXT'); T(m,(x+7,y-12),'第一角法/FIRST ANGLE',2.3,'TEXT','CENTER')

def ga_robot(m):
    # front view 1:4, datum at 55,120
    ox,oy=60,115; sc=.32
    PL(m,[(ox,oy),(ox+180*sc,oy),(ox+180*sc,oy+12*sc),(ox,oy+12*sc)],True)
    C(m,(ox+90*sc,oy+38*sc),28*sc); PL(m,[(ox+62*sc,oy+25*sc),(ox+118*sc,oy+25*sc),(ox+112*sc,oy+80*sc),(ox+68*sc,oy+80*sc)],True)
    s=(ox+90*sc,oy+80*sc); e=(s[0]+230*sc*.91,s[1]+230*sc*.41); w=(e[0]+190*sc*.95,e[1]-190*sc*.31)
    PL(m,[(s[0],s[1]-12),(e[0],e[1]-12),(e[0],e[1]+12),(s[0],s[1]+12)],True)
    C(m,s,17); C(m,e,15); PL(m,[(e[0],e[1]-10),(w[0],w[1]-10),(w[0],w[1]+10),(e[0],e[1]+10)],True); C(m,w,12)
    PL(m,[(w[0],w[1]-14),(w[0]+40,w[1]-14),(w[0]+40,w[1]+14),(w[0],w[1]+14)],True); L(m,(w[0]+40,w[1]-12),(w[0]+58,w[1]-20)); L(m,(w[0]+40,w[1]+12),(w[0]+58,w[1]+20))
    T(m,(145,200),'主视图 / FRONT VIEW',3,'TEXT','CENTER'); dim_h(m,ox,ox+490*sc,oy-5,oy-18,'490 工作半径/REACH'); dim_v(m,oy,oy+180*sc,ox-4,ox-20,'180 轴高/AXIS H.')
    # top and right views
    PL(m,[(55,265),(215,265),(215,330),(55,330)],True); C(m,(95,297),28); center(m,(95,297),32); PL(m,[(95,286),(210,286),(210,308),(95,308)],True); T(m,(135,337),'俯视图 / TOP VIEW',3,'TEXT','CENTER')
    PL(m,[(265,245),(420,245),(420,330),(265,330)],True); C(m,(310,285),35); center(m,(310,285),40); PL(m,[(310,270),(395,270),(395,300),(310,300)],True); T(m,(340,337),'右视图 / RIGHT VIEW',3,'TEXT','CENTER')
    for i,p in enumerate(((89,149),(113,165),(176,165),(225,149),(110,122),(190,122)),1): balloon(m,p,i)

def ga_feeding(m):
    ox,oy=45,120; sc=.31
    PL(m,[(ox,oy),(ox+450,oy),(ox+450,oy+10),(ox,oy+10)],True)
    C(m,(ox+60,oy+75),55); C(m,(ox+60,oy+75),43,'HIDDEN'); PL(m,[(ox+105,oy+70),(ox+270,oy+70),(ox+270,oy+85),(ox+105,oy+85)],True)
    PL(m,[(ox+270,oy+40),(ox+380,oy+40),(ox+380,oy+120),(ox+270,oy+120)],True); PL(m,[(ox+295,oy+120),(ox+350,oy+120),(ox+350,oy+210),(ox+295,oy+210)],True)
    PL(m,[(ox+390,oy+35),(ox+435,oy+35),(ox+435,oy+110),(ox+390,oy+110)],True)
    T(m,(270,342),'主视图 / FRONT VIEW',3,'TEXT','CENTER'); dim_h(m,ox,ox+450,oy-5,oy-18,'1480 总长/OVERALL'); dim_v(m,oy,oy+210,ox-5,ox-18,'1325 总高/HEIGHT')
    PL(m,[(55,265),(245,265),(245,345),(55,345)],True); C(m,(100,305),45); PL(m,[(145,295),(300,295),(300,315),(145,315)],True); PL(m,[(300,270),(410,270),(410,340),(300,340)],True); T(m,(230,352),'俯视图 / TOP VIEW',3,'TEXT','CENTER')
    for i,p in enumerate(((95,195),(175,195),(245,195),(330,195),(390,195),(450,195)),1): balloon(m,p,i)

def ga_mkh(m):
    ox,oy=45,110; sc=.25
    PL(m,[(ox,oy),(ox+190,oy),(ox+190,oy+15),(ox,oy+15)],True); C(m,(ox+95,oy+55),50); PL(m,[(ox+55,oy+45),(ox+135,oy+45),(ox+125,oy+120),(ox+65,oy+120)],True)
    s=(ox+95,oy+120); e=(s[0]+520*sc*.88,s[1]+520*sc*.47); w=(e[0]+480*sc*.85,e[1]-480*sc*.53)
    PL(m,[(s[0],s[1]-18),(e[0],e[1]-18),(e[0],e[1]+18),(s[0],s[1]+18)],True); C(m,s,28); C(m,e,24)
    PL(m,[(e[0],e[1]-15),(w[0],w[1]-15),(w[0],w[1]+15),(e[0],e[1]+15)],True); C(m,w,20); PL(m,[(w[0],w[1]-20),(w[0]+60,w[1]-20),(w[0]+60,w[1]+20),(w[0],w[1]+20)],True)
    dim_h(m,ox+95,ox+95+1180*sc,oy-5,oy-20,'1180 最大半径/MAX. RADIUS'); T(m,(270,355),'主视图 / FRONT VIEW',3,'TEXT','CENTER')
    C(m,(100,305),52); center(m,(100,305),58); PL(m,[(100,285),(390,285),(390,325),(100,325)],True); T(m,(245,340),'俯视图 / TOP VIEW',3,'TEXT','CENTER')
    for i,p in enumerate(((90,160),(115,185),(185,210),(300,195),(400,170),(60,125)),1): balloon(m,p,i)

def ga_pump(m):
    ox,oy=45,115; sc=.4
    PL(m,[(ox,oy),(ox+400,oy),(ox+400,oy+12),(ox,oy+12)],True); PL(m,[(ox+125,oy+30),(ox+300,oy+30),(ox+300,oy+155),(ox+125,oy+155)],True); C(m,(ox+80,oy+90),48); C(m,(ox+170,oy+85),16); C(m,(ox+215,oy+85),16); C(m,(ox+260,oy+85),16)
    PL(m,[(ox+300,oy+55),(ox+395,oy+55),(ox+395,oy+75),(ox+300,oy+75)],True); PL(m,[(ox+300,oy+125),(ox+395,oy+125),(ox+395,oy+145),(ox+300,oy+145)],True)
    T(m,(250,290),'主视图 / FRONT VIEW',3,'TEXT','CENTER'); dim_h(m,ox,ox+400,oy-3,oy-18,'1036 总长/OVERALL'); dim_v(m,oy,oy+155,ox-3,ox-18,'724 总高/HEIGHT')
    PL(m,[(55,310),(270,310),(270,370),(55,370)],True); C(m,(95,340),32); for_y=(130,175,220)
    for x in for_y: C(m,(x,340),8)
    PL(m,[(270,320),(420,320),(420,335),(270,335)],True); PL(m,[(270,350),(420,350),(420,365),(270,365)],True); T(m,(235,382),'俯视图 / TOP VIEW',3,'TEXT','CENTER')
    for i,p in enumerate(((80,150),(150,170),(205,170),(260,170),(330,150),(385,180)),1): balloon(m,p,i)

def part_plate(m,kind):
    cfg={
      'AI_UPPER':(230,80,5,[(0,0,52),(230,0,46)],'6061-T6','AI-RA-201','大臂侧板','Upper Arm Side Plate'),
      'AI_BASE':(180,180,12,[(0,0,9),(0,0,75)],'Q235B','AI-RA-101','底座安装板','Base Mounting Plate'),
      'AI_FINGER':(70,18,10,[(0,0,4),(35,0,5)],'6061-T6','AI-RA-401','模块化夹指','Modular Gripper Finger'),
      'FEED_TRACK':(620,55,8,[(0,0,0)],'SUS304','AFI-201','直线送料轨道','Linear Feeder Track'),
      'FEED_V':(90,50,34,[(0,0,0)],'GCr15','AFI-301','V形定位座','V-Block Locator'),
      'FEED_MOUNT':(180,180,18,[(0,0,8),(0,0,65)],'Q235B','AFI-302','分料安装板','Separator Mounting Plate'),
      'MKH_ARM':(520,210,14,[(0,0,70),(520,0,112)],'Q345B','MKH-201','大臂侧板','Upper Arm Side Plate'),
      'MKH_BASE':(520,520,32,[(0,0,16),(0,0,225)],'Q345B','MKH-101','基础法兰','Foundation Flange'),
      'MKH_FINGER':(320,70,22,[(0,0,12),(80,0,18)],'40Cr','MKH-401','重载夹指','Heavy Gripper Finger'),
    }[kind]
    length,width,thick,holes,mat,no,cn,en=cfg
    x0,y0=55,145; sx=min(250/length,115/width)
    PL(m,[(x0,y0),(x0+length*sx,y0),(x0+length*sx,y0+width*sx),(x0,y0+width*sx)],True)
    for i in range(4):
        hx=x0+(25 if i%2==0 else length-25)*sx; hy=y0+(20 if i<2 else width-20)*sx; C(m,(hx,hy),max(2,6*sx)); center(m,(hx,hy),6)
    if 'ARM' in kind or kind=='AI_UPPER':
        for t in (.3,.62): C(m,(x0+length*sx*t,y0+width*sx/2),width*sx*.18); center(m,(x0+length*sx*t,y0+width*sx/2),width*sx*.22)
    if 'BASE' in kind:
        for i in range(12):
            a=math.radians(i*30); C(m,(x0+length*sx/2+width*sx*.38*math.cos(a),y0+width*sx/2+width*sx*.38*math.sin(a)),3)
        center(m,(x0+length*sx/2,y0+width*sx/2),width*sx*.48)
    dim_h(m,x0,x0+length*sx,y0-2,y0-16,str(length)); dim_v(m,y0,y0+width*sx,x0-2,x0-16,str(width))
    # side/section
    sx2=0.8; xx=330; PL(m,[(xx,y0),(xx+thick*sx2,y0),(xx+thick*sx2,y0+width*sx),(xx,y0+width*sx)],True); dim_h(m,xx,xx+thick*sx2,y0-2,y0-16,str(thick))
    T(m,(180,275),'主视图 / FRONT VIEW',3,'TEXT','CENTER'); T(m,(345,275),'A-A 剖视 / SECTION A-A',3,'TEXT','CENTER')
    leader(m,(x0+25*sx,y0+20*sx),(x0-5,y0+width*sx+20),'4×通孔 / 4× THRU HOLES');
    notes(m,45,105,[f'材料：{mat} / MATERIAL: {mat}.', '未注尺寸公差按 GB/T 1804-m。', '未注形状和位置公差按 GB/T 1184-K。', '未注倒角 C1，去除毛刺和锐边。', '关键安装面表面粗糙度 Ra 1.6。'])
    return cn,en,no,mat

def pump_part(m,kind):
    if kind=='PUMP_SHAFT':
        cn,en,no,mat='偏心轴','Eccentric Shaft','EPP-201','42CrMo'; x0,y=50,200; seg=[(45,32),(50,38),(38,56),(38,38),(50,38),(45,32)]; x=x0
        for l,d in seg: PL(m,[(x,y-d/2),(x+l,y-d/2),(x+l,y+d/2),(x,y+d/2)],True); x+=l
        center(m,((x0+x)/2,y),(x-x0)/2+10,45); dim_h(m,x0,x,y-45,y-60,'266 总长/OVERALL'); dim_v(m,y-28,y+28,x0+133,x0+145,'Ø56 MAX'); leader(m,(x0+115,y+28),(x0+90,y+65),'偏心量 e=18 / ECCENTRICITY')
    elif kind=='PUMP_LINER':
        cn,en,no,mat='柱塞缸套','Cylinder Liner','EPP-301','38CrMoAl'; x0,y=80,205
        PL(m,[(x0,y-37),(x0+155,y-37),(x0+155,y+37),(x0,y+37)],True); PL(m,[(x0,y-24),(x0+155,y-24),(x0+155,y+24),(x0,y+24)],True,'HIDDEN'); center(m,(x0+77,y),90,45); C(m,(330,205),37); C(m,(330,205),24); center(m,(330,205),45)
        dim_h(m,x0,x0+155,y-40,y-55,'155'); leader(m,(330,229),(360,255),'Ø48 H7 内孔/BORE')
    else:
        cn,en,no,mat='柱塞','Plunger','EPP-302','40Cr'; x0,y=70,205
        PL(m,[(x0,y-20),(x0+215,y-20),(x0+215,y+20),(x0,y+20)],True); center(m,(x0+108,y),120,30); C(m,(350,205),20); center(m,(350,205),28); dim_h(m,x0,x0+215,y-25,y-42,'215'); dim_v(m,y-20,y+20,x0+215,x0+235,'Ø40 h6')
    T(m,(185,275),'主视图 / FRONT VIEW',3,'TEXT','CENTER'); T(m,(345,275),'端视图 / END VIEW',3,'TEXT','CENTER')
    notes(m,45,110,[f'材料：{mat} / MATERIAL: {mat}.','热处理：调质；按零件要求进行表面处理。','关键配合面表面粗糙度 Ra 0.8。','未注尺寸公差按 GB/T 1804-m。','去除锐边，清洗后涂防锈油。'])
    return cn,en,no,mat


# Detailed orthographic views generated directly from the validated STEP assemblies.
# The earlier construction sketches remain useful as lightweight fallbacks, while
# these definitions intentionally override them for the final drawing package.
_STEP_CACHE = {}


def _step_model(filename):
    path = Path(__file__).resolve().parent.parent / 'models' / filename
    key = str(path)
    if key not in _STEP_CACHE:
        _STEP_CACHE[key] = b3d.import_step(path)
    return _STEP_CACHE[key]


def _edge_polyline(edge):
    try:
        length = float(edge.length)
        if length < 0.35:
            return []
        geom = str(edge.geom_type)
        count = 2 if 'LINE' in geom else max(6, min(28, int(length / 12) + 5))
        pts = [edge.position_at(i / (count - 1)) for i in range(count)]
        result = []
        for p in pts:
            xy = (float(p.X), float(p.Y))
            if not result or math.hypot(xy[0] - result[-1][0], xy[1] - result[-1][1]) > 0.02:
                result.append(xy)
        return result
    except Exception:
        return []


def _project_edges(model, direction, up):
    bb = model.bounding_box()
    cx = (bb.min.X + bb.max.X) / 2
    cy = (bb.min.Y + bb.max.Y) / 2
    cz = (bb.min.Z + bb.max.Z) / 2
    span = max(bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z)
    origin = (cx + direction[0] * span * 8, cy + direction[1] * span * 8, cz + direction[2] * span * 8)
    visible, hidden = model.project_to_viewport(origin, up, look_at=(cx, cy, cz))
    vis = [p for edge in visible for p in [_edge_polyline(edge)] if len(p) >= 2]
    hid = [p for edge in hidden[::4] for p in [_edge_polyline(edge)] if len(p) >= 2]
    return vis, hid


def _draw_step_view(m, model, direction, up, box, title, hidden=True):
    visible, hidden_edges = _project_edges(model, direction, up)
    all_pts = [p for poly in visible for p in poly]
    if hidden:
        all_pts.extend(p for poly in hidden_edges for p in poly)
    if not all_pts:
        return
    xmin = min(p[0] for p in all_pts); xmax = max(p[0] for p in all_pts)
    ymin = min(p[1] for p in all_pts); ymax = max(p[1] for p in all_pts)
    bx, by, bw, bh = box
    scale = min(bw / max(xmax - xmin, 1), bh / max(ymax - ymin, 1)) * 0.96
    tx = bx + (bw - (xmax - xmin) * scale) / 2 - xmin * scale
    ty = by + (bh - (ymax - ymin) * scale) / 2 - ymin * scale
    for poly in visible:
        PL(m, [(x * scale + tx, y * scale + ty) for x, y in poly], False, 'OBJECT', 18)
    if hidden:
        for poly in hidden_edges:
            PL(m, [(x * scale + tx, y * scale + ty) for x, y in poly], False, 'HIDDEN', 13)
    T(m, (bx + bw / 2, by + bh + 6), title, 3.2, 'TEXT', 'CENTER')


def _detailed_ga(m, filename, overall_text, balloons):
    model = _step_model(filename)
    _draw_step_view(m, model, (0, -1, 0), (0, 0, 1), (35, 120, 355, 145), '主视图 / FRONT VIEW', True)
    _draw_step_view(m, model, (0, 0, 1), (0, 1, 0), (35, 285, 165, 82), '俯视图 / TOP VIEW', False)
    _draw_step_view(m, model, (1, 0, 0), (0, 0, 1), (220, 285, 170, 82), '右视图 / RIGHT VIEW', False)
    dim_h(m, 35, 390, 116, 106, overall_text)
    for i, p in enumerate(balloons, 1):
        balloon(m, p, i)


def ga_robot(m):
    _detailed_ga(m, 'detailed_robot_workcell.step', '1200 总体宽度（参考）/OVERALL WIDTH REF.', ((75,150),(120,205),(175,230),(235,205),(300,175),(360,150)))


def ga_feeding(m):
    _detailed_ga(m, 'automatic_feeding_inspection.step', '1480 总长（参考）/OVERALL LENGTH REF.', ((65,150),(125,185),(190,205),(255,205),(320,180),(375,150)))


def ga_mkh(m):
    _detailed_ga(m, 'mkh650_manipulator.step', '1180 最大工作半径（参考）/MAX. RADIUS REF.', ((70,145),(115,180),(175,225),(245,210),(315,175),(365,145)))


def ga_pump(m):
    _detailed_ga(m, 'eccentric_plunger_pump.step', '1036 总长（参考）/OVERALL LENGTH REF.', ((65,150),(125,185),(185,210),(250,210),(315,180),(370,150)))

GA={
 'AI_GA':('AI视觉四轴分拣机械臂总装图','AI Vision 4-Axis Robot Overall Assembly','AI-RA-000','1:4',ga_robot,[('1','底座/Base','1','Q235B',''),('2','J1模块/J1','1','ASSY',''),('3','大臂/Upper arm','1','6061',''),('4','小臂/Forearm','1','6061',''),('5','腕部/Wrist','1','ASSY',''),('6','夹爪/Gripper','1','ASSY','')]),
 'FEED_GA':('阶梯轴自动上料检测系统总装图','Stepped-Shaft Feeding Inspection Overall Assembly','AFI-000','1:5',ga_feeding,[('1','振动盘/Bowl','1','ASSY',''),('2','直线轨道/Track','1','SUS304',''),('3','分料站/Separator','1','ASSY',''),('4','检测站/Inspection','1','ASSY',''),('5','排料/Sorting','1','ASSY',''),('6','机架/Frame','1','AL','')]),
 'MKH_GA':('MKH-650四轴搬运机械手总装图','MKH-650 4-Axis Manipulator Overall Assembly','MKH-000','1:5',ga_mkh,[('1','基础/Base','1','Q345B',''),('2','J1模块/J1','1','ASSY',''),('3','大臂/Upper arm','1','Q345B',''),('4','小臂/Forearm','1','Q345B',''),('5','腕部/Wrist','1','ASSY',''),('6','夹爪/Gripper','1','ASSY','')]),
 'PUMP_GA':('偏心三柱塞泵总装图','Eccentric Triplex Plunger Pump Overall Assembly','EPP-000','1:3',ga_pump,[('1','电机/Motor','1','11 kW',''),('2','箱体/Crankcase','1','HT250',''),('3','偏心轴/Shaft','1','42CrMo',''),('4','柱塞组件/Plunger','3','ASSY',''),('5','吸入总管/Suction','1','CS',''),('6','排出总管/Discharge','1','AS','')]),
}

PART_KEYS={
 'AI_UPPER','AI_BASE','AI_FINGER','FEED_TRACK','FEED_V','FEED_MOUNT','MKH_ARM','MKH_BASE','MKH_FINGER','PUMP_SHAFT','PUMP_LINER','PUMP_PLUNGER'
}

def generate(key):
    if key in GA:
        cn,en,no,scale,fn,rows=GA[key]; doc,m,w,h=setup('A2',cn,en,no,'见明细栏 / SEE BOM',scale); fn(m); bom(m,420,390,rows); notes(m,35,95,['装配前清洗全部零件，去除毛刺和锐边。','关键法兰采用止口和圆柱销定位。','运动部件装配后手动检查全行程，不得卡滞。','紧固件按规定力矩拧紧，并作防松标记。','标注“参考”的尺寸仅用于总体布置，不作为加工依据。']); first_angle_symbol(m,380,95); return doc
    if key in PART_KEYS:
        # title data must be known before setup; use temporary drawing then update title fields by rebuilding.
        tmp=ezdxf.new('R2013');
        mapping={
          'AI_UPPER':('大臂侧板','Upper Arm Side Plate','AI-RA-201','6061-T6','1:1'), 'AI_BASE':('底座安装板','Base Mounting Plate','AI-RA-101','Q235B','1:1'), 'AI_FINGER':('模块化夹指','Modular Gripper Finger','AI-RA-401','6061-T6','2:1'),
          'FEED_TRACK':('直线送料轨道','Linear Feeder Track','AFI-201','SUS304','1:2'), 'FEED_V':('V形定位座','V-Block Locator','AFI-301','GCr15','2:1'), 'FEED_MOUNT':('分料安装板','Separator Mounting Plate','AFI-302','Q235B','1:1'),
          'MKH_ARM':('大臂侧板','Upper Arm Side Plate','MKH-201','Q345B','1:2'), 'MKH_BASE':('基础法兰','Foundation Flange','MKH-101','Q345B','1:2'), 'MKH_FINGER':('重载夹指','Heavy Gripper Finger','MKH-401','40Cr','1:2'),
          'PUMP_SHAFT':('偏心轴','Eccentric Shaft','EPP-201','42CrMo','1:1'), 'PUMP_LINER':('柱塞缸套','Cylinder Liner','EPP-301','38CrMoAl','1:1'), 'PUMP_PLUNGER':('柱塞','Plunger','EPP-302','40Cr','1:1')}
        cn,en,no,mat,scale=mapping[key]; doc,m,w,h=setup('A3',cn,en,no,mat,scale)
        if key.startswith('PUMP_'): pump_part(m,key)
        else: part_plate(m,key)
        first_angle_symbol(m,365,100); return doc
    raise KeyError(key)
