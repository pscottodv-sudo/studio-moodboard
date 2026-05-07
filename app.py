import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import random
import textwrap
from collections import Counter
import math

# --- 1. CONFIGURAZIONE INTERFACCIA E STATO ---
st.set_page_config(page_title="Studio Moodboard Pro", layout="wide", initial_sidebar_state="collapsed")

if 'app_mode' not in st.session_state: st.session_state.app_mode = 'home'
if 'models_list' not in st.session_state: st.session_state.models_list = [{"name": "", "photo": None}]
if 'crew_list' not in st.session_state: st.session_state.crew_list = []
if 'concept_text' not in st.session_state: st.session_state.concept_text = ""
if 'custom_palette' not in st.session_state: st.session_state.custom_palette = []
if 'extracted_from' not in st.session_state: st.session_state.extracted_from = []

# --- CSS STILE "NOTHING" (Stabile, Leggibile, No Emoji, Arrotondato) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DotGothic16&family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif !important; color: #000000 !important; }
    h1, h2, h3 { font-family: 'DotGothic16', monospace !important; text-transform: uppercase; letter-spacing: 1.5px; }
    .stApp { background-color: #F4F4F4 !important; background-image: radial-gradient(#CCCCCC 1px, transparent 1px); background-size: 20px 20px; }
    header {visibility: hidden;} footer {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { background-color: #FFFFFF; border: 2px solid #000000; border-radius: 50px; padding: 6px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 50px; padding: 10px 20px; color: #666666; font-family: 'DotGothic16', monospace !important; font-size: 16px !important; background-color: transparent; border: none !important; }
    .stTabs [aria-selected="true"] { background-color: #000000 !important; color: #FFFFFF !important; }
    .stButton>button { border-radius: 999px !important; background-color: #FFFFFF !important; color: #000000 !important; font-family: 'DotGothic16', monospace !important; font-size: 18px !important; border: 2px solid #000000 !important; padding: 12px 24px !important; box-shadow: 4px 4px 0px #000000 !important; text-transform: uppercase; }
    .stButton>button:hover { background-color: #E60000 !important; color: #FFFFFF !important; border-color: #E60000 !important; transform: translate(2px, 2px); box-shadow: 2px 2px 0px #000000 !important; }
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div { background-color: #FFFFFF !important; border: 2px solid #000000 !important; border-radius: 24px !important; padding: 12px 16px !important; color: #000000 !important; font-family: 'Inter', sans-serif !important; }
    .stSelectbox [data-baseweb="select"] * { color: #000000 !important; -webkit-text-fill-color: #000000 !important; opacity: 1 !important; }
    ul[role="listbox"] { background-color: #FFFFFF !important; border: 2px solid #000000 !important; border-radius: 16px !important; }
    li[role="option"] { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
    li[role="option"]:hover { background-color: #E60000 !important; color: #FFFFFF !important; }
    label { font-family: 'DotGothic16', monospace !important; text-transform: uppercase; margin-left: 8px; }
    [data-testid="column"] { background-color: #FFFFFF; border-radius: 32px; padding: 24px; border: 2px solid #000000; box-shadow: 6px 6px 0px rgba(0,0,0,0.05); }
    /* Override per Color Picker compatto */
    [data-testid="stColorPicker"] { margin-top: -10px; }
</style>
""", unsafe_allow_html=True)

THEMES = {
    "Neutro (Soft)": {"bg": "#FFFFFF", "text": "#111111", "accent": "#888888"},
    "Editorial (Ivory)": {"bg": "#F4F1EA", "text": "#281E14", "accent": "#A08C78"},
    "Dark Mode": {"bg": "#121212", "text": "#E9ECEF", "accent": "#ADB5BD"}
}

# --- FUNZIONI DI UTILITÀ ---
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def get_fonts():
    font_paths = ["arial.ttf", "Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:\\Windows\\Fonts\\arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"]
    for path in font_paths:
        try:
            return (ImageFont.truetype(path, 280), ImageFont.truetype(path, 90), ImageFont.truetype(path, 55), ImageFont.truetype(path, 75))
        except IOError: continue
    try: return (ImageFont.load_default(size=280), ImageFont.load_default(size=90), ImageFont.load_default(size=55), ImageFont.load_default(size=75))
    except TypeError: d = ImageFont.load_default(); return d, d, d, d

def color_distance(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def extract_palette_hex(image_files, num_colors=6):
    all_colors = []
    for img_f in image_files[:8]: 
        if hasattr(img_f, 'seek'): img_f.seek(0)
        img = Image.open(img_f).convert("RGB").resize((60, 60))
        all_colors.extend(list(img.getdata()))
    if not all_colors: return []
    counts = Counter([(r//15*15, g//15*15, b//15*15) for r, g, b in all_colors])
    sorted_colors = [item[0] for item in counts.most_common(100)]
    unique_palette = []
    if sorted_colors:
        unique_palette.append(sorted_colors[0])
        for c in sorted_colors[1:]:
            if len(unique_palette) >= num_colors: break
            if all(color_distance(c, existing) > 65 for existing in unique_palette):
                unique_palette.append(c)
    return ['#%02x%02x%02x' % c for c in unique_palette]

def ai_enhance_concept():
    current = st.session_state.concept_text
    if len(current) < 5: 
        st.session_state.concept_text = "Progetto focalizzato su estetica contemporanea, combinando elementi brutalisti e minimali per una narrazione visiva d'impatto."
    else:
        st.session_state.concept_text = f"Un'esplorazione visiva audace: {current}. L'atmosfera fonde contrasti crudi con un'estetica editoriale high-end, creando un immaginario memorabile e all'avanguardia."

# --- MOTORE UNICO CANVAS ---
def create_pro_document(details, models, crew, mood_imgs, loc_imgs, styling, custom_palette, logo_img=None):
    bg, tx, ac = hex_to_rgb(styling["bg"]), hex_to_rgb(styling["text"]), hex_to_rgb(styling["accent"])
    w = 2500 if styling["orientation"].startswith("Verticale") else 3500
    m = 180 
    f_h1, f_h2, f_lbl, f_val = get_fonts()
    
    canvas = Image.new("RGB", (w, 15000), bg)
    draw = ImageDraw.Draw(canvas)
    current_y = m

    title_wrapped = textwrap.fill(details["title"].upper(), width=18)
    for line in title_wrapped.split('\n'):
        draw.text((m, current_y), line, fill=tx, font=f_h1)
        current_y += 300
    
    current_y += 80
    desc_wrapped = textwrap.fill(details["desc"], width=50)
    for line in desc_wrapped.split('\n'):
        draw.text((m, current_y), line, fill=ac, font=f_h2)
        current_y += 110
    
    current_y += 200
    
    info_cols = [("BRAND", details.get("brand", "")), ("LOCATION", details.get("location", "")), ("DATE", details.get("date", ""))]
    col_x, step_x = m, (w - 2*m) // 3
    for label, value in info_cols:
        if value:
            draw.text((col_x, current_y), label, fill=ac, font=f_lbl)
            draw.text((col_x, current_y + 80), value.upper(), fill=tx, font=f_val)
        col_x += step_x
    current_y += 350

    if loc_imgs:
        l_w = (w - 2*m - 100) // 3
        max_loc_h, x_pos = 0, m
        for img_f in loc_imgs[:3]:
            if hasattr(img_f, 'seek'): img_f.seek(0)
            l_img = Image.open(img_f).convert("RGB")
            new_h = int(l_w * (l_img.height / l_img.width))
            l_img = l_img.resize((l_w, new_h), Image.Resampling.LANCZOS)
            canvas.paste(l_img, (x_pos, current_y))
            max_loc_h = max(max_loc_h, new_h)
            x_pos += l_w + 50
        current_y += max_loc_h + 150

    if crew or any(mod['name'] for mod in models):
        draw.line([(m, current_y), (w-m, current_y)], fill=ac, width=4)
        current_y += 100
        draw.text((m, current_y), "// TEAM E CAST", fill=ac, font=f_lbl)
        current_y += 150

        if crew:
            cx = m
            for i, member in enumerate(crew):
                if i > 0 and i % 4 == 0: cx = m; current_y += 250
                draw.text((cx, current_y), member['role'].upper(), fill=ac, font=f_lbl)
                draw.text((cx, current_y + 70), member['name'].upper(), fill=tx, font=f_val)
                cx += (w - 2*m) // 4
            current_y += 350

        if any(mod['name'] for mod in models):
            mod_w = (w - 2*m - 150) // 5
            mx = m
            max_m_h = 0
            for mod in models:
                if mod['photo']:
                    if hasattr(mod['photo'], 'seek'): mod['photo'].seek(0)
                    m_img = Image.open(mod['photo']).convert("RGB")
                    # RIPRISTINATO: Mantiene le proporzioni originali senza tagliare
                    m_h = int(mod_w * (m_img.height / m_img.width))
                    m_img = m_img.resize((mod_w, m_h), Image.Resampling.LANCZOS)
                    canvas.paste(m_img, (mx, current_y))
                    draw.text((mx, current_y + m_h + 30), mod['name'].upper(), fill=tx, font=f_val)
                    max_m_h = max(max_m_h, m_h)
                mx += mod_w + 35
            current_y += max_m_h + 300

    if mood_imgs:
        draw.line([(m, current_y), (w-m, current_y)], fill=ac, width=4)
        current_y += 100
        draw.text((m, current_y), "// DIREZIONE VISIVA", fill=ac, font=f_lbl)
        current_y += 150

        if styling['layout'] == "Scrapbook STRONG":
            cols = 3 if w < 3000 else 4
            grid_w = (w - 2*m) // cols
            last_y_in_grid = current_y
            for i, img_f in enumerate(mood_imgs):
                col, row = i % cols, i // cols
                if hasattr(img_f, 'seek'): img_f.seek(0)
                img = Image.open(img_f).convert("RGB")
                if styling['filter'] == "Bianco e Nero": img = img.convert("L").convert("RGB")
                img_w = int(grid_w * random.uniform(0.85, 0.98))
                img_h = int(img_w * (img.height/img.width))
                img = img.resize((img_w, img_h), Image.Resampling.LANCZOS)
                img_final = ImageOps.expand(img, border=25, fill='#FFFFFF').convert("RGBA")
                img_final = img_final.rotate(random.randint(-4, 4), expand=True, resample=Image.BICUBIC)
                pos_x = m + (col * grid_w) + random.randint(-40, 40)
                pos_y = current_y + (row * (grid_w + 150)) + random.randint(-30, 30)
                if img_final.mode == "RGBA": canvas.paste(img_final, (int(pos_x), int(pos_y)), img_final)
                else: canvas.paste(img_final, (int(pos_x), int(pos_y)))
                last_y_in_grid = max(last_y_in_grid, pos_y + img_final.height)
            current_y = last_y_in_grid + 200
        else:
            cols = 3
            mb_w = (w - 2*m - 100) // cols
            col_y = [current_y] * cols
            for img_f in mood_imgs:
                if hasattr(img_f, 'seek'): img_f.seek(0)
                img = Image.open(img_f).convert("RGB")
                new_h = int(mb_w * (img.height/img.width))
                img = img.resize((mb_w, new_h), Image.Resampling.LANCZOS)
                target = col_y.index(min(col_y))
                canvas.paste(img, (m + target*(mb_w+50), col_y[target]))
                col_y[target] += new_h + 50
            current_y = max(col_y) + 200

    if custom_palette:
        draw.line([(m, current_y), (w-m, current_y)], fill=ac, width=4)
        current_y += 100
        draw.text((m, current_y), "// PALETTE COLORI DEL PROGETTO", fill=ac, font=f_lbl)
        current_y += 150
        
        swatch_size = (w - 2*m - (len(custom_palette)-1)*60) // len(custom_palette)
        px = m
        for hex_code in custom_palette:
            rgb_col = hex_to_rgb(hex_code)
            draw.rectangle([px, current_y, px + swatch_size, current_y + swatch_size], fill=rgb_col)
            draw.text((px, current_y + swatch_size + 40), hex_code.upper(), fill=tx, font=f_val)
            px += swatch_size + 60
        current_y += swatch_size + 400

    if logo_img:
        if hasattr(logo_img, 'seek'): logo_img.seek(0)
        logo = Image.open(logo_img).convert("RGBA")
        target_logo_w = int(w * 0.15) 
        target_logo_h = int(target_logo_w * (logo.height / logo.width))
        logo = logo.resize((target_logo_w, target_logo_h), Image.Resampling.LANCZOS)
        canvas.paste(logo, (w - m - target_logo_w, current_y), logo)
        current_y += target_logo_h + 100

    final_canvas = canvas.crop((0, 0, w, current_y + m))
    return [final_canvas]

# --- INTERFACCIA STREAMLIT ---
if st.session_state.app_mode == 'home':
    st.markdown("<h1 style='text-align:center; margin-top:10vh; font-size:4rem;'>MOODBOARD.OS</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1]) 
    with c2:
        if st.button("MODO BASE", use_container_width=True): st.session_state.app_mode = 'base'; st.rerun()
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("MODO AVANZATO", use_container_width=True): st.session_state.app_mode = 'adv'; st.rerun()

elif st.session_state.app_mode in ['base', 'adv']:
    col_nav, _ = st.columns([1, 5])
    with col_nav:
        if st.button("RETURN"): st.session_state.app_mode = 'home'; st.rerun()
    
    col_left, col_right = st.columns([1.5, 2.5], gap="large")
    
    with col_left:
        st.markdown("<h3>CONFIGURAZIONE</h3>", unsafe_allow_html=True)
        
        if st.session_state.app_mode == 'adv':
            tab1, tab2, tab3, tab4 = st.tabs(["PROGETTO", "LOCATION", "TEAM", "VISUAL"])
            with tab1:
                t_title = st.text_input("TITOLO PROGETTO")
                st.text_area("CONCEPT", key="concept_text")
                if st.button("MIGLIORA CON AI"): ai_enhance_concept(); st.rerun()
                st.divider()
                s_orient = st.radio("FORMATO FOGLIO", ["Verticale", "Orizzontale"], horizontal=True)
                logo_file = st.file_uploader("LOGO AGENZIA / STUDIO (Opzionale, PNG trasparente)", type=['png'])
            with tab2:
                t_brand = st.text_input("CLIENTE / BRAND")
                t_loc_name = st.text_input("NOME LOCATION")
                t_date = st.text_input("DATA SHOOTING")
                loc_photos = st.file_uploader("FOTO LOCATION", accept_multiple_files=True)
            with tab3:
                for i, member in enumerate(st.session_state.crew_list):
                    r1, r2 = st.columns(2)
                    member['role'] = r1.text_input(f"RUOLO", value=member['role'], key=f"r_{i}")
                    member['name'] = r2.text_input(f"NOME", value=member['name'], key=f"n_{i}")
                if st.button("+ AGGIUNGI CREW"): st.session_state.crew_list.append({"role": "", "name": ""}); st.rerun()
                st.divider()
                for i, mod in enumerate(st.session_state.models_list):
                    mod['name'] = st.text_input(f"MODELLO {i+1}", value=mod['name'], key=f"mn_{i}")
                    mod['photo'] = st.file_uploader(f"FOTO MODELLO {i+1}", key=f"mp_{i}")
                if st.button("+ AGGIUNGI MODELLO"): st.session_state.models_list.append({"name": "", "photo": None}); st.rerun()
            with tab4:
                s_theme = st.selectbox("TEMA COLORI BASE", list(THEMES.keys()))
                s_layout = st.selectbox("IMPAGINAZIONE", ["Minimal", "Scrapbook STRONG"])
                s_filter = st.selectbox("FILTRO FOTO", ["Nessuno", "Bianco e Nero"])
                st.divider()
                mood_photos = st.file_uploader("MOODBOARD (REFERENCE VISIVE)", accept_multiple_files=True)
                
                if mood_photos:
                    current_filenames = [f.name for f in mood_photos]
                    if st.session_state.extracted_from != current_filenames:
                        st.session_state.custom_palette = extract_palette_hex(mood_photos)
                        st.session_state.extracted_from = current_filenames
                    
                    st.markdown("<b>MODIFICA PALETTE ESTRATTA:</b>", unsafe_allow_html=True)
                    if st.session_state.custom_palette:
                        cols = st.columns(len(st.session_state.custom_palette))
                        for idx, col in enumerate(cols):
                            st.session_state.custom_palette[idx] = col.color_picker(f"C{idx+1}", st.session_state.custom_palette[idx], key=f"cp_{idx}")

        else: 
            t_title = st.text_input("TITOLO PROGETTO")
            st.text_area("CONCEPT / DESCRIZIONE", key="concept_text")
            if st.button("MIGLIORA CON AI"): ai_enhance_concept(); st.rerun()
            mood_photos = st.file_uploader("MOODBOARD (REFERENCE VISIVE)", accept_multiple_files=True)
            
            if mood_photos:
                current_filenames = [f.name for f in mood_photos]
                if st.session_state.extracted_from != current_filenames:
                    st.session_state.custom_palette = extract_palette_hex(mood_photos)
                    st.session_state.extracted_from = current_filenames
                st.markdown("<b>MODIFICA PALETTE:</b>", unsafe_allow_html=True)
                cols = st.columns(len(st.session_state.custom_palette))
                for idx, col in enumerate(cols):
                    st.session_state.custom_palette[idx] = col.color_picker(f"C{idx+1}", st.session_state.custom_palette[idx], key=f"cp_base_{idx}")

            with st.expander("STILE E LAYOUT"):
                s_orient = st.radio("FORMATO FOGLIO", ["Verticale", "Orizzontale"], horizontal=True)
                s_theme = st.selectbox("TEMA COLORI", list(THEMES.keys()))
                s_layout = st.selectbox("IMPAGINAZIONE", ["Minimal", "Scrapbook STRONG"])
                s_filter = st.selectbox("FILTRO FOTO", ["Nessuno", "Bianco e Nero"])
            
            t_brand, t_loc_name, t_date, loc_photos, logo_file = "", "", "", [], None

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("GENERA TREATMENT", use_container_width=True):
            with st.spinner("Compilazione in corso..."):
                styling = {**THEMES[s_theme], "layout": s_layout, "filter": s_filter, "orientation": s_orient}
                st.session_state.final_pages = create_pro_document(
                    {"title": t_title, "desc": st.session_state.concept_text, "brand": t_brand, "location": t_loc_name, "date": t_date},
                    st.session_state.models_list if st.session_state.app_mode == 'adv' else [],
                    st.session_state.crew_list if st.session_state.app_mode == 'adv' else [],
                    mood_photos, loc_photos, styling, st.session_state.custom_palette, logo_file
                )

    with col_right:
        st.markdown("<h3>ANTEPRIMA</h3>", unsafe_allow_html=True)
        if 'final_pages' in st.session_state:
            img = st.session_state.final_pages[0]
            st.image(img, use_container_width=True)
            
            # RIPRISTINATO: Esportazione diretta in PDF ad alta risoluzione
            pdf_buf = io.BytesIO()
            img.save(pdf_buf, format="PDF", resolution=150.0)
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="SCARICA PDF",
                data=pdf_buf.getvalue(),
                file_name=f"{t_title.replace(' ','_')}_TREATMENT.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("Compila i dati e clicca 'GENERA TREATMENT' per sbloccare l'esportazione del PDF.")
