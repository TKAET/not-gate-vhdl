from pathlib import Path
import random
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'simulation/logisim_vectors'
DEST.mkdir(parents=True,exist_ok=True)

def write(name,header,rows):
    (DEST/(name+'.csv')).write_text(','.join(header)+'\n'+'\n'.join(','.join(map(str,r)) for r in rows)+'\n',encoding='utf-8')

write('rs_latch',['S','R','Q','Q_bar'],[(0,1,0,1),(0,0,0,1),(1,0,1,0),(0,0,1,0),(1,1,0,0),(0,1,0,1),(0,0,0,1),(1,0,1,0),(0,0,1,0)])
rng=random.Random(2024095705)
rows=[(0,1,0,1)];q=0
for _ in range(150):
    d,en=rng.randrange(2),rng.randrange(2)
    if en:q=d
    rows.append((d,en,q,1-q))
write('d_latch',['D','EN','Q','Q_bar'],rows)
rows=[(0,0,'-','-'),(0,1,0,1)];q=0;clk=1
for _ in range(100):
    clk=0; rows.append((0,clk,q,1-q))
    d=rng.randrange(2);rows.append((d,clk,q,1-q))
    clk=1;q=d;rows.append((d,clk,q,1-q))
    d=rng.randrange(2);rows.append((d,clk,q,1-q))
write('d_ff',['D','CLK','Q','Q_bar'],rows)
rows=[(0,1,0,'-','-'),(0,1,1,0,1)];q=0
for j,k in [(0,0),(1,0),(0,0),(0,1),(1,1),(1,1)]+[(rng.randrange(2),rng.randrange(2)) for _ in range(100)]:
    rows.append((j,k,0,q,1-q))
    q=(j*(1-q))|((1-k)*q)
    rows.append((j,k,1,q,1-q))
write('jk_ff',['J','K','CLK','Q','Q_bar'],rows)
# Asynchronous clear/set asserted and released at both clock levels, including both high.
rows=[];q=0;prev_clk=0
events=[(0,0,0,1),(1,0,0,0),(1,1,0,0),(0,1,1,0),(1,1,1,1),(1,1,1,0),(0,1,0,0),(0,0,0,0),(0,1,0,0)]
events += [(rng.randrange(2),rng.randrange(2),rng.randrange(2),rng.randrange(2)) for _ in range(200)]
for d,clk,s,r in events:
    # Put D and async controls in place before clock movement, preserving setup time.
    if r:q=0
    elif s:q=1
    rows.append((d,prev_clk,s,r,q,1-q))
    if r:q=0
    elif s:q=1
    elif prev_clk==0 and clk==1:q=d
    rows.append((d,clk,s,r,q,1-q));prev_clk=clk
write('d_ff_async',['D','CLK','SET','CLR','Q','Q_bar'],rows)
