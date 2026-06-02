
import gradio as gr
import os
from groq import Groq
# ADD these after line: from groq import Groq
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — required for Gradio/HF
import matplotlib.pyplot as plt
import io
import base64
import tempfile

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ══════════════════════════════════════════════════════════════
# COMPLETE KNOWLEDGE BASE — every word from the document
# ══════════════════════════════════════════════════════════════

DRUG_DB = {
    "URTI (Cough, Common cold)": {
        "safe_by_trimester": {
            "1st trimester": "Paracetamol 650mg QDS for fever, Cetirizine 10mg once a day for nasal symptoms, simple saline nasal drops, Amoxicillin 500mg three times a day for 7-10 days",
            "2nd trimester": "Paracetamol 650mg QDS for fever, Cetirizine 10mg once a day for nasal symptoms, simple saline nasal drops, Amoxicillin 500mg three times a day for 7-10 days",
            "3rd trimester": "Paracetamol 650mg QDS for fever, Cetirizine 10mg once a day for nasal symptoms, simple saline nasal drops, Amoxicillin 500mg three times a day for 7-10 days",
        },
        "unsafe": "Avoid decongestant nasal sprays, Codeine cough syrups, NSAIDs, fluoroquinolones, doxycycline",
        "alternatives": "Amoxicillin-Clavulanate 625mg twice a day for 7 days, Azithromycin 500mg once a day for 3 days",
        "supportive": "Steam inhalation, warm salt water gargles, adequate rest and hydration, honey for cough, humidifier",
        "penicillin_remove": ["Amoxicillin", "Amoxicillin-Clavulanate"],
    },
    "Urinary Tract Infection (UTI)": {
        "safe_by_trimester": {
            "1st trimester": "Cefixime 200mg twice a day for 5-7 days, fosfomycin 3g single dose, Amoxicillin-Clavulanate 625mg twice a day for 7 days",
            "2nd trimester": "Nitrofurantoin 100mg twice a day for 5-7 days, fosfomycin 3g single dose, cefixime 200mg twice a day for 5-7 days, Amoxicillin-Clavulanate 625mg twice a day for 7 days",
            "3rd trimester": "Cefixime 200mg twice a day for 5-7 days, fosfomycin 3g single dose, Amoxicillin-Clavulanate 625mg twice a day for 7 days",
        },
        "unsafe": "Avoid fluoroquinolones, tetracyclines, and sulfonamides",
        "alternatives": "Culture-guided antibiotic selection",
        "supportive": "Cranberry juice, adequate hydration",
        "penicillin_remove": ["Amoxicillin-Clavulanate"],
    },
    "Gestational diabetes": {
        "safe_by_trimester": {
            "1st trimester": "Human insulin (regular, NPH, rapid-acting analogs)",
            "2nd trimester": "Human insulin (regular, NPH, rapid-acting analogs)",
            "3rd trimester": "Human insulin (regular, NPH, rapid-acting analogs)",
        },
        "unsafe": "Avoid sulfonylureas, SGLT2 inhibitors, DPP4 inhibitors, oral hypoglycemics",
        "alternatives": "Insulin aspart, lispro (rapid-acting); Metformin (use with caution); Glyburide (use with caution, risk of neonatal hypoglycemia)",
        "supportive": "Regular moderate exercise, daily glucose monitoring, carbohydrate count and portion control, folic acid, prenatal vitamins",
        "penicillin_remove": [],
    },
    "Hemorrhoids and Constipation": {
        "safe_by_trimester": {
            "1st trimester": "Lactulose 15-30ml twice a day, Lignocaine gel 2% locally",
            "2nd trimester": "Lactulose 15-30ml twice a day, Lignocaine gel 2% locally",
            "3rd trimester": "Lactulose 15-30ml twice a day, Lignocaine gel 2% locally",
        },
        "unsafe": "Avoid stimulant laxatives (bisacodyl, senna), mineral oil, magnesium salts in renal impairment, oral stimulant laxatives, rectal suppositories with strong laxatives",
        "alternatives": "Ispaghula husk, Methylcellulose 1-2 tablets twice a day, hydrocortisone 1% ointment, witch hazel pads",
        "supportive": "Increase fibre intake, adequate fluid intake, regular gentle exercise, avoid prolonged straining, use ice packs for acute pain",
        "penicillin_remove": [],
    },
    "GERD or heartburn": {
        "safe_by_trimester": {
            "1st trimester": "Calcium carbonate 500-1000mg as needed, aluminum hydroxide+magnesium hydroxide, sodium alginate after meals",
            "2nd trimester": "Calcium carbonate 500-1000mg as needed, aluminum hydroxide+magnesium hydroxide, sodium alginate after meals",
            "3rd trimester": "Calcium carbonate 500-1000mg as needed, aluminum hydroxide+magnesium hydroxide, sodium alginate after meals",
        },
        "unsafe": "Avoid sodium bicarbonate due to fluid retention, H2 blockers with alcohol content",
        "alternatives": "Omeprazole 20mg daily, esomeprazole 20mg daily, Ranitidine 150mg twice a day",
        "supportive": "Small, frequent meals; avoid spicy, fatty, and acidic foods; do not eat 2-3 hours before bedtime; elevate the head of the bed 6-8 inches; remain upright after meals",
        "penicillin_remove": [],
    },
    "Asthma or breathlessness": {
        "safe_by_trimester": {
            "1st trimester": "Salbutamol 100-200mcg as needed, Budesonide 200-800mcg twice a day, beclomethasone, Montelukast 10mg daily",
            "2nd trimester": "Salbutamol 100-200mcg as needed, Budesonide 200-800mcg twice a day, beclomethasone, Montelukast 10mg daily",
            "3rd trimester": "Salbutamol 100-200mcg as needed, Budesonide 200-800mcg twice a day, beclomethasone, Montelukast 10mg daily",
        },
        "unsafe": "Avoid epinephrine, high-dose systemic steroids long-term, Omalizumab",
        "alternatives": "Increase budesonide to maximum dose, add long-acting beta agonist (formoterol/salmeterol), Theophylline if needed",
        "supportive": "Identify and avoid triggers, smoking cessation, Influenza vaccination, proper inhaler technique",
        "penicillin_remove": [],
    },
    "Depression or Anxiety": {
        "safe_by_trimester": {
            "1st trimester": "Sertraline 500mg daily",
            "2nd trimester": "Sertraline 500mg daily",
            "3rd trimester": "Sertraline 500mg daily",
        },
        "unsafe": "Avoid Paroxetine, MAO inhibitors, Benzodiazepines long-term",
        "alternatives": "Escitalopram 10mg daily, Citalopram 20mg daily",
        "supportive": "Cognitive Behavioural therapy, Interpersonal therapy, support groups, regular exercise, good sleep hygiene, nutritional counseling",
        "penicillin_remove": [],
    },
    "Skin conditions (Rashes, Infections)": {
        "safe_by_trimester": {
            "1st trimester": "Calamine lotion for itching, Hydrocortisone cream 1%, Clotrimazole cream for fungal infections, Mupirocin ointment for bacterial infections, Zinc oxide for barrier protection",
            "2nd trimester": "Calamine lotion for itching, Hydrocortisone cream 1%, Clotrimazole cream for fungal infections, Mupirocin ointment for bacterial infections, Zinc oxide for barrier protection",
            "3rd trimester": "Calamine lotion for itching, Hydrocortisone cream 1%, Clotrimazole cream for fungal infections, Mupirocin ointment for bacterial infections, Zinc oxide for barrier protection",
        },
        "unsafe": "Avoid Retinoids (tretinoin, adapalene), high-potency topical steroids, long-term systemic retinoids, Methotrexate, Cyclosporine",
        "alternatives": "Cetirizine 10mg daily for itching, Prednisolone 20-40mg daily, Fluconazole 150mg single dose for candidiasis",
        "supportive": "Gentle skincare, avoid harsh chemicals, sun protection for pigmentation, Moisturizing for dry skin",
        "penicillin_remove": [],
    },
    "Thyroid disorders (Hypo or Hyper)": {
        "safe_by_trimester": {
            "1st trimester": "Hypothyroidism: Levothyroxine takes on an empty stomach 1 hour before breakfast | Hyperthyroidism: propylthiouracil 100-150mg three times a day",
            "2nd trimester": "Hypothyroidism: Levothyroxine takes on an empty stomach 1 hour before breakfast | Hyperthyroidism: methimazole 10-20mg daily",
            "3rd trimester": "Hypothyroidism: Levothyroxine takes on an empty stomach 1 hour before breakfast | Hyperthyroidism: methimazole 10-20mg daily",
        },
        "unsafe": "Avoid Liothyronine, radioactive iodine, high-dose iodine, beta-blockers",
        "alternatives": "Levothyroxine takes on an empty stomach 1 hour before breakfast (hypothyroidism); propylthiouracil 100-150mg three times a day in the first trimester; Methimazole 10-20mg daily for the 2nd/3rd trimester (hyperthyroidism)",
        "supportive": "Maintain regular follow-up, monitor symptoms, ensure proper nutrition",
        "penicillin_remove": [],
    },
    "Gestational Hypertension": {
        "safe_by_trimester": {
            "1st trimester": "Labetalol 100mg twice a day (increase to 400mg twice a day), Nifedipine 20mg twice a day slow-release, Methyldopa 250mg three times a day",
            "2nd trimester": "Labetalol 100mg twice a day (increase to 400mg twice a day), Nifedipine 20mg twice a day slow-release, Methyldopa 250mg three times a day",
            "3rd trimester": "Labetalol 100mg twice a day (increase to 400mg twice a day), Nifedipine 20mg twice a day slow-release, Methyldopa 250mg three times a day",
        },
        "unsafe": "Avoid ACE inhibitors, Atenolol, ARBs, and diuretics",
        "alternatives": "Labetalol+Nifedipine, Methyldopa+Labetalol, Hydralazine",
        "supportive": "BP monitoring, reduce stress",
        "penicillin_remove": [],
    },
    "Nausea and vomiting": {
        "safe_by_trimester": {
            "1st trimester": "Pyridoxine 250mg three times a day, Doxylamine 10mg + Pyridoxine 10mg (up to 4 tablets daily)",
            "2nd trimester": "Pyridoxine 250mg three times a day, Doxylamine 10mg + Pyridoxine 10mg (up to 4 tablets daily)",
            "3rd trimester": "Pyridoxine 250mg three times a day, Doxylamine 10mg + Pyridoxine 10mg (up to 4 tablets daily)",
        },
        "unsafe": "Avoid high-dose vitamins, herbal remedies, domperidone, and prochlorperazine",
        "alternatives": "Metochlorpramide 10mg three times a day, Ondansetron 4-8mg twice a day",
        "supportive": "Small, frequent dry meals; avoid spicy, oily, and strong-smelling foods; ginger tea; adequate hydration; rest in a well-ventilated room",
        "penicillin_remove": [],
    },
    "Headache": {
        "safe_by_trimester": {
            "1st trimester": "Paracetamol 650mg four times a day",
            "2nd trimester": "Paracetamol 650mg four times a day",
            "3rd trimester": "Paracetamol 650mg four times a day",
        },
        "unsafe": "Avoid NSAIDs, Aspirin, Ergotamines, High-dose aspirin, Codeine combinations",
        "alternatives": "Metoclopramide 10mg three times a day",
        "supportive": "Check BP, rest in a quiet dark room, cold compress on forehead, adequate hydration, regular meals",
        "penicillin_remove": [],
        "nsaid_remove": ["NSAIDs"],
    },
    "Fever": {
        "safe_by_trimester": {
            "1st trimester": "Paracetamol 1g four times a day",
            "2nd trimester": "Paracetamol 1g four times a day",
            "3rd trimester": "Paracetamol 1g four times a day",
        },
        "unsafe": "Avoid NSAIDs, Aspirin, Doxycycline, chloramphenicol",
        "alternatives": "Cefixime 200mg twice a day, Amoxicillin-Clavulanate 625mg twice a day, Azithromycin 500mg once a day for 3 days",
        "supportive": "Adequate fluid intake, monitor temperature every 4-6 hours",
        "penicillin_remove": ["Amoxicillin-Clavulanate"],
    },
}

# ══════════════════════════════════════════════════════════════
# INSTANT LOCAL INFERENCE ENGINE — no API call needed
# ══════════════════════════════════════════════════════════════

def compute_result(condition, trimester, allergy, allergy_types,
                   # UTI
                   uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
                   # Gestational diabetes
                   dm_history, dm_thirst, dm_urination, dm_glucose,
                   # Hemorrhoids
                   hm_diff, hm_hard, hm_bleed, hm_pain,
                   # GERD
                   gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
                   # Asthma
                   asth_wheeze, asth_hard, asth_tight, asth_rapid,
                   # Depression
                   dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
                   # Skin
                   sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
                   # Thyroid
                   thy_cluster, thy_tsh,
                   # URTI
                   uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
                   # Gestational HTN
                   htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
                   # Nausea
                   nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
                   # Headache
                   ha_hbp, ha_blur, ha_intensity, ha_improve,
                   # Fever
                   fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt):

    if not condition or not trimester:
        return "⚠️ Please select a Trimester and Condition before analyzing."

    confidence = "LOW"
    severity = "MILD"
    special_alert = ""
    extra_note = ""

    # ── UTI ──────────────────────────────────────────────────
    if condition == "Urinary Tract Infection (UTI)":
        yes_count = sum([uti_burn == "Yes", uti_freq == "Yes"])
        if uti_burn == "Yes" and uti_freq == "Yes":
            confidence = "HIGH"
        elif yes_count == 1:
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if uti_fever == "Yes" or uti_flank == "Yes":
            severity = "CONCERNING"
            special_alert = "⚠️ Possible complicated UTI – seek medical evaluation."
        else:
            severity = "MILD"

    # ── Gestational Diabetes ──────────────────────────────────
    elif condition == "Gestational diabetes":
        g = float(dm_glucose) if dm_glucose else 0
        if g > 126 or dm_history == "Yes":
            confidence = "HIGH"
        elif g > 92 and (dm_thirst == "Yes" or dm_urination == "Yes"):
            confidence = "HIGH"
        elif 92 <= g <= 125:
            confidence = "MODERATE"
        elif dm_thirst == "Yes" and dm_urination == "Yes":
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if g > 126:
            severity = "CONCERNING"
            special_alert = "⚠️ Fasting glucose > 126 mg/dL – seek medical evaluation."
        elif 92 <= g <= 125:
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Hemorrhoids and Constipation ─────────────────────────
    elif condition == "Hemorrhoids and Constipation":
        if hm_diff == "Yes" and hm_hard == "Yes" and (hm_pain == "Yes" or hm_bleed == "Yes"):
            confidence = "HIGH"
        elif hm_diff == "Yes" and hm_hard == "Yes":
            confidence = "MODERATE"
        elif hm_pain == "Yes" and hm_bleed == "Yes":
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if hm_bleed == "Yes" or hm_pain == "Yes":
            severity = "CONCERNING"
            if hm_bleed == "Yes":
                special_alert = "⚠️ Severe rectal bleeding – seek medical evaluation."
        elif hm_diff == "Yes" and hm_hard == "Yes":
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── GERD / Heartburn ─────────────────────────────────────
    elif condition == "GERD or heartburn":
        if gerd_burn == "Yes" and (gerd_meals == "Yes" or gerd_lying == "Yes") and gerd_sour == "Yes":
            confidence = "HIGH"
        elif gerd_burn == "Yes" and (gerd_meals == "Yes" or gerd_lying == "Yes"):
            confidence = "MODERATE"
        elif gerd_sour == "Yes":
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if gerd_dysph == "Yes" or gerd_blood == "Yes":
            severity = "CONCERNING"
            special_alert = "⚠️ Dysphagia or blood in vomiting – seek medical evaluation."
        else:
            severity = "MODERATE"

    # ── Asthma / Breathlessness ───────────────────────────────
    elif condition == "Asthma or breathlessness":
        if asth_wheeze == "Yes" and asth_tight == "Yes" and (asth_hard == "Yes" or asth_rapid == "Yes"):
            confidence = "HIGH"
        elif asth_wheeze == "Yes" and (asth_tight == "Yes" or asth_hard == "Yes"):
            confidence = "MODERATE"
        elif asth_tight == "Yes" and asth_hard == "Yes":
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if asth_hard == "Yes" and asth_rapid == "Yes":
            severity = "CONCERNING"
            special_alert = "⚠️ Severe breathlessness – seek medical evaluation."
        elif asth_wheeze == "Yes" and asth_tight == "Yes":
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Depression / Anxiety ──────────────────────────────────
    elif condition == "Depression or Anxiety":
        sym_count = sum([dep_sad=="Yes", dep_interest=="Yes", dep_energy=="Yes", dep_sleep=="Yes", dep_conc=="Yes"])
        if dep_sad == "Yes" and dep_interest == "Yes" and (dep_energy=="Yes" or dep_sleep=="Yes" or dep_conc=="Yes"):
            confidence = "HIGH"
        elif dep_sad == "Yes" and (dep_energy=="Yes" or dep_sleep=="Yes"):
            confidence = "MODERATE"
        elif dep_interest == "Yes" and (dep_energy=="Yes" or dep_conc=="Yes"):
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if sym_count >= 4 and dep_sleep == "Yes" and dep_conc == "Yes":
            severity = "CONCERNING"
            special_alert = "⚠️ Severity concerning – seek medical evaluation."
        elif 2 <= sym_count <= 3:
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Skin Conditions ───────────────────────────────────────
    elif condition == "Skin conditions (Rashes, Infections)":
        if sk_rash == "Yes" and (sk_itch=="Yes" or sk_pain=="Yes") and (sk_swell=="Yes" or sk_disc=="Yes"):
            confidence = "HIGH"
        elif sk_rash == "Yes" and (sk_itch=="Yes" or sk_pain=="Yes"):
            confidence = "MODERATE"
        elif sk_disc == "Yes":
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if sk_disc == "Yes" or (sk_swell=="Yes" and sk_pain=="Yes"):
            severity = "CONCERNING"
            if sk_disc == "Yes":
                special_alert = "⚠️ Discharge/pus present – seek medical evaluation."
        elif sk_rash == "Yes" and sk_itch == "Yes":
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Thyroid Disorders ─────────────────────────────────────
    elif condition == "Thyroid disorders (Hypo or Hyper)":
        tsh = float(thy_tsh) if thy_tsh else 2.5
        # Normal TSH in pregnancy ~0.1–2.5 (1st), 0.2–3.0 (2nd/3rd)
        upper_normal = 2.5 if trimester == "1st trimester" else 3.0
        lower_normal = 0.1
        if tsh > upper_normal and thy_cluster == "A (Hypothyroidism)":
            confidence = "HIGH"
            extra_note = "Hypothyroidism indicated."
        elif tsh < lower_normal and thy_cluster == "B (Hyperthyroidism)":
            confidence = "HIGH"
            extra_note = "Hyperthyroidism indicated."
        elif tsh > upper_normal or tsh < lower_normal:
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if tsh > 10 or tsh < 0.01:
            severity = "CONCERNING"
            special_alert = "⚠️ TSH extremely abnormal – seek medical evaluation."
        elif tsh > upper_normal or tsh < lower_normal:
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── URTI ─────────────────────────────────────────────────
    elif condition == "URTI (Cough, Common cold)":
        resp_count = sum([uri_cough=="Yes", uri_throat=="Yes", uri_nose=="Yes"])
        if resp_count == 3:
            confidence = "HIGH"
        elif resp_count == 2 or (uri_fever=="Yes" and resp_count >= 1):
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        wbc_high = uri_wbc and float(uri_wbc) > 11 if uri_wbc else False
        if uri_fever == "Yes" or wbc_high:
            severity = "CONCERNING"
            if uri_fever == "Yes":
                special_alert = "⚠️ High fever with chills – seek medical evaluation."
        elif resp_count >= 2:
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Gestational Hypertension ──────────────────────────────
    elif condition == "Gestational Hypertension":
        s1 = float(htn_sys1) if htn_sys1 else 0
        d1 = float(htn_dia1) if htn_dia1 else 0
        s2 = float(htn_sys2) if htn_sys2 else 0
        d2 = float(htn_dia2) if htn_dia2 else 0
        if s1 >= 140 or d1 >= 90:
            confidence = "HIGH"
        elif (s2 >= 140 or d2 >= 90) and (s1 >= 140 or d1 >= 90):
            confidence = "HIGH"
        elif (130 <= s1 <= 139) or (80 <= d1 <= 89):
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if s1 >= 160 or d1 >= 110:
            severity = "CONCERNING"
            special_alert = "⚠️ Severely elevated BP – seek emergency medical evaluation."
        elif (s1 >= 140 or d1 >= 90) and (htn_head == "Yes" or htn_blur == "Yes"):
            severity = "CONCERNING"
            special_alert = "⚠️ Elevated BP with symptoms – seek medical evaluation."
        elif s1 >= 140 or d1 >= 90:
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Nausea and Vomiting ───────────────────────────────────
    elif condition == "Nausea and vomiting":
        vfreq = float(nv_freq) if nv_freq else 0
        vdays = float(nv_days) if nv_days else 0
        if vfreq >= 1 and vdays > 1:
            confidence = "HIGH"
        elif vfreq >= 1:
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if vfreq >= 5 or nv_eat=="No" or nv_dehy=="Yes" or nv_wt=="Yes":
            severity = "CONCERNING"
            special_alert = "⚠️ Severe vomiting/dehydration/weight loss – seek medical evaluation."
        elif 2 <= vfreq <= 4 and nv_eat == "Yes":
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Headache ──────────────────────────────────────────────
    elif condition == "Headache":
        if ha_intensity == "Mild (tight band)" and ha_improve == "Yes" and ha_hbp == "No" and ha_blur == "No":
            confidence = "HIGH"
        elif ha_intensity == "Intense (pulsating)" and ha_improve == "Yes":
            confidence = "MODERATE"
        elif ha_intensity == "Mild (tight band)" and ha_improve == "No":
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if ha_hbp == "Yes" or ha_blur == "Yes":
            severity = "CONCERNING"
            special_alert = "⚠️ Headache with high BP or visual disturbance – seek medical evaluation."
        elif ha_intensity == "Intense (pulsating)" and ha_improve == "Yes":
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Fever ─────────────────────────────────────────────────
    elif condition == "Fever":
        temp = float(fv_temp) if fv_temp else 0
        fdays = float(fv_days) if fv_days else 0
        plt_low = fv_plt and float(fv_plt) < 150 if fv_plt else False
        wbc_abn = fv_wbc and (float(fv_wbc) > 11 or float(fv_wbc) < 4) if fv_wbc else False
        if temp >= 100.4:
            confidence = "HIGH"
        elif 99 <= temp < 100.4 and (fv_chills=="Yes" or fv_assoc=="Yes"):
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        if temp >= 102 or fdays > 3 or plt_low or wbc_abn:
            severity = "CONCERNING"
            special_alert = "⚠️ High fever or prolonged duration – seek medical evaluation."
        elif 100.4 <= temp < 102 and fdays <= 3:
            severity = "MODERATE"
        else:
            severity = "MILD"

    # ── Build drug output with safety filter pipeline ─────────
    db = DRUG_DB.get(condition, {})
    safe_drugs = db.get("safe_by_trimester", {}).get(trimester, "Consult a healthcare professional.")
    unsafe = db.get("unsafe", "")
    alternatives = db.get("alternatives", "")
    supportive = db.get("supportive", "")
    penicillin_remove = db.get("penicillin_remove", [])

    allergy_warning = ""
    trimester_note = "Recommendations adjusted based on pregnancy trimester."

    # Step 3: Apply Allergy Filter
    if allergy == "Yes" and allergy_types:
        removed = []
        if any("penicillin" in a.lower() for a in allergy_types):
            for drug in penicillin_remove:
                if drug.lower() in safe_drugs.lower():
                    safe_drugs = safe_drugs.replace(drug, f"[REMOVED-allergy:{drug}]")
                    removed.append(drug)
        if any("nsaid" in a.lower() or "painkiller" in a.lower() for a in allergy_types):
            for d in ["ibuprofen", "NSAIDs", "Aspirin"]:
                if d.lower() in safe_drugs.lower():
                    removed.append(d)
        if removed:
            allergy_warning = f"⚠️ Certain drugs were excluded due to reported allergy: {', '.join(removed)}"
            safe_drugs = safe_drugs  # already marked above

    # Step 5: No safe option handling
    if not safe_drugs.strip() or safe_drugs.strip() == "":
        safe_drugs = "Limited safe options available. Please consult a healthcare professional."

    # ── Format final output ───────────────────────────────────
    severity_emoji = {"MILD": "🟢", "MODERATE": "🟡", "CONCERNING": "🔴"}.get(severity, "⚪")
    confidence_emoji = {"HIGH": "✅", "MODERATE": "🔶", "LOW": "⬇️"}.get(confidence, "⚪")

    out = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CLINICAL ASSESSMENT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Summary:
Based on your symptoms, this appears to be {condition} with {severity} severity.
● Condition:    {condition}
● Trimester:    {trimester}
{confidence_emoji} Confidence:  {confidence}
{severity_emoji} Severity:    {severity}
{f"  {extra_note}" if extra_note else ""}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💊 SAFE MEDICATIONS ({trimester}):
{safe_drugs}
🔄 ALTERNATIVES:
{alternatives}
🚫 UNSAFE DRUGS TO AVOID:
{unsafe}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  WARNINGS / ALERTS:
{allergy_warning if allergy_warning else "No allergy-related exclusions."}
{trimester_note}
{special_alert if special_alert else ""}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌿 SUPPORTIVE CARE (Non-Pharmacological):
{supportive}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚕️  DISCLAIMER: This is a clinical decision support tool only.
Always consult a qualified healthcare professional before
making any medication decisions during pregnancy.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    return out

# ══════════════════════════════════════════════════════════════
# CHART GENERATOR — Symptom Match Rate Bar Chart
# ══════════════════════════════════════════════════════════════

def generate_chart(condition, confidence, severity, symptom_labels, yes_answers):
    """
    symptom_labels : list of str  — e.g. ["Burning", "Frequency", "Fever", "Flank Pain"]
    yes_answers    : list of bool — e.g. [True, True, True, False]
    confidence     : "HIGH" / "MODERATE" / "LOW"
    severity       : "MILD" / "MODERATE" / "CONCERNING"
    Returns        : filepath (str) to a saved PNG — Gradio gr.Image accepts this
    """
    total   = len(yes_answers)
    yes_cnt = sum(yes_answers)
    match_pct = round((yes_cnt / total) * 100) if total > 0 else 0

    conf_map = {"HIGH": 85, "MODERATE": 55, "LOW": 25}
    sev_map  = {"CONCERNING": 90, "MODERATE": 55, "MILD": 20}
    conf_val = conf_map.get(confidence, 50)
    sev_val  = sev_map.get(severity, 50)

    # ── colour scheme ────────────────────────────────────────
    bar_colours = []
    for answered in yes_answers:
        bar_colours.append("#0d9488" if answered else "#e2e8f0")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5),
                             facecolor="#f8fafc", gridspec_kw={"width_ratios": [2, 1]})
    fig.suptitle(f"Symptom Analysis — {condition}",
                 fontsize=13, fontweight="bold", color="#1e293b", y=1.02)

    # ── LEFT: per-symptom bars ────────────────────────────────
    ax1 = axes[0]
    x_pos  = range(len(symptom_labels))
    heights = [100 if a else 15 for a in yes_answers]          # 100 = Yes, 15 = No (visual stub)
    bars = ax1.bar(x_pos, heights, color=bar_colours,
                   edgecolor="white", linewidth=1.5, width=0.55, zorder=3)

    # labels on top of bars
    for bar, answered, label in zip(bars, yes_answers, symptom_labels):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 3,
                 "✓ Yes" if answered else "✗ No",
                 ha="center", va="bottom",
                 fontsize=9, color="#0d9488" if answered else "#94a3b8",
                 fontweight="bold")

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(symptom_labels, rotation=20, ha="right", fontsize=9)
    ax1.set_yticks([])
    ax1.set_ylabel("")
    ax1.set_title(f"Symptom Response  ({yes_cnt}/{total} positive)",
                  fontsize=10, color="#475569")
    ax1.set_facecolor("#f8fafc")
    ax1.spines[["top","right","left"]].set_visible(False)
    ax1.spines["bottom"].set_color("#e2e8f0")
    ax1.set_ylim(0, 130)
    ax1.grid(axis="y", color="#e2e8f0", linewidth=0.5, zorder=0)

    # ── RIGHT: summary gauge bars ─────────────────────────────
    ax2 = axes[1]
    categories = ["Symptom\nMatch %", "Confidence\nLevel", "Severity\nLevel"]
    values     = [match_pct, conf_val, sev_val]
    gauge_cols = []
    for v in values:
        if v >= 70:   gauge_cols.append("#ef4444")   # red = high/concerning
        elif v >= 40: gauge_cols.append("#f59e0b")   # amber = moderate
        else:         gauge_cols.append("#22c55e")   # green = mild/low

    y_pos = range(len(categories))
    h_bars = ax2.barh(y_pos, values, color=gauge_cols,
                      edgecolor="white", linewidth=1.2, height=0.5, zorder=3)
    for bar, val in zip(h_bars, values):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                 f"{val}%", va="center", fontsize=9, fontweight="bold", color="#1e293b")

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(categories, fontsize=9)
    ax2.set_xlim(0, 115)
    ax2.set_xticks([])
    ax2.set_title("Clinical Summary", fontsize=10, color="#475569")
    ax2.set_facecolor("#f8fafc")
    ax2.spines[["top","right","bottom"]].set_visible(False)
    ax2.spines["left"].set_color("#e2e8f0")
    ax2.grid(axis="x", color="#e2e8f0", linewidth=0.5, zorder=0)

    plt.tight_layout()

    # save to a temp file — Gradio gr.Image reads file paths
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(tmp.name, dpi=130, bbox_inches="tight", facecolor="#f8fafc")
    plt.close(fig)
    return tmp.name

# ══════════════════════════════════════════════════════════════
# GROQ AI EXPLANATION — reads chart data, returns plain text
# ══════════════════════════════════════════════════════════════

def get_ai_explanation(condition, trimester, confidence, severity,
                       symptom_labels, yes_answers, special_alert=""):
    """
    Sends structured chart data (not the image — Groq text models are faster
    and cheaper than vision models for this use-case) to llama-3.3-70b via Groq.
    Returns a short, empathetic paragraph for the Toolbox panel.
    """
    total   = len(yes_answers)
    yes_cnt = sum(yes_answers)
    match_pct = round((yes_cnt / total) * 100) if total > 0 else 0

    sym_detail = "\n".join(
        [f"  • {lbl}: {'YES ✓' if ans else 'No ✗'}"
         for lbl, ans in zip(symptom_labels, yes_answers)]
    )

    prompt = f"""Maternal health assistant. Respond in 2 SHORT sentences only. No bullet points. No jargon. Be warm.
Condition: {condition} | Trimester: {trimester} | Confidence: {confidence} | Severity: {severity}
Positive symptoms: {yes_cnt}/{total}
{f"Alert: {special_alert}" if special_alert else ""}
Summarise findings and give ONE gentle next step."""

    import httpx
    try:
        http_client = httpx.Client(timeout=15.0)
        fast_client = Groq(api_key=os.environ.get("GROQ_API_KEY"), http_client=http_client)
        response = fast_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI explanation could not be generated. ({str(e)[:80]})"

# ══════════════════════════════════════════════════════════════
# SYMPTOM EXTRACTOR — maps condition inputs → labels + booleans
# ══════════════════════════════════════════════════════════════

def extract_symptoms(condition,
                     uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
                     dm_history, dm_thirst, dm_urination, dm_glucose,
                     hm_diff, hm_hard, hm_bleed, hm_pain,
                     gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
                     asth_wheeze, asth_hard, asth_tight, asth_rapid,
                     dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
                     sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
                     thy_cluster, thy_tsh,
                     uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
                     htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
                     nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
                     ha_hbp, ha_blur, ha_intensity, ha_improve,
                     fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt):

    mapping = {
        "Urinary Tract Infection (UTI)": (
            ["Burning", "Frequency", "Fever", "Flank Pain", "WBC Elevated"],
            [uti_burn=="Yes", uti_freq=="Yes", uti_fever=="Yes", uti_flank=="Yes",
             bool(uti_wbc and float(uti_wbc) > 11)]
        ),
        "Gestational diabetes": (
            ["Prior History", "Excessive Thirst", "Frequent Urination", "High Glucose"],
            [dm_history=="Yes", dm_thirst=="Yes", dm_urination=="Yes",
             bool(dm_glucose and float(dm_glucose) > 92)]
        ),
        "Hemorrhoids and Constipation": (
            ["Difficult Passage", "Hard Stool", "Bleeding", "Pain"],
            [hm_diff=="Yes", hm_hard=="Yes", hm_bleed=="Yes", hm_pain=="Yes"]
        ),
        "GERD or heartburn": (
            ["Burning", "After Meals", "Lying Down", "Sour Taste", "Dysphagia", "Blood"],
            [gerd_burn=="Yes", gerd_meals=="Yes", gerd_lying=="Yes",
             gerd_sour=="Yes", gerd_dysph=="Yes", gerd_blood=="Yes"]
        ),
        "Asthma or breathlessness": (
            ["Wheeze", "Breathless", "Chest Tight", "Rapid Breathing"],
            [asth_wheeze=="Yes", asth_hard=="Yes", asth_tight=="Yes", asth_rapid=="Yes"]
        ),
        "Depression or Anxiety": (
            ["Sadness", "Lost Interest", "Low Energy", "Poor Sleep", "Poor Concentration"],
            [dep_sad=="Yes", dep_interest=="Yes", dep_energy=="Yes",
             dep_sleep=="Yes", dep_conc=="Yes"]
        ),
        "Skin conditions (Rashes, Infections)": (
            ["Rash", "Itching", "Pain", "Swelling", "Discharge"],
            [sk_rash=="Yes", sk_itch=="Yes", sk_pain=="Yes", sk_swell=="Yes", sk_disc=="Yes"]
        ),
        "Thyroid disorders (Hypo or Hyper)": (
            ["Symptom Cluster", "TSH Abnormal"],
            [thy_cluster != "None", bool(thy_tsh and (float(thy_tsh) > 3 or float(thy_tsh) < 0.1))]
        ),
        "URTI (Cough, Common cold)": (
            ["Cough", "Sore Throat", "Runny Nose", "Fever", "WBC Elevated"],
            [uri_cough=="Yes", uri_throat=="Yes", uri_nose=="Yes", uri_fever=="Yes",
             bool(uri_wbc and float(uri_wbc) > 11)]
        ),
        "Gestational Hypertension": (
            ["BP ≥140/90 (1st)", "BP ≥140/90 (2nd)", "Headache", "Visual Blurring"],
            [bool(htn_sys1 and float(htn_sys1) >= 140) or bool(htn_dia1 and float(htn_dia1) >= 90),
             bool(htn_sys2 and float(htn_sys2) >= 140) or bool(htn_dia2 and float(htn_dia2) >= 90),
             htn_head=="Yes", htn_blur=="Yes"]
        ),
        "Nausea and vomiting": (
            ["Vomiting ≥1×/day", "Can Eat", "Dehydrated", "Weight Loss"],
            [bool(nv_freq and float(nv_freq) >= 1), nv_eat=="Yes",
             nv_dehy=="Yes", nv_wt=="Yes"]
        ),
        "Headache": (
            ["High BP", "Visual Blurring", "Intense", "Improves w/ Paracetamol"],
            [ha_hbp=="Yes", ha_blur=="Yes",
             ha_intensity == "Intense (pulsating)", ha_improve=="Yes"]
        ),
        "Fever": (
            ["Temp ≥100.4°F", "Duration >3 days", "Associated Symptoms", "Chills"],
            [bool(fv_temp and float(fv_temp) >= 100.4),
             bool(fv_days and float(fv_days) > 3),
             fv_assoc=="Yes", fv_chills=="Yes"]
        ),
    }
    return mapping.get(condition, (["No data"], [False]))

# ══════════════════════════════════════════════════════════════
# GRADIO UI
# ══════════════════════════════════════════════════════════════

_css = open("style.css").read()

CONDITIONS = [
    "URTI (Cough, Common cold)",
    "Urinary Tract Infection (UTI)",
    "Gestational diabetes",
    "Hemorrhoids and Constipation",
    "GERD or heartburn",
    "Asthma or breathlessness",
    "Depression or Anxiety",
    "Skin conditions (Rashes, Infections)",
    "Thyroid disorders (Hypo or Hyper)",
    "Gestational Hypertension",
    "Nausea and vomiting",
    "Headache",
    "Fever",
]

YES_NO = ["Yes", "No"]

def show_condition_panel(condition):
    panels = {
        "URTI (Cough, Common cold)":        [True,  False, False, False, False, False, False, False, False, False, False, False, False],
        "Urinary Tract Infection (UTI)":     [False, True,  False, False, False, False, False, False, False, False, False, False, False],
        "Gestational diabetes":              [False, False, True,  False, False, False, False, False, False, False, False, False, False],
        "Hemorrhoids and Constipation":      [False, False, False, True,  False, False, False, False, False, False, False, False, False],
        "GERD or heartburn":                 [False, False, False, False, True,  False, False, False, False, False, False, False, False],
        "Asthma or breathlessness":          [False, False, False, False, False, True,  False, False, False, False, False, False, False],
        "Depression or Anxiety":             [False, False, False, False, False, False, True,  False, False, False, False, False, False],
        "Skin conditions (Rashes, Infections)":[False,False, False, False, False, False, False, True,  False, False, False, False, False],
        "Thyroid disorders (Hypo or Hyper)": [False, False, False, False, False, False, False, False, True,  False, False, False, False],
        "Gestational Hypertension":          [False, False, False, False, False, False, False, False, False, True,  False, False, False],
        "Nausea and vomiting":               [False, False, False, False, False, False, False, False, False, False, True,  False, False],
        "Headache":                          [False, False, False, False, False, False, False, False, False, False, False, True,  False],
        "Fever":                             [False, False, False, False, False, False, False, False, False, False, False, False, True ],
    }
    flags = panels.get(condition, [False]*13)
    return [gr.update(visible=f) for f in flags]

with gr.Blocks(title="Maternal GestaGen – AI Pregnancy Health Assistant", css=_css, theme=gr.themes.Base()) as demo:

    gr.HTML("""
    <div class="hero-header">
      <div class="hero-glow"></div>
      <div class="hero-content">
        <div class="hero-icon">🤱</div>
        <h1 class="hero-title">Maternal GestaGen</h1>
        <p class="hero-subtitle">AI-Powered Clinical Decision Support for Pregnancy Health</p>
        <p class="hero-tagline">Safe · Evidence-Based · Trimester-Aware · Instant Results</p>
      </div>
    </div>
    """)

    with gr.Row(elem_classes="main-row"):
        # ── LEFT COLUMN ──────────────────────────────────────
        with gr.Column(scale=1, elem_classes="card-panel"):
            gr.HTML('<div class="section-header"><span class="section-icon">👤</span> Patient Profile</div>')

            trimester = gr.Radio(
                choices=["1st trimester", "2nd trimester", "3rd trimester"],
                label="Trimester", elem_classes="radio-group"
            )
            age = gr.Number(label="Age (years)", minimum=15, maximum=55, precision=0)

            conditions_chk = gr.CheckboxGroup(
                choices=["Hypertension", "Diabetes", "Asthma", "Thyroid disorder", "Epilepsy", "None"],
                label="Known Medical Conditions (select all that apply)"
            )

            gr.HTML('<div class="section-header"><span class="section-icon">💊</span> Medications & Allergies</div>')

            allergy = gr.Radio(choices=["No", "Yes"], label="Known Drug Allergies?")
            allergy_types = gr.CheckboxGroup(
                choices=[
                    "Antibiotics (e.g., penicillin group)",
                    "Painkillers (NSAIDs)",
                    "Sulfa drugs",
                    "Other (anticonvulsants, chemotherapeutic agents)"
                ],
                label="Specify allergy type(s):", visible=False
            )
            allergy.change(fn=lambda a: gr.update(visible=(a=="Yes")), inputs=allergy, outputs=allergy_types)

            medications = gr.CheckboxGroup(
                choices=[
                    "Prescription medications",
                    "Over-the-counter (OTC) medicines",
                    "Mental health medications",
                    "None / not taking any medications or substances"
                ],
                label="Current Medications (select all that apply)"
            )

            gr.HTML('<div class="section-header"><span class="section-icon">🚨</span> Red Flag Assessment</div>')
            red_flags = gr.CheckboxGroup(
                choices=["Severe abdominal pain","Bleeding","Extreme Difficulty breathing","Loss of consciousness","Seizure","None"],
                label="Select any red flag symptoms ('None' if not applicable)",
                elem_classes="red-flag-group"
            )

        # ── RIGHT COLUMN ──────────────────────────────────────
        with gr.Column(scale=1, elem_classes="card-panel"):
            gr.HTML('<div class="section-header"><span class="section-icon">🩺</span> Condition & Symptoms</div>')

            selected_condition = gr.Dropdown(
                choices=CONDITIONS,
                label="What condition or symptom are you experiencing?",
                value=None,
                interactive=True,
                elem_classes="dropdown-field gradio-dropdown"    
            )

            # ── URTI ──────────────────────────────────────────
            with gr.Group(visible=False) as panel_urti:
                gr.HTML('<div class="q-header">🤧 URTI — Symptom Questions</div>')
                uri_cough  = gr.Radio(YES_NO, label="Cough?", value="No")
                uri_throat = gr.Radio(YES_NO, label="Sore throat?", value="No")
                uri_nose   = gr.Radio(YES_NO, label="Runny nose?", value="No")
                uri_fever  = gr.Radio(YES_NO, label="Fever?", value="No")
                uri_wbc    = gr.Textbox(label="WBCs count (optional — enter value or leave blank)", placeholder="e.g. 8.5")

            # ── UTI ───────────────────────────────────────────
            with gr.Group(visible=False) as panel_uti:
                gr.HTML('<div class="q-header">🧫 UTI — Symptom Questions</div>')
                uti_burn  = gr.Radio(YES_NO, label="Burning during urination?", value="No")
                uti_freq  = gr.Radio(YES_NO, label="Increased urine frequency?", value="No")
                uti_fever = gr.Radio(YES_NO, label="Fever?", value="No")
                uti_flank = gr.Radio(YES_NO, label="Flank pain?", value="No")
                uti_wbc   = gr.Textbox(label="WBC count (optional)", placeholder="e.g. 10.2")

            # ── Gestational Diabetes ──────────────────────────
            with gr.Group(visible=False) as panel_dm:
                gr.HTML('<div class="q-header">🩸 Gestational Diabetes — Symptom Questions</div>')
                dm_history  = gr.Radio(YES_NO, label="History of diabetes before pregnancy?", value="No")
                dm_thirst   = gr.Radio(YES_NO, label="Increased thirst?", value="No")
                dm_urination= gr.Radio(YES_NO, label="Increased Urination?", value="No")
                dm_glucose  = gr.Textbox(label="Fasting glucose (mg/dl) — required", placeholder="e.g. 110")

            # ── Hemorrhoids ───────────────────────────────────
            with gr.Group(visible=False) as panel_hm:
                gr.HTML('<div class="q-header">🩹 Hemorrhoids & Constipation — Symptom Questions</div>')
                hm_diff  = gr.Radio(YES_NO, label="Having difficulty passing stools?", value="No")
                hm_hard  = gr.Radio(YES_NO, label="Experiencing hard stools?", value="No")
                hm_bleed = gr.Radio(YES_NO, label="Bleeding passing stool?", value="No")
                hm_pain  = gr.Radio(YES_NO, label="Pain while sitting?", value="No")

            # ── GERD ──────────────────────────────────────────
            with gr.Group(visible=False) as panel_gerd:
                gr.HTML('<div class="q-header">🔥 GERD / Heartburn — Symptom Questions</div>')
                gerd_burn  = gr.Radio(YES_NO, label="Chest pain or chest burning?", value="No")
                gerd_meals = gr.Radio(YES_NO, label="Does it get worse upon eating or after meals?", value="No")
                gerd_lying = gr.Radio(YES_NO, label="Does it get worse upon lying down?", value="No")
                gerd_sour  = gr.Radio(YES_NO, label="Do you often feel a sour taste in your mouth?", value="No")
                gerd_dysph = gr.Radio(YES_NO, label="Difficulty swallowing - dysphagia?", value="No")
                gerd_blood = gr.Radio(YES_NO, label="Vomiting with blood?", value="No")

            # ── Asthma ────────────────────────────────────────
            with gr.Group(visible=False) as panel_asth:
                gr.HTML('<div class="q-header">💨 Asthma / Breathlessness — Symptom Questions</div>')
                asth_wheeze = gr.Radio(YES_NO, label="Do you experience wheezing or a whistling sound?", value="No")
                asth_hard   = gr.Radio(YES_NO, label="Do you need to work hard to breathe?", value="No")
                asth_tight  = gr.Radio(YES_NO, label="Do you experience chest tightness?", value="No")
                asth_rapid  = gr.Radio(YES_NO, label="Rapid breathing or palpitations?", value="No")

            # ── Depression ────────────────────────────────────
            with gr.Group(visible=False) as panel_dep:
                gr.HTML('<div class="q-header">💙 Depression / Anxiety — Symptom Questions</div>')
                dep_sad      = gr.Radio(YES_NO, label="Feeling of sadness, low mood, or emptiness?", value="No")
                dep_interest = gr.Radio(YES_NO, label="Lack of interest in normal activities?", value="No")
                dep_energy   = gr.Radio(YES_NO, label="Lack of energy or tiredness?", value="No")
                dep_sleep    = gr.Radio(YES_NO, label="Sleep disturbances or irregularities?", value="No")
                dep_conc     = gr.Radio(YES_NO, label="Difficulty concentrating?", value="No")

            # ── Skin ──────────────────────────────────────────
            with gr.Group(visible=False) as panel_skin:
                gr.HTML('<div class="q-header">🌿 Skin Conditions — Symptom Questions</div>')
                sk_rash  = gr.Radio(YES_NO, label="Redness or rash?", value="No")
                sk_itch  = gr.Radio(YES_NO, label="Itching?", value="No")
                sk_pain  = gr.Radio(YES_NO, label="Pain?", value="No")
                sk_swell = gr.Radio(YES_NO, label="Swelling?", value="No")
                sk_disc  = gr.Radio(YES_NO, label="Any discharge/pus?", value="No")

            # ── Thyroid ───────────────────────────────────────
            with gr.Group(visible=False) as panel_thy:
                gr.HTML('<div class="q-header">🦋 Thyroid Disorders — Symptom Questions</div>')
                thy_cluster = gr.Radio(
                    ["A (Hypothyroidism)", "B (Hyperthyroidism)"],
                    label="Choose symptom cluster:\n  A = Weight gain, constipation, cold intolerance, slow heart rate\n  B = Weight loss, diarrhoea, heat intolerance, palpitations / increased heart rate",
                    value="A (Hypothyroidism)"
                )
                thy_tsh = gr.Textbox(label="TSH level (numeric value)", placeholder="e.g. 4.2")

            # ── Gestational Hypertension ──────────────────────
            with gr.Group(visible=False) as panel_htn:
                gr.HTML('<div class="q-header">❤️ Gestational Hypertension — Symptom Questions</div>')
                htn_sys1  = gr.Textbox(label="Systolic BP – first reading", placeholder="e.g. 145")
                htn_dia1  = gr.Textbox(label="Diastolic BP – first reading", placeholder="e.g. 95")
                htn_sys2  = gr.Textbox(label="Systolic BP – second reading (optional)", placeholder="e.g. 142")
                htn_dia2  = gr.Textbox(label="Diastolic BP – second reading (optional)", placeholder="e.g. 93")
                htn_weeks = gr.Textbox(label="Onset: how many weeks after conception?", placeholder="e.g. 22")
                htn_head  = gr.Radio(YES_NO, label="Headache?", value="No")
                htn_blur  = gr.Radio(YES_NO, label="Blurry vision?", value="No")

            # ── Nausea & Vomiting ─────────────────────────────
            with gr.Group(visible=False) as panel_nv:
                gr.HTML('<div class="q-header">🤢 Nausea & Vomiting — Symptom Questions</div>')
                nv_freq = gr.Textbox(label="Frequency of vomiting per day (number)", placeholder="e.g. 3")
                nv_eat  = gr.Radio(YES_NO, label="Are you able to eat?", value="Yes")
                nv_dehy = gr.Radio(YES_NO, label="Any signs of dehydration (dark urine, no urination, extreme thirst)?", value="No")
                nv_wt   = gr.Radio(YES_NO, label="Significant weight loss?", value="No")
                nv_days = gr.Textbox(label="How long have you experienced this condition in days?", placeholder="e.g. 4")

            # ── Headache ──────────────────────────────────────
            with gr.Group(visible=False) as panel_ha:
                gr.HTML('<div class="q-header">🤕 Headache — Symptom Questions</div>')
                ha_hbp      = gr.Radio(YES_NO, label="Do you experience headaches with high blood pressure?", value="No")
                ha_blur     = gr.Radio(YES_NO, label="Do you experience any blurry vision, flashing lights, or swelling of extremities?", value="No")
                ha_intensity= gr.Radio(["Mild (tight band)", "Intense (pulsating)"], label="What is intensity?", value="Mild (tight band)")
                ha_improve  = gr.Radio(YES_NO, label="Does it improve with rest, hydration, or food?", value="Yes")

            # ── Fever ─────────────────────────────────────────
            with gr.Group(visible=False) as panel_fv:
                gr.HTML('<div class="q-header">🌡️ Fever — Symptom Questions</div>')
                fv_temp   = gr.Textbox(label="Temperature (Fahrenheit)", placeholder="e.g. 101.2")
                fv_days   = gr.Textbox(label="Duration in days", placeholder="e.g. 2")
                fv_assoc  = gr.Radio(YES_NO, label="Any associated symptoms like cough, UTI, or infection?", value="No")
                fv_chills = gr.Radio(YES_NO, label="Chills or cold?", value="No")
                fv_wbc    = gr.Textbox(label="WBCs (optional)", placeholder="e.g. 11.0")
                fv_plt    = gr.Textbox(label="Platelet count (optional)", placeholder="e.g. 180")

    # ── Condition change → show relevant panel instantly ──────
    all_panels = [panel_urti, panel_uti, panel_dm, panel_hm, panel_gerd,
                  panel_asth, panel_dep, panel_skin, panel_thy, panel_htn,
                  panel_nv, panel_ha, panel_fv]

    selected_condition.change(
        fn=show_condition_panel,
        inputs=selected_condition,
        outputs=all_panels,
        queue=False
    )

    # ── Analyze Button ────────────────────────────────────────
    with gr.Row(elem_classes="btn-row"):
        analyze_btn = gr.Button("🔬 Analyze & Generate Instant Report", variant="primary", size="lg", elem_classes="analyze-btn")

    # ── Output ────────────────────────────────────────────────
    with gr.Row():
        with gr.Column(elem_classes="output-panel"):
            gr.HTML('<div class="section-header output-header"><span class="section-icon">📊</span> Clinical Assessment Report</div>')
            output = gr.Textbox(
                label="", lines=28,
                placeholder="Your personalized pregnancy health assessment will appear here instantly...",
                elem_classes="output-box"
            )

    # ── Visual Analytics + AI Toolbox ─────────────────────────
    with gr.Row(elem_classes="analytics-row"):
        with gr.Column(scale=1, elem_classes="analytics-card"):
            gr.HTML('''
              <div class="analytics-heading chart-heading">
                <span class="heading-icon">📈</span>
                Visual Analytics
              </div>
              <div class="analytics-badge teal">📊 Symptom Match Chart</div>
            ''')
            with gr.Column(elem_classes="analytics-card-body chart-image-wrap"):
                chart_output = gr.Image(label="", type="filepath", visible=False)

        with gr.Column(scale=1, elem_classes="analytics-card"):
            gr.HTML('''
              <div class="analytics-heading ai-heading">
                <span class="heading-icon">🧠</span>
                AI Explanation Toolbox
              </div>
              <div class="analytics-badge navy">✨ Powered by Groq · Llama 3.3</div>
            ''')
            with gr.Column(elem_classes="analytics-card-body"):
                ai_explanation = gr.Textbox(
                    label="",
                    lines=7,
                    placeholder="AI-generated explanation will appear here after analysis...",
                    elem_classes="toolbox-text",
                    visible=False
                )

    # Red flag check + compute
    def analyze_with_redflag(
        red_flags, condition, trimester, allergy, allergy_types,
        uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
        dm_history, dm_thirst, dm_urination, dm_glucose,
        hm_diff, hm_hard, hm_bleed, hm_pain,
        gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
        asth_wheeze, asth_hard, asth_tight, asth_rapid,
        dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
        sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
        thy_cluster, thy_tsh,
        uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
        htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
        nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
        ha_hbp, ha_blur, ha_intensity, ha_improve,
        fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
    ):
        # Red flag check — stop immediately
        critical = [f for f in (red_flags or []) if f != "None"]
        if critical:
            alert_text = """⚠️ URGENT ALERT:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nThis may require immediate medical attention.\n\nPlease seek emergency care immediately.\n\n🚨 Red flag(s) reported: """ + ", ".join(critical) + """\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nSTOP — Do not proceed. Go to nearest emergency facility."""
            return alert_text, gr.update(visible=False), gr.update(visible=False)

        # 1. Run existing clinical logic
        report = compute_result(
            condition, trimester, allergy, allergy_types,
            uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
            dm_history, dm_thirst, dm_urination, dm_glucose,
            hm_diff, hm_hard, hm_bleed, hm_pain,
            gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
            asth_wheeze, asth_hard, asth_tight, asth_rapid,
            dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
            sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
            thy_cluster, thy_tsh,
            uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
            htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
            nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
            ha_hbp, ha_blur, ha_intensity, ha_improve,
            fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
        )

        # 2. Extract confidence/severity from report text
        confidence = "HIGH" if "Confidence:  HIGH" in report else \
                     "MODERATE" if "Confidence:  MODERATE" in report else "LOW"
        severity   = "CONCERNING" if "Severity:    CONCERNING" in report else \
                     "MODERATE"   if "Severity:    MODERATE"   in report else "MILD"
        special_alert = ""
        for line in report.splitlines():
            if line.startswith("⚠️ Possible") or line.startswith("⚠️ Severe") or \
               line.startswith("⚠️ High") or line.startswith("⚠️ Fasting") or \
               line.startswith("⚠️ TSH") or line.startswith("⚠️ Elevated"):
                special_alert = line.strip()
                break

        # 3. Get symptom labels & answers
        symptom_labels, yes_answers = extract_symptoms(
            condition,
            uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
            dm_history, dm_thirst, dm_urination, dm_glucose,
            hm_diff, hm_hard, hm_bleed, hm_pain,
            gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
            asth_wheeze, asth_hard, asth_tight, asth_rapid,
            dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
            sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
            thy_cluster, thy_tsh,
            uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
            htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
            nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
            ha_hbp, ha_blur, ha_intensity, ha_improve,
            fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
        )

        # 4 & 5. Generate chart + Groq explanation in parallel with hard timeout
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_chart = executor.submit(
                generate_chart, condition, confidence, severity,
                symptom_labels, yes_answers
            )
            future_ai = executor.submit(
                get_ai_explanation, condition, trimester, confidence, severity,
                symptom_labels, yes_answers, special_alert
            )
            try:
                chart_path = future_chart.result(timeout=20)
            except Exception:
                chart_path = None
            try:
                explanation = future_ai.result(timeout=18)
            except Exception:
                explanation = "⚠️ AI explanation timed out. Please try again."

        return (report,
                gr.update(value=chart_path, visible=True),
                gr.update(value=explanation, visible=True))

    ALL_INPUTS = [
        red_flags, selected_condition, trimester, allergy, allergy_types,
        uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
        dm_history, dm_thirst, dm_urination, dm_glucose,
        hm_diff, hm_hard, hm_bleed, hm_pain,
        gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
        asth_wheeze, asth_hard, asth_tight, asth_rapid,
        dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
        sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
        thy_cluster, thy_tsh,
        uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
        htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
        nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
        ha_hbp, ha_blur, ha_intensity, ha_improve,
        fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
    ]

    # ── STEP 1: Report + Chart — instant, no queue ────────────
    def step1_report_and_chart(
        red_flags, condition, trimester, allergy, allergy_types,
        uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
        dm_history, dm_thirst, dm_urination, dm_glucose,
        hm_diff, hm_hard, hm_bleed, hm_pain,
        gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
        asth_wheeze, asth_hard, asth_tight, asth_rapid,
        dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
        sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
        thy_cluster, thy_tsh,
        uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
        htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
        nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
        ha_hbp, ha_blur, ha_intensity, ha_improve,
        fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
    ):
        critical = [f for f in (red_flags or []) if f != "None"]
        if critical:
            alert_text = "⚠️ URGENT ALERT:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nThis may require immediate medical attention.\n\nPlease seek emergency care immediately.\n\n🚨 Red flag(s) reported: " + ", ".join(critical) + "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nSTOP — Do not proceed. Go to nearest emergency facility."
            return alert_text, gr.update(visible=False), gr.update(value="", visible=False)

        report = compute_result(
            condition, trimester, allergy, allergy_types,
            uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
            dm_history, dm_thirst, dm_urination, dm_glucose,
            hm_diff, hm_hard, hm_bleed, hm_pain,
            gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
            asth_wheeze, asth_hard, asth_tight, asth_rapid,
            dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
            sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
            thy_cluster, thy_tsh,
            uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
            htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
            nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
            ha_hbp, ha_blur, ha_intensity, ha_improve,
            fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
        )

        symptom_labels, yes_answers = extract_symptoms(
            condition,
            uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
            dm_history, dm_thirst, dm_urination, dm_glucose,
            hm_diff, hm_hard, hm_bleed, hm_pain,
            gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
            asth_wheeze, asth_hard, asth_tight, asth_rapid,
            dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
            sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
            thy_cluster, thy_tsh,
            uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
            htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
            nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
            ha_hbp, ha_blur, ha_intensity, ha_improve,
            fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
        )

        confidence = "HIGH" if "Confidence:  HIGH" in report else                      "MODERATE" if "Confidence:  MODERATE" in report else "LOW"
        severity   = "CONCERNING" if "Severity:    CONCERNING" in report else                      "MODERATE"   if "Severity:    MODERATE"   in report else "MILD"

        try:
            chart_path = generate_chart(condition, confidence, severity, symptom_labels, yes_answers)
        except Exception:
            chart_path = None

        return (report,
                gr.update(value=chart_path, visible=chart_path is not None),
                gr.update(value="⏳ Generating AI explanation...", visible=True))

    # ── STEP 2: AI Explanation only — fires right after step 1 ─
    def step2_ai_explanation(
        red_flags, condition, trimester, allergy, allergy_types,
        uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
        dm_history, dm_thirst, dm_urination, dm_glucose,
        hm_diff, hm_hard, hm_bleed, hm_pain,
        gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
        asth_wheeze, asth_hard, asth_tight, asth_rapid,
        dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
        sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
        thy_cluster, thy_tsh,
        uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
        htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
        nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
        ha_hbp, ha_blur, ha_intensity, ha_improve,
        fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
    ):
        critical = [f for f in (red_flags or []) if f != "None"]
        if critical or not condition or not trimester:
            return gr.update(visible=False)

        symptom_labels, yes_answers = extract_symptoms(
            condition,
            uti_burn, uti_freq, uti_fever, uti_flank, uti_wbc,
            dm_history, dm_thirst, dm_urination, dm_glucose,
            hm_diff, hm_hard, hm_bleed, hm_pain,
            gerd_burn, gerd_meals, gerd_lying, gerd_sour, gerd_dysph, gerd_blood,
            asth_wheeze, asth_hard, asth_tight, asth_rapid,
            dep_sad, dep_interest, dep_energy, dep_sleep, dep_conc,
            sk_rash, sk_itch, sk_pain, sk_swell, sk_disc,
            thy_cluster, thy_tsh,
            uri_cough, uri_throat, uri_nose, uri_fever, uri_wbc,
            htn_sys1, htn_dia1, htn_sys2, htn_dia2, htn_weeks, htn_head, htn_blur,
            nv_freq, nv_eat, nv_dehy, nv_wt, nv_days,
            ha_hbp, ha_blur, ha_intensity, ha_improve,
            fv_temp, fv_days, fv_assoc, fv_chills, fv_wbc, fv_plt
        )
        confidence = "MODERATE"
        severity = "MILD"
        explanation = get_ai_explanation(
            condition, trimester, confidence, severity,
            symptom_labels, yes_answers, ""
        )
        return gr.update(value=explanation, visible=True)

    # Step 1 fires instantly — report + chart, no queue
    analyze_btn.click(
        fn=step1_report_and_chart,
        inputs=ALL_INPUTS,
        outputs=[output, chart_output, ai_explanation],
        queue=False
    ).then(
        # Step 2 fires right after — AI explanation only
        fn=step2_ai_explanation,
        inputs=ALL_INPUTS,
        outputs=ai_explanation,
        queue=False
    )
    
    gr.HTML("""
    <div class="disclaimer-footer">
      <p>⚕️ <strong>Medical Disclaimer:</strong> Maternal GestaGen is a clinical decision <em>support</em> tool only.
      Always consult a qualified healthcare professional before making any medication decisions during pregnancy.
      In case of emergency, call your local emergency number immediately.</p>
    </div>
    """)

if __name__ == "__main__":
    demo.launch(js="""
    function() {
        function fixDropdown() {
            const dropdown = document.querySelector('.dropdown-field, .gradio-dropdown');
            if (!dropdown) return;
            const input = dropdown.querySelector('input');
            if (!input) return;
            input.addEventListener('click', () => {
                setTimeout(() => {
                    const ul = document.querySelector('ul.options');
                    if (!ul) return;
                    const wrap = dropdown.querySelector('.wrap');
                    const rect = wrap.getBoundingClientRect();
                    
                }, 10);   /* 10ms — catches the list before browser reflows it */
            });
        }
        setTimeout(fixDropdown, 1200);
    }
    """)


