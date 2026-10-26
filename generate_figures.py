"""
CE 766: Watershed Management - Course Project
Figure 1 Generator: Site-Specific Data Synthesis & Preliminary Baseline Results
Author: Jashanpreet Singh (23B0985)
"""

import os
import math
import random
import csv

class PDFCanvas:
    def __init__(self, w=1100, h=820):
        self.w = w
        self.h = h
        self.stream = []

    def rect(self, x, y, rw, rh, fill=None, stroke=None, lw=1):
        s = ''
        if lw != 1:
            s += f'{lw:.2f} w\n'
        if fill:
            s += f'{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg\n'
        if stroke:
            s += f'{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG\n'
        s += f'{x:.2f} {y:.2f} {rw:.2f} {rh:.2f} re\n'
        if fill and stroke:
            s += 'B\n'
        elif fill:
            s += 'f\n'
        elif stroke:
            s += 'S\n'
        self.stream.append(s)

    def line(self, x1, y1, x2, y2, stroke=(0,0,0), lw=1, dash=None):
        s = ''
        if dash:
            s += f'[{dash[0]} {dash[1]}] 0 d\n'
        else:
            s += '[] 0 d\n'
        s += f'{lw:.2f} w\n'
        s += f'{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG\n'
        s += f'{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S\n'
        self.stream.append(s)

    def polyline(self, points, stroke=(0,0,0), lw=1, dash=None):
        if len(points) < 2:
            return
        s = ''
        if dash:
            s += f'[{dash[0]} {dash[1]}] 0 d\n'
        else:
            s += '[] 0 d\n'
        s += f'{lw:.2f} w\n'
        s += f'{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG\n'
        s += f'{points[0][0]:.2f} {points[0][1]:.2f} m\n'
        for pt in points[1:]:
            s += f'{pt[0]:.2f} {pt[1]:.2f} l\n'
        s += 'S\n'
        self.stream.append(s)

    def polygon(self, points, fill=None, stroke=None, lw=1):
        if len(points) < 3:
            return
        s = ''
        if lw != 1:
            s += f'{lw:.2f} w\n'
        if fill:
            s += f'{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg\n'
        if stroke:
            s += f'{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG\n'
        s += f'{points[0][0]:.2f} {points[0][1]:.2f} m\n'
        for pt in points[1:]:
            s += f'{pt[0]:.2f} {pt[1]:.2f} l\n'
        s += 'h\n'
        if fill and stroke:
            s += 'B\n'
        elif fill:
            s += 'f\n'
        elif stroke:
            s += 'S\n'
        self.stream.append(s)

    def circle(self, cx, cy, r, fill=None, stroke=None, lw=1):
        # 4-bezier approximation of a circle
        k = 0.5522847498 * r
        s = ''
        if lw != 1:
            s += f'{lw:.2f} w\n'
        if fill:
            s += f'{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg\n'
        if stroke:
            s += f'{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG\n'
        s += f'{cx + r:.2f} {cy:.2f} m\n'
        s += f'{cx + r:.2f} {cy + k:.2f} {cx + k:.2f} {cy + r:.2f} {cx:.2f} {cy + r:.2f} c\n'
        s += f'{cx - k:.2f} {cy + r:.2f} {cx - r:.2f} {cy + k:.2f} {cx - r:.2f} {cy:.2f} c\n'
        s += f'{cx - r:.2f} {cy - k:.2f} {cx - k:.2f} {cy - r:.2f} {cx:.2f} {cy - r:.2f} c\n'
        s += f'{cx + k:.2f} {cy - r:.2f} {cx + r:.2f} {cy - k:.2f} {cx + r:.2f} {cy:.2f} c\n'
        if fill and stroke:
            s += 'B\n'
        elif fill:
            s += 'f\n'
        elif stroke:
            s += 'S\n'
        self.stream.append(s)

    def text(self, x, y, txt, size=11, font='F1', color=(0,0,0)):
        txt = txt.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        s = f'BT\n/{font} {size:.1f} Tf\n{color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg\n{x:.2f} {y:.2f} Td\n({txt}) Tj\nET\n'
        self.stream.append(s)

    def get_pdf_bytes(self):
        content = ''.join(self.stream).encode('latin1')
        objs = []
        objs.append(b'<< /Type /Catalog /Pages 2 0 R >>')
        objs.append(b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>')
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.w} {self.h}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>'.encode('latin1'))
        objs.append(f'<< /Length {len(content)} >>\nstream\n'.encode('latin1') + content + b'\nendstream')
        objs.append(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
        objs.append(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')

        out = bytearray(b'%PDF-1.4\n')
        offsets = []
        for i, obj in enumerate(objs):
            offsets.append(len(out))
            out.extend(f'{i+1} 0 obj\n'.encode('latin1'))
            out.extend(obj)
            out.extend(b'\nendobj\n')

        xref_pos = len(out)
        out.extend(f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode('latin1'))
        for off in offsets:
            out.extend(f'{off:010d} 00000 n \n'.encode('latin1'))
        out.extend(f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n'.encode('latin1'))
        return bytes(out)

def build_figure():
    pdf = PDFCanvas(1100, 820)
    
    # Background
    pdf.rect(0, 0, 1100, 820, fill=(0.965, 0.970, 0.980))

    # Header Card
    pdf.rect(30, 740, 1040, 65, fill=(1, 1, 1), stroke=(0.80, 0.84, 0.90), lw=1.2)
    pdf.text(50, 778, "CE 766: Watershed Management - Data and Preliminary Results", size=17, font='F2', color=(0.10, 0.18, 0.36))
    pdf.text(50, 752, "Powai Lake Phosphorus Management: Hydro-limnological Synthesis & Baseline Model Run", size=12, font='F1', color=(0.30, 0.35, 0.45))
    pdf.text(780, 752, "Student: Jashanpreet Singh (23B0985)", size=11, font='F2', color=(0.15, 0.35, 0.60))

    # Panel coordinates
    # Col 1: x = 40 to 525 (w = 485)
    # Col 2: x = 575 to 1060 (w = 485)
    # Row 1 (top): y = 415 to 720 (h = 305)
    # Row 2 (bot): y = 45 to 385 (h = 340)

    # =========================================================================
    # PANEL (A): Historical Rainfall & Catchment Runoff (1991–2025)
    # =========================================================================
    ax_x, ax_y, ax_w, ax_h = 50, 425, 480, 290
    pdf.rect(ax_x, ax_y, ax_w, ax_h, fill=(1, 1, 1), stroke=(0.82, 0.85, 0.90), lw=1)
    pdf.text(ax_x + 15, ax_y + ax_h - 22, "(a) Catchment Hydrology & Natural P Inflow (IMD 1991-2025)", size=12, font='F2', color=(0.10, 0.20, 0.40))

    # Read rainfall data
    rf_data = []
    with open('data/imd_rainfall_powai_1991_2025.csv', 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rf_data.append({
                'year': int(r['year']),
                'rain': float(r['annual_rainfall_mm']),
                'runoff': float(r['runoff_mm']),
                'nat_p': float(r['natural_p_inflow_tons'])
            })

    # Plot area for panel A
    px_x, px_y, px_w, px_h = ax_x + 55, ax_y + 40, ax_w - 95, ax_h - 80
    pdf.rect(px_x, px_y, px_w, px_h, fill=(0.985, 0.990, 1.0), stroke=(0.75, 0.78, 0.82), lw=0.8)

    # Gridlines and Y-axis (Rainfall 0 to 4000 mm)
    for y_val in [0, 1000, 2000, 3000, 4000]:
        py = px_y + (y_val / 4000.0) * px_h
        pdf.line(px_x, py, px_x + px_w, py, stroke=(0.88, 0.90, 0.93), lw=0.6)
        pdf.text(px_x - 35, py - 4, f"{y_val}", size=9, font='F1', color=(0.35, 0.40, 0.45))
        # Right y-axis (P load 0 to 4.0 t/yr)
        p_val = (y_val / 4000.0) * 4.0
        pdf.text(px_x + px_w + 8, py - 4, f"{p_val:.1f}", size=9, font='F1', color=(0.50, 0.25, 0.10))

    pdf.text(px_x - 48, px_y + px_h / 2 - 20, "Precip / Runoff (mm)", size=9, font='F2', color=(0.20, 0.30, 0.50))
    pdf.text(px_x + px_w + 12, px_y + px_h / 2 + 35, "Natural P (t/yr)", size=9, font='F2', color=(0.60, 0.25, 0.10))

    # Draw bars for rainfall and line for runoff
    bar_w = px_w / len(rf_data) * 0.75
    runoff_pts = []
    for i, d in enumerate(rf_data):
        bx = px_x + (i + 0.15) * (px_w / len(rf_data))
        bh = (d['rain'] / 4000.0) * px_h
        pdf.rect(bx, px_y, bar_w, bh, fill=(0.55, 0.72, 0.92), stroke=(0.35, 0.55, 0.80), lw=0.5)

        rx = bx + bar_w / 2
        ry = px_y + (d['runoff'] / 4000.0) * px_h
        runoff_pts.append((rx, ry))

        # Year labels every 5 years
        if d['year'] % 5 == 0:
            pdf.text(rx - 10, px_y - 14, str(d['year']), size=8, font='F1', color=(0.3, 0.3, 0.3))

    pdf.polyline(runoff_pts, stroke=(0.10, 0.45, 0.35), lw=1.5)

    # Highlights
    pdf.text(px_x + 130, px_y + px_h - 18, "2005 Deluge (3410 mm)", size=8, font='F2', color=(0.7, 0.1, 0.1))
    pdf.text(px_x + 275, px_y + px_h - 18, "2019 Wet (3670 mm)", size=8, font='F2', color=(0.7, 0.1, 0.1))
    pdf.text(px_x + 235, px_y + 105, "2015 Drought", size=8, font='F1', color=(0.6, 0.3, 0.1))

    # Legend for Panel A
    pdf.rect(px_x + 10, px_y + px_h - 38, 125, 30, fill=(1,1,1), stroke=(0.8,0.8,0.8), lw=0.5)
    pdf.rect(px_x + 15, px_y + px_h - 22, 10, 8, fill=(0.55, 0.72, 0.92))
    pdf.text(px_x + 30, px_y + px_h - 22, "IMD Rainfall (mm)", size=8, font='F1')
    pdf.line(px_x + 15, px_y + px_h - 32, px_x + 25, px_y + px_h - 32, stroke=(0.10, 0.45, 0.35), lw=1.5)
    pdf.text(px_x + 30, px_y + px_h - 34, "SCS Runoff / P-Load", size=8, font='F1')

    # =========================================================================
    # PANEL (B): Copernicus Sentinel-2 NDCI Chlorophyll Proxy (2017–2025)
    # =========================================================================
    bx_x, bx_y, bx_w, bx_h = 570, 425, 480, 290
    pdf.rect(bx_x, bx_y, bx_w, bx_h, fill=(1, 1, 1), stroke=(0.82, 0.85, 0.90), lw=1)
    pdf.text(bx_x + 15, bx_y + bx_h - 22, "(b) Sentinel-2 NDCI Chlorophyll Proxy (2017-2025)", size=12, font='F2', color=(0.10, 0.20, 0.40))

    qpx_x, qpx_y, qpx_w, qpx_h = bx_x + 50, bx_y + 40, bx_w - 75, bx_h - 80

    # Zones: NDCI from 0.0 to 0.60
    # 0.0 to 0.10 Mesotrophic (green-tint)
    # 0.10 to 0.25 Eutrophic (amber-tint)
    # 0.25 to 0.60 Hyper-eutrophic (red-tint)
    y_eutro = qpx_y + (0.10 / 0.60) * qpx_h
    y_hyper = qpx_y + (0.25 / 0.60) * qpx_h

    pdf.rect(qpx_x, qpx_y, qpx_w, y_eutro - qpx_y, fill=(0.92, 0.98, 0.92))
    pdf.rect(qpx_x, y_eutro, qpx_w, y_hyper - y_eutro, fill=(0.99, 0.96, 0.90))
    pdf.rect(qpx_x, y_hyper, qpx_w, (qpx_y + qpx_h) - y_hyper, fill=(0.99, 0.92, 0.92))
    pdf.rect(qpx_x, qpx_y, qpx_w, qpx_h, stroke=(0.75, 0.78, 0.82), lw=0.8)

    # Threshold lines
    pdf.line(qpx_x, y_eutro, qpx_x + qpx_w, y_eutro, stroke=(0.3, 0.7, 0.3), lw=1, dash=(3, 2))
    pdf.line(qpx_x, y_hyper, qpx_x + qpx_w, y_hyper, stroke=(0.8, 0.3, 0.2), lw=1, dash=(4, 2))

    pdf.text(qpx_x + qpx_w - 110, y_eutro + 3, "Eutrophic threshold (0.10)", size=7.5, font='F1', color=(0.2, 0.5, 0.2))
    pdf.text(qpx_x + qpx_w - 130, y_hyper + 3, "Hyper-eutrophic threshold (0.25)", size=7.5, font='F2', color=(0.7, 0.2, 0.1))

    # Y ticks
    for nd in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        ny = qpx_y + (nd / 0.60) * qpx_h
        pdf.line(qpx_x, ny, qpx_x + qpx_w, ny, stroke=(0.85, 0.85, 0.85), lw=0.5)
        pdf.text(qpx_x - 30, ny - 4, f"{nd:.1f}", size=8.5, font='F1', color=(0.35, 0.40, 0.45))

    pdf.text(qpx_x - 45, qpx_y + qpx_h / 2 - 15, "NDCI Index", size=9, font='F2', color=(0.20, 0.30, 0.50))

    # Read NDCI data
    ndci_data = []
    with open('data/sentinel2_ndci_powai_2017_2025.csv', 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            ndci_data.append(float(r['ndci']))

    # Plot monthly NDCI points & line
    ndci_pts = []
    n_pts = len(ndci_data)
    for i, val in enumerate(ndci_data):
        nx = qpx_x + (i / (n_pts - 1)) * qpx_w
        ny = qpx_y + (val / 0.60) * qpx_h
        ndci_pts.append((nx, ny))
        pdf.circle(nx, ny, 1.6, fill=(0.15, 0.55, 0.30))

    pdf.polyline(ndci_pts, stroke=(0.15, 0.55, 0.30), lw=0.9)

    # Years along X-axis
    for y_idx, yr in enumerate(range(2017, 2026)):
        xx = qpx_x + (y_idx * 12 / (n_pts - 1)) * qpx_w
        pdf.text(xx - 8, qpx_y - 14, str(yr), size=8, font='F1', color=(0.3, 0.3, 0.3))

    # Annotations on blooms
    pdf.text(qpx_x + 15, qpx_y + qpx_h - 16, "Post-Monsoon Microcystis Scums (NDCI > 0.40)", size=8, font='F2', color=(0.6, 0.1, 0.1))
    pdf.text(qpx_x + 15, qpx_y + qpx_h - 28, "Summer Eichhornia (Water-Hyacinth) Proliferation", size=8, font='F1', color=(0.3, 0.4, 0.2))

    # =========================================================================
    # PANEL (C): Preliminary Baseline Simulation Run (2026–2050)
    # =========================================================================
    cx_x, cx_y, cx_w, cx_h = 50, 45, 480, 345
    pdf.rect(cx_x, cx_y, cx_w, cx_h, fill=(1, 1, 1), stroke=(0.82, 0.85, 0.90), lw=1)
    pdf.text(cx_x + 15, cx_y + cx_h - 22, "(c) Preliminary Baseline Simulation (2026-2050; No Action)", size=12, font='F2', color=(0.10, 0.20, 0.40))

    cpx_x, cpx_y, cpx_w, cpx_h = cx_x + 55, cx_y + 40, cx_w - 80, cx_h - 80
    pdf.rect(cpx_x, cpx_y, cpx_w, cpx_h, fill=(0.99, 0.99, 1.0), stroke=(0.75, 0.78, 0.82), lw=0.8)

    # Y-axis: Lake P Stock X(t) in tons (0 to 80 t)
    for p_val in [0, 10, 20, 30, 40, 50, 60, 70, 80]:
        py = cpx_y + (p_val / 80.0) * cpx_h
        pdf.line(cpx_x, py, cpx_x + cpx_w, py, stroke=(0.88, 0.90, 0.93), lw=0.6)
        pdf.text(cpx_x - 30, py - 4, f"{p_val}", size=9, font='F1', color=(0.35, 0.40, 0.45))

    pdf.text(cpx_x - 48, cpx_y + cpx_h / 2 - 25, "Lake P Stock X (tons)", size=9, font='F2', color=(0.20, 0.30, 0.50))

    # X-axis: 2025 to 2050
    for yr in range(2025, 2055, 5):
        xx = cpx_x + ((yr - 2025) / 25.0) * cpx_w
        pdf.text(xx - 10, cpx_y - 14, str(yr), size=8.5, font='F1', color=(0.3, 0.3, 0.3))

    # Read simulation summary
    sim_data = []
    with open('data/baseline_simulation_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sim_data.append({
                'year': int(r['year']),
                'mean': float(r['mean']),
                'p10': float(r['p10']),
                'p90': float(r['p90']),
                'median': float(r['median'])
            })

    # Draw shaded envelope (p10 to p90)
    poly_pts = []
    for d in sim_data:
        xx = cpx_x + ((d['year'] - 2025) / 25.0) * cpx_w
        yy = cpx_y + (d['p90'] / 80.0) * cpx_h
        poly_pts.append((xx, yy))
    for d in reversed(sim_data):
        xx = cpx_x + ((d['year'] - 2025) / 25.0) * cpx_w
        yy = cpx_y + (d['p10'] / 80.0) * cpx_h
        poly_pts.append((xx, yy))
    pdf.polygon(poly_pts, fill=(0.80, 0.88, 0.98))

    # Draw individual random replicate paths for illustration
    random.seed(101)
    for rep in range(12):
        pts = []
        X = 12.5
        for yr in range(2025, 2051):
            xx = cpx_x + ((yr - 2025) / 25.0) * cpx_w
            yy = cpx_y + (X / 80.0) * cpx_h
            pts.append((xx, yy))
            # Step
            Y = math.exp(0.704 + 0.35 * random.gauss(0, 1))
            rec = 12.0 * (X**8) / (2.4**8 + X**8)
            X = max(0.1, X + 18.0 + Y - 0.48 * X + rec)
        pdf.polyline(pts, stroke=(0.60, 0.75, 0.92), lw=0.6)

    # Draw median line
    median_pts = []
    for d in sim_data:
        xx = cpx_x + ((d['year'] - 2025) / 25.0) * cpx_w
        yy = cpx_y + (d['median'] / 80.0) * cpx_h
        median_pts.append((xx, yy))
    pdf.polyline(median_pts, stroke=(0.08, 0.22, 0.55), lw=2.2)

    # Critical threshold line (X_crit = 1.0 t)
    y_crit = cpx_y + (1.0 / 80.0) * cpx_h
    pdf.line(cpx_x, y_crit, cpx_x + cpx_w, y_crit, stroke=(0.85, 0.15, 0.15), lw=1.8, dash=(4, 2))
    pdf.text(cpx_x + 10, y_crit + 4, "Critical Eutrophication Threshold X_crit = 1.0 t (0.10 mg/L)", size=8, font='F2', color=(0.85, 0.15, 0.15))

    # Warning alert box inside panel C
    pdf.rect(cpx_x + 65, cpx_y + 110, 240, 36, fill=(1.0, 0.94, 0.94), stroke=(0.85, 0.3, 0.3), lw=0.8)
    pdf.text(cpx_x + 75, cpx_y + 132, "100% Policy Failure (100 Replicates)", size=8.5, font='F2', color=(0.75, 0.1, 0.1))
    pdf.text(cpx_x + 75, cpx_y + 118, "Eq. Stock: 67.0 t | Sediment Recycling: ~37% of Input", size=7.5, font='F1', color=(0.4, 0.15, 0.15))

    # Legend for Panel C
    pdf.rect(cpx_x + 15, cpx_y + cpx_h - 45, 175, 38, fill=(1,1,1), stroke=(0.8,0.8,0.8), lw=0.5)
    pdf.line(cpx_x + 22, cpx_y + cpx_h - 18, cpx_x + 42, cpx_y + cpx_h - 18, stroke=(0.08, 0.22, 0.55), lw=2)
    pdf.text(cpx_x + 48, cpx_y + cpx_h - 21, "Median Stock Trajectory", size=8, font='F1')
    pdf.rect(cpx_x + 22, cpx_y + cpx_h - 35, 20, 8, fill=(0.80, 0.88, 0.98))
    pdf.text(cpx_x + 48, cpx_y + cpx_h - 36, "10th - 90th Percentile Range", size=8, font='F1')

    # =========================================================================
    # PANEL (D): Non-linear Tipping Point & Bistability Hysteresis
    # =========================================================================
    dx_x, dx_y, dx_w, dx_h = 570, 45, 480, 345
    pdf.rect(dx_x, dx_y, dx_w, dx_h, fill=(1, 1, 1), stroke=(0.82, 0.85, 0.90), lw=1)
    pdf.text(dx_x + 15, dx_y + dx_h - 22, "(d) Phosphorus Flux Balance & Bistability Mechanism", size=12, font='F2', color=(0.10, 0.20, 0.40))

    dpx_x, dpx_y, dpx_w, dpx_h = dx_x + 55, dx_y + 40, dx_w - 75, dx_h - 80
    pdf.rect(dpx_x, dpx_y, dpx_w, dpx_h, fill=(0.99, 1.0, 0.99), stroke=(0.75, 0.78, 0.82), lw=0.8)

    # Flux Y-axis (0 to 40 t/yr)
    for f_val in [0, 10, 20, 30, 40]:
        fy = dpx_y + (f_val / 40.0) * dpx_h
        pdf.line(dpx_x, fy, dpx_x + dpx_w, fy, stroke=(0.88, 0.90, 0.93), lw=0.6)
        pdf.text(dpx_x - 28, fy - 4, f"{f_val}", size=9, font='F1', color=(0.35, 0.40, 0.45))

    pdf.text(dpx_x - 48, dpx_y + dpx_h / 2 - 25, "Annual P Flux (t/yr)", size=9, font='F2', color=(0.20, 0.30, 0.50))

    # X-axis: Stock X (0 to 80 tons)
    for x_val in [0, 20, 40, 60, 80]:
        xx = dpx_x + (x_val / 80.0) * dpx_w
        pdf.text(xx - 8, dpx_y - 14, str(x_val), size=8.5, font='F1', color=(0.3, 0.3, 0.3))

    pdf.text(dpx_x + dpx_w / 2 - 40, dpx_y - 28, "Lake Phosphorus Stock X (tons)", size=9, font='F2', color=(0.20, 0.30, 0.50))

    # Loss curve: L(X) = b * X = 0.48 * X
    loss_pts = []
    for x_val in range(0, 81):
        xx = dpx_x + (x_val / 80.0) * dpx_w
        loss = 0.48 * x_val
        yy = dpx_y + (loss / 40.0) * dpx_h
        loss_pts.append((xx, yy))
    pdf.polyline(loss_pts, stroke=(0.2, 0.2, 0.2), lw=1.8, dash=(3, 2))

    # Inflow curves: I(X) = a + Y_mean + r * X^q / (m^q + X^q)
    # 1. Baseline: a = 18.0 t/yr
    base_in_pts = []
    # 2. Planned 8 MLD plant: a = 10.0 t/yr
    plan_in_pts = []
    # 3. Aggressive diversion: a = 1.0 t/yr
    remed_in_pts = []

    m, q, r, Y_mean = 2.4, 8.0, 12.0, 2.1
    for step_i in range(160):
        x_val = step_i * (80.0 / 159.0)
        xx = dpx_x + (x_val / 80.0) * dpx_w
        rec = r * (x_val**q) / (m**q + x_val**q) if x_val > 0 else 0.0

        i_base = 18.0 + Y_mean + rec
        i_plan = 10.0 + Y_mean + rec
        i_remed = 1.0 + Y_mean + rec

        base_in_pts.append((xx, dpx_y + (i_base / 40.0) * dpx_h))
        plan_in_pts.append((xx, dpx_y + (i_plan / 40.0) * dpx_h))
        remed_in_pts.append((xx, dpx_y + (i_remed / 40.0) * dpx_h))

    pdf.polyline(base_in_pts, stroke=(0.85, 0.15, 0.15), lw=2.0)
    pdf.polyline(plan_in_pts, stroke=(0.90, 0.50, 0.10), lw=1.6)
    pdf.polyline(remed_in_pts, stroke=(0.10, 0.60, 0.30), lw=1.6)

    # Equilibrium attractor circles (where inflow intersects loss)
    # Baseline eq at ~67 t
    pdf.circle(dpx_x + (67.0 / 80.0) * dpx_w, dpx_y + (32.1 / 40.0) * dpx_h, 4.5, fill=(0.85, 0.15, 0.15), stroke=(0,0,0), lw=1)
    pdf.text(dpx_x + (67.0 / 80.0) * dpx_w - 75, dpx_y + (32.1 / 40.0) * dpx_h + 10, "Baseline Eq (X* ~ 67 t)", size=8, font='F2', color=(0.85, 0.15, 0.15))

    # Planned 8 MLD eq at ~50 t
    pdf.circle(dpx_x + (50.2 / 80.0) * dpx_w, dpx_y + (24.1 / 40.0) * dpx_h, 4.5, fill=(0.90, 0.50, 0.10), stroke=(0,0,0), lw=1)
    pdf.text(dpx_x + (50.2 / 80.0) * dpx_w - 65, dpx_y + (24.1 / 40.0) * dpx_h - 18, "8 MLD Eq (X* ~ 50 t)", size=8, font='F2', color=(0.80, 0.40, 0.05))

    # Aggressive oligotrophic eq at ~6.5 t
    pdf.circle(dpx_x + (6.5 / 80.0) * dpx_w, dpx_y + (3.1 / 40.0) * dpx_h, 4.5, fill=(0.10, 0.60, 0.30), stroke=(0,0,0), lw=1)
    pdf.text(dpx_x + (6.5 / 80.0) * dpx_w + 10, dpx_y + (3.1 / 40.0) * dpx_h + 2, "Aggressive Eq (Clean)", size=8, font='F2', color=(0.10, 0.55, 0.25))

    # Legend for Panel D
    pdf.rect(dpx_x + 10, dpx_y + dpx_h - 68, 190, 62, fill=(1,1,1), stroke=(0.8,0.8,0.8), lw=0.5)
    pdf.line(dpx_x + 15, dpx_y + dpx_h - 16, dpx_x + 35, dpx_y + dpx_h - 16, stroke=(0.2, 0.2, 0.2), lw=1.5, dash=(3, 2))
    pdf.text(dpx_x + 40, dpx_y + dpx_h - 19, "Loss L(X) = b*X (b=0.48)", size=7.5, font='F1')

    pdf.line(dpx_x + 15, dpx_y + dpx_h - 29, dpx_x + 35, dpx_y + dpx_h - 29, stroke=(0.85, 0.15, 0.15), lw=2)
    pdf.text(dpx_x + 40, dpx_y + dpx_h - 32, "Baseline Input (a=18.0 t/yr)", size=7.5, font='F1')

    pdf.line(dpx_x + 15, dpx_y + dpx_h - 42, dpx_x + 35, dpx_y + dpx_h - 42, stroke=(0.90, 0.50, 0.10), lw=1.8)
    pdf.text(dpx_x + 40, dpx_y + dpx_h - 45, "Planned 8 MLD STP (a=10.0 t/yr)", size=7.5, font='F1')

    pdf.line(dpx_x + 15, dpx_y + dpx_h - 55, dpx_x + 35, dpx_y + dpx_h - 55, stroke=(0.10, 0.60, 0.30), lw=1.8)
    pdf.text(dpx_x + 40, dpx_y + dpx_h - 58, "Aggressive Cut (a=1.0 t/yr)", size=7.5, font='F1')

    # Footer
    pdf.text(50, 18, "CE 766 Watershed Management Project · IIT Bombay · Generated for Moodle Milestone: Data and Preliminary Results", size=8.5, font='F1', color=(0.5, 0.55, 0.6))

    pdf_path = 'figures/figure1_preliminary_results.pdf'
    png_path = 'figures/figure1_preliminary_results.png'
    with open(pdf_path, 'wb') as f:
        f.write(pdf.get_pdf_bytes())

    os.system(f'sips -s format png {pdf_path} --out {png_path} >/dev/null')
    print(f"Figure generated successfully: {pdf_path} and {png_path}")

def build_svg():
    """Generate standalone SVG version for high-definition web display and embedding."""
    # Read datasets
    rf_data = []
    with open('data/imd_rainfall_powai_1991_2025.csv', 'r') as f:
        for r in csv.DictReader(f):
            rf_data.append(r)
    ndci_data = []
    with open('data/sentinel2_ndci_powai_2017_2025.csv', 'r') as f:
        for r in csv.DictReader(f):
            ndci_data.append(float(r['ndci']))
    sim_data = []
    with open('data/baseline_simulation_results.csv', 'r') as f:
        for r in csv.DictReader(f):
            sim_data.append(r)

    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 820" width="100%" height="100%" style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">')
    svg.append('<rect width="1100" height="820" fill="#f8fafc"/>')

    # Header Card
    svg.append('<rect x="30" y="20" width="1040" height="65" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    svg.append('<text x="50" y="46" font-size="17" font-weight="bold" fill="#0f172a">CE 766: Watershed Management - Data and Preliminary Results</text>')
    svg.append('<text x="50" y="68" font-size="12" fill="#475569">Powai Lake Phosphorus Management: Hydro-limnological Synthesis &amp; Baseline Model Run</text>')
    svg.append('<text x="780" y="58" font-size="11" font-weight="bold" fill="#1e40af">Student: Jashanpreet Singh (23B0985)</text>')

    # Panel A: (50, 105, 480, 310)
    svg.append('<rect x="50" y="105" width="480" height="310" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append('<text x="65" y="130" font-size="13" font-weight="bold" fill="#1e293b">(a) Catchment Hydrology &amp; Natural P Inflow (IMD 1991–2025)</text>')
    # Plot box
    px, py, pw, ph = 105, 155, 385, 220
    svg.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#f8fafc" stroke="#94a3b8" stroke-width="0.8"/>')
    for y_val in [0, 1000, 2000, 3000, 4000]:
        yy = py + ph - (y_val / 4000.0) * ph
        svg.append(f'<line x1="{px}" y1="{yy}" x2="{px+pw}" y2="{yy}" stroke="#e2e8f0" stroke-width="0.8"/>')
        svg.append(f'<text x="{px-35}" y="{yy+4}" font-size="9" fill="#64748b">{y_val}</text>')
        svg.append(f'<text x="{px+pw+8}" y="{yy+4}" font-size="9" fill="#9a3412">{(y_val/1000):.1f}</text>')
    svg.append(f'<text x="{px-45}" y="{py+ph/2}" font-size="9.5" font-weight="bold" fill="#334155" transform="rotate(-90 {px-45} {py+ph/2})" text-anchor="middle">Precip / Runoff (mm)</text>')
    svg.append(f'<text x="{px+pw+35}" y="{py+ph/2}" font-size="9.5" font-weight="bold" fill="#9a3412" transform="rotate(90 {px+pw+35} {py+ph/2})" text-anchor="middle">Natural P (t/yr)</text>')

    # Bars & line
    bw = (pw / len(rf_data)) * 0.72
    runoff_pts = []
    for i, r in enumerate(rf_data):
        bx = px + (i + 0.14) * (pw / len(rf_data))
        bh = (float(r['annual_rainfall_mm']) / 4000.0) * ph
        by = py + ph - bh
        svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="#93c5fd" stroke="#3b82f6" stroke-width="0.5"/>')
        rx = bx + bw/2
        ry = py + ph - (float(r['runoff_mm']) / 4000.0) * ph
        runoff_pts.append(f"{rx:.1f},{ry:.1f}")
        if int(r['year']) % 5 == 0:
            svg.append(f'<text x="{rx:.1f}" y="{py+ph+16}" font-size="8.5" fill="#475569" text-anchor="middle">{r["year"]}</text>')
    svg.append(f'<polyline points="{" ".join(runoff_pts)}" fill="none" stroke="#0f766e" stroke-width="2"/>')

    # Panel B: (570, 105, 480, 310)
    svg.append('<rect x="570" y="105" width="480" height="310" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append('<text x="585" y="130" font-size="13" font-weight="bold" fill="#1e293b">(b) Sentinel-2 NDCI Chlorophyll Proxy (2017–2025)</text>')
    qpx, qpy, qpw, qph = 620, 155, 405, 220
    y_eut = qpy + qph - (0.10 / 0.60) * qph
    y_hyp = qpy + qph - (0.25 / 0.60) * qph
    svg.append(f'<rect x="{qpx}" y="{y_eut}" width="{qpw}" height="{qpy+qph-y_eut}" fill="#f0fdf4"/>')
    svg.append(f'<rect x="{qpx}" y="{y_hyp}" width="{qpw}" height="{y_eut-y_hyp}" fill="#fffbeb"/>')
    svg.append(f'<rect x="{qpx}" y="{qpy}" width="{qpw}" height="{y_hyp-qpy}" fill="#fef2f2"/>')
    svg.append(f'<rect x="{qpx}" y="{qpy}" width="{qpw}" height="{qph}" fill="none" stroke="#94a3b8" stroke-width="0.8"/>')
    svg.append(f'<line x1="{qpx}" y1="{y_eut}" x2="{qpx+qpw}" y2="{y_eut}" stroke="#16a34a" stroke-width="1.2" stroke-dasharray="4,3"/>')
    svg.append(f'<line x1="{qpx}" y1="{y_hyp}" x2="{qpx+qpw}" y2="{y_hyp}" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="4,3"/>')
    svg.append(f'<text x="{qpx+qpw-130}" y="{y_hyp-4}" font-size="8" font-weight="bold" fill="#dc2626">Hyper-eutrophic threshold (0.25)</text>')
    svg.append(f'<text x="{qpx+qpw-110}" y="{y_eut-4}" font-size="8" fill="#16a34a">Eutrophic threshold (0.10)</text>')

    for nd in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        ny = qpy + qph - (nd / 0.60) * qph
        svg.append(f'<line x1="{qpx}" y1="{ny}" x2="{qpx+qpw}" y2="{ny}" stroke="#e2e8f0" stroke-width="0.8"/>')
        svg.append(f'<text x="{qpx-26}" y="{ny+3}" font-size="8.5" fill="#64748b">{nd:.1f}</text>')
    svg.append(f'<text x="{qpx-35}" y="{qpy+qph/2}" font-size="9.5" font-weight="bold" fill="#334155" transform="rotate(-90 {qpx-35} {qpy+qph/2})" text-anchor="middle">Sentinel-2 NDCI</text>')

    nd_pts = []
    for i, val in enumerate(ndci_data):
        nx = qpx + (i / (len(ndci_data) - 1)) * qpw
        ny = qpy + qph - (val / 0.60) * qph
        nd_pts.append(f"{nx:.1f},{ny:.1f}")
        svg.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="2" fill="#047857"/>')
    svg.append(f'<polyline points="{" ".join(nd_pts)}" fill="none" stroke="#059669" stroke-width="1.2"/>')
    for y_idx, yr in enumerate(range(2017, 2026)):
        xx = qpx + (y_idx * 12 / (len(ndci_data) - 1)) * qpw
        svg.append(f'<text x="{xx:.1f}" y="{qpy+qph+16}" font-size="8.5" fill="#475569" text-anchor="middle">{yr}</text>')

    # Panel C: (50, 440, 480, 335)
    svg.append('<rect x="50" y="440" width="480" height="335" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append('<text x="65" y="465" font-size="13" font-weight="bold" fill="#1e293b">(c) Preliminary Baseline Simulation (2026–2050; No Action)</text>')
    cpx, cpy, cpw, cph = 105, 490, 395, 235
    svg.append(f'<rect x="{cpx}" y="{cpy}" width="{cpw}" height="{cph}" fill="#f8fafc" stroke="#94a3b8" stroke-width="0.8"/>')
    for p_val in [0, 10, 20, 30, 40, 50, 60, 70, 80]:
        py = cpy + cph - (p_val / 80.0) * cph
        svg.append(f'<line x1="{cpx}" y1="{py}" x2="{cpx+cpw}" y2="{py}" stroke="#e2e8f0" stroke-width="0.8"/>')
        svg.append(f'<text x="{cpx-24}" y="{py+3}" font-size="8.5" fill="#64748b">{p_val}</text>')
    svg.append(f'<text x="{cpx-38}" y="{cpy+cph/2}" font-size="9.5" font-weight="bold" fill="#334155" transform="rotate(-90 {cpx-38} {cpy+cph/2})" text-anchor="middle">Lake P Stock X (tons)</text>')

    poly_top = []
    poly_bot = []
    med_pts = []
    for d in sim_data:
        xx = cpx + ((int(d['year']) - 2025) / 25.0) * cpw
        yt = cpy + cph - (float(d['p90']) / 80.0) * cph
        yb = cpy + cph - (float(d['p10']) / 80.0) * cph
        ym = cpy + cph - (float(d['median']) / 80.0) * cph
        poly_top.append(f"{xx:.1f},{yt:.1f}")
        poly_bot.insert(0, f"{xx:.1f},{yb:.1f}")
        med_pts.append(f"{xx:.1f},{ym:.1f}")
    svg.append(f'<polygon points="{" ".join(poly_top + poly_bot)}" fill="#bfdbfe" opacity="0.6"/>')
    svg.append(f'<polyline points="{" ".join(med_pts)}" fill="none" stroke="#1e3a8a" stroke-width="2.5"/>')
    ycrit = cpy + cph - (1.0 / 80.0) * cph
    svg.append(f'<line x1="{cpx}" y1="{ycrit}" x2="{cpx+cpw}" y2="{ycrit}" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="5,3"/>')
    svg.append(f'<text x="{cpx+10}" y="{ycrit-6}" font-size="8.5" font-weight="bold" fill="#dc2626">Critical Eutrophication Threshold X_crit = 1.0 t (0.10 mg/L)</text>')
    for yr in range(2025, 2055, 5):
        xx = cpx + ((yr - 2025) / 25.0) * cpw
        svg.append(f'<text x="{xx:.1f}" y="{cpy+cph+16}" font-size="8.5" fill="#475569" text-anchor="middle">{yr}</text>')

    # Panel D: (570, 440, 480, 335)
    svg.append('<rect x="570" y="440" width="480" height="335" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append('<text x="585" y="465" font-size="13" font-weight="bold" fill="#1e293b">(d) Phosphorus Flux Balance &amp; Bistability Mechanism</text>')
    dpx, dpy, dpw, dph = 620, 490, 405, 235
    svg.append(f'<rect x="{dpx}" y="{dpy}" width="{dpw}" height="{dph}" fill="#f8fafc" stroke="#94a3b8" stroke-width="0.8"/>')
    for f_val in [0, 10, 20, 30, 40]:
        fy = dpy + dph - (f_val / 40.0) * dph
        svg.append(f'<line x1="{dpx}" y1="{fy}" x2="{dpx+dpw}" y2="{fy}" stroke="#e2e8f0" stroke-width="0.8"/>')
        svg.append(f'<text x="{dpx-22}" y="{fy+3}" font-size="8.5" fill="#64748b">{f_val}</text>')
    svg.append(f'<text x="{dpx-38}" y="{dpy+dph/2}" font-size="9.5" font-weight="bold" fill="#334155" transform="rotate(-90 {dpx-38} {dpy+dph/2})" text-anchor="middle">Annual P Flux (t/yr)</text>')
    for x_val in [0, 20, 40, 60, 80]:
        xx = dpx + (x_val / 80.0) * dpw
        svg.append(f'<text x="{xx:.1f}" y="{dpy+dph+16}" font-size="8.5" fill="#475569" text-anchor="middle">{x_val}</text>')
    svg.append(f'<text x="{dpx+dpw/2}" y="{dpy+dph+28}" font-size="9.5" font-weight="bold" fill="#334155" text-anchor="middle">Lake Phosphorus Stock X (tons)</text>')

    # Curves
    loss_pts = [f"{dpx:.1f},{dpy+dph:.1f}", f"{dpx+dpw:.1f},{dpy+dph-(0.48*80/40.0)*dph:.1f}"]
    svg.append(f'<polyline points="{" ".join(loss_pts)}" fill="none" stroke="#334155" stroke-width="1.8" stroke-dasharray="4,3"/>')

    base_in, plan_in, cut_in = [], [], []
    for step in range(160):
        x = step * (80.0 / 159.0)
        rec = 12.0 * (x**8) / (2.4**8 + x**8) if x > 0 else 0.0
        xx = dpx + (x / 80.0) * dpw
        yb = dpy + dph - ((18.0 + 2.1 + rec) / 40.0) * dph
        yp = dpy + dph - ((10.0 + 2.1 + rec) / 40.0) * dph
        yc = dpy + dph - ((1.0 + 2.1 + rec) / 40.0) * dph
        base_in.append(f"{xx:.1f},{yb:.1f}")
        plan_in.append(f"{xx:.1f},{yp:.1f}")
        cut_in.append(f"{xx:.1f},{yc:.1f}")

    svg.append(f'<polyline points="{" ".join(base_in)}" fill="none" stroke="#dc2626" stroke-width="2.2"/>')
    svg.append(f'<polyline points="{" ".join(plan_in)}" fill="none" stroke="#f59e0b" stroke-width="1.8"/>')
    svg.append(f'<polyline points="{" ".join(cut_in)}" fill="none" stroke="#16a34a" stroke-width="1.8"/>')

    # Attractor markers
    eq_base_x = dpx + (67.0 / 80.0) * dpw
    eq_base_y = dpy + dph - (32.1 / 40.0) * dph
    svg.append(f'<circle cx="{eq_base_x:.1f}" cy="{eq_base_y:.1f}" r="5" fill="#dc2626" stroke="#000000" stroke-width="1.2"/>')
    svg.append(f'<text x="{eq_base_x-90:.1f}" y="{eq_base_y-8:.1f}" font-size="8.5" font-weight="bold" fill="#dc2626">Baseline Eq (X* ~ 67 t)</text>')

    svg.append('</svg>')

    svg_path = 'figures/figure1_preliminary_results.svg'
    with open(svg_path, 'w') as f:
        f.write('\n'.join(svg))
    print(f"SVG generated successfully: {svg_path}")

if __name__ == '__main__':
    build_figure()
    build_svg()
