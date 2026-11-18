from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "report" / "assets"
OUT_DIR = ROOT / "outputs"
PDF_PATH = OUT_DIR / "Sequential_Logic_Lab_Report.pdf"

ASSET_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


def font(size: int, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size)


def xy(text: str) -> tuple[int, int]:
    m = re.fullmatch(r"\((\d+),(\d+)\)", text)
    if not m:
        raise ValueError(text)
    return int(m.group(1)), int(m.group(2))


def attrs(comp) -> dict[str, str]:
    return {a.attrib["name"]: a.attrib.get("val", "") for a in comp.findall("a")}


def render_circuit(circ_path: Path, title: str, out_path: Path):
    root = ET.parse(circ_path).getroot()
    circuit = root.find("circuit")
    comps = list(circuit.findall("comp"))
    wires = list(circuit.findall("wire"))
    points = []
    for wire in wires:
        points.extend([xy(wire.attrib["from"]), xy(wire.attrib["to"])])
    for comp in comps:
        points.append(xy(comp.attrib["loc"]))
    min_x = min(x for x, _ in points) - 35
    max_x = max(x for x, _ in points) + 70
    min_y = min(y for _, y in points) - 35
    max_y = max(y for _, y in points) + 45
    scale = min(1.45, 1420 / (max_x - min_x))
    width = int((max_x - min_x) * scale + 80)
    height = int((max_y - min_y) * scale + 120)
    image = PILImage.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)

    def p(point):
        x, y = point
        return int((x - min_x) * scale + 40), int((y - min_y) * scale + 85)

    draw.text((width // 2, 24), title, font=font(28, True), fill="#0f172a", anchor="ma")
    draw.text((width // 2, 58), "Gate-level implementation from the submitted Logisim project", font=font(16), fill="#475569", anchor="ma")

    for wire in wires:
        a, b = p(xy(wire.attrib["from"])), p(xy(wire.attrib["to"]))
        draw.line([a, b], fill="#16803c", width=max(3, int(3 * scale)))

    endpoint_counts = {}
    for wire in wires:
        for raw in (wire.attrib["from"], wire.attrib["to"]):
            endpoint_counts[raw] = endpoint_counts.get(raw, 0) + 1
    for raw, count in endpoint_counts.items():
        if count >= 3:
            x, y = p(xy(raw))
            r = 5
            draw.ellipse((x - r, y - r, x + r, y + r), fill="#166534")

    for comp in comps:
        cx, cy = p(xy(comp.attrib["loc"]))
        name = comp.attrib["name"]
        a = attrs(comp)
        if name == "Pin":
            is_out = a.get("type") == "output" or a.get("output") == "true"
            r = 7
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#0f172a", outline="#ffffff", width=2)
            label = a.get("label", "PIN")
            anchor = "lm" if is_out else "rm"
            tx = cx + 13 if is_out else cx - 13
            draw.text((tx, cy), label, font=font(18, True), fill="#0f172a", anchor=anchor)
            continue
        if "Gate" in name:
            gate = name.replace(" Gate", "").upper()
            x0, y0 = cx - int(50 * scale), cy - int(25 * scale)
            x1, y1 = cx - int(5 * scale), cy + int(25 * scale)
            draw.rounded_rectangle((x0, y0, x1, y1), radius=12, fill="#dbeafe", outline="#1d4ed8", width=3)
            draw.text(((x0 + x1) // 2, cy), gate, font=font(14, True), fill="#1e3a8a", anchor="mm")
            if gate in {"NAND", "NOR", "NOT"}:
                r = max(4, int(5 * scale))
                draw.ellipse((cx - 2 * r, cy - r, cx, cy + r), fill="#ffffff", outline="#1d4ed8", width=2)

    image.save(out_path)


def parse_vcd(path: Path, wanted: list[str]):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    id_to_name = {}
    name_to_id = {}
    in_defs = True
    for line in lines:
        s = line.strip()
        if s == "$enddefinitions $end":
            in_defs = False
            break
        if s.startswith("$var "):
            parts = s.split()
            ident, name = parts[3], parts[4]
            if name in wanted and name not in name_to_id:
                name_to_id[name] = ident
                id_to_name[ident] = name
    changes = {name: [] for name in wanted}
    now = 0
    start = lines.index("$enddefinitions $end") + 1
    for line in lines[start:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            now = int(s[1:]) / 1_000_000.0
        elif s[0] in "01xXzZUuWwLlHh-" and s[1:] in id_to_name:
            changes[id_to_name[s[1:]]].append((now, s[0].lower()))
    max_time = max((t for values in changes.values() for t, _ in values), default=1)
    return changes, max(max_time, now)


def render_wave(vcd_path: Path, title: str, signals: list[str], out_path: Path):
    changes, max_time = parse_vcd(vcd_path, signals)
    width = 1600
    left, right, top, row_h, bottom = 190, 55, 105, 90, 75
    height = top + row_h * len(signals) + bottom
    image = PILImage.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)
    draw.text((width // 2, 25), title, font=font(28, True), fill="#0f172a", anchor="ma")
    draw.text((width // 2, 60), "GHDL self-checking simulation waveform", font=font(16), fill="#475569", anchor="ma")
    plot_w = width - left - right
    tick = 5 if max_time <= 80 else 10
    t = 0
    while t <= max_time + 0.01:
        x = left + int(plot_w * t / max_time)
        draw.line((x, top - 5, x, top + row_h * len(signals)), fill="#e2e8f0", width=2)
        draw.text((x, top + row_h * len(signals) + 12), f"{t:g}", font=font(14), fill="#475569", anchor="ma")
        t += tick
    draw.text((width - right, height - 20), "Time (ns)", font=font(15, True), fill="#334155", anchor="ra")
    palette = ["#2563eb", "#059669", "#dc2626", "#7c3aed", "#ea580c", "#0891b2"]
    for idx, name in enumerate(signals):
        y_mid = top + idx * row_h + row_h // 2
        y_hi, y_lo, y_x = y_mid - 22, y_mid + 22, y_mid
        draw.text((left - 22, y_mid), name, font=font(19, True), fill="#0f172a", anchor="rm")
        draw.line((left, y_lo + 12, width - right, y_lo + 12), fill="#f1f5f9", width=1)
        values = changes[name]
        if not values:
            continue
        current_t, current_v = values[0]
        current_y = y_hi if current_v == "1" else y_lo if current_v == "0" else y_x
        color = palette[idx % len(palette)]
        for next_t, next_v in values[1:]:
            x0 = left + int(plot_w * current_t / max_time)
            x1 = left + int(plot_w * next_t / max_time)
            next_y = y_hi if next_v == "1" else y_lo if next_v == "0" else y_x
            draw.line((x0, current_y, x1, current_y), fill=color, width=5)
            draw.line((x1, current_y, x1, next_y), fill=color, width=5)
            current_t, current_v, current_y = next_t, next_v, next_y
        x0 = left + int(plot_w * current_t / max_time)
        draw.line((x0, current_y, width - right, current_y), fill=color, width=5)
    image.save(out_path)


def scaled_image(path: Path, max_w=7.1 * inch, max_h=4.3 * inch):
    with PILImage.open(path) as img:
        w, h = img.size
    factor = min(max_w / w, max_h / h)
    return Image(str(path), width=w * factor, height=h * factor)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=34, textColor=colors.HexColor("#0f172a"), alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#475569"), alignment=TA_CENTER))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor("#1d4ed8"), spaceAfter=10, keepWithNext=0))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#0f172a"), spaceBefore=7, spaceAfter=6))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=14, textColor=colors.HexColor("#1e293b"), spaceAfter=7))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#475569")))
styles.add(ParagraphStyle(name="Captionx", parent=styles["BodyText"], fontName="Helvetica-Oblique", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#475569"), spaceBefore=4, spaceAfter=8))


def table(data, widths=None, header=True):
    cell_style = ParagraphStyle(name="table_cell", fontName="Helvetica", fontSize=8.2, leading=10.2, textColor=colors.HexColor("#0f172a"))
    head_style = ParagraphStyle(name="table_head", fontName="Helvetica-Bold", fontSize=8.2, leading=10.2, textColor=colors.white)
    wrapped = []
    for row_index, row in enumerate(data):
        wrapped.append([Paragraph(html.escape(str(value)), head_style if header and row_index == 0 else cell_style) for value in row])
    t = Table(wrapped, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(commands))
    return t


def page_decor(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.line(18 * mm, h - 15 * mm, w - 18 * mm, h - 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(18 * mm, h - 11 * mm, "Sequential Logic Lab - VHDL and Logisim")
    canvas.drawRightString(w - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


exercises = [
    {
        "title": "1. RS Latch",
        "desc": "An active-high RS latch is formed by two cross-coupled NOR gates. Set drives Q high, Reset drives Q low, and S=R=0 preserves the previous state. S=R=1 is forbidden because both outputs are forced low and releasing both inputs together can produce an unpredictable final state in real hardware.",
        "truth": [["S", "R", "Q(next)", "Operation"], ["0", "0", "Q(previous)", "Hold"], ["1", "0", "1", "Set"], ["0", "1", "0", "Reset"], ["1", "1", "0, Q_bar=0", "Forbidden"]],
        "circ": "01_rs_latch_nor.circ", "vhd": "rs_latch.vhd", "tb": "tb_rs_latch", "signals": ["s", "r", "q", "q_bar"],
        "core": "if s = '1' and r = '0' then\n    q_i <= '1'; q_bar_i <= '0';\nelsif s = '0' and r = '1' then\n    q_i <= '0'; q_bar_i <= '1';\nelsif s = '1' and r = '1' then\n    q_i <= '0'; q_bar_i <= '0';\nend if; -- 00 holds",
        "obs": "The self-checking testbench verifies Set, Hold-after-Set, Reset, Hold-after-Reset, and the forbidden input. All assertions pass at 60 ns.",
    },
    {
        "title": "2. D Latch with Enable",
        "desc": "The NAND implementation first generates active-low Set and Reset controls from D, not-D, and EN, then applies them to a cross-coupled NAND latch. When EN is high the latch is transparent; when EN is low both latch inputs are inactive and the previous Q is retained.",
        "truth": [["EN", "D", "Q(next)", "Operation"], ["0", "X", "Q(previous)", "Hold"], ["1", "0", "0", "Transparent low"], ["1", "1", "1", "Transparent high"]],
        "circ": "02_d_latch_nand.circ", "vhd": "d_latch.vhd", "tb": "tb_d_latch", "signals": ["d", "en", "q", "q_bar"],
        "core": "process (d, en)\nbegin\n    if en = '1' then\n        q_i <= d;\n    end if; -- EN=0 holds\nend process;",
        "obs": "The waveform shows D changing while EN=0 without affecting Q. With EN=1, Q follows D. Disabling EN freezes the most recently captured value. All assertions pass at 60 ns.",
    },
    {
        "title": "3. Positive-Edge D Flip-Flop",
        "desc": "The VHDL design samples D only on rising_edge(clk). The gate-level circuit is a master-slave structure made from two NAND D latches and a clock inverter. The master is transparent while CLK is low and the slave is transparent while CLK is high, so the external output changes only at the low-to-high transition.",
        "truth": [["Clock event", "D", "Q(next)", "Operation"], ["Rising edge", "0", "0", "Capture 0"], ["Rising edge", "1", "1", "Capture 1"], ["No rising edge", "X", "Q(previous)", "Hold"]],
        "circ": "03_d_flip_flop_master_slave.circ", "vhd": "d_ff.vhd", "tb": "tb_d_ff", "signals": ["clk", "d", "q", "q_bar"],
        "core": "process (clk)\nbegin\n    if rising_edge(clk) then\n        q_i <= d;\n    end if;\nend process;",
        "obs": "Q captures D at each rising edge and remains unchanged at falling edges and between edges. The self-checking simulation passes at 30 ns and continues to the 60 ns stop time.",
    },
    {
        "title": "4. Positive-Edge JK Flip-Flop",
        "desc": "The JK flip-flop provides Hold, Reset, Set, and Toggle modes. NAND gates implement D_next = J*Q_bar + not(K)*Q using feedback from the slave outputs. A NAND master-slave stage captures this next-state value on the rising clock edge. The characteristic equation also allows Set or Reset to establish a known initial state in the gate simulation.",
        "truth": [["J", "K", "Q(next)", "Operation"], ["0", "0", "Q(previous)", "Hold"], ["0", "1", "0", "Reset"], ["1", "0", "1", "Set"], ["1", "1", "not Q(previous)", "Toggle"]],
        "circ": "04_jk_flip_flop_nand.circ", "vhd": "jk_ff.vhd", "tb": "tb_jk_ff", "signals": ["clk", "j", "k", "q", "q_bar"],
        "core": "if rising_edge(clk) then\n    case j & k is\n        when \"00\" => null;\n        when \"01\" => q_i <= '0';\n        when \"10\" => q_i <= '1';\n        when \"11\" => q_i <= not q_i;\n        when others => q_i <= 'X';\n    end case;\nend if;",
        "obs": "The testbench applies all four modes. Two consecutive rising edges with J=K=1 demonstrate both toggle directions. All assertions pass at 56 ns.",
    },
    {
        "title": "5. D Flip-Flop with Asynchronous Set and Clear",
        "desc": "SET and CLR are active high and operate independently of the clock. Clear has priority. The NAND circuit forms CLR_n and PRE_n = NAND(SET, CLR_n), and applies these controls to both master and slave storage stages. Each data-enable is masked by CLR_n and PRE_n during asynchronous control, preventing normal data from conflicting with Set or Clear. Releasing either control preserves Q until a subsequent valid rising edge.",
        "truth": [["CLR", "SET", "Clock", "Q(next)", "Operation"], ["1", "X", "X", "0", "Asynchronous clear"], ["0", "1", "X", "1", "Asynchronous set"], ["0", "0", "Rising", "D", "Normal capture"], ["0", "0", "No rising", "Q(previous)", "Hold"]],
        "circ": "05_d_ff_async_set_clear.circ", "vhd": "d_ff_async.vhd", "tb": "tb_d_ff_async", "signals": ["clk", "d", "set", "clr", "q", "q_bar"],
        "core": "process (clk, set, clr)\nbegin\n    if clr = '1' then\n        q_i <= '0';\n    elsif set = '1' then\n        q_i <= '1';\n    elsif rising_edge(clk) then\n        q_i <= d;\n    end if;\nend process;",
        "obs": "CLR changes Q immediately to 0, SET changes Q immediately to 1, and CLR wins when both are asserted. After both controls are released, rising-edge D capture resumes. All assertions pass at 38 ns.",
    },
]


for idx, ex in enumerate(exercises, 1):
    ex["schematic_path"] = ASSET_DIR / f"{idx:02d}_logisim_schematic.png"
    ex["wave_path"] = ASSET_DIR / f"{idx:02d}_waveform.png"
    if not ex["schematic_path"].exists():
        raise RuntimeError('Run run_gate_checks.ps1 to generate actual Logisim images first')
    unit = Path(ex['vhd']).stem
    log = (ROOT/'simulation/logs'/f'logisim_{unit}.log').read_text(encoding='utf-8-sig')
    match = re.search(r'LOGISIM PASS: (\d+) sequential vectors; no oscillation', log)
    eq = (ROOT/'simulation/logs'/f'equivalence_{unit}.log').read_text(encoding='utf-8-sig')
    if not match or f'VECTOR EQUIVALENCE PASS: {unit}' not in eq:
        raise RuntimeError(f'Unverified circuit: {unit}')
    ex['rows'] = int(match.group(1))
    render_wave(ROOT / "simulation" / "vcd" / f"{ex['tb']}.vcd", ex["title"], ex["signals"], ex["wave_path"])


story = []
story += [Spacer(1, 38 * mm), Paragraph("Sequential Logic Lab", styles["Title2"]), Paragraph("RS Latch, D Latch, D Flip-Flop, JK Flip-Flop, and Asynchronous Set/Clear D Flip-Flop", styles["Subtitle"]), Spacer(1, 18 * mm)]
story += [table([["Implementation", "Deliverables"], ["Gate level", "Five Logisim-evolution .circ files using individual gates and feedback paths"], ["VHDL", "Five synthesizable design units plus five self-checking testbenches"], ["Verification", "GHDL synthesis, assertion-based simulation, VCD waveforms, and gate-level test procedures"]], [42 * mm, 118 * mm])]
story += [Spacer(1, 24 * mm), Paragraph("Student: HUANGZE", styles["Subtitle"]), Spacer(1, 5 * mm), Paragraph("Student ID: 2024095705", styles["Subtitle"]), Spacer(1, 5 * mm), Paragraph("Verified revision: 18 November 2026", styles["Subtitle"]), PageBreak()]

story += [Paragraph("Objectives and Method", styles["H1x"]), Paragraph("The objective is to implement and verify five fundamental sequential circuits in two equivalent forms: individual gates in Logisim and synthesizable VHDL. No pre-built latch or flip-flop components are used. Storage is created by cross-coupled gates. Same-named Logisim tunnels connect wires, including feedback nets; they contain no logic or storage.", styles["Bodyx"])]
story += [Paragraph("Tool flow", styles["H2x"]), table([["Stage", "Tool / method", "Result"], ["Gate simulation", "Actual Logisim-evolution 5.0.0 propagation engine", "All 1,194 ordered vectors pass"], ["VHDL analysis", "GHDL 6.0.0, VHDL-2008", "All design and testbench units compile"], ["Synthesis", "ghdl --synth --latches", "All five design units pass"], ["Equivalence", "Same CSV vectors independently run in Logisim and GHDL", "Matching expected Q and Q_bar on every checked row"], ["Evidence", "Native Logisim rendering, GHDL VCD and raw logs", "Included with source and test vectors"]], [26 * mm, 67 * mm, 67 * mm])]
story += [Spacer(1, 8 * mm), Paragraph("Equivalence principle", styles["H2x"]), Paragraph("Each VHDL design implements the same input/output state transition described by its gate-level circuit. Latches use incomplete assignments intentionally to retain state. Flip-flops use rising_edge(clk). The asynchronous design orders CLR before SET, which gives clear the required priority.", styles["Bodyx"])]
story += [Paragraph("Verification summary", styles["H2x"]), table([["Design", "Synthesis", "Both simulators", "Ordered vectors"], ["RS latch", "PASS", "PASS", "9"], ["D latch", "PASS", "PASS", "151"], ["D flip-flop", "PASS", "PASS", "402"], ["JK flip-flop", "PASS", "PASS", "214"], ["Async D flip-flop", "PASS", "PASS", "418"]], [43 * mm, 28 * mm, 45 * mm, 44 * mm]), Spacer(1,5*mm), Paragraph("Scope: digital functional verification after gate propagation settles. Data is made stable before clock edges. Gate power-up is not assumed; vectors establish a known state before checking it. The RS forbidden assertion is tested, but simultaneous release from that condition is not assigned a deterministic physical outcome. Device setup/hold times, metastability, and FPGA placement are outside this functional simulation.",styles['Smallx']), PageBreak()]

for ex in exercises:
    unit=Path(ex['vhd']).stem
    story += [Paragraph(ex["title"], styles["H1x"]), Paragraph(ex["desc"], styles["Bodyx"]), Paragraph("State table", styles["H2x"]), table(ex["truth"]), Spacer(1, 6 * mm), Paragraph("Synthesizable VHDL", styles["H2x"]), Paragraph(f"Source: vhdl/src/{ex['vhd']}. Complete source and testbench are in the repository.",styles['Bodyx']), Preformatted(ex["core"],ParagraphStyle(name=f"code{unit}",fontName='Courier',fontSize=9,leading=13)),PageBreak()]
    story += [Paragraph(ex["title"], styles["H1x"]), Paragraph("Native Logisim schematic",styles['H2x']),Paragraph("This figure is drawn by Logisim from the tested .circ file after propagation. Identical tunnel labels denote electrically connected nets; Q and Q_bar labels explicitly carry feedback into earlier gates.",styles['Smallx']),scaled_image(ex['schematic_path'],max_w=6.8*inch,max_h=7.2*inch),Paragraph(f"logisim/{ex['circ']} - {ex['rows']} ordered test vectors PASS; no oscillation.",styles['Captionx']),PageBreak()]
    story += [Paragraph(ex["title"],styles['H1x']),Paragraph("VHDL waveform and cross-check",styles['H2x']),scaled_image(ex['wave_path']),Paragraph(ex['obs'],styles['Captionx']),Spacer(1,6*mm),table([['Verification','Observed result'],['VHDL synthesis','PASS'],['Directed VHDL assertions','PASS'],['Logisim propagation engine',f"PASS: {ex['rows']} ordered vectors"],['GHDL with identical CSV vectors',f"PASS: {ex['rows']} rows"],['Stored evidence',f"simulation/logs/logisim_{unit}.log; equivalence_{unit}.log"]],[54*mm,106*mm]),Spacer(1,5*mm),Paragraph('Expected values in the CSV are generated from the state table, then independently checked against the native Logisim circuit and the VHDL design. A dash in an output column means that the power-up value is deliberately not assumed.',styles['Bodyx']),PageBreak()]

story += [Paragraph("Reproduction and Submission", styles["H1x"]), Paragraph("Install GHDL 6.0.0, JDK 21 or later, and Logisim-evolution 5.0.0. Run the two PowerShell scripts below from this assignment directory. The first performs VHDL analysis, synthesis and directed simulation. The second runs the actual Logisim engine and replays the same CSV vectors in GHDL. Supply -LogisimJar if Logisim is installed elsewhere.", styles["Bodyx"])]
story += [Preformatted("./scripts/run_all.ps1\n./scripts/run_gate_checks.ps1", ParagraphStyle(name="cmd", fontName="Courier-Bold", fontSize=10, leading=14)), Spacer(1, 6 * mm)]
story += [Paragraph("Manual Logisim checks", styles["H2x"]), table([["Circuit", "Inputs to apply", "Expected observation"], ["RS latch", "10, 00, 01, 00, 11", "Set, hold, reset, hold, both outputs low"], ["D latch", "Change D with EN=0; then EN=1", "Hold while disabled; Q follows D while enabled"], ["D flip-flop", "Change D between clock edges", "Q changes only at a rising edge"], ["JK flip-flop", "JK=00,10,01,11", "Hold, set, reset, toggle"], ["Async D flip-flop", "Assert CLR, SET, both; then clock D", "Immediate clear, immediate set, clear priority, normal capture"]], [40 * mm, 58 * mm, 62 * mm])]
story += [Spacer(1, 7 * mm), Paragraph("Repository checklist", styles["H2x"]), table([["Required item", "Location", "Status"], ["VHDL design files", "vhdl/src/*.vhd", "Included"], ["VHDL testbenches", "vhdl/tb/*.vhd", "Included"], ["Logisim projects", "logisim/*.circ", "Included"], ["Simulation logs and waveforms", "simulation/logs and simulation/vcd", "Included"], ["PDF report", "Sequential_Logic_Lab_Report.pdf", "Included"]], [48 * mm, 78 * mm, 34 * mm])]
story += [Spacer(1, 8 * mm), Paragraph("Conclusion", styles["H2x"]), Paragraph("All five circuits were implemented in both required forms. The VHDL units compile, synthesize, and pass self-checking simulations. The Logisim projects contain only individual logic gates, input/output pins, wires, and explicit feedback. The supplied state tables and waveforms demonstrate the required operating modes and the clear-over-set priority.", styles["Bodyx"])]

doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=20 * mm, bottomMargin=16 * mm, title="Sequential Logic Lab Report", author="HUANGZE")
doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)
print(PDF_PATH)
