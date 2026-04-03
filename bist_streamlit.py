import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── SAYFA AYARLARI ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BIST Sinyal Tarayıcı",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── HİSSE LİSTESİ ────────────────────────────────────────────────────────────
TOP50 = {
    "POLTK","BMSTL","LIDER","AVTUR","MOBTL","ISCTR","DOAS","TRCAS","CMBTN","ISBTR",
    "LUKSK","DOHOL","DOCO","VBTYZ","MERIT","TEHOL","VAKKO","ALGYO","FRIGO","BMSCH",
    "HEDEF","ETILR","ASELS","ESCOM","AKSA","ULUUN","GRTHO","OYAKC","FMIZP","RYSAS",
    "KARSN","SMRVA","BRYAT","YAPRK","NETAS","SELEC","SAFKR","CELHA","ECILC","BURCE",
    "GLCVY","EGEEN","ACSEL","KUYAS","RYGYO","INDES","MAGEN","AKSEN","ARCLK","YYAPI",
}

HISSELER = [
    "ACSEL","ADEL","ADESE","ADGYO","AFYON","AGHOL","AGESA","AGROT","AHSGY","AHGAZ",
    "AKYHO","AKENR","AKFGY","AKFIS","AKFYE","AKHAN","ATEKS","AKSGY","AKMGY","AKSA",
    "AKSEN","AKGRT","AKSUE","ALCAR","ALGYO","ALARK","ALBRK","ALCTL","ALFAS","ALKIM",
    "ALKA","AYCES","ALTNY","ALKLC","ALVES","ANSGR","AEFES","ANHYT","ASUZU","ANGEN",
    "ANELE","ARCLK","ARDYZ","ARENA","ARFYE","ARMGD","ARSAN","ARTMS","ARZUM","ASGYO",
    "ASELS","ASTOR","ATAGY","ATATR","ATAKP","AGYO","ATSYH","ATLAS","ATATP","AVOD",
    "AVGYO","AVTUR","AVHOL","AVPGY","AYDEM","AYEN","AYES","AYGAZ","AZTEK","A1CAP",
    "A1YEN","BAGFS","BAHKM","BAKAB","BALAT","BALSU","BNTAS","BANVT","BARMA","BASGZ",
    "BASCM","BEGYO","BTCIM","BSOKE","BYDNR","BAYRK","BERA","BRKSN","BESLR","BESTE",
    "BJKAS","BEYAZ","BIENY","BIGTK","BLCYT","BIMAS","BINBN","BIOEN","BRKVY","BRKO",
    "BIGEN","BRLSM","BRMEN","BIZIM","BLUME","BMSTL","BMSCH","BOBET","BORSK","BORLS",
    "BRSAN","BRYAT","BFREN","BOSSA","BRISA","BULGS","BURCE","BURVA","BUCIM","BVSAN",
    "BIGCH","CRFSA","CASA","CEMZY","CEOEM","CCOLA","CONSE","COSMO","CRDFA","CVKMD",
    "CWENE","CGCAM","CANTE","CATES","CLEBI","CELHA","CEMAS","CEMTS","CMBTN","CMENT",
    "CIMSA","CUSAN","DAGI","DAPGM","DARDL","DGATE","DCTTR","DMSAS","DENGE","DZGYO",
    "DERIM","DERHL","DESA","DESPC","DSTKF","DEVA","DNISI","DIRIT","DITAS","DMRGD",
    "DOCO","DOFRB","DOFER","DOHOL","DGNMO","ARASE","DOGUB","DGGYO","DOAS","DOKTA",
    "DURDO","DURKN","DUNYH","DYOBY","EBEBK","ECOGR","ECZYT","EDATA","EDIP","EFOR",
    "EGEEN","EGGUB","EGPRO","EGSER","EPLAS","EGEGY","ECILC","EKIZ","EKOS","EKSUN",
    "ELITE","EMKEL","EMNIS","EKGYO","EMPAE","ENDAE","ENJSA","ENERY","ENKAI","ENSRI",
    "ERBOS","ERCB","EREGL","KIMMR","ERSU","ESCAR","ESCOM","ESEN","ETILR","EUKYO",
    "EUYO","ETYAT","EUHOL","TEZOL","EUREN","EUPWR","EYGYO","FADE","FMIZP","FENER",
    "FLAP","FONET","FROTO","FORMT","FRMPL","FORTE","FRIGO","FZLGY","GWIND","GSRAY",
    "GARFA","GRNYO","GATEG","GEDIK","GEDZA","GLCVY","GENIL","GENTS","GENKM","GEREL",
    "GZNMI","GIPTA","GMTAS","GESAN","GLBMD","GLYHO","GOODY","GOKNR","GOLTS","GOZDE",
    "GRTHO","GSDDE","GSDHO","GUBRF","GLRYH","GLRMK","GUNDG","GRSEL","SAHOL","HLGYO",
    "HRKET","HATEK","HATSN","HDFGS","HEDEF","HEKTS","HKTM","HTTBT","HOROZ","HUBVC",
    "HUNER","HURGZ","ENTRA","ICBCT","ICUGS","INGRM","INVEO","INVES","ISKPL","IEYHO",
    "IDGYO","IHEVA","IHLGM","IHGZT","IHAAS","IHLAS","IHYAY","IMASM","INDES","INFO",
    "INTEK","INTEM","ISDMR","ISFIN","ISGYO","ISGSY","ISMEN","ISYAT","ISBIR","ISSEN",
    "IZINV","IZENR","IZMDC","IZFAS","JANTS","KFEIN","KLKIM","KLSER","KLYPV","KAPLM",
    "KRDMA","KRDMB","KRDMD","KAREL","KARSN","KRTEK","KARTN","KTLEV","KATMR","KAYSE",
    "KENT","KRVGD","KERVN","TCKRC","KZBGY","KLGYO","KLRHO","KMPUR","KLMSN","KCAER",
    "KCHOL","KOCMT","KLSYN","KNFRT","KONTR","KONYA","KONKA","KGYO","KORDS","KRPLS",
    "KOTON","KOPOL","KRGYO","KRSTL","KRONT","KSTUR","KUVVA","KUYAS","KBORU","KZGYO",
    "KUTPO","KTSKR","LIDER","LIDFA","LILAK","LMKDC","LINK","LOGO","LKMNH","LRSHO",
    "LUKSK","LYDHO","LYDYE","MACKO","MAKIM","MAKTK","MANAS","MAGEN","MARKA","MARMR",
    "MAALT","MRSHL","MRGYO","MARTI","MTRKS","MAVI","MZHLD","MEDTR","MEGMT","MEGAP",
    "MEKAG","MNDRS","MEPET","MERCN","MERIT","MERKO","METRO","MTRYO","MEYSU","MHRGY",
    "MIATK","MGROS","MSGYO","MPARK","MMCAS","MOBTL","MOGAN","MNDTR","MOPAS","EGEPO",
    "NATEN","NTGAZ","NTHOL","NETAS","NETCD","NIBAS","NUHCM","NUGYO","OBAMS","OBASE",
    "ODAS","ODINE","OFSYM","ONCSM","ONRYT","ORCAY","ORGE","ORMA","OSMEN","OSTIM",
    "OTKAR","OTTO","OYAKC","OYYAT","OYAYO","OYLUM","OZKGY","OZATD","OZGYO","OZRDN",
    "OZSUB","OZYSR","PAMEL","PNLSN","PAGYO","PAPIL","PRDGS","PRKME","PARSN","PASEU",
    "PSGYO","PAHOL","PATEK","PCILT","PGSUS","PEKGY","PENGD","PENTA","PSDTC","PETKM",
    "PKENT","PETUN","PINSU","PNSUT","PKART","PLTUR","POLHO","POLTK","PRZMA","RNPOL",
    "RALYH","RAYSG","REEDR","RYGYO","RYSAS","RODRG","ROYAL","RGYAS","RTALB","RUBNS",
    "RUZYE","SAFKR","SANEL","SNICA","SANFM","SANKO","SAMAT","SARKY","SASA","SVGYO",
    "SAYAS","SDTTR","SEGMN","SEKUR","SELEC","SELVA","SERNT","SRVGY","SEYKM","SILVR",
    "SNGYO","SKYLP","SMRTG","SMART","SODSN","SOKE","SKTAS","SONME","SNPAM","SUMAS",
    "SUNTK","SURGY","SUWEN","SMRVA","SEKFK","SEGYO","SKYMD","SKBNK","SOKM","TABGD",
    "TATGD","TATEN","TAVHL","TEKTU","TKFEN","TKNSA","TMPOL","TRHOL","TERA","TEHOL",
    "TGSAS","TOASO","TRGYO","TRMET","TRENJ","TLMAN","TSPOR","TDGYO","TSGYO","TUCLK",
    "TUKAS","TRCAS","TUREX","MARBL","TRILC","TCELL","TMSN","TUPRS","TRALT","THYAO",
    "PRKAB","TTKOM","TTRAK","TBORG","TURGG","GARAN","HALKB","ISATR","ISBTR","ISCTR",
    "ISKUR","KLNMA","TSKB","TURSG","SISE","VAKBN","UFUK","ULAS","ULUFA","ULUSE",
    "ULUUN","UMPAS","USAK","UCAYM","ULKER","UNLU","VAKFA","VAKFN","VKGYO","VKFYO",
    "VAKKO","VANGD","VBTYZ","VRGYO","VERUS","VERTU","VESBE","VESTL","VKING","VSNMD",
    "YKBNK","YAPRK","YATAS","YYLGD","YAYLA","YGGYO","YEOTK","YGYO","YYAPI","YESIL",
    "YBTAS","YIGIT","YONGA","YKSLN","YUNSA","ZGYO","ZEDUR","ZERGY","ZRGYO","ZOREN",
    "BINHO",
]

# ─── YARDIMCI FONKSİYONLAR ────────────────────────────────────────────────────
def ema(seri, periyot):
    if hasattr(seri, "squeeze"):
        seri = seri.squeeze()
    return seri.ewm(span=periyot, adjust=False).mean()

def atr_hesapla(df, periyot=14):
    close = df["Close"].squeeze() if hasattr(df["Close"], "squeeze") else df["Close"]
    high  = df["High"].squeeze()  if hasattr(df["High"],  "squeeze") else df["High"]
    low   = df["Low"].squeeze()   if hasattr(df["Low"],   "squeeze") else df["Low"]
    hl = high - low
    hc = (high - close.shift(1)).abs()
    lc = (low  - close.shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.ewm(span=periyot, adjust=False).mean()

def veri_cek(ticker, gun=300):
    try:
        df = yf.download(ticker + ".IS", period=f"{gun}d",
                         interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 60:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        for col in df.columns:
            v = df[col]
            df[col] = v.iloc[:, 0] if hasattr(v, "iloc") and v.ndim == 2 else v.squeeze()
        return df
    except Exception:
        return None

# ─── ENDEKS FİLTRESİ ──────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def endeks_kontrol():
    for sembol in ["XU100.IS", "^XU100", "BIST100.IS"]:
        try:
            df = yf.download(sembol, period="300d",
                             interval="1d", progress=False, auto_adjust=True)
            if df.empty or len(df) < 10:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            for col in df.columns:
                v = df[col]
                df[col] = v.iloc[:, 0] if hasattr(v, "iloc") and v.ndim == 2 else v.squeeze()
            df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()
            df.dropna(subset=["EMA200"], inplace=True)
            if df.empty: continue
            son      = df.iloc[-1]
            kapanis  = float(son["Close"])
            ema200   = float(son["EMA200"])
            aktif    = kapanis > ema200
            fark_pct = (kapanis - ema200) / ema200 * 100
            return aktif, kapanis, ema200, fark_pct
        except Exception:
            continue
    return None, None, None, None

# ─── SİNYAL TARAMA ────────────────────────────────────────────────────────────
def sinyal_tara(df, params):
    """
    Strateji:
      1. EMA trend: EMA20 > EMA50 > EMA100 > EMA200
      2. MACD histogram negatiften pozitife döndü
      3. YENİ: Fiyat EMA20 üzerinde olmalı
      4. YENİ: Hacim > 20 günlük ort. hacim x 1.5
    """
    atr_per     = params["atr_periyot"]
    atr_kat     = params["atr_katsayi"]
    rr          = params["rr_katsayi"]
    macd_hizli  = params["macd_hizli"]
    macd_yavas  = params["macd_yavas"]
    macd_sinyal = params["macd_sinyal"]
    hacim_carpan= params["hacim_carpan"]

    df = df.copy()
    for col in ["Open","High","Low","Close","Volume"]:
        if col in df.columns:
            v = df[col]
            df[col] = v.iloc[:, 0] if hasattr(v, "iloc") and v.ndim == 2 else v

    close  = df["Close"].squeeze()
    volume = df["Volume"].squeeze()

    df["EMA20"]   = ema(close, 20)
    df["EMA50"]   = ema(close, 50)
    df["EMA100"]  = ema(close, 100)
    df["EMA200"]  = ema(close, 200)
    df["ATR"]     = atr_hesapla(df, atr_per)
    df["VOL_ORT"] = volume.rolling(20).mean()

    # MACD
    ema_h          = close.ewm(span=macd_hizli,  adjust=False).mean()
    ema_y          = close.ewm(span=macd_yavas,  adjust=False).mean()
    df["MACD"]     = ema_h - ema_y
    df["MACD_SIG"] = df["MACD"].ewm(span=macd_sinyal, adjust=False).mean()
    df["MACD_HIS"] = df["MACD"] - df["MACD_SIG"]

    df.dropna(subset=["EMA200","ATR","VOL_ORT","MACD_HIS"], inplace=True)
    if len(df) < 2:
        return None, "veri_yetersiz"

    son    = df.iloc[-1]
    onceki = df.iloc[-2]

    # 1. EMA trend filtresi
    if not (float(son["EMA20"]) > float(son["EMA50"]) >
            float(son["EMA100"]) > float(son["EMA200"])):
        return None, "trend"

    # 2. MACD histogram dönüşü
    if not (float(onceki["MACD_HIS"]) < 0 and
            float(son["MACD_HIS"])    > 0):
        return None, "macd"

    # 3. YENİ: Fiyat EMA20 üzerinde olmalı
    kapanis = float(son["Close"])
    if kapanis <= float(son["EMA20"]):
        return None, "fiyat_ema20"

    # 4. YENİ: Hacim filtresi
    vol_ort = float(son["VOL_ORT"])
    vol_son = float(son["Volume"])
    if vol_ort > 0 and vol_son < vol_ort * hacim_carpan:
        return None, "hacim"

    atr_val   = float(son["ATR"])
    stop      = round(kapanis - atr_kat * atr_val, 2)
    hedef     = round(kapanis + rr * atr_kat * atr_val, 2)
    hacim_kat = round(vol_son / vol_ort, 2) if vol_ort > 0 else 0

    return {
        "Son Kapanis": round(kapanis, 2),
        "MACD_HIS"   : round(float(son["MACD_HIS"]), 4),
        "MACD"       : round(float(son["MACD"]), 4),
        "Stop"       : stop,
        "Stop%"      : round((kapanis - stop) / kapanis * 100, 1),
        "Hedef"      : hedef,
        "Hedef%"     : round((hedef - kapanis) / kapanis * 100, 1),
        "ATR"        : round(atr_val, 2),
        "Hacim/Ort"  : hacim_kat,
    }, "ok"

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Ayarlar")

portfoy = st.sidebar.number_input(
    "Portföy (TL)", min_value=10000, max_value=10000000,
    value=950000, step=10000
)
risk_yuzde = st.sidebar.slider("Risk %", 0.5, 5.0, 1.0, 0.5)
rr_katsayi  = st.sidebar.slider("R:R Katsayısı", 1.0, 5.0, 3.0, 0.5)
atr_katsayi = st.sidebar.slider("ATR Katsayısı", 0.5, 3.0, 1.5, 0.5)
atr_periyot = st.sidebar.slider("ATR Periyodu",  7,   21,  14,  1)

st.sidebar.markdown("### 📊 MACD")
macd_hizli  = st.sidebar.slider("MACD Hızlı EMA", 5,  20, 12, 1)
macd_yavas  = st.sidebar.slider("MACD Yavaş EMA", 10, 50, 26, 1)
macd_sinyal = st.sidebar.slider("MACD Sinyal",    5,  20,  9, 1)

st.sidebar.markdown("### 🔍 Filtreler")
hacim_carpan = st.sidebar.slider(
    "Hacim Çarpanı (x ort.)", 1.0, 3.0, 1.5, 0.5,
    help="Sinyal gününde hacim, 20 günlük ortalama hacmin kaç katı olmalı"
)
endeks_bypass = st.sidebar.checkbox(
    "⚠️ Endeks filtresini atla", value=False,
    help="BIST100 EMA200 altında olsa bile tarama yapılmasına izin verir."
)

params = {
    "atr_periyot" : atr_periyot,
    "atr_katsayi" : atr_katsayi,
    "rr_katsayi"  : rr_katsayi,
    "macd_hizli"  : macd_hizli,
    "macd_yavas"  : macd_yavas,
    "macd_sinyal" : macd_sinyal,
    "hacim_carpan": hacim_carpan,
}

# ─── ANA SAYFA ────────────────────────────────────────────────────────────────
st.title("📈 BIST Sinyal Tarayıcı")
st.caption(f"Endeks Filtreli | EMA Trend | Fiyat > EMA20 | Hacim > {hacim_carpan}x | MACD Histogram Dönüşü")

# ─── ENDEKS DURUMU ────────────────────────────────────────────────────────────
aktif, xu100, xu_ema200, xu_fark = endeks_kontrol()

if aktif is None:
    st.warning("⚠️ BIST100 verisi alınamadı — endeks filtresi devre dışı.")
    endeks_gecti = True
elif aktif:
    st.success(
        f"✅ **BIST100 Aktif** — "
        f"Kapanış: {xu100:,.0f}  |  EMA200: {xu_ema200:,.0f}  |  "
        f"Fark: **+{xu_fark:.1f}%** — Strateji bugün aktif."
    )
    endeks_gecti = True
else:
    st.error(
        f"🚫 **BIST100 EMA200 Altında** — "
        f"Kapanış: {xu100:,.0f}  |  EMA200: {xu_ema200:,.0f}  |  "
        f"Fark: **{xu_fark:.1f}%** — Strateji bugün pasif."
    )
    endeks_gecti = False

if endeks_bypass:
    endeks_gecti = True
    st.warning("⚠️ Endeks filtresi devre dışı bırakıldı.")

st.markdown("---")

# ─── TARA BUTONU ──────────────────────────────────────────────────────────────
tara_disabled = not endeks_gecti

if tara_disabled:
    st.info("Endeks EMA200 altında — tarama devre dışı. Sol menüden 'Endeks filtresini atla' seçeneğini açabilirsiniz.")

if st.button("🔍 Tara", use_container_width=True, type="primary", disabled=tara_disabled):
    risk_tl   = portfoy * risk_yuzde / 100
    sinyaller = []
    hatalar   = []
    elenen    = {"trend": 0, "macd": 0, "fiyat_ema20": 0, "hacim": 0, "diger": 0}

    progress = st.progress(0, text="Tarama başlıyor...")
    toplam   = len(HISSELER)

    for i, hisse in enumerate(HISSELER):
        progress.progress(
            (i + 1) / toplam,
            text=f"Taraniyor: {hisse} ({i+1}/{toplam})"
        )
        df = veri_cek(hisse)
        if df is None:
            hatalar.append(hisse)
            continue

        sonuc, sebep = sinyal_tara(df, params)

        if sonuc is None:
            if sebep in elenen:
                elenen[sebep] += 1
            else:
                elenen["diger"] += 1
            continue

        kapanis    = sonuc["Son Kapanis"]
        stop       = sonuc["Stop"]
        risk_hisse = kapanis - stop
        if risk_hisse <= 0:
            continue
        lot      = max(1, int(risk_tl / risk_hisse))
        giris_tl = round(lot * kapanis, 2)

        sinyaller.append({
            "★"          : "★" if hisse in TOP50 else "",
            "Hisse"      : hisse,
            "Kapanis"    : kapanis,
            "MACD_HIS"   : sonuc["MACD_HIS"],
            "MACD"       : sonuc["MACD"],
            "Hacim/Ort"  : sonuc["Hacim/Ort"],
            "Stop"       : stop,
            "Stop%"      : sonuc["Stop%"],
            "Hedef"      : sonuc["Hedef"],
            "Hedef%"     : sonuc["Hedef%"],
            "ATR"        : sonuc["ATR"],
            "Lot"        : lot,
            "Giris TL"   : giris_tl,
            "Risk TL"    : round(risk_tl, 2),
        })

    progress.empty()
    st.session_state["sinyaller"] = sinyaller
    st.session_state["hatalar"]   = hatalar
    st.session_state["elenen"]    = elenen
    st.session_state["tarih"]     = datetime.now().strftime("%d.%m.%Y %H:%M")

# ─── SONUÇLAR ─────────────────────────────────────────────────────────────────
if "sinyaller" in st.session_state:
    sinyaller = st.session_state["sinyaller"]
    tarih     = st.session_state["tarih"]
    hatalar   = st.session_state.get("hatalar", [])
    elenen    = st.session_state.get("elenen", {})

    st.markdown(f"### Tarama Sonuçları — {tarih}")

    # Metrik kartları
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sinyal Sayısı", len(sinyaller))
    col2.metric("Taranan Hisse", len(HISSELER))
    col3.metric("Veri Hatası",   len(hatalar))
    col4.metric("Endeks",        "✅ Aktif" if endeks_gecti else "🚫 Pasif")

    # Filtre istatistikleri
    with st.expander("📊 Filtre istatistikleri — kaç hisse nerede elendi?"):
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("EMA Trend",    elenen.get("trend", 0),       help="EMA20>50>100>200 koşulu")
        fc2.metric("MACD Dönüşü",  elenen.get("macd", 0),        help="Histogram negatiften pozitife geçmedi")
        fc3.metric("Fiyat < EMA20",elenen.get("fiyat_ema20", 0), help="Kapanış EMA20 altında")
        fc4.metric("Düşük Hacim",  elenen.get("hacim", 0),       help=f"Hacim < {hacim_carpan}x ortalama")

    # Veri hatası
    if len(hatalar) > 0:
        with st.expander(f"⚠️ Veri alınamayan {len(hatalar)} hisse"):
            st.caption("Yahoo Finance'den veri çekilemedi. Sembol değişimi, askı veya geçici bağlantı sorunu olabilir.")
            cols = st.columns(6)
            for i, h in enumerate(sorted(hatalar)):
                tv_url = f"https://tr.tradingview.com/chart/?symbol=BIST:{h}"
                cols[i % 6].markdown(f"[{h}]({tv_url})")

    if len(sinyaller) == 0:
        st.warning("Bugün kriterlere uyan hisse bulunamadı.")
    else:
        df_sonuc = pd.DataFrame(sinyaller).sort_values(
            by=["★", "MACD_HIS"], ascending=[False, False]
        )

        top50_var = df_sonuc[df_sonuc["★"] == "★"]
        if len(top50_var) > 0:
            st.success(
                f"★ **{len(top50_var)} hisse Top50 listesinde!** "
                f"({', '.join(top50_var['Hisse'].tolist())}) — öncelikli değerlendir."
            )

        df_goster = df_sonuc.copy()
        df_goster["Stop%"]      = df_goster["Stop%"].apply(lambda x: f"-%{x}")
        df_goster["Hedef%"]     = df_goster["Hedef%"].apply(lambda x: f"+%{x}")
        df_goster["Hacim/Ort"]  = df_goster["Hacim/Ort"].apply(lambda x: f"{x:.2f}x")
        df_goster["📈 Grafik"]  = df_goster["Hisse"].apply(
            lambda h: f"https://tr.tradingview.com/chart/?symbol=BIST:{h}"
        )

        st.dataframe(
            df_goster[["★","Hisse","Kapanis","MACD_HIS","Hacim/Ort",
                        "Stop","Stop%","Hedef","Hedef%","ATR","Lot","Giris TL","Risk TL","📈 Grafik"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "📈 Grafik": st.column_config.LinkColumn(
                    "📈 Grafik",
                    help="TradingView'da aç",
                    display_text="TradingView →"
                )
            }
        )

        # Özet
        toplam_giris = df_sonuc["Giris TL"].sum()
        toplam_risk  = df_sonuc["Risk TL"].sum()
        c1, c2 = st.columns(2)
        c1.metric("Toplam Sermaye Kullanımı", f"{toplam_giris:,.0f} TL")
        c2.metric("Toplam Risk",
                  f"{toplam_risk:,.0f} TL  (%{toplam_risk/portfoy*100:.1f} portföy)")

        csv = df_sonuc.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ CSV İndir",
            data=csv,
            file_name="bist_sinyaller_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv",
            mime="text/csv",
        )

        # ─── GRAFİK ───────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📊 Grafik")

        secili = st.selectbox("Hisse seçin:", [r["Hisse"] for r in sinyaller])
        df_grafik = veri_cek(secili, gun=150)

        if df_grafik is not None:
            for col in ["Open","High","Low","Close","Volume"]:
                if col in df_grafik.columns:
                    v = df_grafik[col]
                    df_grafik[col] = v.iloc[:, 0] if hasattr(v, "iloc") and v.ndim == 2 else v

            c      = df_grafik["Close"].squeeze()
            ema_h  = c.ewm(span=macd_hizli, adjust=False).mean()
            ema_y  = c.ewm(span=macd_yavas, adjust=False).mean()
            df_grafik["EMA20"]    = ema(c, 20)
            df_grafik["EMA50"]    = ema(c, 50)
            df_grafik["EMA100"]   = ema(c, 100)
            df_grafik["EMA200"]   = ema(c, 200)
            df_grafik["MACD"]     = ema_h - ema_y
            df_grafik["MACD_SIG"] = df_grafik["MACD"].ewm(span=macd_sinyal, adjust=False).mean()
            df_grafik["MACD_HIS"] = df_grafik["MACD"] - df_grafik["MACD_SIG"]

            secili_sinyal = next(r for r in sinyaller if r["Hisse"] == secili)

            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                row_heights=[0.7, 0.3], vertical_spacing=0.04
            )

            fig.add_trace(go.Candlestick(
                x=df_grafik.index,
                open=df_grafik["Open"], high=df_grafik["High"],
                low=df_grafik["Low"],   close=df_grafik["Close"],
                name="Fiyat",
                increasing_line_color="#22c55e",
                decreasing_line_color="#ef4444",
            ), row=1, col=1)

            for col_name, renk, genislik in [
                ("EMA20","#38bdf8",1.5), ("EMA50","#f59e0b",1.5),
                ("EMA100","#a78bfa",1),  ("EMA200","#f472b6",1),
            ]:
                fig.add_trace(go.Scatter(
                    x=df_grafik.index, y=df_grafik[col_name],
                    name=col_name, line=dict(color=renk, width=genislik)
                ), row=1, col=1)

            son_tarih = df_grafik.index[-1]
            bitis     = son_tarih + timedelta(days=15)
            for seviye, renk, isim in [
                (secili_sinyal["Stop"],  "#ef4444", "Stop"),
                (secili_sinyal["Hedef"], "#22c55e", "Hedef"),
            ]:
                fig.add_shape(
                    type="line",
                    x0=son_tarih, x1=bitis, y0=seviye, y1=seviye,
                    line=dict(color=renk, width=1.5, dash="dash"),
                    row=1, col=1
                )
                fig.add_annotation(
                    x=bitis, y=seviye,
                    text=f"{isim} {seviye:.2f}",
                    showarrow=False,
                    font=dict(color=renk, size=11),
                    xanchor="left", row=1, col=1
                )

            colors = ["#3fb950" if v >= 0 else "#ef4444" for v in df_grafik["MACD_HIS"]]
            fig.add_trace(go.Bar(
                x=df_grafik.index, y=df_grafik["MACD_HIS"],
                name="MACD His.", marker_color=colors, opacity=0.7
            ), row=2, col=1)
            fig.add_trace(go.Scatter(
                x=df_grafik.index, y=df_grafik["MACD"],
                name="MACD", line=dict(color="#38bdf8", width=1.5)
            ), row=2, col=1)
            fig.add_trace(go.Scatter(
                x=df_grafik.index, y=df_grafik["MACD_SIG"],
                name="Sinyal", line=dict(color="#f59e0b", width=1.5)
            ), row=2, col=1)
            fig.add_hline(y=0, line_dash="dot", line_color="#64748b", row=2, col=1)
            fig.add_vline(
                x=son_tarih, line_dash="dot",
                line_color="#facc15", line_width=1,
                row="all", col=1
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0d0f14",
                plot_bgcolor="#0d0f14",
                height=650,
                showlegend=True,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=80, t=30, b=10),
                font=dict(family="Consolas", size=11),
            )
            fig.update_yaxes(gridcolor="#1e293b")
            fig.update_xaxes(gridcolor="#1e293b")

            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
| | |
|---|---|
| **Giriş** | {secili_sinyal['Kapanis']:.2f} TL |
| **Stop** | {secili_sinyal['Stop']:.2f} TL (-%{secili_sinyal['Stop%']}) |
| **Hedef** | {secili_sinyal['Hedef']:.2f} TL (+%{secili_sinyal['Hedef%']}) |
| **R:R** | 1:{rr_katsayi:.0f} |
| **Hacim/Ort** | {secili_sinyal['Hacim/Ort']:.2f}x |
| **Lot** | {secili_sinyal['Lot']:,} adet |
| **Giriş Tutarı** | {secili_sinyal['Giris TL']:,.0f} TL |
| **Risk** | {secili_sinyal['Risk TL']:,.0f} TL |
""")

    st.markdown("---")
    st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir.")
