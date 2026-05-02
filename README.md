# 🧬 RadResume: RCR Radiotherapy Interruption and dose compensation Calculator

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Medical Physics](https://img.shields.io/badge/Medical_Physics-Clinical_Tool-01579b?style=for-the-badge)

**RadResume** is a clinical-grade Streamlit application designed for Medical Physicists and Radiation Oncologists. It calculates biological compensation for radiotherapy interruptions based strictly on the **Royal College of Radiologists (RCR) "The timely delivery of radical radiotherapy: guidelines for the management of unscheduled treatment interruptions Fourth edition" (2019)**.

[https://www.rcr.ac.uk/our-services/all-our-publications/clinical-oncology-publications/timely-delivery-of-radical-radiotherapy-guidelines-for-the-management-of-unscheduled-treatment-interruptions-fourth-edition/]

Unscheduled interruptions in radical radiotherapy allow tumour cells to repopulate, increasing the risk of local recurrence. RadResume helps clinical teams calculate the compensation needed — additional fractions, adjusted dose, or accelerated scheduling — to recover the prescribed biological dose when treatment is delayed. Based on the RCR 4th Edition guidelines (2019)."

## 🌟 Key Features

*   **Strict RCR Compliance:** Uses the exact mathematical formulations from RCR Appendix B (Equation B), properly handling Overall Treatment Time (OTT) extensions, $T_{delay}$, and tumor repopulation ($K$ factors).
*   **Suggested Clinical Presets:** Includes a comprehensive database of predefined radiobiological parameters (Category, $\alpha/\beta$, $K$, $T_{delay}$) for common treatment sites (e.g., Head & Neck, Prostate, Gastrointestinal, Palliative).
*   **Hierarchical Action Plans:** Suggests compensations following the clinical priority established by the RCR:
    1.  Linac Transfer / Weekend Treatments.
    2.  BID (Twice-a-day) Scheduling.
    3.  Exact Dose per Fraction Adjustment.
    4.  Adding Extra Fractions (Standard Extension).
*   **Normal Tissue Tolerance (BED3):** Automatically calculates and monitors the Biological Effective Dose for late-responding normal tissues, issuing clinical warnings if the proposed compensation exceeds the original prescription budget by >5%.
*   **Clinical Governance (IR(ME)R 2017):** Generates an exportable `.txt` Audit Record detailing all calculation parameters, biological delays, and clinical decisions for departmental filing and compliance.

## 🚀 Installation & Setup

To run RadResume locally, you need Python installed on your system. Follow these steps:

1. **Clone the repository:**
   ```bash
    git clone [https://github.com/YourUsername/RadResume.git](https://github.com/YourUsername/RadResume.git)
    cd RadResume
2. **Create a virtual environment (Recommended):**
   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. **Install the required dependencies:**
    ```bash
    pip install streamlit
4. **Run the application:**
    ```bash
    streamlit run Interruptions.py
   
## 💻 How to Use
1. **Select Protocol:** Open the left sidebar and select the "Treatment Site / Intent". The app will automatically load the RCR-recommended radiobiological parameters. You can override these in the "Advanced Radiobiology Parameters" expander if clinically justified.

2. **Input Original Prescription:** Enter the total prescribed dose and the total number of fractions.

3. **Set Current Status:** Input how many fractions have already been delivered before the interruption.

4. **Define the Gap:** Enter the date of the last delivered fraction and the expected restart date. Configure your department's standard rest days (e.g., weekends) and holidays.

5. **Calculate:** Click the "CALCULATE NEW PRESCRIPTION" button to view the precise OTT extension, BED metrics, and the hierarchical compensation tabs.

6. **Audit & Export:** Review the internal QA panel if needed, and download the Audit Record for your clinical governance files.


## ⚠️ Legal Disclaimer & Terms of Use
Notice: This software is intended for educational and research purposes only. It is not a medical device and has not been cleared by any regulatory body (e.g., FDA, CE, MHRA) for clinical use.

* **Responsibility:** The user assumes all responsibility for the interpretation and clinical application of the results provided by this tool.

* **Verification:** Calculations must be independently verified by a certified Medical Physicist or Radiation Oncologist before making any clinical decisions.

* **Liability:** The developers of RadResume shall not be held liable for any damages, clinical errors, or consequences arising from the use or misuse of this software.

* **Compliance:** Any change to fractionation or dose schedules must be authorized and justified by the prescribing practitioner, in accordance with local regulations (e.g., IR(ME)R 2017 in the UK).

LinkedIn: Luis Fernando Paredes https://www.linkedin.com/in/lfparedes1/
Email: luisfernandoparedes2@gmail.com
