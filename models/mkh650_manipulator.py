"""MKH-650 modular four-axis industrial manipulator concept assembly.

Resume/report baseline: 20 kg rated payload and 1180 mm working radius.
"""
from math import cos, radians, sin
from engineering_primitives import *

L1,L2,TOOL=520.0,480.0,180.0
Z0=520.0
A1=28.0
A2=-32.0


def industrial_joint(parts,p,r,w,prefix,motor_size):
    x,y,z=p
    parts.extend([
        cy(r,w,p,prefix+"_cast_housing",ORANGE),
        cy(r*.84,w+8,p,prefix+"_cross_roller_bearing",DARK),
        cy(r*.65,w+14,p,prefix+"_reducer_output",STEEL),
        cy(r*.3,w+20,p,prefix+"_hollow_output_shaft",DARK),
        cy(r*1.16,14,(x,y+w/2+7,z),prefix+"_output_flange",ORANGE),
        bx(motor_size,motor_size*.88,motor_size*.88,(x,y-w/2-motor_size*.55,z),prefix+"_servo_motor",DARK),
        bx(motor_size*.46,motor_size*.3,motor_size*.2,(x,y-w/2-motor_size,z+motor_size*.5),prefix+"_motor_connector",BLUE),
    ])
    bolt_circle_y(parts,(x,z),r*.91,12,y+w/2+15,prefix+"_flange_bolt",8)


def truss_link(parts,a,b,width,height,prefix):
    y=a[1]
    parts.extend([
        beam_xz((a[0],y-width*.43,a[2]),(b[0],y-width*.43,b[2]),14,height,prefix+"_left_plate",ORANGE),
        beam_xz((a[0],y+width*.43,a[2]),(b[0],y+width*.43,b[2]),14,height,prefix+"_right_plate",ORANGE),
        beam_xz(a,b,width*.62,14,prefix+"_upper_box_spine",ORANGE),
        beam_xz((a[0],y,a[2]-height*.38),(b[0],y,b[2]-height*.38),width*.62,12,prefix+"_lower_box_spine",ORANGE),
    ])
    for i,t in enumerate((.12,.25,.38,.51,.64,.77,.9),1):
        x=a[0]+(b[0]-a[0])*t; z=a[2]+(b[2]-a[2])*t
        pcolor=ORANGE if i%2 else DARK
        parts.append(bx(14,width*.78,height*.72,(x,y,z),f"{prefix}_internal_rib_{i:02d}",pcolor))
    for i,t in enumerate((.22,.48,.74),1):
        x=a[0]+(b[0]-a[0])*t; z=a[2]+(b[2]-a[2])*t
        parts.extend([cy(height*.25,16,(x,y-width*.48,z),f"{prefix}_left_access_ring_{i}",DARK),cy(height*.25,16,(x,y+width*.48,z),f"{prefix}_right_access_ring_{i}",DARK)])
    parts.append(beam_xz((a[0]+20,y,a[2]+height*.46),(b[0]-20,y,b[2]+height*.46),width*.82,10,prefix+"_service_cover",DARK))


def heavy_gripper(parts,p):
    x,y,z=p
    parts.extend([
        cx(72,22,p,"iso9409_tool_flange",STEEL),
        bx(150,180,90,(x+88,y,z),"pneumatic_gripper_body",DARK),
        bx(140,34,30,(x+170,y-64,z),"left_parallel_slide",STEEL),
        bx(140,34,30,(x+170,y+64,z),"right_parallel_slide",STEEL),
        bx(170,22,70,(x+250,y-64,z-30),"left_heavy_finger",ORANGE),
        bx(170,22,70,(x+250,y+64,z-30),"right_heavy_finger",ORANGE),
        bx(90,14,80,(x+320,y-64,z-45),"left_serrated_pad",DARK),
        bx(90,14,80,(x+320,y+64,z-45),"right_serrated_pad",DARK),
        bx(90,70,55,(x+100,y,z+76),"gripper_valve_block",BLUE),
    ])


def gen_step():
    p=[]
    # foundation and rotary base
    p.extend([
        bx(760,700,30,(0,0,15),"foundation_plate",DARK),
        bx(660,600,80,(0,0,70),"grouted_base_block",MID),
        cz(260,32,(0,0,126),"j1_anchor_flange",ORANGE),
        cz(205,260,(0,0,272),"j1_slew_housing",ORANGE),
        cz(165,272,(0,0,272),"j1_slew_bearing_envelope",DARK),
        cz(230,28,(0,0,422),"j1_output_platform",ORANGE),
        bx(260,250,230,(0,0,465),"shoulder_tower",ORANGE),
        bx(18,340,210,(-120,0,430),"tower_left_gusset",ORANGE),
        bx(18,340,210,(120,0,430),"tower_right_gusset",ORANGE),
        bx(185,175,175,(-260,0,270),"j1_servo_motor",DARK),
        bx(36,220,160,(-170,0,270),"j1_belt_guard",MID),
        bx(150,12,160,(0,-132,470),"tower_access_panel",DARK),
    ])
    bolt_circle_z(p,(0,0),225,16,125,"foundation_anchor",16)
    bolt_circle_z(p,(0,0),195,14,438,"j1_output_bolt",10)
    s=(0,0,Z0)
    e=(L1*cos(radians(A1)),0,Z0+L1*sin(radians(A1)))
    w=(e[0]+L2*cos(radians(A2)),0,e[2]+L2*sin(radians(A2)))
    industrial_joint(p,s,135,210,"j2",165)
    truss_link(p,s,e,190,210,"mkh_upper_arm")
    industrial_joint(p,e,112,180,"j3",145)
    truss_link(p,e,w,160,175,"mkh_forearm")
    # balancing linkage and cylinders
    p.extend([
        cy(52,190,(80,0,675),"balance_lower_pivot",DARK),
        beam_xz((80,-82,675),(e[0]-110,-82,e[2]+85),34,42,"balance_link_left",STEEL),
        beam_xz((80,82,675),(e[0]-110,82,e[2]+85),34,42,"balance_link_right",STEEL),
        beam_xz((-30,-105,570),(e[0]-130,-105,e[2]+30),68,80,"gas_spring_barrel",DARK),
        beam_xz((e[0]-130,-105,e[2]+30),(e[0]-40,-105,e[2]+100),28,30,"gas_spring_rod",STEEL),
    ])
    # wrist J4 and gripper
    p.extend([
        cx(94,150,w,"j4_wrist_housing",ORANGE),cx(74,165,w,"j4_planetary_reducer",DARK),
        bx(118,110,108,(w[0]-75,w[1],w[2]+118),"j4_servo_motor",DARK),
        bx(35,105,120,(w[0]-20,w[1],w[2]+80),"j4_timing_belt_cover",MID),
    ])
    heavy_gripper(p,(w[0]+85,w[1],w[2]))
    cable_chain(p,(-90,-135,560),(e[0]-20,-135,e[2]+145),24,"upper_service_chain",(26,42,15))
    cable_chain(p,(e[0],-115,e[2]+125),(w[0]-20,-105,w[2]+115),20,"forearm_service_chain",(22,36,13))
    # modular service platform and safety items
    p.extend([
        bx(420,260,18,(-360,260,285),"maintenance_platform",STEEL),
        bx(40,40,520,(-540,360,290),"platform_guard_post_1",YELLOW),
        bx(40,40,520,(-180,360,290),"platform_guard_post_2",YELLOW),
        bx(400,25,25,(-360,360,520),"platform_guard_rail",YELLOW),
        bx(180,100,230,(-470,-260,300),"j1_terminal_box",LIGHT),
        bx(130,14,170,(-470,-315,300),"terminal_box_door",MID),
        cz(25,25,(-510,-330,405),"local_emergency_stop",RED),
        bx(100,70,36,(120,150,630),"lubrication_distribution_block",BLUE),
    ])
    for i in range(8): p.append(cx(8,80,(70+i*18,150,630),f"lubrication_connector_{i+1}",STEEL))
    return assembly(p,"mkh650_modular_four_axis_manipulator")

if __name__ == "__main__": pass
