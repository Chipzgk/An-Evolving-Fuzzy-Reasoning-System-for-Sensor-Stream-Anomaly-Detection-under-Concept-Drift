"""Smart Factory Monitoring — Evolving Fuzzy Reasoning System (demo).

Run:  streamlit run app.py

Five screens (plan "Demo dự kiến"):
 1. Live stream: sensors, anomaly score, system status
 2. Simulated environment change -> concept drift detected (ADWIN)
 3. Evolving fuzzy: membership functions before/after, rule base
 4. Static vs Evolving: performance before/after drift, recovery
 5. Explainability: memberships -> fired rules -> anomaly score
All numbers are computed live with src/ (same pipeline as notebooks 09-13).
Ground-truth labels are shown for evaluation only; the system never uses them.
"""
from __future__ import annotations

import os
import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data import (GRADUAL_DRIFT_END, GRADUAL_DRIFT_START, SUDDEN_DRIFT_POINT,
                      SENSOR_COLUMNS, add_gaussian_noise, load_dataset,
                      make_scenarios, train_sensor_std)
from src.evaluation import evaluate
from src.evolving import PrequentialRunner
from src.fuzzy import (OUTPUT_UNIVERSE, RULES, STATIC_GRID_MFS, TAU, TERMS,
                       UNIVERSES, FuzzySystem, format_rule, sample_values)

st.set_page_config(page_title="Smart Factory — Evolving Fuzzy Monitor", layout="wide")

# categorical slots (validated reference palette) + reserved status colors
C_STATIC, C_EVOLVING, C_CONTROL = "#2a78d6", "#eb6834", "#1baf7a"
C_GOOD, C_CRIT, C_MUTED = "#0ca30c", "#d03b3b", "#8a8984"
TERM_COLORS = {"low": "#2a78d6", "medium": "#1baf7a", "high": "#eb6834"}
VAR_LABEL = {"air_temp": "Air temperature [K]", "process_temp": "Process temperature [K]",
             "rpm": "Rotational speed [rpm]", "torque": "Torque [Nm]", "tool_wear": "Tool wear [min]"}
ONSET = {"Control": None, "Sudden Drift": SUDDEN_DRIFT_POINT, "Gradual Drift": GRADUAL_DRIFT_START}


# ---------------------------------------------------------------- data
@st.cache_data(show_spinner="Đang chạy luồng prequential (Static + Evolving)…")
def simulate(scenario: str, noise: float, seed: int):
    df = load_dataset()
    sc = make_scenarios(df)
    stream = sc[scenario]
    if noise > 0:
        stream = add_gaussian_noise(stream, noise, train_sensor_std(df), seed=seed)
    out = {}
    for model in ["Static", "Evolving"]:
        r = PrequentialRunner(evolve=(model == "Evolving"))
        log = r.run(stream)
        out[model] = {"log": log, "events": r.events, "grid": r.grid_mfs}
    ctrl = PrequentialRunner(evolve=False).run(sc["Control"])
    return stream, out, ctrl


def event_time(events, name):
    return next((e["t"] for e in events if e["event"] == name), None)


def fis_at(model, t, res):
    """Knowledge the system actually used to score sample t (test-then-adapt)."""
    ad = event_time(res[model]["events"], "adapted")
    if model == "Evolving" and ad is not None and t > ad:
        return FuzzySystem(res[model]["grid"]), True
    return FuzzySystem(), False


def base_layout(fig, height=260, title=None, ytitle=None, xtitle="Stream index t"):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=40 if title else 10, b=10),
                      title=title, legend=dict(orientation="h", y=1.12, x=0),
                      hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(title=xtitle, showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(title=ytitle, showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    return fig


def vline(fig, x, text, color, dash="dash"):
    if x is not None:
        fig.add_vline(x=x, line=dict(color=color, dash=dash, width=1.5),
                      annotation_text=text, annotation_position="top left", annotation_font_size=11)


# ---------------------------------------------------------------- sidebar
ss = st.session_state
ss.setdefault("t_slider", int(os.environ.get("DEMO_T", 1100)))  # start position of the demo
if ss.get("advance"):
    ss["t_slider"] = min(1999, ss["t_slider"] + ss.get("step", 25))
    ss["advance"] = False

st.sidebar.title("Smart Factory Monitor")
scenario = st.sidebar.selectbox("Kịch bản luồng", ["Sudden Drift", "Gradual Drift", "Control"],
                                help="Drift là mô phỏng có kiểm soát (RPM −150, Torque +8), không phải drift tự nhiên của AI4I.")
noise = st.sidebar.select_slider("Nhiễu cảm biến (σ × std train)", [0.0, 0.05, 0.1, 0.2, 0.3], value=0.0)
seed = st.sidebar.number_input("Seed nhiễu", 0, 99, 0, disabled=noise == 0)
view_model = st.sidebar.radio("Hệ đang vận hành", ["Evolving", "Static"], horizontal=True)
t = st.sidebar.slider("Thời điểm t (mẫu)", 0, 1999, key="t_slider")
c1, c2 = st.sidebar.columns(2)
playing = c1.toggle("▶ Phát", value=False)
ss["step"] = c2.selectbox("Bước", [10, 25, 50, 100], index=1, label_visibility="collapsed")
st.sidebar.caption(f"τ = {TAU} (chọn trên Validation) · W = 200 · ADWIN δ = 0.002")

stream, res, ctrl = simulate(scenario, float(noise), int(seed))
log = res[view_model]["log"]
det = event_time(res["Evolving"]["events"], "drift_detected")
adapt = event_time(res["Evolving"]["events"], "adapted")
onset = ONSET[scenario]

tabs = st.tabs(["1 · Giám sát luồng", "2 · Concept drift", "3 · Evolving fuzzy",
                "4 · Static vs Evolving", "5 · Explainability"])

# ---------------------------------------------------------------- 1. live
with tabs[0]:
    row = stream.iloc[t]
    rec = log.iloc[t]
    anomaly = bool(rec.pred)
    st.subheader(f"Mẫu t = {t}  ·  UDI {int(row.UDI)}  ·  hệ {view_model}")
    cols = st.columns(7)
    cols[0].metric("Air temp [K]", f"{row[SENSOR_COLUMNS['air_temp']]:.1f}")
    cols[1].metric("Process temp [K]", f"{row[SENSOR_COLUMNS['process_temp']]:.1f}")
    cols[2].metric("RPM", f"{row[SENSOR_COLUMNS['rpm']]:.0f}")
    cols[3].metric("Torque [Nm]", f"{row[SENSOR_COLUMNS['torque']]:.1f}")
    cols[4].metric("Tool wear [min]", f"{row[SENSOR_COLUMNS['tool_wear']]:.0f}")
    cols[5].metric("Anomaly score", f"{rec.score:.3f}", help=f"Cảnh báo khi score ≥ τ = {TAU}")
    status = ("⚠ ANOMALY", C_CRIT) if anomaly else ("✓ NORMAL", C_GOOD)
    cols[6].markdown(f"<div style='border:2px solid {status[1]};border-radius:8px;padding:10px;text-align:center;"
                     f"font-weight:700;color:{status[1]};margin-top:8px'>{status[0]}</div>", unsafe_allow_html=True)
    if rec.label == 1:
        st.caption("Ground truth: mẫu này là **Machine failure** (chỉ hiển thị để đánh giá; hệ thống không dùng nhãn).")

    lo = max(0, t - 300)
    w = log.iloc[lo:t + 1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=w.t, y=w.score, name="Anomaly score", line=dict(color=C_EVOLVING if view_model == "Evolving" else C_STATIC, width=2)))
    alarms = w[w.pred == 1]
    fig.add_trace(go.Scatter(x=alarms.t, y=alarms.score, mode="markers", name="Cảnh báo (score ≥ τ)",
                             marker=dict(symbol="triangle-up", size=9, color=C_CRIT)))
    fails = w[w.label == 1]
    fig.add_trace(go.Scatter(x=fails.t, y=np.full(len(fails), 0.03), mode="markers", name="Lỗi thật (ground truth)",
                             marker=dict(symbol="x", size=9, color=C_MUTED)))
    fig.add_hline(y=TAU, line=dict(color=C_MUTED, dash="dot"), annotation_text="τ = 0.67")
    vline(fig, det if det is not None and det <= t else None, "ADWIN", C_CRIT)
    vline(fig, adapt if (view_model == "Evolving" and adapt is not None and adapt <= t) else None, "adapted", C_GOOD, "dot")
    fig.update_yaxes(range=[0, 1])
    st.plotly_chart(base_layout(fig, 300, "Anomaly score — 300 mẫu gần nhất", "score"), use_container_width=True)

    sc = st.columns(4)
    for c, var in zip(sc, ["rpm", "torque", "air_temp", "tool_wear"]):
        f = go.Figure(go.Scatter(x=stream.index[lo:t + 1], y=stream[SENSOR_COLUMNS[var]].iloc[lo:t + 1],
                                 line=dict(color=C_STATIC, width=1.5), name=VAR_LABEL[var]))
        c.plotly_chart(base_layout(f, 200, VAR_LABEL[var]), use_container_width=True)

# ---------------------------------------------------------------- 2. drift
with tabs[1]:
    st.subheader("Mô phỏng thay đổi môi trường → phát hiện drift không cần nhãn")
    if onset is None:
        st.info("Kịch bản Control: không tiêm drift. ADWIN "
                + ("không phát cảnh báo nào." if det is None else f"phát cảnh báo tại t = {det} (báo động nhầm)."))
    else:
        desc = ("đột ngột tại t = 1000" if scenario == "Sudden Drift" else f"tuyến tính t = {GRADUAL_DRIFT_START}→{GRADUAL_DRIFT_END}")
        st.markdown(f"**Environment change (mô phỏng):** RPM −150 rpm, Torque +8 Nm, {desc}. Nhãn không đổi.")
        if det is not None and t >= det:
            st.error(f"⚠ Concept drift detected at t = {det}  (ADWIN trên chuỗi anomaly score, không dùng nhãn) · "
                     f"delay {det - (SUDDEN_DRIFT_POINT if scenario == 'Sudden Drift' else GRADUAL_DRIFT_END)} mẫu "
                     f"{'sau onset' if scenario == 'Sudden Drift' else 'sau khi drift đạt cực đại'}")
        elif onset is not None and t >= onset:
            st.warning("Drift đã bắt đầu (ground truth mô phỏng) nhưng ADWIN chưa đủ bằng chứng thống kê.")
        else:
            st.success("✓ Luồng ổn định — chưa có drift.")
    s = res["Static"]["log"].iloc[:t + 1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.t, y=s.score.rolling(50, min_periods=1).mean(), name="Static score (TB trượt 50)",
                             line=dict(color=C_STATIC, width=2)))
    fig.add_hline(y=TAU, line=dict(color=C_MUTED, dash="dot"))
    if onset is not None and t >= onset:
        vline(fig, onset, "drift onset (mô phỏng)", C_MUTED, "dot")
    vline(fig, det if det is not None and t >= det else None, "ADWIN detect", C_CRIT)
    if det is not None and t > det:
        fig.add_vrect(x0=det + 1, x1=min(t, det + 200), fillcolor=C_EVOLVING, opacity=0.08, line_width=0,
                      annotation_text="buffer W=200", annotation_position="bottom left")
    fig.update_xaxes(range=[0, 2000]); fig.update_yaxes(range=[0, 0.8])
    st.plotly_chart(base_layout(fig, 320, "Mặt bằng anomaly score của hệ Static", "score"), use_container_width=True)
    cc = st.columns(2)
    for c, var in zip(cc, ["rpm", "torque"]):
        y = stream[SENSOR_COLUMNS[var]].iloc[:t + 1]
        f = go.Figure(go.Scatter(x=y.index, y=y.rolling(50, min_periods=1).mean(), line=dict(color=C_STATIC, width=2),
                                 name=f"{VAR_LABEL[var]} (TB trượt 50)"))
        if onset is not None and t >= onset:
            vline(f, onset, "onset", C_MUTED, "dot")
        f.update_xaxes(range=[0, 2000])
        c.plotly_chart(base_layout(f, 230, VAR_LABEL[var] + " — trung bình trượt"), use_container_width=True)

# ---------------------------------------------------------------- 3. evolving
with tabs[2]:
    st.subheader("Evolving fuzzy: tịnh tiến hàm thuộc của biến bị drift")
    ev = res["Evolving"]["events"]
    ad_ev = next((e for e in ev if e["event"] == "adapted"), None)
    done = ad_ev is not None and t > ad_ev["t"]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Số luật trước → sau", "12 → 12")
    m2.metric("Trạng thái", "Đã thích nghi" if done else ("Đang thu buffer" if det is not None and t > det else "Chưa thích nghi"))
    hlp = "Δ = mean(buffer 200 mẫu) − tâm MF MEDIUM ban đầu. Độ dịch tiêm thật: −150 rpm / +8 Nm."
    m3.metric("ΔRPM ước lượng", f"{ad_ev['shifts']['rpm']:+.1f}" if done else "—", help=hlp)
    m4.metric("ΔTorque ước lượng", f"{ad_ev['shifts']['torque']:+.2f}" if done else "—", help=hlp)
    cols = st.columns(2)
    for c, var in zip(cols, ["rpm", "torque"]):
        f = go.Figure()
        for term in TERMS:
            f.add_trace(go.Scatter(x=UNIVERSES[var], y=STATIC_GRID_MFS[var][term], name=f"{term.upper()} (trước)",
                                   line=dict(color=TERM_COLORS[term], width=2)))
            if done:
                f.add_trace(go.Scatter(x=UNIVERSES[var], y=res["Evolving"]["grid"][var][term], name=f"{term.upper()} (sau)",
                                       line=dict(color=TERM_COLORS[term], width=2, dash="dash")))
        x_now = stream[SENSOR_COLUMNS[var]].iloc[t]
        f.add_vline(x=x_now, line=dict(color=C_MUTED, width=1), annotation_text=f"x(t)={x_now:.1f}")
        f.update_yaxes(range=[0, 1.05])
        base_layout(f, 360, VAR_LABEL[var], "μ", VAR_LABEL[var])
        f.update_layout(legend=dict(orientation="h", y=-0.3, x=0), hovermode="closest")
        c.plotly_chart(f, use_container_width=True)
    st.caption("Nét liền = MF trước thích nghi, nét đứt = sau. Vết cắt thẳng đứng ở mép miền giá trị là do dịch MF trên lưới hữu hạn "
               "(ngoài universe → μ = 0); không có mẫu nào rơi vào vùng đó trong các kịch bản đã chạy. "
               "Air/Process temperature và Tool wear được giữ nguyên (protected). 12 luật và τ đóng băng. "
               "Thêm/bớt luật được thử ở Phase 12 (cần nhãn phản hồi) — cấu hình chọn trên Validation không thay đổi luật nào trên Test.")
    st.dataframe(pd.DataFrame([{"Rule": rid, "IF … THEN …": format_rule(a, c)} for rid, a, c in RULES]),
                 hide_index=True, use_container_width=True, height=250)

# ---------------------------------------------------------------- 4. comparison
with tabs[3]:
    st.subheader("Static vs Evolving trên cùng luồng")
    sl, el = res["Static"]["log"], res["Evolving"]["log"]
    rows = []
    segs = {"Toàn luồng tới t": (0, t + 1)}
    if onset is not None:
        segs["A · trước drift"] = (0, min(onset, t + 1))
        if adapt is not None:
            segs["B · drift, chưa thích nghi"] = (onset, min(adapt + 1, t + 1))
            segs["C · sau thích nghi"] = (adapt + 1, t + 1)
    for seg, (a, b) in segs.items():
        if b - a <= 0:
            continue
        for name, lg in [("Static", sl), ("Evolving", el), ("Control ref (không drift)", ctrl)]:
            if name.startswith("Control") and not seg.startswith("C"):
                continue
            w = lg.iloc[a:b]
            m = evaluate(w.label, w.score)
            rows.append({"Đoạn": seg, "Hệ": name, "n": b - a, "lỗi thật": int(w.label.sum()), "TP": m["TP"], "FP": m["FP"],
                         "FN": m["FN"], "Precision": m["Precision"], "Recall": m["Recall"], "F1": m["F1"], "FPR": m["FPR"]})
    st.dataframe(pd.DataFrame(rows).round({k: 3 for k in ["Precision", "Recall", "F1", "FPR"]}),
                 hide_index=True, use_container_width=True)
    st.caption("Mỗi đoạn chỉ có vài ca lỗi → Recall theo đoạn rất nhiễu. 'Control ref' là tham chiếu oracle (hệ Static trên luồng không drift, cùng cửa sổ), chỉ dùng để đánh giá.")
    f = go.Figure()
    for name, lg, col in [("Static", sl, C_STATIC), ("Evolving", el, C_EVOLVING)]:
        fp = ((lg.pred == 1) & (lg.label == 0)).cumsum().iloc[:t + 1]
        f.add_trace(go.Scatter(x=fp.index, y=fp, name=f"{name} — FP tích lũy", line=dict(color=col, width=2)))
    if onset is not None and t >= onset:
        vline(f, onset, "onset", C_MUTED, "dot")
    vline(f, adapt if adapt is not None and t >= adapt else None, "adapted", C_GOOD, "dot")
    f.update_xaxes(range=[0, 2000])
    st.plotly_chart(base_layout(f, 300, "Cảnh báo giả tích lũy theo thời gian", "FP"), use_container_width=True)
    full = {n: evaluate(lg.label, lg.score) for n, lg in [("Static", sl), ("Evolving", el)]}
    f2 = go.Figure()
    for n, col in [("Static", C_STATIC), ("Evolving", C_EVOLVING)]:
        vals = [full[n][k] for k in ["Precision", "Recall", "F1", "FPR"]]
        f2.add_trace(go.Bar(x=["Precision", "Recall", "F1", "FPR"], y=vals, name=n, marker_color=col,
                            text=[f"{v:.3f}" for v in vals], textposition="outside"))
    f2.update_layout(barmode="group", bargap=0.3, bargroupgap=0.05)
    st.plotly_chart(base_layout(f2, 300, "Toàn luồng 2000 mẫu", None, ""), use_container_width=True)

# ---------------------------------------------------------------- 5. explain
with tabs[4]:
    fis, adapted_now = fis_at(view_model, t, res)
    row = stream.iloc[t]
    ex = fis.explain(row, top_k=12)
    st.subheader(f"Vì sao mẫu t = {t} có score {ex['score']:.3f}?  ({view_model}{', MF đã thích nghi' if adapted_now else ''})")
    parts = [f"{v.replace('_', ' ').title()} = {ex['values'][v]:.1f} → **{term.upper()} ({mu:.2f})**"
             for v, (term, mu) in ex["dominant_terms"].items()]
    st.markdown("  \n".join(parts))
    fired = ex["fired_rules"]
    if fired:
        st.markdown("**Luật được kích hoạt** (α = min của các điều kiện):")
        st.dataframe(pd.DataFrame([{"Rule": rid, "α": round(a, 3), "IF … THEN …": format_rule(ants, cons)}
                                   for rid, a, cons, ants in fired]), hide_index=True, use_container_width=True)
    else:
        st.info("Không luật nào kích hoạt → score = 0.")
    verdict = "⚠ ANOMALY" if ex["score"] >= TAU else "✓ NORMAL"
    st.markdown(f"→ Centroid của tập mờ đầu ra = **{ex['score']:.3f}** so với τ = {TAU} → **{verdict}**")
    c1, c2 = st.columns([2, 3])
    mem = pd.DataFrame([{"Biến": v, "Term": term.upper(), "μ": ex["memberships"][v][term]}
                        for v in ex["memberships"] for term in TERMS])
    fm = go.Figure()
    for term in TERMS:
        d = mem[mem.Term == term.upper()]
        fm.add_trace(go.Bar(x=d["Biến"], y=d["μ"], name=term.upper(), marker_color=TERM_COLORS[term]))
    fm.update_layout(barmode="group"); fm.update_yaxes(range=[0, 1.05])
    c1.plotly_chart(base_layout(fm, 300, "Độ thuộc từng biến", "μ", ""), use_container_width=True)
    fo = go.Figure(go.Scatter(x=OUTPUT_UNIVERSE, y=ex["aggregated"], fill="tozeroy", name="Tập mờ đầu ra (aggregated)",
                              line=dict(color=C_EVOLVING if view_model == "Evolving" else C_STATIC, width=2)))
    fo.add_vline(x=ex["score"], line=dict(color=C_CRIT if ex["score"] >= TAU else C_GOOD, width=2),
                 annotation_text=f"centroid = {ex['score']:.3f}")
    fo.add_vline(x=TAU, line=dict(color=C_MUTED, dash="dot"), annotation_text="τ", annotation_position="bottom right")
    fo.update_yaxes(range=[0, 1.05])
    c2.plotly_chart(base_layout(fo, 300, "Tổng hợp max–min và giải mờ centroid", "μ", "anomaly"), use_container_width=True)

# ---------------------------------------------------------------- autoplay
if playing and t < 1999:
    time.sleep(0.35)
    ss["advance"] = True
    st.rerun()
