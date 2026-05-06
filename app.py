import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import random
import textwrap
from collections import Counter

# --- 1. CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Studio Moodboard Pro", layout="wide", initial_sidebar_state="collapsed")

# --- CSS STILE "NOTHING" ARROTONDATO + FIX DEFINITIVO SELECTBOX ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DotGothic16&family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. TIPOGRAFIA BASE (Niente Emoji) */
    html, body, [class*="css"] { 
        font-family: 'Inter', -apple-system, sans-serif !important; 
        color: #000000 !important;
    }
    
    /* Titoli con il font Dot-Matrix per il branding */
    h1, h2, h3 {
        font-family: 'DotGothic16', monospace !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* 2. SFONDO A GRIGLIA LEGGERA */
    .stApp { 
        background-color: #F4F4F4 !important; 
        background-image: radial-gradient(#CCCCCC 1px, transparent 1px);
        background-size: 20px 20px;
    }
    
    header {visibility: hidden;} footer {visibility: hidden;}

    /* 3. STILE SCHEDE (TABS) - Estremamente arrotondato (Pillola) */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: #FFFFFF;
        border: 2px solid #000000; 
        border-radius: 50px; 
        padding: 6px; 
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 50px; 
        padding: 10px 20px; 
        color: #666666;
        font-family: 'DotGothic16', monospace !important;
        font-size: 16px !important;
        background-color: transparent;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #000000 !important; 
        color: #FFFFFF !important; 
    }

    /* 4. BOTTONI PRINCIPALI - Forma a pillola perfetta */
    .stButton>button { 
        border-radius: 999px !important; 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        font-family: 'DotGothic16', monospace !important;
        font-size: 18px !important;
        font-weight: 400 !important; 
        border: 2px solid #000000 !important;
        padding: 12px 24px !important;
        transition: all 0.1s ease-in-out;
        box-shadow: 4px 4px 0px #000000 !important; 
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #E60000 !important; 
        color: #FFFFFF !important;
        border-color: #E60000 !important;
        transform: translate(2px, 2px); 
        box-shadow: 2px 2px 0px #000000 !important; 
    }
    .stButton>button:active {
        transform: translate(4px, 4px);
        box-shadow: 0px 0px 0px transparent !important; 
    }

    /* 5. CAMPI DI TESTO E INPUT - Arrotondamento marcato */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        border-radius: 24px !important; 
        padding: 12px 16px !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-family: 'Inter', sans-serif !important; 
        font-weight: 500 !important;
        box-shadow: none !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #E60000 !important; 
        outline: none !important;
    }
    
    /* ==================================================
       FIX DEFINITIVO SELECTBOX (TESTO INVISIBILE)
       ================================================== */
       
    /* FORZA IL TESTO NERO NELLA TENDINA CHIUSA */
    .stSelectbox [data-baseweb="select"] * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* FORZA IL COLORE DELLA TENDINA APERTA (MENU FLUTTUANTE) */
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        border-radius: 16px !important;
        padding: 8px !important;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.2) !important;
    }
    li[role="option"] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        background-color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        margin-bottom: 2px !important;
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #E60000 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    /* ================================================== */
    
    /* Etichette dei campi */
    label, .st-emotion-cache-10trnc2 {
        font-family: 'DotGothic16', monospace !important;
        font-size: 14px !important;
        color: #000000 !important;
        text-transform: uppercase;
        margin-left: 8px; 
    }

    /* 6. UPLOADER FILE */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #000000 !important;
        border-radius: 24px !important; 
        background-color: #FFFFFF !important;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #E60000 !important;
        background-color: rgba(230, 0, 0, 0.05) !important;
    }

    /* Contenitori laterali morbidi */
    [data-testid="column"] {
        background-color: #FFFFFF;
        border-radius: 32px; 
        padding: 24px;
        border: 2px solid #000000;
        box-shadow: 6px 6px 0px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

if 'app_mode' not in st.session_state: st.session_state.app_mode = 'home'
if 'models_list' not in st.session_state: st.session_state.models_list = [{"name": "", "photo": None}]
if 'crew_list' not in st.session_state: st.session_state.crew_list = []

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
    try:
        return (ImageFont.truetype("arial.ttf", 130), ImageFont.truetype("arial.ttf", 45),
                ImageFont.truetype("arial.ttf", 26), ImageFont.truetype("arial.ttf", 36))
    except:
        d = ImageFont.load_default()
        return d, d, d, d

def extract_palette(image_files, num_colors=6):
    colors = []
    for img_f in image_files[:5]: 
        if hasattr(img_f, 'seek'):
            img_f.seek(0)
        img = Image.open(img_f).convert("RGB").resize((50, 50))
        for r, g, b in img.getdata():
            colors.append((r - r%20, g - g%20, b - b%20))
    if not colors:
        return []
    most_common = Counter(colors).most_common(num_colors)
    return [c[0] for c in most_common]

# --- MOTORE UNICO CANVAS ---
def create_pro_document(details, models, crew, mood_imgs, loc_imgs, styling):
    bg, tx, ac = hex_to_rgb(styling["bg"]), hex_to_rgb(styling["text"]), hex_to_rgb(styling["accent"])
    w = 2000 if styling["orientation"].startswith("Verticale") else 3000
    m = 150 
    f_h1, f_h2, f_lbl, f_val = get_fonts()
    canvas = Image.new("RGB", (w, 10000), bg)
    draw = ImageDraw.Draw(canvas)
    current_y = m

    draw.text((m, current_y), details["title"].upper(), fill=tx, font=f_h1)
    current_y += 160
    draw.text((m, current_y), details["desc"], fill=ac, font=f_h2)
    current_y += 180
    
    info_cols = [("BRAND", details.get("brand", "")), ("LOCATION", details.get("location", "")), ("DATA", details.get("date", ""))]
    col_x, step_x = m, (w - 2*m) // 3
    for label, value in info_cols:
        if value:
            draw.text((col_x, current_y), label, fill=ac, font=f_lbl)
            draw.text((col_x, current_y + 45), value.upper(), fill=tx, font=f_val)
        col_x += step_x
    current_y += 200

    if loc_imgs:
        l_w = (w - 2*m - 60) // 3
        max_loc_h, x_pos = 0, m
        for img_f in loc_imgs[:3]:
            if hasattr(img_f, 'seek'): img_f.seek(0)
            l_img = Image.open(img_f).convert("RGB")
            new_h = int(l_w * (l_img.height / l_img.width))
            l_img = l_img.resize((l_w, new_h))
            canvas.paste(l_img, (x_pos, current_y))
            max_loc_h = max(max_loc_h, new_h)
            x_pos += l_w + 30
        current_y += max_loc_h + 100

    if crew or any(mod['name'] for mod in models):
        draw.line([(m, current_y), (w-m, current_y)], fill=ac, width=2)
        current_y += 60
        draw.text((m, current_y), "// TEAM & CASTING", fill=ac, font=f_lbl)
        current_y += 80

        if crew:
            cx = m
            for i, member in enumerate(crew):
                if i > 0 and i % 4 == 0: cx = m; current_y += 150
                draw.text((cx, current_y), member['role'].upper(), fill=ac, font=f_lbl)
                draw.text((cx, current_y + 35), member['name'].upper(), fill=tx, font=f_val)
                cx += (w - 2*m) // 4
            current_y += 200

        if any(mod['name'] for mod in models):
            mod_w = (w - 2*m - 120) // 5
            mx = m
            max_m_h = 0
            for mod in models:
                if mod['photo']:
                    if hasattr(mod['photo'], 'seek'): mod['photo'].seek(0)
                    m_img = Image.open(mod['photo']).convert("RGB")
                    m_h = int(mod_w * (m_img.height / m_img.width))
                    m_img = m_img.resize((mod_w, m_h))
                    canvas.paste(m_img, (mx, current_y))
                    draw.text((mx, current_y + m_h + 10), mod['name'].upper(), fill=tx, font=f_val)
                    max_m_h = max(max_m_h, m_h)
                mx += mod_w + 30
            current_y += max_m_h + 200

    if mood_imgs:
        draw.line([(m, current_y), (w-m, current_y)], fill=ac, width=2)
        current_y += 60
        draw.text((m, current_y), "// VISUAL DIRECTION", fill=ac, font=f_lbl)
        current_y += 120

        if styling['layout'] == "Scrapbook STRONG":
            cols = 3 if w < 2500 else 4
            grid_w = (w - 2*m) // cols
            last_y_in_grid = current_y
            for i, img_f in enumerate(mood_imgs):
                col, row = i % cols, i // cols
                if hasattr(img_f, 'seek'): img_f.seek(0)
                img = Image.open(img_f).convert("RGB")
                if styling['filter'] == "Bianco e Nero": img = img.convert("L").convert("RGB")
                img_w = int(grid_w * random.uniform(0.85, 0.95))
                img_h = int(img_w * (img.height/img.width))
                img = img.resize((img_w, img_h))
                img_final = ImageOps.expand(img, border=20, fill='#FFFFFF').convert("RGBA")
                img_final = img_final.rotate(random.randint(-4, 4), expand=True)
                pos_x = m + (col * grid_w) + random.randint(-40, 40)
                pos_y = current_y + (row * (grid_w + 100)) + random.randint(-30, 30)
                canvas.paste(img_final, (pos_x, pos_y), img_final)
                last_y_in_grid = max(last_y_in_grid, pos_y + img_final.height)
            current_y = last_y_in_grid + 150
        else:
            cols = 3
            mb_w = (w - 2*m - 80) // cols
            col_y = [current_y] * cols
            for img_f in mood_imgs:
                if hasattr(img_f, 'seek'): img_f.seek(0)
                img = Image.open(img_f).convert("RGB")
                new_h = int(mb_w * (img.height/img.width))
                img = img.resize((mb_w, new_h))
                target = col_y.index(min(col_y))
                canvas.paste(img, (m + target*(mb_w+40), col_y[target]))
                col_y[target] += new_h + 40
            current_y = max(col_y) + 150

    if mood_imgs:
        draw.line([(m, current_y), (w-m, current_y)], fill=ac, width=2)
        current_y += 60
        draw.text((m, current_y), "// COLOR PALETTE", fill=ac, font=f_lbl)
        current_y += 100
        
        palette = extract_palette(mood_imgs)
        if palette:
            swatch_size = (w - 2*m - (len(palette)-1)*40) // len(palette)
            px = m
            for color in palette:
                draw.rectangle([px, current_y, px + swatch_size, current_y + swatch_size], fill=color)
                hex_code = '#%02x%02x%02x' % color
                draw.text((px, current_y + swatch_size + 20), hex_code.upper(), fill=tx, font=f_val)
                px += swatch_size + 40
            current_y += swatch_size + 200

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
        if st.button("< RETURN"): st.session_state.app_mode = 'home'; st.rerun()
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.5, 2.5], gap="large")
    
    with col_left:
        st.markdown("<h3>SETUP</h3>", unsafe_allow_html=True)
        
        if st.session_state.app_mode == 'adv':
            tab1, tab2, tab3, tab4 = st.tabs(["PROJ", "LOCATION", "TEAM", "VISUAL"])
            with tab1:
                t_title = st.text_input("PROJECT TITLE")
                t_desc = st.text_area("CONCEPT")
                s_orient = st.radio("FORMAT", ["Verticale", "Orizzontale"], horizontal=True)
            with tab2:
                t_brand = st.text_input("BRAND")
                t_loc_name = st.text_input("LOCATION")
                t_date = st.text_input("DATE")
                loc_photos = st.file_uploader("UPLOAD LOCATION", accept_multiple_files=True)
            with tab3:
                for i, member in enumerate(st.session_state.crew_list):
                    r1, r2 = st.columns(2)
                    member['role'] = r1.text_input(f"ROLE", value=member['role'], key=f"r_{i}")
                    member['name'] = r2.text_input(f"NAME", value=member['name'], key=f"n_{i}")
                if st.button("+ ADD CREW"): st.session_state.crew_list.append({"role": "", "name": ""}); st.rerun()
                st.divider()
                for i, mod in enumerate(st.session_state.models_list):
                    mod['name'] = st.text_input(f"MODEL {i+1}", value=mod['name'], key=f"mn_{i}")
                    mod['photo'] = st.file_uploader(f"PHOTO {i+1}", key=f"mp_{i}")
                if st.button("+ ADD MODEL"): st.session_state.models_list.append({"name": "", "photo": None}); st.rerun()
            with tab4:
                mood_photos = st.file_uploader("MOODBOARD (REFS)", accept_multiple_files=True)
                s_theme = st.selectbox("COLOR THEME", list(THEMES.keys()))
                s_layout = st.selectbox("LAYOUT", ["Minimal", "Scrapbook STRONG"])
                s_filter = st.selectbox("FILTER", ["Nessuno", "Bianco e Nero"])
        
        else: 
            t_title = st.text_input("PROJECT TITLE")
            t_desc = st.text_area("CONCEPT / DESC")
            mood_photos = st.file_uploader("MOODBOARD REFS", accept_multiple_files=True)
            
            with st.expander("STYLE OVERRIDE"):
                s_orient = st.radio("FORMAT", ["Verticale", "Orizzontale"], horizontal=True)
                s_theme = st.selectbox("COLOR THEME", list(THEMES.keys()))
                s_layout = st.selectbox("LAYOUT", ["Minimal", "Scrapbook STRONG"])
                s_filter = st.selectbox("FILTER", ["Nessuno", "Bianco e Nero"])
            
            t_brand, t_loc_name, t_date, loc_photos = "", "", "", []

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("COMPILE TREATMENT", use_container_width=True):
            with st.spinner("EXECUTING..."):
                styling = {**THEMES[s_theme], "layout": s_layout, "filter": s_filter, "orientation": s_orient}
                st.session_state.final_pages = create_pro_document(
                    {"title": t_title, "desc": t_desc, "brand": t_brand, "location": t_loc_name, "date": t_date},
                    st.session_state.models_list if st.session_state.app_mode == 'adv' else [],
                    st.session_state.crew_list if st.session_state.app_mode == 'adv' else [],
                    mood_photos, loc_photos, styling
                )

    with col_right:
        st.markdown("<h3>PREVIEW</h3>", unsafe_allow_html=True)
        if 'final_pages' in st.session_state:
            img = st.session_state.final_pages[0]
            st.image(img, use_container_width=True)
            
            pdf_buf = io.BytesIO()
            img.save(pdf_buf, format="PDF", resolution=100.0)
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="DOWNLOAD PDF",
                data=pdf_buf.getvalue(),
                file_name=f"{t_title.replace(' ','_')}_TREATMENT.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("AWAITING INPUT... COMPILE DATA ON THE LEFT TO GENERATE PREVIEW.")