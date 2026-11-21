import hmac
import io
import json
import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="E-correct", page_icon="✓", layout="wide")

MIME = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "pdf": "application/pdf",
}
TYPES = ["png", "jpg", "jpeg", "webp", "pdf"]
NIVEAUX = ["6ème", "5ème", "4ème", "3ème", "2nde", "1ère", "Tle"]
TYPES_EVAL = ["Interrogation", "Devoir", "Composition"]

# Armoiries de la République togolaise (image intégrée, aucun fichier à ajouter)
ARMOIRIES_B64 = "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"

# ============================================================== DESIGN ====

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=DM+Sans:wght@400;500;700&display=swap');

:root {
  --foret: #153B2B;
  --foret-2: #1F5240;
  --citron: #E4F56B;
  --sauge: #EAF0E4;
  --creme: #F7F9F3;
  --encre: #17261E;
  --gris: #5E6F64;
  --bord: #D5DECF;
}

.stApp { background: var(--sauge); color: var(--encre); font-family: 'DM Sans', sans-serif; }
button, input, textarea { font-family: 'DM Sans', sans-serif !important; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.2rem; max-width: 1100px; }

h1, h2, h3 { font-family: 'Bricolage Grotesque', sans-serif; color: var(--foret); letter-spacing: -0.01em; }

[data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--bord); }

/* Emblème */
.embleme { display: flex; flex-direction: column; align-items: center; gap: 6px; margin: 2px 0 12px; }
.embleme img { height: 78px; }
.embleme .rt { font-size: .72rem; font-weight: 700; letter-spacing: .06em; color: var(--foret); }

/* Barre du haut */
.topbar { background: var(--foret); color: #fff; border-radius: 18px; padding: 14px 22px;
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.brand { display: flex; align-items: center; gap: 12px; font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 700; font-size: 1.4rem; }
.mark { width: 36px; height: 36px; border-radius: 50%; background: var(--citron); color: var(--foret);
  display: grid; place-items: center; font-size: .95rem; font-weight: 700; }
.pill { background: var(--citron); color: var(--foret); font-weight: 700; border-radius: 999px;
  padding: 6px 14px; font-size: .85rem; }

/* Étapes */
.steps { display: flex; gap: 10px; margin-bottom: 18px; flex-wrap: wrap; }
.step { flex: 1; min-width: 150px; background: #fff; border: 1px solid var(--bord); border-radius: 14px;
  padding: 10px 14px; display: flex; align-items: center; gap: 10px; color: var(--gris); font-weight: 500; }
.step .dot { width: 26px; height: 26px; border-radius: 50%; background: var(--sauge);
  display: grid; place-items: center; font-weight: 700; color: var(--foret); }
.step.active { border-color: var(--foret); color: var(--foret); box-shadow: 0 0 0 2px var(--citron); }
.step.active .dot { background: var(--foret); color: #fff; }
.step.done { color: var(--foret); }
.step.done .dot { background: var(--citron); }

/* Onglets */
button[data-baseweb="tab"] { font-weight: 600; color: var(--gris); }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--foret); }
div[data-baseweb="tab-highlight"] { background: var(--foret) !important; }

/* Boutons */
.stButton > button, .stDownloadButton > button {
  border-radius: 12px; font-weight: 600; border: 1.5px solid var(--foret);
  background: #fff; color: var(--foret); padding: .55rem 1.1rem; }
.stButton > button p, .stDownloadButton > button p { color: inherit !important; }
.stButton > button:hover, .stDownloadButton > button:hover {
  background: var(--citron); border-color: var(--foret); color: var(--foret); }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
  background: var(--foret); color: #fff; }
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
  background: var(--citron); color: var(--foret); }
.stButton > button:disabled { opacity: .45; }

/* Zone de dépôt */
[data-testid="stFileUploaderDropzone"] { background: var(--creme); border: 2px dashed var(--foret-2);
  border-radius: 16px; }

/* Cartes de chiffres */
[data-testid="stMetric"] { background: #fff; border: 1px solid var(--bord); border-radius: 16px; padding: 14px 16px; }
[data-testid="stMetricValue"] { font-family: 'Bricolage Grotesque', sans-serif; color: var(--foret); }

/* Copies repliables */
[data-testid="stExpander"] { background: #fff; border: 1px solid var(--bord) !important; border-radius: 16px; }

/* Pastilles */
.badge { display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: .8rem; font-weight: 700;
  margin-right: 6px; }
.badge.ok { background: var(--citron); color: var(--foret); }
.badge.todo { background: #FCE9C8; color: #8A4B08; }
.badge.info { background: #fff; color: var(--foret); border: 1px solid var(--bord); }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ================================================================ OUTILS ===


def txt(x):
    return "" if x is None or (isinstance(x, float) and pd.isna(x)) else str(x).strip()


def num(x):
    v = pd.to_numeric(x, errors="coerce")
    return 0.0 if pd.isna(v) else float(v)


def secret(nom):
    """Lit un secret (Streamlit Cloud) ou une variable d'environnement."""
    try:
        valeur = st.secrets.get(nom, "")
    except Exception:
        valeur = ""
    return str(valeur or os.environ.get(nom, "")).strip()


def decode_qr(data):
    try:
        import cv2
        import numpy as np
    except ImportError:
        return "missing", None
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return "none", None
    valeur, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return ("ok", valeur) if valeur else ("none", None)


def badges_epreuve(ex):
    return (
        f'<span class="badge info">{ex["niveau"]}</span>'
        f'<span class="badge info">{ex["matiere"] or "Matière non précisée"}</span>'
        f'<span class="badge info">{ex["type"]}</span>'
        f'<span class="badge info">Correcteur : {ex["correcteur"] or "non précisé"}</span>'
    )


# ================================================================ GEMINI ===


def to_parts(pages):
    return [types.Part.from_bytes(data=b, mime_type=m) for b, m in pages]


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text)


def ask_gemini(client, model, prompt, pages, tries=3):
    contents = [prompt] + to_parts(pages)
    config = types.GenerateContentConfig(
        response_mime_type="application/json", temperature=0.2
    )
    last_error = None
    for i in range(tries):
        try:
            resp = client.models.generate_content(
                model=model, contents=contents, config=config
            )
            return parse_json(resp.text)
        except Exception as e:  # 503, JSON invalide, etc.
            last_error = e
            time.sleep(2 * (i + 1))
    raise last_error


def contexte(exam):
    return (
        f"Contexte : classe de {exam['niveau']}, matière : {exam['matiere'] or 'non précisée'}, "
        f"type d'évaluation : {exam['type'].lower()}. Adapte le vocabulaire et le niveau de détail à cette classe.\n\n"
    )


PROMPT_CORRIGE = """Tu es un enseignant expert. Les fichiers joints sont une ÉPREUVE d'examen.
Ta tâche : produire le CORRIGÉ TYPE complet.

Règles :
- Repère le barème écrit sur l'épreuve (points par question ou sous-question) et RESPECTE-LE. N'invente jamais un barème : s'il est absent pour une question, mets bareme = 0.
- Traite chaque question et sous-question séparément (numero : "1", "1.a", "Exercice 2 - Q3", etc.).
- notion : intitulé court (2 à 5 mots) de la notion ou compétence du programme évaluée par la question (ex. "Loi d'Ohm", "Conjugaison au passé composé"). Réutilise exactement le même intitulé quand plusieurs questions évaluent la même notion.
- reponse_attendue : réponse correcte détaillée, avec les étapes de calcul, formules et unités quand c'est pertinent.
- Écris en français.

Réponds UNIQUEMENT en JSON, sans texte autour, avec ce format :
{"questions": [
  {"numero": "...", "notion": "...", "enonce": "...", "reponse_attendue": "...", "bareme": 0.0}
]}"""


def prompt_corrige(exam):
    return contexte(exam) + PROMPT_CORRIGE


def prompt_correction(corrige, exam):
    return contexte(exam) + f"""Tu es un correcteur rigoureux et juste. Voici le corrigé type validé par l'enseignant (JSON) :
{json.dumps(corrige, ensure_ascii=False)}

Les fichiers joints sont les pages de la COPIE d'un élève. Corrige-la question par question.

Règles :
- Compare la réponse de l'élève au corrigé. Accorde des points partiels si la méthode est juste mais le résultat faux, ou si la réponse est incomplète.
- Ne dépasse jamais le barème de la question.
- Si la question n'est pas traitée, points_obtenus = 0.
- Si l'écriture est illisible, dis-le dans le commentaire et ne devine pas.
- Ne lis, ne rapporte et ne mentionne aucun nom d'élève.
- Commentaire : une phrase courte et utile en français.

Réponds UNIQUEMENT en JSON, sans texte autour, avec ce format :
{{"notes": [{{"numero": "...", "points_obtenus": 0.0, "commentaire": "..."}}],
  "appreciation": "bilan global en 2 phrases"}}"""


# ================================================================== ÉTAT ===

DEFAUTS = {
    "corrige_df": None,
    "corrige_valide": None,
    "exam": None,
    "resultats": [],
    "cam_pages": [],
    "cam_n": 0,
    "up_n": 0,
    "flash": None,
}
for k, v in DEFAUTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def clamp(df):
    d = df.copy()
    d["points"] = pd.to_numeric(d["points"], errors="coerce").fillna(0).clip(lower=0)
    d["points"] = d[["points", "sur"]].min(axis=1)
    return d


def note_de(r):
    return float(r["detail"]["points"].sum())


def bilan_notions(validees, seuil):
    morceaux = []
    for r in validees:
        d = r["detail"].copy()
        d["eleve"] = r["libelle"]
        morceaux.append(d)
    tout = pd.concat(morceaux)
    lignes = []
    for notion, g in tout.groupby("notion", sort=False):
        sur = g["sur"].sum()
        if sur <= 0:
            continue
        taux = g["points"].sum() / sur * 100
        par_eleve = g.groupby("eleve", sort=False)[["points", "sur"]].sum()
        par_eleve = par_eleve[par_eleve["sur"] > 0]
        difficulte = par_eleve[par_eleve["points"] / par_eleve["sur"] * 100 < seuil].index.tolist()
        lignes.append(
            {
                "Notion": notion,
                "Maîtrise (%)": round(taux),
                "Statut": "Maîtrisée" if taux >= seuil else "À reprendre",
                "Élèves en difficulté": len(difficulte),
                "_liste": difficulte,
            }
        )
    return lignes


# ================================================================ SIDEBAR ===

cle_serveur = secret("GEMINI_API_KEY")
if cle_serveur:
    # Application en ligne : la clé reste cachée, personne ne peut la voir.
    api_key = cle_serveur
    model = secret("GEMINI_MODEL") or "gemini-3.6-flash"
else:
    st.sidebar.header("Configuration")
    api_key = st.sidebar.text_input(
        "Clé API Gemini",
        type="password",
        help="Clé gratuite sur Google AI Studio.",
    )
    model = st.sidebar.text_input("Modèle Gemini", value="gemini-3.6-flash")
st.sidebar.divider()
if st.sidebar.button("Nouvelle épreuve"):
    for k, v in DEFAUTS.items():
        st.session_state[k] = [] if isinstance(v, list) else v
    st.rerun()

# ================================================================ EN-TÊTE ===

resultats = st.session_state.resultats
valide = st.session_state.corrige_valide is not None
a_des_copies = len(resultats) > 0
a_des_validees = any(r["statut"] == "Validée" for r in resultats)

etats = [valide, a_des_copies, a_des_validees]
actif = next((i for i, e in enumerate(etats) if not e), 2)
noms = ["Épreuve et corrigé", "Correction des copies", "Résultats"]
etapes = ""
for i, (nom, fait) in enumerate(zip(noms, etats)):
    classe = "done" if fait else ("active" if i == actif else "")
    marque = "✓" if fait else str(i + 1)
    etapes += f'<div class="step {classe}"><span class="dot">{marque}</span>{nom}</div>'

st.markdown(
    '<div class="embleme">'
    f'<img src="data:image/png;base64,{ARMOIRIES_B64}" alt="Armoiries de la République togolaise">'
    '<div class="rt">RÉPUBLIQUE TOGOLAISE</div></div>'
    '<div class="topbar"><div class="brand"><span class="mark">E✓</span>E-correct</div>'
    '<span class="pill">Correction assistée par IA</span></div>'
    f'<div class="steps">{etapes}</div>',
    unsafe_allow_html=True,
)

mot_de_passe = secret("MOT_DE_PASSE")
if mot_de_passe and not st.session_state.get("acces_ok"):
    saisie = st.text_input("Mot de passe d'accès", type="password")
    if saisie and hmac.compare_digest(saisie, mot_de_passe):
        st.session_state.acces_ok = True
        st.rerun()
    elif saisie:
        st.error("Mot de passe incorrect.")
    st.stop()

if not api_key:
    st.info("Entre ta clé API Gemini dans le menu de gauche pour commencer.")
    st.stop()

client = genai.Client(api_key=api_key)

tab1, tab2, tab3 = st.tabs(noms)

# ====================================================== ÉTAPE 1 : CORRIGÉ ===

with tab1:
    st.subheader("Informations sur l'épreuve")
    a, b = st.columns(2)
    niveau = a.selectbox("Niveau de la classe", NIVEAUX, key="ex_niveau")
    matiere = b.text_input("Matière", key="ex_matiere", placeholder="Ex. Physique-Chimie")
    c, d = st.columns(2)
    type_eval = c.selectbox("Type d'évaluation", TYPES_EVAL, key="ex_type")
    correcteur = d.text_input("Nom du correcteur", key="ex_correcteur")

    st.subheader("Envoie l'épreuve")
    st.caption("Photos ou PDF, avec le barème écrit sur l'épreuve.")
    epreuve = st.file_uploader(
        "Épreuve",
        type=TYPES,
        accept_multiple_files=True,
        key="epreuve",
        label_visibility="collapsed",
    )

    if st.button("Générer le corrigé type", type="primary", disabled=not epreuve):
        exam = {
            "id": datetime.now().strftime("EX-%y%m%d-%H%M"),
            "niveau": niveau,
            "matiere": matiere.strip(),
            "type": type_eval,
            "correcteur": correcteur.strip(),
        }
        pages = [
            (f.getvalue(), MIME.get(f.name.rsplit(".", 1)[-1].lower(), f.type))
            for f in epreuve
        ]
        with st.spinner("Génération du corrigé en cours..."):
            try:
                data = ask_gemini(client, model, prompt_corrige(exam), pages)
                cols = ["numero", "notion", "enonce", "reponse_attendue", "bareme"]
                df0 = pd.DataFrame(data["questions"]).reindex(columns=cols)
                df0["notion"] = df0["notion"].fillna("Général").replace("", "Général")
                st.session_state.corrige_df = df0
                st.session_state.exam = exam
                st.session_state.corrige_valide = None
                st.session_state.resultats = []
            except Exception as e:
                st.error(f"La génération a échoué : {e}")

    if st.session_state.corrige_df is not None:
        st.subheader("Corrigé type")
        st.caption(
            "Relis-le et corrige-le si besoin avant de le valider. "
            "Tu peux modifier les cellules, ajouter ou supprimer des lignes."
        )
        verrouille = st.session_state.corrige_valide is not None
        df = st.data_editor(
            st.session_state.corrige_df,
            num_rows="dynamic",
            disabled=verrouille,
            column_config={
                "numero": st.column_config.TextColumn("N°", width="small"),
                "notion": st.column_config.TextColumn("Notion évaluée"),
                "enonce": st.column_config.TextColumn("Énoncé"),
                "reponse_attendue": st.column_config.TextColumn("Réponse attendue"),
                "bareme": st.column_config.NumberColumn("Barème", min_value=0.0, step=0.25),
            },
            key="editeur_corrige",
        )
        total = pd.to_numeric(df["bareme"], errors="coerce").fillna(0).sum()
        st.metric("Total du barème", f"{total:g}")
        if total == 0:
            st.warning("Aucun barème détecté : renseigne les points dans la colonne Barème.")

        if not verrouille:
            if st.button("Valider le corrigé", type="primary", disabled=total == 0):
                propre = []
                for _, row in df.iterrows():
                    if not txt(row["numero"]):
                        continue
                    propre.append(
                        {
                            "numero": txt(row["numero"]),
                            "notion": txt(row["notion"]) or "Général",
                            "enonce": txt(row["enonce"]),
                            "reponse_attendue": txt(row["reponse_attendue"]),
                            "bareme": num(row["bareme"]),
                        }
                    )
                st.session_state.corrige_df = df
                st.session_state.corrige_valide = propre
                st.rerun()
        else:
            st.success("Corrigé validé. Passe à l'onglet « Correction des copies ».")
            if st.button("Modifier le corrigé"):
                st.session_state.corrige_valide = None
                st.session_state.resultats = []
                st.rerun()

    if st.session_state.corrige_valide is not None and st.session_state.exam:
        st.subheader("Fiche de l'épreuve")
        st.markdown(badges_epreuve(st.session_state.exam), unsafe_allow_html=True)

# ======================================================= ÉTAPE 2 : COPIES ===

with tab2:
    if st.session_state.flash:
        st.success(st.session_state.flash)
        st.session_state.flash = None

    if st.session_state.corrige_valide is None:
        st.info("Valide d'abord le corrigé type dans l'onglet « Épreuve et corrigé ».")
    else:
        corrige = st.session_state.corrige_valide
        exam = st.session_state.exam
        numero_copie = len(resultats) + 1
        copie_id = f"Copie #{numero_copie:03d}"

        st.subheader(copie_id)
        st.markdown(badges_epreuve(exam), unsafe_allow_html=True)
        cle = st.session_state.up_n

        with st.expander("Scanner le code QR de la copie", expanded=True):
            sc1, sc2 = st.columns(2)
            photo_qr = sc1.camera_input("Photographier le code QR", key=f"qrcam_{cle}")
            fichier_qr = sc2.file_uploader(
                "ou téléverser une photo du code QR",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"qrup_{cle}",
            )
            source = photo_qr if photo_qr is not None else fichier_qr
            if source is not None:
                etat, valeur = decode_qr(source.getvalue())
                if etat == "missing":
                    st.info("Pour lire les codes QR, installe : python -m pip install opencv-python-headless")
                elif etat == "ok":
                    if st.session_state.get(f"qrlast_{cle}") != valeur:
                        st.session_state[f"qrlast_{cle}"] = valeur
                        st.session_state[f"qr_{cle}"] = valeur
                    st.success(f"Code lu : {valeur}")
                else:
                    st.warning("Code non lu. Rapproche-toi, évite les reflets, ou saisis le code à la main.")

        code_qr = st.text_input(
            "Code QR de la copie",
            key=f"qr_{cle}",
            help="Rempli automatiquement après le scan. Tu peux aussi le saisir à la main.",
        )
        n1, n2 = st.columns(2)
        nom_eleve = n1.text_input("Nom de l'élève (facultatif)", key=f"nom_{cle}")
        prenoms = n2.text_input("Prénoms (facultatif)", key=f"pre_{cle}")
        st.caption("Le code, le nom et les prénoms restent dans l'application : ils ne sont pas envoyés à l'IA.")

        st.write("Ajoute toutes les pages de la même copie, puis lance la correction.")
        t_up, t_cam = st.tabs(["Téléverser", "Photographier"])

        with t_up:
            ups = st.file_uploader(
                "Pages de la copie",
                type=TYPES,
                accept_multiple_files=True,
                key=f"up_{st.session_state.up_n}",
                label_visibility="collapsed",
            )

        with t_cam:
            photo = st.camera_input(
                "Photographie une page de la copie",
                key=f"cam_{st.session_state.cam_n}",
            )
            if photo is not None and st.button("Ajouter cette page", key=f"addcam_{st.session_state.cam_n}"):
                st.session_state.cam_pages.append((photo.getvalue(), "image/jpeg"))
                st.session_state.cam_n += 1
                st.rerun()
            if st.session_state.cam_pages:
                st.caption(f"{len(st.session_state.cam_pages)} photo(s) ajoutée(s)")
                if st.button("Vider les photos"):
                    st.session_state.cam_pages = []
                    st.rerun()

        pages = [
            (f.getvalue(), MIME.get(f.name.rsplit(".", 1)[-1].lower(), f.type))
            for f in (ups or [])
        ] + list(st.session_state.cam_pages)

        st.caption(f"{len(pages)} page(s) prête(s) pour la correction")

        if st.button("Corriger la copie", type="primary", disabled=not pages):
            with st.spinner("Correction en cours..."):
                try:
                    res = ask_gemini(client, model, prompt_correction(corrige, exam), pages)
                    par_numero = {str(n.get("numero")): n for n in res.get("notes", [])}
                    lignes = []
                    for q in corrige:
                        n = par_numero.get(q["numero"], {})
                        sur = q["bareme"]
                        pts = num(n.get("points_obtenus"))
                        lignes.append(
                            {
                                "numero": q["numero"],
                                "notion": q["notion"],
                                "points": max(0.0, min(pts, sur)),
                                "sur": sur,
                                "commentaire": n.get("commentaire", "Non traitée"),
                            }
                        )
                    complet = f"{nom_eleve.strip()} {prenoms.strip()}".strip()
                    st.session_state.resultats.append(
                        {
                            "id": copie_id,
                            "nom": nom_eleve.strip(),
                            "prenoms": prenoms.strip(),
                            "code_qr": code_qr.strip(),
                            "libelle": complet or code_qr.strip() or copie_id,
                            "detail": pd.DataFrame(lignes),
                            "appreciation": res.get("appreciation", ""),
                            "statut": "À valider",
                        }
                    )
                    st.session_state.cam_pages = []
                    st.session_state.cam_n += 1
                    st.session_state.up_n += 1
                    st.session_state.flash = (
                        f"{copie_id} corrigée. "
                        "Ouvre l'onglet « Résultats » pour vérifier et valider la note."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"La correction a échoué : {e}")

# ===================================================== ÉTAPE 3 : RÉSULTATS ===

with tab3:
    if not resultats:
        st.info("Les résultats apparaîtront ici dès la première copie corrigée.")
    else:
        exam = st.session_state.exam or {}
        total_bareme = float(resultats[0]["detail"]["sur"].sum())
        validees = [r for r in resultats if r["statut"] == "Validée"]

        def sur20(r):
            return note_de(r) / total_bareme * 20 if total_bareme else 0.0

        # ---- Statistiques
        st.subheader("Statistiques")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Copies corrigées", len(resultats))
        c2.metric("Copies validées", f"{len(validees)}/{len(resultats)}")
        if validees:
            notes20 = pd.Series([sur20(r) for r in validees])
            c3.metric("Moyenne", f"{notes20.mean():.2f}/20")
            c4.metric("Médiane", f"{notes20.median():.2f}/20")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Meilleure note", f"{notes20.max():.2f}/20")
            d2.metric("Plus faible note", f"{notes20.min():.2f}/20")
            d3.metric("Réussite (≥ 10/20)", f"{round(100 * (notes20 >= 10).mean())} %")
            d4.metric("Élèves ≥ 10/20", f"{int((notes20 >= 10).sum())}/{len(notes20)}")
        else:
            c3.metric("Moyenne", "—")
            c4.metric("Médiane", "—")
            st.caption("Les statistiques portent sur les copies validées. Valide une copie pour les voir.")

        if validees:
            g1, g2 = st.columns(2)
            with g1:
                st.markdown("**Répartition des notes**")
                tranches = pd.cut(
                    notes20,
                    bins=[0, 5, 10, 15, 20.01],
                    right=False,
                    labels=["0–5", "5–10", "10–15", "15–20"],
                )
                st.bar_chart(tranches.value_counts().sort_index(), color="#153B2B")
            with g2:
                st.markdown("**Réussite par question (%)**")
                somme = pd.concat([r["detail"] for r in validees]).groupby("numero", sort=False)[["points", "sur"]].sum()
                taux = (somme["points"] / somme["sur"].where(somme["sur"] > 0) * 100).round(0)
                st.bar_chart(taux, color="#1F5240")

        # ---- Bilan des notions
        if validees:
            st.subheader("Bilan des notions")
            seuil = st.slider("Seuil de maîtrise (%)", 10, 90, 50, step=5)
            bilan = bilan_notions(validees, seuil)
            if bilan:
                table = pd.DataFrame(bilan).drop(columns=["_liste"])
                st.dataframe(
                    table,
                    hide_index=True,
                    column_config={
                        "Maîtrise (%)": st.column_config.ProgressColumn(
                            "Maîtrise (%)", min_value=0, max_value=100, format="%d %%"
                        )
                    },
                )
                a_reprendre = [b for b in bilan if b["Élèves en difficulté"] > 0]
                if a_reprendre:
                    st.markdown("**Élèves qui n'ont pas maîtrisé la notion**")
                    for b in a_reprendre:
                        with st.expander(f"{b['Notion']} — {b['Élèves en difficulté']} élève(s)"):
                            st.markdown("\n".join(f"- {e}" for e in b["_liste"]))
                else:
                    st.success("Toutes les notions sont maîtrisées par tous les élèves validés.")

        # ---- Tableau et export
        st.subheader("Notes")
        synthese = pd.DataFrame(
            [
                {
                    "Copie": r["id"],
                    "Code QR": r.get("code_qr", ""),
                    "Nom": r["nom"],
                    "Prénoms": r["prenoms"],
                    "Note": note_de(r),
                    "Sur": total_bareme,
                    "Note /20": round(sur20(r), 2),
                    "Statut": r["statut"],
                    "Niveau": exam.get("niveau", ""),
                    "Matière": exam.get("matiere", ""),
                    "Type": exam.get("type", ""),
                    "Correcteur": exam.get("correcteur", ""),
                }
                for r in resultats
            ]
        )
        st.dataframe(synthese, hide_index=True)
        st.download_button(
            "Télécharger les notes (CSV)",
            synthese.to_csv(index=False).encode("utf-8-sig"),
            file_name="notes.csv",
            mime="text/csv",
        )

        # ---- Vérification et validation
        st.subheader("Vérifier et valider les copies")
        st.caption("Modifie les points ou les commentaires si l'IA s'est trompée, puis valide la note.")
        for idx, r in enumerate(resultats):
            fait = r["statut"] == "Validée"
            titre = f"{r['id']} — {r['libelle']} — {note_de(r):g}/{total_bareme:g} — {r['statut']}"
            with st.expander(titre, expanded=not fait and idx == len(resultats) - 1):
                classe = "ok" if fait else "todo"
                st.markdown(f'<span class="badge {classe}">{r["statut"]}</span>', unsafe_allow_html=True)
                if r["appreciation"]:
                    st.write(r["appreciation"])
                edite = st.data_editor(
                    r["detail"],
                    disabled=True if fait else ["numero", "notion", "sur"],
                    hide_index=True,
                    column_config={
                        "numero": st.column_config.TextColumn("N°", width="small"),
                        "notion": st.column_config.TextColumn("Notion"),
                        "points": st.column_config.NumberColumn("Points", min_value=0.0, step=0.25),
                        "sur": st.column_config.NumberColumn("Sur"),
                        "commentaire": st.column_config.TextColumn("Commentaire"),
                    },
                    key=f"ed_{r['id']}_{r['statut']}",
                )
                st.markdown(f"**Total : {float(clamp(edite)['points'].sum()):g} / {total_bareme:g}**")
                if not fait:
                    if st.button("Valider la note", key=f"val_{r['id']}", type="primary"):
                        r["detail"] = clamp(edite)
                        r["statut"] = "Validée"
                        st.rerun()
                else:
                    if st.button("Rouvrir pour modifier", key=f"open_{r['id']}"):
                        r["statut"] = "À valider"
                        st.rerun()
