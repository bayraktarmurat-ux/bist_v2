"""
BIST — Gunluk Sinyal Tarayici (Endeks Filtreli, R:R 1:4)
=========================================================
Piyasa acilmadan once calistirin.

Strateji:
  ENDEKS   : BIST100 kapanis > EMA200 ise strateji aktif, degilse bekle
  TREND    : EMA20 > EMA50 > EMA100 > EMA200
  FIYAT    : Kapanis > EMA20 (fiyat EMA20 uzerinde olmali)
  HACIM    : Gunluk hacim > 20 gunluk ort. hacim x 1.5
  MACD     : MACD histogrami negatiften pozitife dondu
  GIRIS    : Bugun acilista (dun kapanis yakininda)
  STOP     : ATR(14) x 1.5
  HEDEF    : Stop mesafesi x 4.0 (1:4 R:R)
  LOT      : Portfoyun %1'i risk bazli

Kurulum : pip install yfinance pandas
Calistir: python bist_tarayici.py
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

# ═══════════════════════════════════════════
#  EN BASARILI 50 HİSSE (backtest ile belirlendi)
# ═══════════════════════════════════════════
TOP50 = {
    "POLTK","BMSTL","LIDER","AVTUR","MOBTL","ISCTR","DOAS","TRCAS","CMBTN","ISBTR",
    "LUKSK","DOHOL","DOCO","VBTYZ","MERIT","TEHOL","VAKKO","ALGYO","FRIGO","BMSCH",
    "HEDEF","ETILR","ASELS","ESCOM","AKSA","ULUUN","GRTHO","OYAKC","FMIZP","RYSAS",
    "KARSN","SMRVA","BRYAT","YAPRK","NETAS","SELEC","SAFKR","CELHA","ECILC","BURCE",
    "GLCVY","EGEEN","ACSEL","KUYAS","RYGYO","INDES","MAGEN","AKSEN","ARCLK","YYAPI",
}

# ═══════════════════════════════════════════
#  AYARLAR
# ═══════════════════════════════════════════
PORTFOY           = 950_000
RISK_YUZDESI      = 1.0
ATR_PERIYOT       = 14
ATR_KATSAYI       = 1.5
RR_KATSAYI        = 3.0
EMA_PERIYOTLAR    = [20, 50, 100, 200]
ENDEKS_SEMBOL     = "XU100.IS"
MACD_HIZLI        = 12
MACD_YAVAS        = 26
MACD_SINYAL       = 9
HACIM_CARPAN      = 1.5   # Hacim filtresi: gunluk hacim > ort_hacim x bu deger
HACIM_ORT_PERIYOT = 20    # Ortalama hacim hesap periyodu

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

# ═══════════════════════════════════════════
#  INDIKTOR HESAPLAMA
# ═══════════════════════════════════════════
def hesapla_ind(df):
    c = df["Close"].squeeze() if hasattr(df["Close"], "squeeze") else df["Close"]
    h = df["High"].squeeze()  if hasattr(df["High"],  "squeeze") else df["High"]
    l = df["Low"].squeeze()   if hasattr(df["Low"],   "squeeze") else df["Low"]
    v = df["Volume"].squeeze() if hasattr(df["Volume"], "squeeze") else df["Volume"]
    for p in EMA_PERIYOTLAR:
        df[f"EMA{p}"] = c.ewm(span=p, adjust=False).mean()
    # MACD
    ema_h          = c.ewm(span=MACD_HIZLI,  adjust=False).mean()
    ema_y          = c.ewm(span=MACD_YAVAS,  adjust=False).mean()
    df["MACD"]     = ema_h - ema_y
    df["MACD_SIG"] = df["MACD"].ewm(span=MACD_SINYAL, adjust=False).mean()
    df["MACD_HIS"] = df["MACD"] - df["MACD_SIG"]
    # ATR
    df["H_L"]   = h - l
    df["H_PC"]  = (h - c.shift(1)).abs()
    df["L_PC"]  = (l - c.shift(1)).abs()
    df["TR"]    = df[["H_L","H_PC","L_PC"]].max(axis=1)
    df["ATR"]   = df["TR"].rolling(ATR_PERIYOT).mean()
    # Hacim ortalaması
    df["VOL_ORT"] = v.rolling(HACIM_ORT_PERIYOT).mean()
    return df

def trend_ok(row):
    return row["EMA20"] > row["EMA50"] > row["EMA100"] > row["EMA200"]

def fiyat_ema20_ustunde(row):
    """Fiyat EMA20 üzerinde mi?"""
    return float(row["Close"]) > float(row["EMA20"])

def hacim_ok(row):
    """Günlük hacim 20 günlük ortalamanın 1.5 katı üzerinde mi?"""
    vol     = float(row["Volume"])
    vol_ort = float(row["VOL_ORT"])
    if vol_ort <= 0: return False
    return vol >= vol_ort * HACIM_CARPAN

# ═══════════════════════════════════════════
#  BASLIK
# ═══════════════════════════════════════════
simdi = datetime.now()
print()
print("=" * 68)
print("  BIST — GUNLUK SINYAL TARAYICI")
print(f"  Tarih     : {simdi.strftime('%d.%m.%Y %H:%M')}")
print(f"  Portfoy   : {PORTFOY:,.0f} TL  |  Risk/Islem: %{RISK_YUZDESI}")
print(f"  Strateji  : Endeks filtreli | MACD Histogram Donusu | R:R 1:{RR_KATSAYI:.0f}")
print(f"  Filtreler : Fiyat > EMA20 | Hacim > {HACIM_CARPAN}x ort. hacim")
print(f"  Hisse     : {len(BIST_HISSELER)} adet taranacak")
print("=" * 68)
print()

# ═══════════════════════════════════════════
#  ADIM 1: ENDEKS FİLTRESİ
# ═══════════════════════════════════════════
print("  [1/3] BIST100 endeks kontrolu...", end="", flush=True)
try:
    endeks = yf.Ticker(ENDEKS_SEMBOL).history(period="1y", interval="1d")
    endeks.index = endeks.index.tz_localize(None)
    endeks["EMA200"] = endeks["Close"].ewm(span=200, adjust=False).mean()
    endeks.dropna(subset=["EMA200"], inplace=True)
    son_endeks = endeks.iloc[-1]
    endeks_aktif = son_endeks["Close"] > son_endeks["EMA200"]
    endeks_fark  = ((son_endeks["Close"] - son_endeks["EMA200"]) / son_endeks["EMA200"]) * 100
    durum = "AKTIF" if endeks_aktif else "PASIF"
    print(f"\r  [1/3] BIST100: {son_endeks['Close']:,.0f}  |  EMA200: {son_endeks['EMA200']:,.0f}"
          f"  |  Fark: {endeks_fark:+.1f}%  |  Strateji: {durum}")
except Exception as e:
    print(f"\r  [1/3] BIST100 verisi alinamadi: {e}")
    endeks_aktif = False

print()

if not endeks_aktif:
    print("  BIST100 EMA200 ALTINDA — Bugun islem acilmaz.")
    print()
    print("  Neden: Strateji sadece endeksin EMA200 uzerinde oldugu")
    print("  gun sinyal uretir. Piyasa genel trend altindayken")
    print("  bireysel hisse sinyalleri guvenilir degildir.")
    print()
    print("=" * 68)
    exit()

# ═══════════════════════════════════════════
#  ADIM 2: HİSSE TARAMA
# ═══════════════════════════════════════════
print("  [2/3] Hisseler taranıyor...")
print()

sinyaller = []
elenen = {"trend": 0, "macd": 0, "fiyat_ema20": 0, "hacim": 0}

for i, sembol in enumerate(BIST_HISSELER):
    print(f"  [{i+1:03d}/{len(BIST_HISSELER)}] {sembol:<10} taranıyor...", end="\r", flush=True)
    try:
        df = yf.Ticker(sembol + ".IS").history(period="2y", interval="1d")
        if df.empty or len(df) < 50: continue
        df.index = df.index.tz_localize(None)
        df = hesapla_ind(df)
        df.dropna(subset=["EMA200","MACD_HIS","ATR","VOL_ORT"], inplace=True)
        if len(df) < 2: continue

        son    = df.iloc[-1]
        onceki = df.iloc[-2]

        # 1) Trend filtresi: EMA20 > EMA50 > EMA100 > EMA200
        if not trend_ok(son):
            elenen["trend"] += 1
            continue

        # 2) MACD histogram: negatiften pozitife döndü
        if not (float(onceki["MACD_HIS"]) < 0 and
                float(son["MACD_HIS"])     > 0):
            elenen["macd"] += 1
            continue

        # 3) YENİ: Fiyat EMA20 üzerinde olmalı
        if not fiyat_ema20_ustunde(son):
            elenen["fiyat_ema20"] += 1
            continue

        # 4) YENİ: Hacim filtresi — günlük hacim > 20 günlük ort x 1.5
        if not hacim_ok(son):
            elenen["hacim"] += 1
            continue

        # İşlem detayları
        kapanis    = float(son["Close"])
        atr        = float(son["ATR"])
        vol        = float(son["Volume"])
        vol_ort    = float(son["VOL_ORT"])
        stop_fiyat = kapanis - (atr * ATR_KATSAYI)
        stop_mes   = kapanis - stop_fiyat
        hedef_fiy  = kapanis + (stop_mes * RR_KATSAYI)
        risk_tl    = PORTFOY * (RISK_YUZDESI / 100)
        lot        = max(1, int(risk_tl / stop_mes))
        giris_tl   = round(kapanis * lot, 0)

        sinyaller.append({
            "Hisse"      : sembol,
            "Top50"      : sembol in TOP50,
            "Son Kapan." : round(kapanis, 2),
            "MACD_HIS"   : round(float(son["MACD_HIS"]), 4),
            "MACD"       : round(float(son["MACD"]), 4),
            "ATR"        : round(atr, 2),
            "Hacim/Ort"  : round(vol / vol_ort, 2),
            "Stop"       : round(stop_fiyat, 2),
            "Stop%"      : round((stop_mes / kapanis) * 100, 1),
            "Hedef"      : round(hedef_fiy, 2),
            "Hedef%"     : round((hedef_fiy - kapanis) / kapanis * 100, 1),
            "Lot"        : lot,
            "Giris TL"   : giris_tl,
            "Risk TL"    : round(risk_tl, 0),
        })

    except Exception:
        continue

print(" " * 60, end="\r")

# ═══════════════════════════════════════════
#  ADIM 3: SONUÇLAR
# ═══════════════════════════════════════════
print(f"  [3/3] Tarama tamamlandi. {len(sinyaller)} sinyal bulundu.")
print()
print(f"  Filtre istatistikleri:")
print(f"    EMA trend filtresi    : {elenen['trend']} hisse elendi")
print(f"    MACD donusu filtresi  : {elenen['macd']} hisse elendi")
print(f"    Fiyat > EMA20 filtresi: {elenen['fiyat_ema20']} hisse elendi")
print(f"    Hacim filtresi        : {elenen['hacim']} hisse elendi")
print()

SEP  = "  " + "-" * 64
SEP2 = "  " + "=" * 64

if not sinyaller:
    print(SEP2)
    print("  Bugun kriterlere uyan hisse bulunamadi.")
    print()
    print("  Ipucu: Endeks aktif ama sinyal yok — piyasa")
    print("  momentumun henuz olusmadigi bir gun olabilir.")
    print(SEP2)
else:
    sinyaller.sort(key=lambda x: (not x["Top50"], -x["MACD_HIS"]))
    top50_count = sum(1 for s in sinyaller if s["Top50"])

    print(SEP2)
    print(f"  BUGUN ALINABILECEK HİSSELER — {simdi.strftime('%d.%m.%Y')}")
    print(f"  Toplam {len(sinyaller)} sinyal  |  R:R 1:{RR_KATSAYI:.0f}  |  Risk/Islem: %{RISK_YUZDESI}")
    if top50_count > 0:
        print(f"  ★ {top50_count} hisse Top50 listesinde — oncelikli degerlendir!")
    print(SEP2)

    for s in sinyaller:
        star = "  ★ TOP50 — ONECELİKLİ!" if s["Top50"] else ""
        print(f"  {'─'*62}")
        print(f"  {s['Hisse']}{star}")
        print(f"     Son Kapanis : {s['Son Kapan.']:.2f} TL")
        print(f"  ├─ MACD His.  : {s['MACD_HIS']:+.4f}  (negatiften pozitife dondü ✓)")
        print(f"  ├─ MACD       : {s['MACD']:+.4f}")
        print(f"  ├─ ATR(14)    : {s['ATR']:.2f}")
        print(f"  ├─ Hacim/Ort  : {s['Hacim/Ort']:.2f}x  (min {HACIM_CARPAN}x ✓)")
        print()
        print(f"  ├─ GIRIS  : {s['Son Kapan.']:.2f} TL")
        print(f"  ├─ STOP   : {s['Stop']:.2f} TL  (-%{s['Stop%']})")
        print(f"  ├─ HEDEF  : {s['Hedef']:.2f} TL  (+%{s['Hedef%']})")
        print(f"  ├─ R:R    : 1:{RR_KATSAYI:.0f}")
        print()
        print(f"  ├─ LOT    : {s['Lot']:,} adet")
        print(f"  ├─ Giris  : {s['Giris TL']:,.0f} TL")
        print(f"  └─ Risk   : {s['Risk TL']:,.0f} TL  (%{RISK_YUZDESI} portfoy)")
        print()

    print(SEP2)
    print("  OZET TABLO:")
    print(SEP2)
    df_out = pd.DataFrame(sinyaller)
    df_out["★"] = df_out["Hisse"].apply(lambda h: "★" if h in TOP50 else "")
    kolonlar = ["★","Hisse","Son Kapan.","MACD_HIS","Hacim/Ort","Stop","Hedef","Lot","Giris TL","Risk TL"]
    print(df_out[kolonlar].to_string(index=False))

    toplam_giris = df_out["Giris TL"].sum()
    toplam_risk  = df_out["Risk TL"].sum()
    print()
    print(f"  Toplam Sermaye Kullanimi : {toplam_giris:>14,.0f} TL")
    print(f"  Toplam Risk              : {toplam_risk:>14,.0f} TL  (%{toplam_risk/PORTFOY*100:.1f} portfoy)")
    print(SEP2)

    zaman = simdi.strftime("%Y%m%d_%H%M")
    csv_dosya = f"bist_sinyaller_{zaman}.csv"
    df_out.to_csv(csv_dosya, index=False, encoding="utf-8-sig")
    print(f"  Kaydedildi: {csv_dosya}")

print()
print("  UYARILAR:")
print("  - Piyasa acilisinda fiyati teyit edin (gap olabilir)")
print("  - Stop ve hedef dun kapanisina gore hesaplandi")
print("  - Bu analiz yatirim tavsiyesi degildir")
print(SEP2)
print()
