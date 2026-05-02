import streamlit as st
import math
from datetime import date, timedelta

# 1. Page Configuration (RadResume Identity)
st.set_page_config(
    page_title="RadResume | RCR Radiotherapy Interruption Calculator",
    page_icon="🧬",
    layout="wide"
)

# --- CSS STYLES FOR RADRESUME LOOK & FEEL ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧬 RadResume: Radiotherapy Interruptions & dose compensation")
st.info("Calculates the dose compensation required when a radiotherapy course is interrupted by machine breakdown, patient illness or any unplanned event, based on RCR guidelines for the management of unscheduled treatment interruptions, Fourth edition(2019).")

# =============================================================
# 2. SIDEBAR: RADIOBIOLOGY (System Configuration)
# =============================================================
st.sidebar.header("🧮 Radiobiological Settings")

with st.sidebar:
    st.subheader("Clinical Protocol (Suggested Presets)")

    # 1. Base de datos ampliada de "Preajustes Inteligentes"
    protocol_presets = {
        "Head & Neck / Cervix / Lung (Fast SCC)": {
            "cat": 1, "ab": 10.0, "k": 0.9, "tdelay": 28
        },
        "Oesophagus (SCC / Fast Adeno)": {
            "cat": 1, "ab": 10.0, "k": 0.9, "tdelay": 28
        },
        "Gastrointestinal (Stomach, Colon, Pancreas)*": {
            "cat": 2, "ab": 10.0, "k": 0.4, "tdelay": 21
        },
        "Liver (HCC - Standard Fractionation)*": {
            "cat": 2, "ab": 10.0, "k": 0.4, "tdelay": 21
        },
        "Breast / Bladder (Standard)": {
            "cat": 2, "ab": 4.0, "k": 0.5, "tdelay": 21
        },
        "Kidney (RCC)*": {
            "cat": 2, "ab": 3.0, "k": 0.2, "tdelay": 0
        },
        "Prostate (Slow / Hypofractionated)*": {
            "cat": 2, "ab": 3.0, "k": 0.2, "tdelay": 0
        },
        "Palliative Intent (Category 3)": {
            "cat": 3, "ab": 10.0, "k": 0.0, "tdelay": 0
        },
        "Custom Configuration": {
            "cat": 1, "ab": 10.0, "k": 0.6, "tdelay": 28
        }
    }

    # 2. Selector clínico principal
    selected_protocol = st.selectbox(
        "Select Treatment Site / Intent",
        list(protocol_presets.keys()),
        help="Automatically loads RCR parameters. These can be overridden in the Advanced menu."
    )
    st.caption("* Note: K estimated by extrapolation for these sites — limited direct RCR evidence.")

    # Cargar los datos del preset seleccionado
    preset = protocol_presets[selected_protocol]
    cat_labels = {1: "Category 1 (Fast)", 2: "Category 2 (Standard)", 3: "Category 3 (Palliative)"}
    rcr_category_num = preset['cat']



    # 4. DIVULGACIÓN PROGRESIVA: Ocultar los parámetros complejos editables
    with st.expander("⚙️ Modify selected Radiobiology Parameters"):
        st.caption("Override default RCR values if clinically justified.")

        rcr_category_num = st.number_input("RCR Category", min_value=1, max_value=3, value=preset['cat'])
        alfa_beta = st.number_input("Tumour α/β (Gy)", min_value=1.0, value=preset['ab'], step=0.5)
        factor_k = st.number_input("K Factor (Gy/day)", min_value=0.0, value=preset['k'], step=0.1)
        t_delay = st.number_input("T_delay (Days)", min_value=0, value=preset['tdelay'], step=1)

        st.divider()
        st.caption("Normal Tissue (OARs)")
        AB_NORMAL = st.number_input("Normal Tissue α/β (Gy)", min_value=1.0, value=3.0, step=0.5)

    # 3. Transparencia Clínica: Mostrar los parámetros asumidos en un cuadro informativo
    st.info(f"""
        **{cat_labels[rcr_category_num]}**
        - **Tumour α/β:** {alfa_beta} Gy
        - **Loss (K):** {factor_k} Gy/day
        - **T_delay:** {t_delay} days
        - **OARs α/β:** {AB_NORMAL} Gy
        """)

    st.divider()
    st.caption("Global LQ Model Configuration.")

# =============================================================
# 3. MAIN WINDOW: CLINICAL DATA (Single Column)
# =============================================================
col_input, col_space, col_results = st.columns([1.2, 0.1, 1.2])

with col_input:
    st.subheader("📋 Treatment & Interruption Data")

    # 1. Original Prescription
    with st.container():
        st.markdown("### 1. Original Prescription")
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            dosis_total = st.number_input("Total Prescribed Dose (Gy)", min_value=0.1, value=60.0, step=1.0)
            total_fracciones = st.number_input("Total number of fractions", min_value=1, value=30, step=1)

        with col_p2:
            dosis_por_fraccion = dosis_total / total_fracciones
            st.number_input("Dose per Fraction (Gy)", value=float(dosis_por_fraccion), disabled=True,
                            help="Calculated automatically: Total Dose / Total Fractions")

    st.write("")

    # 2. Current Status
    with st.container():
        st.markdown("### 2. Current Status")
        default_delivered = min(10, int(total_fracciones))
        fracciones_dadas = st.number_input("Fractions already delivered", min_value=0, max_value=int(total_fracciones),
                                           value=default_delivered)

    st.write("")

    # 3. Interruption Details
    with st.container():
        st.markdown("### 3. Interruption Details")
        f1 = st.date_input("Date of last fraction delivered", value=date.today())
        f2 = st.date_input("Expected restart date", value=date.today() + timedelta(days=1))

        with st.expander("⚙️ Department Configuration (Rest Days & Holidays)"):
            dias_descanso = st.multiselect(
                "Standard machine rest days",
                options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Saturday", "Sunday"]
            )
            trabaja_festivos = st.radio("Does the department work on holidays?", ["Yes", "No"], index=1,
                                        horizontal=True)
            if trabaja_festivos == "No":
                festivos = st.number_input("Holidays during the gap", min_value=0, value=0, step=1)
            else:
                festivos = 0

        # EXACT RCR LOGIC (OTT EXTENSION)
        dias_naturales = (f2 - f1).days
        day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        dias_descanso_num = [day_map[d] for d in dias_descanso]

        fecha_reinicio_planificada = f1 + timedelta(days=1)
        while fecha_reinicio_planificada.weekday() in dias_descanso_num:
            fecha_reinicio_planificada += timedelta(days=1)

        dias_retraso_biologico = max(0, (f2 - fecha_reinicio_planificada).days)

        turnos_perdidos = 0
        if dias_naturales > 0:
            for i in range(1, dias_naturales):
                eval_day = f1 + timedelta(days=i)
                if eval_day.weekday() not in dias_descanso_num:
                    turnos_perdidos += 1

            turnos_perdidos = max(0, turnos_perdidos - festivos)

            if turnos_perdidos == 0 and dias_retraso_biologico == 0:
                st.success("✅ The gap corresponds to standard rest/holidays. No turns or biological days lost.")
            else:
                st.info(f"Sessions (turns) to recover: **{turnos_perdidos}** \n\n"
                        f"Biological prolongation (OTT): **{dias_retraso_biologico} days**")
        elif dias_naturales < 0:
            st.error("Error: Restart date must be after the last fraction.")

    st.write("")

    # 4. Clinical Intent
    with st.container():
        st.markdown("### 4. Clinical Intent")
        c1, c2 = st.columns(2)
        with c1:
            es_paliativo = st.checkbox("Palliative intent", value=(rcr_category_num == 3),
                                       disabled=(rcr_category_num == 3))
        with c2:
            es_sabr = st.checkbox("SABR / SRS Treatment", help="Accelerated scheduling is contraindicated for SABR.")

    st.write("")
    calcular = st.button("CALCULATE NEW PRESCRIPTION", use_container_width=True, type="primary")

# =============================================================
# 4. MAIN WINDOW: RESULTS
# =============================================================
with col_results:
    if calcular and dias_naturales >= 0:

        # --- MAJOR 4: Priority Action Alert ---
        if dias_retraso_biologico > 2 and not es_paliativo:
            st.error(
                f"🔴 **RCR PRIORITY ACTION:** OTT prolongation of **{dias_retraso_biologico} days** exceeds the 2-day standard. Immediate compensation required. Transfer to matched linac is the preferred first option (RCR Section 5.1).")
        elif dias_retraso_biologico in [1, 2] and not es_paliativo:
            st.warning(
                f"⚠️ OTT prolonged by {dias_retraso_biologico} day(s). Compensation recommended per RCR guidelines.")

        st.subheader("🎯 Compensation Options")


        # =========================================================
        # --- CRITICAL 2: EXACT MATHEMATICAL LOGIC (FINAL FIX) ----
        # =========================================================

        # ── Función de tiempo calendario correcta ─────────────────────────────
        def T_calendario(n_fx):
            """Días entre primera y última fracción en esquema L-V sin interrupciones"""
            if n_fx <= 0:
                return 0
            semanas = (n_fx - 1) // 5
            resto = (n_fx - 1) % 5
            return semanas * 7 + resto


        # ── Parámetros de tiempo ─────────────────────────────────
        T_original = T_calendario(total_fracciones)
        T_total = T_original + dias_retraso_biologico
        frac_originales_que_faltaban = total_fracciones - fracciones_dadas


        # ── BED tumoral — Ecuación B del Appendix B ──────────────
        def bed_tumour(n_fx, d, ab, k, T, T_del):
            physical = n_fx * d * (1 + d / ab)
            repop = k * max(0.0, T - T_del)
            return physical - repop


        # BED10 del plan completo prescrito
        BED10_prescrito = bed_tumour(total_fracciones, dosis_por_fraccion, alfa_beta, factor_k, T_original, t_delay)

        # Despejando BED físico post-gap necesario (Eq. B Appendix B)
        bed_fisico_postgap_needed = (
                BED10_prescrito
                + factor_k * max(0.0, T_total - t_delay)
                - fracciones_dadas * dosis_por_fraccion * (1 + dosis_por_fraccion / alfa_beta)
        )
        bed_fisico_postgap_needed = max(0.0, bed_fisico_postgap_needed)

        # Fracciones necesarias manteniendo misma dosis por fracción
        bed_frac = dosis_por_fraccion * (1 + dosis_por_fraccion / alfa_beta)
        n_restante_raw = bed_fisico_postgap_needed / bed_frac if bed_frac > 0 else 0
        n_restante_final = round(n_restante_raw)
        fracciones_extra = n_restante_final - frac_originales_que_faltaban

        # Diferencia de BED por redondeo
        bed_fisico_total = (
                fracciones_dadas * dosis_por_fraccion * (1 + dosis_por_fraccion / alfa_beta)
                + n_restante_final * dosis_por_fraccion * (1 + dosis_por_fraccion / alfa_beta)
        )
        BED10_final = bed_fisico_total - factor_k * max(0.0, T_total - t_delay)
        diff_bed = BED10_final - BED10_prescrito

        # Variables exclusivas para mostrar en el reporte de auditoría
        T_pregap_reporte = T_calendario(fracciones_dadas)
        BED10_pregap_reporte = bed_tumour(fracciones_dadas, dosis_por_fraccion, alfa_beta, factor_k, T_pregap_reporte,
                                          t_delay)

        # --- MAJOR 1: NORMAL TISSUE BED3 CALCULATION ---
        bed3_frac = dosis_por_fraccion * (1 + dosis_por_fraccion / AB_NORMAL)
        bed3_prescribed = total_fracciones * bed3_frac
        bed3_delivered = fracciones_dadas * bed3_frac
        bed3_remaining = bed3_prescribed - bed3_delivered

        st.write("")

        # --- CLINICAL LOGIC: PALLIATIVE VS RADICAL ---
        if es_paliativo:
            st.markdown(f"""
            <div style="background-color:#fff3e0; padding:20px; border-radius:10px; border-left: 5px solid #e65100;">
                <h4 style="margin:0; color:#e65100;">Action Plan (Palliative):</h4>
                <p style="margin-top:10px; color:#333;">Complete the original {frac_originales_que_faltaban} pending fractions.</p>
            </div>
            """, unsafe_allow_html=True)

            if dias_retraso_biologico > 7:
                st.warning(
                    f"⚠️ **RCR Category 3:** Prolongation of {dias_retraso_biologico} days exceeds the 7-day threshold. Compensation may be required (RCR Section 3.3). Clinical judgement required — consider hypofractionation options.")
            else:
                st.success(
                    f"✅ **RCR Category 3:** Prolongation of {dias_retraso_biologico} days is within acceptable range. No extra compensation strictly required.")

        else:
            # --- PREFERRED CLINICAL OPTION (PERMANENT BANNER) ---
            st.markdown(f"""
            <div style="background-color:#e8f5e9; padding:15px; border-radius:8px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
                <h4 style="margin:0; color:#2e7d32;">🥇 Primary RCR Recommendation: Linac Transfer</h4>
                <p style="margin:5px 0 0 0; font-size:0.95em; color:#333;">
                    Transfer the patient to a matched machine on the same day or treat on a planned rest day (weekend). 
                    <b>If executed, no biological extension (OTT) occurs</b> and the original prescription remains unchanged. 
                    If this is not logistically possible, evaluate the calculated options below.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # --- CALCULATED OPTIONS (3 TABS) ---
            tab1, tab2, tab3 = st.tabs(["1️⃣ BID Scheduling", "2️⃣ Exact Dose Adjustment", "⚠️ 3️⃣ Add Fractions"])

            with tab1:
                if es_sabr:
                    st.error(
                        "🚫 **BID CONTRAINDICATED:** Accelerated scheduling is not appropriate for SABR. Treatment on non-consecutive days should resume after any delay (RCR Section 5.5).")
                elif dosis_por_fraccion > 2.2:
                    st.error(
                        f"🚫 **BID NOT RECOMMENDED:** Current fraction size is {dosis_por_fraccion:.2f} Gy, exceeding the RCR limit of 2.2 Gy for twice-daily treatment (RCR 4th Ed., Section 5.2). Risk of incomplete repair.")
                elif turnos_perdidos > 0:
                    if turnos_perdidos <= frac_originales_que_faltaban:
                        st.markdown(f"""
                        <div style="background-color:#e1f5fe; padding:15px; border-radius:8px; border-left: 5px solid #01579b;">
                            <h4 style="margin:0; color:#01579b;">Acceleration Protocol: BID</h4>
                            <h3 style="margin:5px 0; color:#01579b;">Deliver: {turnos_perdidos} BID session(s)</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.info(
                            f"📅 **Action:** Deliver the remaining {frac_originales_que_faltaban} fractions without adding extra days. Schedule **{turnos_perdidos}** of these days as BID. Minimum 6-hour interval required (RCR Section 5.2).")
                    else:
                        st.error(
                            f"⚠️ **Not feasible:** You need to recover {turnos_perdidos} turns, but only have {frac_originales_que_faltaban} fractions left.")
                else:
                    st.success("No physical turns were lost. BID scheduling is not required.")

            with tab2:
                if n_restante_final > 0:
                    a = n_restante_final / alfa_beta
                    b = n_restante_final
                    c = -bed_fisico_postgap_needed
                    discriminant = (b ** 2) - (4 * a * c)

                    if discriminant >= 0:
                        exact_dose = (-b + math.sqrt(discriminant)) / (2 * a)

                        st.markdown(f"""
                        <div style="background-color:#f3e5f5; padding:15px; border-radius:8px; border-left: 5px solid #6a1b9a;">
                            <h4 style="margin:0; color:#6a1b9a;">Precision Protocol: Adjust Dose</h4>
                            <h3 style="margin:5px 0; color:#6a1b9a;">Deliver: {n_restante_final} fx of {exact_dose:.2f} Gy</h3>
                        </div>
                        """, unsafe_allow_html=True)

                        if exact_dose > 2.5:
                            st.warning(
                                f"⚠️ **Caution:** Proposed fraction dose is {exact_dose:.2f} Gy. RCR Example 3 warns this may significantly increase late normal tissue effects.")

                        bed3_proposed_tab2 = n_restante_final * exact_dose * (1 + exact_dose / AB_NORMAL)
                        excess_pct_tab2 = ((
                                                       bed3_proposed_tab2 - bed3_remaining) / bed3_remaining * 100) if bed3_remaining > 0 else 0

                        if excess_pct_tab2 > 5:
                            st.error(
                                f"🚫 **NORMAL TISSUE TOLERANCE WARNING:** Proposed scheme exceeds remaining BED₃ by **{excess_pct_tab2:.1f}%**. Review with clinical team before prescribing (RCR Appendix B, Step 3).")
                        elif excess_pct_tab2 > 0:
                            st.warning(
                                f"⚠️ Normal tissue BED₃ slightly exceeded by **{excess_pct_tab2:.1f}%**. Consider splitting the difference as per RCR Example 3.")
                else:
                    st.error("No remaining fractions available to adjust.")

            with tab3:
                st.markdown(f"""
                <div style="background-color:#fff3e0; padding:15px; border-radius:8px; border-left: 5px solid #e65100;">
                    <h4 style="margin:0; color:#e65100;">Standard Protocol: Add Fractions</h4>
                    <p style="margin:5px 0 10px 0; font-size:0.9em; color:#333;">Extends the overall treatment time. Least preferred option.</p>
                    <ul style="margin-bottom:10px; font-size:1.0em; color:#333;">
                        <li>Original fractions pending: <b>{frac_originales_que_faltaban}</b></li>
                        <li>Extra fractions to add: <b style="color:#d32f2f;">+{fracciones_extra}</b></li>
                    </ul>
                    <h3 style="margin:5px 0; color:#e65100;">Total remaining: {n_restante_final} fx of {dosis_por_fraccion:.2f} Gy</h3>
                </div>
                """, unsafe_allow_html=True)

                if fracciones_extra > 0:
                    st.info(f"🔄 Integer rounding creates a tumor biological excess of **{diff_bed:+.2f} Gy BED**.")
                elif fracciones_extra == 0 and turnos_perdidos > 0:
                    st.success(
                        f"✅ Loss is too small to justify an extra fraction. Tumor deficit: **{diff_bed:.2f} Gy BED**.")

                bed3_proposed_tab3 = n_restante_final * dosis_por_fraccion * (1 + dosis_por_fraccion / AB_NORMAL)
                excess_pct_tab3 = (
                            (bed3_proposed_tab3 - bed3_remaining) / bed3_remaining * 100) if bed3_remaining > 0 else 0

                if excess_pct_tab3 > 5:
                    st.error(
                        f"🚫 **NORMAL TISSUE TOLERANCE WARNING:** Exceeds remaining BED₃ by **{excess_pct_tab3:.1f}%**. Review with clinical team.")
                elif excess_pct_tab3 > 0:
                    st.warning(f"⚠️ Normal tissue BED₃ slightly exceeded by **{excess_pct_tab3:.1f}%**.")
        # =========================================================
        # --- PANEL DE DEPURACIÓN Y VERIFICACIÓN (QA) -------------
        # =========================================================
        with st.expander("🛠️ Internal Calculation Verification Panel (QA)"):
            st.markdown(f"""
            *Exact values calculated by the radiobiological engine for validation:*

            **⏳ Times & Constants**
            * **K Factor:** `{factor_k}` Gy/day
            * **T_delay:** `{t_delay}` days
            * **OTT Extension:** `{dias_retraso_biologico}` days
            * **T_original (Plan):** `{T_original}` days
            * **T_total (Real):** `{T_total}` days

            **🎯 BED₁₀ (Tumor)**
            * **Prescribed Target:** `{BED10_prescrito:.3f}` Gy₁₀
            * **Delivered (Pre-gap):** `{BED10_pregap_reporte:.3f}` Gy₁₀
            * **Physical to Compensate:** `{bed_fisico_postgap_needed:.3f}` Gy₁₀
            * **Final Achieved:** `{BED10_final:.3f}` Gy₁₀

            **🛡️ BED₃ (Normal Tissue)**
            * **Prescribed Limit:** `{bed3_prescribed:.3f}` Gy₃
            * **Already Consumed:** `{bed3_delivered:.3f}` Gy₃
            * **Remaining Available:** `{bed3_remaining:.3f}` Gy₃
            """)

        # =========================================================
        # --- MINOR 2: EXPORTABLE AUDIT REPORT (UPDATED) ----------
        # =========================================================
        st.divider()
        report_text = f"""RadResume — RCR Interruption Audit Record
{'=' * 50}
Date of calculation : {date.today()}
Case reference      : [COMPLETE BEFORE FILING]

TREATMENT PROTOCOL
Protocol selected   : {selected_protocol}
RCR Category        : {rcr_category_num} — {cat_labels[rcr_category_num]}
Tumour α/β          : {alfa_beta} Gy
K factor            : {factor_k} Gy/day
T_delay             : {t_delay} days
Normal tissue α/β   : {AB_NORMAL} Gy

ORIGINAL PRESCRIPTION
Total dose          : {dosis_total} Gy
Total fractions     : {total_fracciones} fx
Dose per fraction   : {dosis_por_fraccion:.2f} Gy
Prescribed BED₁₀    : {BED10_prescrito:.2f} Gy₁₀
Prescribed BED₃     : {bed3_prescribed:.2f} Gy₃

INTERRUPTION DETAILS
Last fraction date  : {f1}
Planned restart     : {f2}
Calendar gap        : {dias_naturales} days
Fractions delivered : {fracciones_dadas} / {total_fracciones}
Turns lost          : {turnos_perdidos}
OTT extension       : {dias_retraso_biologico} days
Pre-gap BED₁₀       : {BED10_pregap_reporte:.2f} Gy₁₀
Pre-gap BED₃        : {bed3_delivered:.2f} Gy₃
Remaining BED₃      : {bed3_remaining:.2f} Gy₃

COMPENSATION SELECTED (complete one)
[ ] Linac transfer / weekend — no biological change required
[ ] BID scheduling — {turnos_perdidos} BID sessions, ≥6 h interval
[ ] Dose adjustment — {n_restante_final} fx of ______ Gy
[ ] Add fractions   — {n_restante_final} fx of {dosis_por_fraccion:.2f} Gy

CLINICAL GOVERNANCE CHECKLIST (RCR Section 7)
[ ] Transfer to matched linac evaluated first (RCR §5.1)
[ ] Normal tissue BED₃ verified within tolerance (RCR App. B)
[ ] Patient informed and re-consent obtained if required (RCR §7.2)
[ ] IR(ME)R 2017 compliance — change authorised by prescribing practitioner
[ ] Entered in departmental interruption registry (RCR §6.5)

Prescribing Oncologist : _______________________
Medical Physicist      : _______________________
Date authorised        : _______________________
{'=' * 50}
Generated by RadResume | For clinical use verify independently.
"""
        st.download_button(
            label="📝 Download Audit Record (TXT)",
            data=report_text,
            file_name="RadResume_Audit_Record.txt",
            mime="text/plain"
        )

    else:
        st.write("")
        st.write("### ⬅️ Configure data and press calculate")

# 5. Footer (RadResume Identity & IRMER Compliance)
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6c757d;">
        <small>RadResume Interruption Module | Clinical verification required by a Medical Physicist or Radiation Oncologist.<br>
        <i>Any change to fractionation or dose schedule must be authorised and justified by the prescribing practitioner, in accordance with IR(ME)R 2017 (RCR Section 7.2).</i></small>
    </div>
    """, unsafe_allow_html=True)
# 5. Footer (RadResume Identity)
# --------------Legal Disclaimer Section------------------------

st.divider()
st.subheader("⚠️ Disclaimer & Terms of Use")

st.markdown("""
<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6;">
    <p style="color: #6c757d; font-size: 0.9em;">
        <strong>Notice:</strong> This software is intended for <strong>educational and research purposes only</strong>. 
        It is not a medical device and has not been cleared by any regulatory body (FDA, CE, etc.) for clinical use.
    </p>
    <ul style="color: #6c757d; font-size: 0.85em;">
        <li><strong>Responsibility:</strong> The user assumes all responsibility for the interpretation and clinical application of the results provided by this tool.</li>
        <li><strong>Verification:</strong> Calculations must be independently verified by a certified Medical Physicist or Radiation Oncologist before any clinical decision.</li>
        <li><strong>Schedule:</strong> Any change to fractionation or dose schedule must be authorised and justified by the prescribing practitioner, in accordance with IR(ME)R 2017 (RCR Section 7.2). </li>
        <li><strong>Liability:</strong> The developers of RadComp shall not be held liable for any damages, clinical errors, or consequences arising from the use or misuse of this software.</li>
    </ul>
    <p style="color: #6c757d; font-size: 0.85em; font-style: italic;">
        By using this application, you acknowledge and agree to these terms.
    </p>
</div>
""", unsafe_allow_html=True)
# Contact & Collaboration Section
st.write("")  # Espacio en blanco
st.subheader("Contact & Feedback")
st.markdown("""
Are you interested in new features or have suggestions for future developments? 
I am open to collaborations and professional opportunities in Medical Physics and Software Development.

- **LinkedIn:** [Luis Fernando Paredes ](https://www.linkedin.com/in/lfparedes1/)
- **GitHub:** [Project Repository](https://github.com/LuisParedesOcampo/RadResume.git)
- **Email:** luisfernandoparedes2@gmail.com

*Developed by a Clinical Medical Physicist*
""")