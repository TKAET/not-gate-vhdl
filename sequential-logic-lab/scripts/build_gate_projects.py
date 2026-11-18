"""Build native Logisim gate projects with explicit, labelled net connections.

Same-named Tunnel components are wires, not storage or logic primitives. Each
gate input/output is wired to a named net. All storage comes from NAND/NOR
feedback. Gates use verified Logisim-evolution port geometry.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def project(path, pins, gates):
    root = ET.Element('project', source='5.0.0', version='1.0')
    for i, lib in [('0', '#Wiring'), ('1', '#Gates'), ('9', '#Base')]:
        ET.SubElement(root, 'lib', name=i, desc=lib)
    ET.SubElement(root, 'main', name='main')
    options = ET.SubElement(root, 'options')
    for name, val in [('gateUndefined', 'ignore'), ('simlimit', '1000'), ('simrand', '0')]:
        ET.SubElement(options, 'a', name=name, val=val)
    ET.SubElement(root, 'mappings')
    toolbar = ET.SubElement(root, 'toolbar')
    for name in ['Poke Tool', 'Edit Tool']:
        ET.SubElement(toolbar, 'tool', lib='9', name=name)
    c = ET.SubElement(root, 'circuit', name='main')
    ET.SubElement(c, 'a', name='appearance', val='logisim_evolution')

    def comp(lib, name, x, y, **attrs):
        el = ET.SubElement(c, 'comp', lib=lib, name=name, loc=f'({x},{y})')
        for k, v in attrs.items():
            ET.SubElement(el, 'a', name=k, val=str(v))
        return el

    def wire(x1, y1, x2, y2):
        assert x1 == x2 or y1 == y2
        ET.SubElement(c, 'wire', {'from': f'({x1},{y1})', 'to': f'({x2},{y2})'})

    for name, output, x, y in pins:
        comp('0', 'Pin', x, y, facing='west' if output else 'east', type='output' if output else 'input', label=name, appearance='classic', labelfont='SansSerif bold 12')
        tx = x-50 if output else x+50
        wire(x, y, tx, y)
        comp('0', 'Tunnel', tx, y, facing='east' if output else 'west', label=name, labelfont='SansSerif plain 12')

    for ref, kind, x, y, inputs, output in gates:
        attrs = {'size': '30' if kind == 'NOT' else '50'}
        if kind != 'NOT':
            attrs['inputs'] = str(len(inputs))
        comp('1', kind + ' Gate', x, y, **attrs)
        offsets = [0] if kind == 'NOT' else [-20, 20] if len(inputs) == 2 else [-20, 0, 20]
        gate_left = x - (30 if kind == 'NOT' else 60)
        for net, off in zip(inputs, offsets):
            wire(gate_left-40, y+off, gate_left, y+off)
            comp('0', 'Tunnel', gate_left-40, y+off, facing='east', label=net, labelfont='SansSerif plain 12')
        wire(x, y, x+50, y)
        comp('0', 'Tunnel', x+50, y, facing='west', label=output, labelfont='SansSerif plain 12')

    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding='UTF-8', xml_declaration=True)


def d_pair(prefix, enable, data, inv_data, x, y, async_controls=False):
    sn, rn = prefix+'S_n', prefix+'R_n'
    q, qb = prefix+'Q', prefix+'Q_bar'
    # Mask data gating while async controls are active: CLR_n * PRE_n = normal.
    en = prefix+'EN' if async_controls else enable
    gates=[]
    if async_controls:
        gates += [(prefix+'ENn', 'NAND', x, y+240, [enable,'CLR_n','PRE_n'], prefix+'EN_n'),
                  (prefix+'EN', 'NAND', x+280, y+240, [prefix+'EN_n',prefix+'EN_n'],en)]
    gates += [(prefix+'S', 'NAND', x,y,[data,en],sn),
              (prefix+'R', 'NAND', x,y+120,[inv_data,en],rn),
              (prefix+'Q', 'NAND',x+280,y,[sn,qb]+(['PRE_n'] if async_controls else []),q),
              (prefix+'QB','NAND',x+280,y+120,[rn,q]+(['CLR_n'] if async_controls else []),qb)]
    return gates


def build_all():
    project(ROOT/'logisim/01_rs_latch_nor.circ', [('S',False,100,80),('R',False,100,160),('Q',True,900,80),('Q_bar',True,900,160)],
            [('U1','NOR',400,300,['R','Q_bar'],'Q'),('U2','NOR',700,300,['S','Q'],'Q_bar')])
    project(ROOT/'logisim/02_d_latch_nand.circ', [('D',False,100,80),('EN',False,100,160),('Q',True,1000,80),('Q_bar',True,1000,160)],
            [('INV','NAND',340,300,['D','D'],'D_n'),('S','NAND',620,300,['D','EN'],'S_n'),('R','NAND',620,440,['D_n','EN'],'R_n'),('Q','NAND',900,300,['S_n','Q_bar'],'Q'),('QB','NAND',900,440,['R_n','Q'],'Q_bar')])
    dff=[('DIN','NAND',300,280,['D','D'],'D_n'),('CLKINV','NOT',300,420,['CLK'],'CLK_n')]
    dff+=d_pair('M_', 'CLK_n','D','D_n',580,280)
    dff+=d_pair('', 'CLK','M_Q','M_Q_bar',580,600)
    project(ROOT/'logisim/03_d_flip_flop_master_slave.circ', [('D',False,100,80),('CLK',False,100,160),('Q',True,1000,80),('Q_bar',True,1000,160)],dff)
    # NAND realization of the characteristic equation D_next=J*Q_bar+not(K)*Q.
    # This arrangement can establish a known state through JK=01/10 even when
    # simulation starts with an unknown Q; the disabled term is forced inactive.
    jk=[('CLKINV','NAND',300,320,['CLK','CLK'],'CLK_n'),
        ('KINV','NAND',300,460,['K','K'],'K_n'),
        ('JTERM','NAND',580,320,['J','Q_bar'],'JQ_n'),
        ('KTERM','NAND',580,460,['K_n','Q'],'KQ_n'),
        ('NEXT','NAND',860,320,['JQ_n','KQ_n'],'D_next'),
        ('NEXTINV','NAND',860,460,['D_next','D_next'],'D_next_n')]
    jk+=d_pair('M_','CLK_n','D_next','D_next_n',580,620)
    jk+=d_pair('', 'CLK','M_Q','M_Q_bar',580,940)
    project(ROOT/'logisim/04_jk_flip_flop_nand.circ', [('J',False,100,80),('K',False,100,150),('CLK',False,100,220),('Q',True,1000,80),('Q_bar',True,1000,150)],jk)
    async_gates=[('DIN','NAND',300,320,['D','D'],'D_n'),('CLKINV','NAND',300,460,['CLK','CLK'],'CLK_n'),
                 ('CLRINV','NAND',300,800,['CLR','CLR'],'CLR_n'),('PRIORITY','NAND',300,940,['SET','CLR_n'],'PRE_n')]
    async_gates+=d_pair('M_','CLK_n','D','D_n',580,320,True)
    async_gates+=d_pair('','CLK','M_Q','M_Q_bar',580,760,True)
    project(ROOT/'logisim/05_d_ff_async_set_clear.circ', [('D',False,100,80),('CLK',False,100,140),('SET',False,100,200),('CLR',False,100,260),('Q',True,1000,80),('Q_bar',True,1000,140)],async_gates)


if __name__=='__main__':
    build_all()
