import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, date
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="BIST Gerçekçi Backtest",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e2433;
        border: 1px solid #2d3548;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-label { font-size: 12px; color: #8b95a8; margin-bottom: 4px; }
    .metric-value { font-size: 24px; font-weight: 700; }
    .metric-pos { color: #22c55e; }
    .metric-neg { color: #ef4444; }
    .metric-neu { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ─── HİSSE LİSTELERİ ──────────────────────────────────────────────────────────
TOP50 = {
    "POLTK","BMSTL","LIDER","AVTUR","MOBTL","ISCTR","DOAS","TRCAS","CMBTN","ISBTR",
    "LUKSK","DOHOL","DOCO","VBTYZ","MERIT","TEHOL","VAKKO","ALGYO","FRIGO","BMSCH",
    "HEDEF","ETILR","ASELS","ESCOM","AKSA","ULUUN","GRTHO","OYAKC","FMIZP","RYSAS",
    "KARSN","SMRVA","BRYAT","YAPRK","NETAS","SELEC","SAFKR","CELHA","ECILC","BURCE",
    "GLCVY","EGEEN","ACSEL","KUYAS","RYGYO","INDES","MAGEN","AKSEN","ARCLK","YYAPI",
}

BIST_HISSELER = [
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
def squeeze(s):
    return s.squeeze() if hasattr(s, "squeeze") else s

def ema(seri, periyot):
    return squeeze(seri).ewm(span=periyot, adjust=False).mean()

def atr_hesapla(df, periyot=14):
    c  = squeeze(df["Close"])
    h  = squeeze(df["High"])
    l  = squeeze(df["Low"])
    hl = h - l
    hc = (h - c.shift(1)).abs()
    lc = (l - c.shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.ewm(span=periyot, adjust=False).mean()

def hesapla_ind(df, atr_per, macd_h, macd_y, macd_s):
    c = squeeze(df["Close"])
    h = squeeze(df["High"])
    l = squeeze(df["Low"])
    v = squeeze(df["Volume"])
    for p in [20, 50, 100, 200]:
        df[f"EMA{p}"] = c.ewm(span=p, adjust=False).mean()
    ema_h          = c.ewm(span=macd_h, adjust=False).mean()
    ema_y          = c.ewm(span=macd_y, adjust=False).mean()
    df["MACD"]     = ema_h - ema_y
    df["MACD_SIG"] = df["MACD"].ewm(span=macd_s, adjust=False).mean()
    df["MACD_HIS"] = df["MACD"] - df["MACD_SIG"]
    hl = h - l
    hc = (h - c.shift(1)).abs()
    lc = (l - c.shift(1)).abs()
    df["TR"]      = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    df["ATR"]     = df["TR"].rolling(atr_per).mean()
    df["VOL_ORT"] = v.rolling(20).mean()
    return df

def veri_cek(ticker, bas, bit):
    try:
        df = yf.download(ticker + ".IS", start=str(bas), end=str(bit),
                         interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        for col in df.columns:
            df[col] = squeeze(df[col])
        df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return None

def endeks_filtre_olustur(bas, bit):
    try:
        df = yf.download("XU100.IS",
                         start=(bas - pd.DateOffset(years=1)).strftime("%Y-%m-%d"),
                         end=str(bit), interval="1d", progress=False, auto_adjust=True)
        if df.empty: return {}
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = df.index.tz_localize(None)
        df["EMA200"] = squeeze(df["Close"]).ewm(span=200, adjust=False).mean()
        df.dropna(subset=["EMA200"], inplace=True)
        return {row.Index.date(): float(row.Close) > float(row.EMA200)
                for row in df.itertuples()}
    except Exception:
        return {}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Backtest Ayarları")

st.sidebar.markdown("### 📅 Tarih Aralığı")
col1, col2 = st.sidebar.columns(2)
bas_tarih = col1.date_input("Başlangıç", value=date(2020, 1, 1),
                             min_value=date(2010, 1, 1), max_value=date.today())
bit_tarih = col2.date_input("Bitiş", value=date.today(),
                             min_value=date(2010, 1, 1), max_value=date.today())

st.sidebar.markdown("### 💰 Sermaye & Pozisyon")
portfoy      = st.sidebar.number_input("Başlangıç Sermaye (TL)", min_value=10000,
                                        max_value=100_000_000, value=1_000_000, step=10000)
max_pozisyon = st.sidebar.slider("Max Eş Zamanlı Pozisyon", 1, 20, 10, 1)
poz_yuzde    = st.sidebar.slider("Pozisyon Büyüklüğü (%)", 5.0, 50.0,
                                  round(100/max_pozisyon, 1), 5.0)

st.sidebar.markdown("### 📐 R:R & Stop")
rr_kat  = st.sidebar.select_slider("R:R Katsayısı",
           options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], value=3.0)
atr_kat = st.sidebar.slider("ATR Katsayısı (Stop)", 0.5, 3.0, 1.5, 0.5)
atr_per = st.sidebar.slider("ATR Periyodu", 7, 21, 14, 1)

st.sidebar.markdown("### 📊 MACD")
macd_h = st.sidebar.slider("MACD Hızlı EMA", 5,  20, 12, 1)
macd_y = st.sidebar.slider("MACD Yavaş EMA", 10, 50, 26, 1)
macd_s = st.sidebar.slider("MACD Sinyal",    5,  20, 9,  1)

st.sidebar.markdown("### 🔍 Filtreler")
endeks_aktif  = st.sidebar.checkbox("Endeks Filtresi (BIST100 > EMA200)", value=True)
hacim_carpan  = st.sidebar.slider("Hacim Çarpanı (x ort.)", 1.0, 3.0, 1.5, 0.5,
                                   help="Sinyal gününde hacim, 20 günlük ort. hacmin kaç katı olmalı")

# ─── BAŞLIK ───────────────────────────────────────────────────────────────────
st.title("📊 BIST Gerçekçi Backtest")
st.caption(f"Pozisyon Yönetimli | MACD Strateji | Fiyat>EMA20 | Hacim>{hacim_carpan}x | Max {max_pozisyon} Pozisyon | R:R 1:{rr_kat:.0f}")

# ─── INFO ─────────────────────────────────────────────────────────────────────
st.info(f"""
**Gerçekçi Backtest Kuralları (v2 — Fiyat>EMA20 & Hacim Filtreli):**
- Aynı anda maksimum **{max_pozisyon}** pozisyon açık olabilir
- Her pozisyon güncel portföyün **%{poz_yuzde:.0f}'i** kadardır (~{portfoy*poz_yuzde/100:,.0f} TL)
- Tüm slotlar dolunca yeni sinyaller beklemeye alınır
- Pozisyon kapanınca slot açılır, sıradaki sinyal değerlendirilir
- **Bileşik getiri** — kazanç arttıkça pozisyon büyüklüğü de artar
""")

# ─── BACKTEST BUTONU ──────────────────────────────────────────────────────────
if st.button("🚀 Backtest Çalıştır", use_container_width=True, type="primary"):

    bas_ts  = pd.Timestamp(bas_tarih)
    bit_ts  = pd.Timestamp(bit_tarih)
    veri_bas = bas_ts - pd.DateOffset(years=1)
    veri_bit = bit_ts + pd.DateOffset(days=2)

    # Endeks
    endeks_f = {}
    if endeks_aktif:
        with st.spinner("Endeks verisi indiriliyor..."):
            endeks_f = endeks_filtre_olustur(bas_ts, veri_bit)

    # Veri indir
    hisse_verileri = {}
    progress = st.progress(0, text="Veriler indiriliyor...")
    for hi, sembol in enumerate(BIST_HISSELER):
        progress.progress((hi+1)/len(BIST_HISSELER),
                          text=f"İndiriliyor: {sembol} ({hi+1}/{len(BIST_HISSELER)})")
        df_raw = veri_cek(sembol, veri_bas.to_pydatetime().date(),
                          veri_bit.to_pydatetime().date())
        if df_raw is None: continue
        try:
            df = df_raw.copy()
            df = hesapla_ind(df, atr_per, macd_h, macd_y, macd_s)
            df.dropna(subset=["EMA200","MACD_HIS","ATR","VOL_ORT"], inplace=True)
            if len(df) >= 50:
                hisse_verileri[sembol] = df
        except Exception:
            continue
    progress.empty()

    # Günlük sinyaller üret
    with st.spinner("Sinyaller hesaplanıyor..."):
        gunluk_sinyaller = {}
        for sembol, df in hisse_verileri.items():
            for i in range(1, len(df)):
                son    = df.iloc[i]
                onceki = df.iloc[i - 1]
                if son.name < bas_ts or son.name > bit_ts: continue
                if endeks_aktif and not endeks_f.get(son.name.date(), True): continue
                if not (float(son["EMA20"]) > float(son["EMA50"]) >
                        float(son["EMA100"]) > float(son["EMA200"])): continue
                if not (float(onceki["MACD_HIS"]) < 0 and
                        float(son["MACD_HIS"])    > 0): continue
                giris  = float(son["Close"])
                # YENİ: Fiyat EMA20 üzerinde olmalı
                if giris <= float(son["EMA20"]): continue
                # YENİ: Hacim filtresi — günlük hacim > 20 günlük ort x hacim_carpan
                vol_ort = float(son["VOL_ORT"])
                if vol_ort > 0 and float(son["Volume"]) < vol_ort * hacim_carpan: continue
                atr_v  = float(son["ATR"])
                stop   = giris - atr_v * atr_kat
                hedef  = giris + (giris - stop) * rr_kat
                if giris - stop <= 0: continue
                tarih = son.name
                if tarih not in gunluk_sinyaller:
                    gunluk_sinyaller[tarih] = []
                gunluk_sinyaller[tarih].append({
                    "sembol": sembol,
                    "giris" : giris,
                    "stop"  : stop,
                    "hedef" : hedef,
                    "top50" : sembol in TOP50,
                })

    # Gerçekçi backtest
    with st.spinner("Pozisyon yönetimi simüle ediliyor..."):
        portfoy_s     = portfoy
        acik_pozlar   = []
        kapali_islem  = []
        atlanan       = 0
        tum_tarihler  = sorted(set(
            d for df in hisse_verileri.values()
            for d in df.index
            if bas_ts <= d <= bit_ts
        ))

        for tarih in tum_tarihler:
            # Açık pozisyonları kontrol et
            kapalanlar = []
            for poz in acik_pozlar:
                sembol = poz["sembol"]
                if sembol not in hisse_verileri: continue
                df     = hisse_verileri[sembol]
                gunluk = df[df.index == tarih]
                if gunluk.empty: continue
                gun_low  = float(gunluk.iloc[0]["Low"])
                gun_high = float(gunluk.iloc[0]["High"])
                sonuc = None
                if gun_low <= poz["stop"]:
                    sonuc = "stop"; cikis = poz["stop"]
                elif gun_high >= poz["hedef"]:
                    sonuc = "hedef"; cikis = poz["hedef"]
                if sonuc:
                    kaz = (cikis - poz["giris"]) * poz["lot"]
                    portfoy_s += kaz
                    kapali_islem.append({
                        "Açılış"      : poz["acilis"].strftime("%d.%m.%Y"),
                        "Kapanış"     : tarih.strftime("%d.%m.%Y"),
                        "Hisse"       : sembol,
                        "★"           : "★" if poz["top50"] else "",
                        "Lot"         : poz["lot"],
                        "Giriş"       : round(poz["giris"], 2),
                        "Alış (TL)"   : round(poz["giris"] * poz["lot"], 0),
                        "Çıkış"       : round(cikis, 2),
                        "Satış (TL)"  : round(cikis * poz["lot"], 0),
                        "Sonuç"       : "✅ Hedef" if sonuc=="hedef" else "❌ Stop",
                        "K/Z (TL)"    : round(kaz, 0),
                        "Portföy"     : round(portfoy_s, 0),
                    })
                    kapalanlar.append(poz)
            for k in kapalanlar:
                acik_pozlar.remove(k)

            # Yeni sinyaller
            if tarih in gunluk_sinyaller:
                sinyaller_bugun = sorted(
                    gunluk_sinyaller[tarih],
                    key=lambda x: (not x["top50"])
                )
                for sinyal in sinyaller_bugun:
                    if any(p["sembol"] == sinyal["sembol"] for p in acik_pozlar):
                        continue
                    if len(acik_pozlar) >= max_pozisyon:
                        atlanan += 1
                        continue
                    poz_tl = portfoy_s * (poz_yuzde / 100)
                    lot    = max(1, int(poz_tl / sinyal["giris"]))
                    acik_pozlar.append({
                        "sembol"  : sinyal["sembol"],
                        "acilis"  : tarih,
                        "giris"   : sinyal["giris"],
                        "stop"    : sinyal["stop"],
                        "hedef"   : sinyal["hedef"],
                        "lot"     : lot,
                        "top50"   : sinyal["top50"],
                    })

        # Açık pozisyonları son fiyatla kapat
        for poz in acik_pozlar:
            sembol = poz["sembol"]
            if sembol not in hisse_verileri: continue
            df  = hisse_verileri[sembol]
            son = df.iloc[-1]
            cikis = float(son["Close"])
            kaz   = (cikis - poz["giris"]) * poz["lot"]
            portfoy_s += kaz
            kapali_islem.append({
                "Açılış"      : poz["acilis"].strftime("%d.%m.%Y"),
                "Kapanış"     : son.name.strftime("%d.%m.%Y"),
                "Hisse"       : sembol,
                "★"           : "★" if poz["top50"] else "",
                "Lot"         : poz["lot"],
                "Giriş"       : round(poz["giris"], 2),
                "Alış (TL)"   : round(poz["giris"] * poz["lot"], 0),
                "Çıkış"       : round(cikis, 2),
                "Satış (TL)"  : round(cikis * poz["lot"], 0),
                "Sonuç"       : "⏳ Açık",
                "K/Z (TL)"    : round(kaz, 0),
                "Portföy"     : round(portfoy_s, 0),
            })

    st.session_state["kapali"]   = kapali_islem
    st.session_state["portfoy_s"]= portfoy_s
    st.session_state["portfoy0"] = portfoy
    st.session_state["atlanan"]  = atlanan
    st.session_state["bas_ts"]   = bas_ts
    st.session_state["bit_ts"]   = bit_ts

# ─── SONUÇLAR ─────────────────────────────────────────────────────────────────
if "kapali" in st.session_state:
    kapali    = st.session_state["kapali"]
    portfoy_s = st.session_state["portfoy_s"]
    portfoy0  = st.session_state["portfoy0"]
    atlanan   = st.session_state["atlanan"]

    if not kapali:
        st.warning("Bu dönemde sinyal bulunamadı.")
        st.stop()

    df_i     = pd.DataFrame(kapali)
    tamam    = df_i[df_i["Sonuç"].str.contains("Hedef|Stop")]
    kazanan  = df_i[df_i["Sonuç"] == "✅ Hedef"]
    kaybeden = df_i[df_i["Sonuç"] == "❌ Stop"]
    toplam   = len(tamam)
    wr       = len(kazanan) / toplam * 100 if toplam > 0 else 0
    getiri   = (portfoy_s - portfoy0) / portfoy0 * 100
    kz_tl    = portfoy_s - portfoy0

    g_renk = "metric-pos" if getiri >= 0 else "metric-neg"
    k_renk = "metric-pos" if kz_tl  >= 0 else "metric-neg"

    # Metrik kartları
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, lbl, val, renk in [
        (c1, "Başlangıç",     f"{portfoy0:,.0f} TL",  "metric-neu"),
        (c2, "Bitiş",         f"{portfoy_s:,.0f} TL", g_renk),
        (c3, "Toplam K/Z",    f"{kz_tl:+,.0f} TL",   k_renk),
        (c4, "Getiri",        f"{getiri:+.1f}%",       g_renk),
        (c5, "Win Rate",      f"{wr:.1f}%",            "metric-neu"),
        (c6, "Atlanan Sinyal",str(atlanan),            "metric-neu"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-value {renk}">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    c7,c8,c9 = st.columns(3)
    for col, lbl, val, renk in [
        (c7, "Toplam İşlem",    str(toplam),        "metric-neu"),
        (c8, "Kazanan (Hedef)", str(len(kazanan)),  "metric-pos"),
        (c9, "Kaybeden (Stop)", str(len(kaybeden)), "metric-neg"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-value {renk}">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Sekmeler
    tab1, tab2, tab3 = st.tabs(["💰 Portföy Eğrisi", "📅 Aylık Performans", "📋 İşlem Listesi"])

    with tab1:
        df_i["Kapanış_dt"] = pd.to_datetime(df_i["Kapanış"], format="%d.%m.%Y")
        df_sorted = df_i.sort_values("Kapanış_dt")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_sorted["Kapanış_dt"], y=df_sorted["Portföy"],
            fill="tozeroy", line=dict(color="#38bdf8", width=2),
            fillcolor="rgba(56,189,248,0.08)", name="Portföy"
        ))
        fig.add_hline(y=portfoy0, line_dash="dash",
                      line_color="#64748b", line_width=1,
                      annotation_text=f"Başlangıç: {portfoy0:,.0f} TL")
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0d0f14",
            plot_bgcolor="#0d0f14", height=400,
            margin=dict(l=10,r=10,t=20,b=10),
            yaxis=dict(gridcolor="#1e293b", tickformat=",.0f", ticksuffix=" TL"),
            xaxis=dict(gridcolor="#1e293b"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df_i["Ay"] = df_i["Kapanış_dt"].dt.to_period("M")
        aylik = df_i.groupby("Ay")["K/Z (TL)"].sum().reset_index()
        aylik["Kümülatif"] = portfoy0 + aylik["K/Z (TL)"].cumsum()

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=aylik["Ay"].astype(str), y=aylik["K/Z (TL)"],
            marker_color=[("#3fb950" if v >= 0 else "#ef4444") for v in aylik["K/Z (TL)"]],
            name="Aylık K/Z", text=[f"{v:+,.0f}" for v in aylik["K/Z (TL)"]],
            textposition="outside"
        ))
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="#0d0f14",
            plot_bgcolor="#0d0f14", height=350,
            margin=dict(l=10,r=10,t=20,b=10),
            yaxis=dict(gridcolor="#1e293b", tickformat=",.0f"),
            xaxis=dict(gridcolor="#1e293b"),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Aylık tablo
        aylik_goster = aylik.copy()
        aylik_goster["Ay"] = aylik_goster["Ay"].astype(str)
        aylik_goster["K/Z (TL)"] = aylik_goster["K/Z (TL)"].apply(lambda x: f"{x:+,.0f}")
        aylik_goster["Kümülatif"] = aylik_goster["Kümülatif"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(aylik_goster, use_container_width=True, hide_index=True)

    with tab3:
        df_goster = df_i.drop(columns=["Kapanış_dt","Ay"], errors="ignore").copy()
        df_goster["Alış (TL)"]  = df_goster["Alış (TL)"].apply(lambda x: f"{x:,.0f}")
        df_goster["Satış (TL)"] = df_goster["Satış (TL)"].apply(lambda x: f"{x:,.0f}")
        df_goster["K/Z (TL)"]   = df_goster["K/Z (TL)"].apply(lambda x: f"{x:+,.0f}")
        df_goster["Portföy"]    = df_goster["Portföy"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(
            df_goster[["Açılış","Kapanış","Hisse","★","Lot","Giriş",
                        "Alış (TL)","Çıkış","Satış (TL)","Sonuç","K/Z (TL)","Portföy"]],
            use_container_width=True, hide_index=True
        )

        csv = df_i.drop(columns=["Kapanış_dt","Ay"], errors="ignore").to_csv(
            index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSV İndir", data=csv,
            file_name=f"gercekci_backtest_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")

    st.markdown("---")
    st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir.")
