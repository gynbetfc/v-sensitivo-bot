import base64, os

def decifrar(texto, shift=7):
    resultado = ""
    for char in texto:
        if char.isalpha():
            base = ord('a') if char.islower() else ord('A')
            resultado += chr((ord(char) - base - shift) % 26 + base)
        else:
            resultado += char
    return resultado

# Ler token salvo ou pedir
token_file = os.path.expanduser('~/.tesla_token')
if os.path.exists(token_file):
    with open(token_file) as f:
        token = f.read().strip()
else:
    token = input('Cole seu token GitHub: ').strip()
    with open(token_file, 'w') as f:
        f.write(token)

os.environ['GITHUB_TOKEN'] = token

# Decodificar e executar
with open(__file__, 'r') as f:
    codigo = f.read()

# Extrair apenas o código ofuscado (após o marcador)
inicio = codigo.find('# --- CODIGO OFUSCADO ---')
if inicio > 0:
    codigo_ofuscado = codigo[inicio:]
    codigo_real = decifrar(codigo_ofuscado)
    exec(codigo_real)

# --- CODIGO OFUSCADO ---
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
#    🌀  V KPUOLPYV CLT HAN TPT KL AVKVZ VZ SHKVZ  🌀
#         KL MVYTH HIBUKHUAL, JVUARUBH L WYXZWLYH
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ⚡ ALZSH 369 IVA c6.5.0 ⚡
# ALZSH-369 NYFAPZ | c_ZLUZPAPCV 6⚡ | 3=1 3⚡ | SVQH LZAYHANNPHZ | ZRPUZ | TLYJHKV WHNV
# IK CPH NPAOBI HWP - TVLKH JVUZBTPKH HV JSPJHY LT "JVTLLHY VWLYHY"
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈

myvt mshzr ptwvya Mshzr, ylukly_altwshal_zaypun, qzvupmf, ylxblza
myvt pxvwapvuhwp.zahisl_hwp ptwvya PX_Vwapvu
myvt khalaptl ptwvya khalaptl
ptwvya aoylhkpun, aptl, zfz, vz, qzvu, dhyupunz, ylxblzaz, bbpk, ihzl64

dhyupunz.mpsalydhyupunz("pnuvyl")
hww = Mshzr(__uhtl__)

# ============= JVUMPNBYHLZLZ MPEHZ =============
THYAPUNHSL = 2
WHFVBA_WHKYHV = 0.85
WLYJLUABHS_IHUJH = 15
KYPCL_WHAO = "czluz_bzlyz"
vz.thrlkpyz(KYPCL_WHAO, lepza_vr=Aybl)

# ⭐⭐⭐ JVUMPNBYHLHV KV TLYJHKV WHNV ⭐⭐⭐
# Jhyylnhy jvumpnbyhlzlz kv Tlyjhkv Whnv
ayf:
    jvumpn_bys = m"oaawz://hwp.npaobi.jvt/ylwvz/nfuilamj/c-zluzpapcv-iva/jvualuaz/jvumpn.qzvu"
    y_jvumpn = ylxblzaz.nla(jvumpn_bys, olhklyz={"Hbaovypghapvu": m"Ilhyly {vz.lucpyvu.nla('NPAOBI_AVRLU', '')}", "Hjjlwa": "hwwspjhapvu/cuk.npaobi.c3+qzvu"})
    pm y_jvumpn.zahabz_jvkl == 200:
        jvumpn_khah = qzvu.svhkz(ihzl64.i64kljvkl(y_jvumpn.qzvu()["jvualua"]).kljvkl())
        TLYJHKV_WHNV_HJJLZZ_AVRLU = jvumpn_khah.nla("TLYJHKV_WHNV_HJJLZZ_AVRLU", "")
        TLYJHKV_WHNV_WBISPJ_RLF = jvumpn_khah.nla("TLYJHKV_WHNV_WBISPJ_RLF", "")
        TVKV_ZPTBSHJHV = jvumpn_khah.nla("TVKV_ZPTBSHJHV", Mhszl)
    lszl:
        TLYJHKV_WHNV_HJJLZZ_AVRLU = vz.lucpyvu.nla("TLYJHKV_WHNV_HJJLZZ_AVRLU", "")
        TLYJHKV_WHNV_WBISPJ_RLF = vz.lucpyvu.nla("TLYJHKV_WHNV_WBISPJ_RLF", "")
lejlwa:
    TLYJHKV_WHNV_HJJLZZ_AVRLU = vz.lucpyvu.nla("TLYJHKV_WHNV_HJJLZZ_AVRLU", "")
    TLYJHKV_WHNV_WBISPJ_RLF = vz.lucpyvu.nla("TLYJHKV_WHNV_WBISPJ_RLF", "")
TVKV_ZPTBSHJHV = Mhszl

# ⭐ WSHUVZ KL CVSAZ ⭐
WSHUVZ = [
    {'pk':1,'tvlkhz':1,'wyljv':0.99,'uvtl':'🔰 PUPJPHUAL','klzj':'Y$0,99/CVSA','ahn':'1 wvy 1'},
    {'pk':2,'tvlkhz':5,'wyljv':4.99,'uvtl':'⭐ IFZPJV','klzj':'Y$1,00/CVSA'},
    {'pk':3,'tvlkhz':15,'wyljv':9.99,'uvtl':'💎 PUALYTLKPFYPV','klzj':'Y$0,67/CVSA','klzjvuav':'33% VMM'},
    {'pk':4,'tvlkhz':35,'wyljv':14.99,'uvtl':'🔥 WYLTPBT','klzj':'Y$0,43/CVSA','klzjvuav':'57% VMM'},
    {'pk':5,'tvlkhz':60,'wyljv':19.99,'uvtl':'👑 BSAYH','klzj':'Y$0,33/CVSA','klzjvuav':'67% VMM'},
]

# ⭐ ZRPUZ KH SVQH ⭐
ZRPUZ = [
    {
        'pk': 'zrpu_whkyhv', 'uvtl': '⚡ ALZSH WHKYHV', 'klzj': 'Alth lzjbyv jvt yhpvz kvbyhkvz', 'wyljv_tvlkhz': 0, 'jhalnvyph': 'ihzpjh',
        'jvy_mbukv': '#0h0h1h', 'jvy_whuls': '#1h1h3l', 'jvy_klzahxbl': '#mmk700', 'jvy_aleav': '#mmm',
        'jvy_ivahv': 'spulhy-nyhkplua(135kln,#jj8800,#mmk700)', 'jvy_ahi_hapch': '#mmk700',
        'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#1h0000,#331100,#553300,#331100,#1h0000)', 'jvy_olhkly_ivykh': '#mmk700',
        'olhkly_leayh': '<kpc jshzz="spnoaupun"></kpc>',
        'jzz_leayh': '.spnoaupun{wvzpapvu:hizvsbal;avw:50%;slma:50%;ayhuzmvyt:ayhuzshal(-50%,-50%);dpkao:150we;olpnoa:150we;ihjrnyvbuk:yhkphs-nyhkplua(jpyjsl ha 30% 30%,ynih(255,215,0,0.3) 0%,ynih(255,165,0,0.15) 30%,ayhuzwhylua 100%);ivykly-yhkpbz:50%;g-pukle:0;hupthapvu:nsvd 3z lhzl-pu-vba pumpupal;wvpualy-lcluaz:uvul}@rlfmyhtlz nsvd{0%,100%{ive-zohkvd:0 0 30we ynih(255,215,0,0.3)}50%{ive-zohkvd:0 0 50we ynih(255,165,0,0.5)}}.spnoaupun::hmaly{jvualua:"⚡";wvzpapvu:hizvsbal;avw:50%;slma:50%;ayhuzmvyt:ayhuzshal(-50%,-50%);mvua-zpgl:50we;hupthapvu:msvha 2z lhzl-pu-vba pumpupal}@rlfmyhtlz msvha{0%,100%{ayhuzmvyt:ayhuzshal(-50%,-50%) zjhsl(1)}50%{ayhuzmvyt:ayhuzshal(-50%,-60%) zjhsl(1.1)}}'
    },
    {
        'pk': 'zrpu_khyr', 'uvtl': '🌑 ALZSH KHYR', 'klzj': 'Whyapjbshz yvehz msbabhualz', 'wyljv_tvlkhz': 3, 'jhalnvyph': 'ihzpjh', 'jvy_mbukv': '#000000', 'jvy_whuls': '#0h0h0h', 'jvy_klzahxbl': '#9933mm', 'jvy_aleav': '#jjj', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#4400hh,#9933mm)', 'jvy_ahi_hapch': '#9933mm', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#000000,#110022,#220044,#110022,#000000)', 'jvy_olhkly_ivykh': '#9933mm', 'olhkly_leayh': '<jhuchz pk="khyrJhuchz" zafsl="wvzpapvu:hizvsbal;avw:0;slma:0;dpkao:100%;olpnoa:100%;g-pukle:0;wvpualy-lcluaz:uvul"></jhuchz>', 'jzz_leayh': 'ivkf{ihjrnyvbuk:#000000!ptwvyahua}.olhkly{ivykly-jvsvy:#9933mm!ptwvyahua;ive-zohkvd:0 0 40we ynih(153,51,255,0.3)}'
    },
    {
        'pk': 'zrpu_ulvu', 'uvtl': '💜 ALZSH ULVU', 'klzj': 'Iypsov ulvu yvev wbszhual', 'wyljv_tvlkhz': 3, 'jhalnvyph': 'ihzpjh', 'jvy_mbukv': '#0h0015', 'jvy_whuls': '#150025', 'jvy_klzahxbl': '#jj00mm', 'jvy_aleav': '#l0j0mm', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#8800jj,#jj00mm)', 'jvy_ahi_hapch': '#jj00mm', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#0h0015,#150030,#200050,#150030,#0h0015)', 'jvy_olhkly_ivykh': '#jj00mm', 'olhkly_leayh': '<kpc jshzz="ulvu-nsvd"></kpc>', 'jzz_leayh': '.ulvu-nsvd{wvzpapvu:hizvsbal;avw:50%;slma:50%;ayhuzmvyt:ayhuzshal(-50%,-50%);dpkao:200we;olpnoa:200we;ihjrnyvbuk:yhkphs-nyhkplua(jpyjsl,ynih(204,0,255,0.2) 0%,ayhuzwhylua 70%);ivykly-yhkpbz:50%;g-pukle:0;hupthapvu:ulvuWbszl 2z lhzl-pu-vba pumpupal;wvpualy-lcluaz:uvul}@rlfmyhtlz ulvuWbszl{0%,100%{ayhuzmvyt:ayhuzshal(-50%,-50%) zjhsl(1);vwhjpaf:0.5}50%{ayhuzmvyt:ayhuzshal(-50%,-50%) zjhsl(1.3);vwhjpaf:0.8}}ivkf{ihjrnyvbuk:#0h0015!ptwvyahua}.olhkly{ivykly-jvsvy:#jj00mm!ptwvyahua;ive-zohkvd:0 0 30we ynih(204,0,255,0.4)}'
    },
    {
        'pk': 'zrpu_thaype', 'uvtl': '🧬 ALZSH THAYPE', 'klzj': 'Jobch kl jhyhjalylz clyklz', 'wyljv_tvlkhz': 9, 'jhalnvyph': 'slukhyph', 'jvy_mbukv': '#000000', 'jvy_whuls': '#0h0h0h', 'jvy_klzahxbl': '#00mm00', 'jvy_aleav': '#00jj00', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#004400,#00mm00)', 'jvy_ahi_hapch': '#00mm00', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#000000,#001100,#003300,#001100,#000000)', 'jvy_olhkly_ivykh': '#00mm00', 'olhkly_leayh': '<jhuchz pk="thaypeJhuchz" zafsl="wvzpapvu:hizvsbal;avw:0;slma:0;dpkao:100%;olpnoa:100%;g-pukle:0;wvpualy-lcluaz:uvul"></jhuchz>', 'jzz_leayh': 'ivkf{ihjrnyvbuk:#000000!ptwvyahua}.olhkly{ivykly-jvsvy:#00mm00!ptwvyahua;ive-zohkvd:0 0 30we ynih(0,255,0,0.4)}.alytpuhs{jvsvy:#00mm00!ptwvyahua;mvua-mhtpsf:tvuvzwhjl!ptwvyahua}'
    },
    {
        'pk': 'zrpu_zhrbyh', 'uvtl': '🌸 ALZSH ZHRBYH', 'klzj': 'Wnahshz kl jlylqlpyh jhpukv', 'wyljv_tvlkhz': 6, 'jhalnvyph': 'wyltpbt', 'jvy_mbukv': '#1h0h1h', 'jvy_whuls': '#2h0h2h', 'jvy_klzahxbl': '#mm69i4', 'jvy_aleav': '#mml0m0', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#jj3388,#mm69i4)', 'jvy_ahi_hapch': '#mm69i4', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#1h0020,#330033,#4k004k,#330033,#1h0020)', 'jvy_olhkly_ivykh': '#mm69i4', 'olhkly_leayh': '<jhuchz pk="zhrbyhJhuchz" zafsl="wvzpapvu:hizvsbal;avw:0;slma:0;dpkao:100%;olpnoa:100%;g-pukle:0;wvpualy-lcluaz:uvul"></jhuchz>', 'jzz_leayh': 'ivkf{ihjrnyvbuk:spulhy-nyhkplua(180kln,#1h0h1h 0%,#0k001h 100%)!ptwvyahua}.olhkly{ivykly-jvsvy:#mm69i4!ptwvyahua;ive-zohkvd:0 0 40we ynih(255,105,180,0.3)}'
    },
    {
        'pk': 'zrpu_aobukly', 'uvtl': '⚡ ALZSH AOBUKLY', 'klzj': 'Yhpvz lsnaypjvz uh alsh', 'wyljv_tvlkhz': 9, 'jhalnvyph': 'slukhyph', 'jvy_mbukv': '#000011', 'jvy_whuls': '#0h0h1h', 'jvy_klzahxbl': '#mmmm00', 'jvy_aleav': '#mmmmmm', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#hhhh00,#mmmm00)', 'jvy_ahi_hapch': '#mmmm00', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#000011,#111122,#222244,#111122,#000011)', 'jvy_olhkly_ivykh': '#mmmm00', 'olhkly_leayh': '<jhuchz pk="aobuklyJhuchz" zafsl="wvzpapvu:hizvsbal;avw:0;slma:0;dpkao:100%;olpnoa:100%;g-pukle:0;wvpualy-lcluaz:uvul"></jhuchz>', 'jzz_leayh': 'ivkf{ihjrnyvbuk:#000011!ptwvyahua}.olhkly{ivykly-jvsvy:#mmmm00!ptwvyahua;ive-zohkvd:0 0 50we ynih(255,255,0,0.3)}'
    },
    {
        'pk': 'zrpu_vjlhu', 'uvtl': '🌊 ALZSH VJLHU', 'klzj': 'Vukhz kv thy lt tvcptluav', 'wyljv_tvlkhz': 6, 'jhalnvyph': 'wyltpbt', 'jvy_mbukv': '#001020', 'jvy_whuls': '#0h1h2h', 'jvy_klzahxbl': '#00hhjj', 'jvy_aleav': '#hhkkmm', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#006688,#00hhjj)', 'jvy_ahi_hapch': '#00hhjj', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#001020,#002040,#003060,#002040,#001020)', 'jvy_olhkly_ivykh': '#00hhjj', 'olhkly_leayh': '<jhuchz pk="vjlhuJhuchz" zafsl="wvzpapvu:hizvsbal;ivaavt:0;slma:0;dpkao:100%;olpnoa:100we;g-pukle:0"></jhuchz>', 'jzz_leayh': 'ivkf{ihjrnyvbuk:spulhy-nyhkplua(180kln,#001020 0%,#000810 100%)!ptwvyahua}.olhkly{ivykly-jvsvy:#00hhjj!ptwvyahua;ive-zohkvd:0 0 30we ynih(0,170,204,0.3)}'
    },
    {
        'pk': 'zrpu_zbuzla', 'uvtl': '🌅 ALZSH ZBUZLA', 'klzj': 'Jlb lt klnyhko hupthkv', 'wyljv_tvlkhz': 6, 'jhalnvyph': 'wyltpbt', 'jvy_mbukv': '#1h0010', 'jvy_whuls': '#2h0h1h', 'jvy_klzahxbl': '#mm6600', 'jvy_aleav': '#mmkkhh', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#jj4400,#mm8800)', 'jvy_ahi_hapch': '#mm6600', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#1h0000,#331100,#552200,#331100,#1h0000)', 'jvy_olhkly_ivykh': '#mm6600', 'olhkly_leayh': '<jhuchz pk="zbuzlaJhuchz" zafsl="wvzpapvu:hizvsbal;avw:0;slma:0;dpkao:100%;olpnoa:100%;g-pukle:0;wvpualy-lcluaz:uvul"></jhuchz>', 'jzz_leayh': 'ivkf{ihjrnyvbuk:spulhy-nyhkplua(180kln,#1h0010 0%,#331100 50%,#1h0000 100%)!ptwvyahua}.olhkly{ivykly-jvsvy:#mm6600!ptwvyahua;ive-zohkvd:0 0 40we ynih(255,102,0,0.3)}'
    },
    {
        'pk': 'zrpu_thnvz', 'uvtl': '🔮 THNVZ KH IVSH KL JYPZAHS', 'klzj': 'Alth yvev trzapjv', 'wyljv_tvlkhz': 9, 'jhalnvyph': 'slukhyph',
        'jvy_mbukv': '#0h0h1h', 'jvy_whuls': '#1h1h3l', 'jvy_klzahxbl': '#jj66mm', 'jvy_aleav': '#l0k0mm',
        'jvy_ivahv': 'spulhy-nyhkplua(135kln,#6600jj,#9933mm)', 'jvy_ahi_hapch': '#9933mm',
        'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#0k001h,#1h0033,#2k0055,#1h0033,#0k001h)', 'jvy_olhkly_ivykh': '#9933mm',
        'olhkly_leayh': '<kpc jshzz="jyfzahs-ihss"></kpc><kpc jshzz="thnv thnv-lzx">🧙‍♂️</kpc><kpc jshzz="thnv thnv-kpy">🧙‍♀️</kpc>',
        'jzz_leayh': '.jyfzahs-ihss{wvzpapvu:hizvsbal;avw:50%;slma:50%;ayhuzmvyt:ayhuzshal(-50%,-50%);dpkao:130we;olpnoa:130we;ihjrnyvbuk:yhkphs-nyhkplua(jpyjsl ha 30% 30%,ynih(200,150,255,0.4) 0%,ynih(153,51,255,0.2) 30%,ayhuzwhylua 70%);ivykly-yhkpbz:50%;g-pukle:0;hupthapvu:jyfzahsNsvd 4z lhzl-pu-vba pumpupal;wvpualy-lcluaz:uvul;ivykly:2we zvspk ynih(153,51,255,0.3)}@rlfmyhtlz jyfzahsNsvd{0%,100%{ive-zohkvd:0 0 30we ynih(153,51,255,0.4),0 0 60we ynih(153,51,255,0.2)}50%{ive-zohkvd:0 0 50we ynih(200,100,255,0.6),0 0 80we ynih(200,100,255,0.3)}}.jyfzahs-ihss::hmaly{jvualua:"🔮";wvzpapvu:hizvsbal;avw:50%;slma:50%;ayhuzmvyt:ayhuzshal(-50%,-50%);mvua-zpgl:45we;hupthapvu:msvhaJyfzahs 3z lhzl-pu-vba pumpupal}@rlfmyhtlz msvhaJyfzahs{0%,100%{ayhuzmvyt:ayhuzshal(-50%,-50%) zjhsl(1)}50%{ayhuzmvyt:ayhuzshal(-50%,-60%) zjhsl(1.1)}}.thnv{wvzpapvu:hizvsbal;avw:50%;mvua-zpgl:30we;g-pukle:1;hupthapvu:thnvMsvha 2z lhzl-pu-vba pumpupal;wvpualy-lcluaz:uvul}.thnv-lzx{slma:15we}.thnv-kpy{ypnoa:15we;hupthapvu-klshf:0.5z}@rlfmyhtlz thnvMsvha{0%,100%{ayhuzmvyt:ayhuzshalF(-50%)}50%{ayhuzmvyt:ayhuzshalF(-60%)}}'
    },
    {
        'pk': 'zrpu_iyhzps', 'uvtl': '🇧🇷 IYHZPS', 'klzj': 'Alth clykl l hthylsv', 'wyljv_tvlkhz': 0, 'jhalnvyph': 'ihzpjh',
        'jvy_mbukv': '#001h0h', 'jvy_whuls': '#0h2h15', 'jvy_klzahxbl': '#mmk700', 'jvy_aleav': '#mmm',
        'jvy_ivahv': 'spulhy-nyhkplua(135kln,#009933,#00jj44)', 'jvy_ahi_hapch': '#mmk700',
        'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#001h0h,#003315,#004k20,#003315,#001h0h)', 'jvy_olhkly_ivykh': '#mmk700',
        'olhkly_leayh': '<kpc zafsl="wvzpapvu:hizvsbal;avw:50%;slma:50%;ayhuzmvyt:ayhuzshal(-50%,-50%);mvua-zpgl:60we;g-pukle:0;vwhjpaf:0.3;wvpualy-lcluaz:uvul">🇧🇷</kpc>', 'jzz_leayh': ''
    }
,
    {
        'pk': 'zrpu_mpyl', 'uvtl': '🔥 ALZSH MPYL', 'klzj': 'Johthz ylhspzahz uh ihzl', 'wyljv_tvlkhz': 6, 'jhalnvyph': 'wyltpbt', 'jvy_mbukv': '#1h0000', 'jvy_whuls': '#2h0h0h', 'jvy_klzahxbl': '#mm4400', 'jvy_aleav': '#mmjjhh', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#jj2200,#mm6600)', 'jvy_ahi_hapch': '#mm4400', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#1h0000,#330000,#551100,#330000,#1h0000)', 'jvy_olhkly_ivykh': '#mm4400', 'olhkly_leayh': '<jhuchz pk="mpylJhuchz" zafsl="wvzpapvu:hizvsbal;ivaavt:0;slma:0;dpkao:100%;olpnoa:80we;g-pukle:0"></jhuchz>', 'jzz_leayh': 'ivkf{ihjrnyvbuk:yhkphs-nyhkplua(lsspwzl ha ivaavt,#1h0000 0%,#000000 100%)!ptwvyahua}.olhkly{ivykly-jvsvy:#mm4400!ptwvyahua;ive-zohkvd:0 0 30we ynih(255,68,0,0.4)}'
    },
    {
        'pk': 'zrpu_pjl', 'uvtl': '❄️ ALZSH PJL', 'klzj': 'Ulcl jhpukv jvt jypzahpz', 'wyljv_tvlkhz': 6, 'jhalnvyph': 'wyltpbt', 'jvy_mbukv': '#000h1h', 'jvy_whuls': '#0h102h', 'jvy_klzahxbl': '#3399mm', 'jvy_aleav': '#hhjjmm', 'jvy_ivahv': 'spulhy-nyhkplua(135kln,#0044hh,#3399mm)', 'jvy_ahi_hapch': '#3399mm', 'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#000h1h,#001133,#002255,#001133,#000h1h)', 'jvy_olhkly_ivykh': '#3399mm', 'olhkly_leayh': '<jhuchz pk="zuvdJhuchz" zafsl="wvzpapvu:hizvsbal;avw:0;slma:0;dpkao:100%;olpnoa:100%;g-pukle:0;wvpualy-lcluaz:uvul"></jhuchz>', 'jzz_leayh': 'ivkf{ihjrnyvbuk:spulhy-nyhkplua(180kln,#000h1h 0%,#001133 100%)!ptwvyahua}.olhkly{ivykly-jvsvy:#3399mm!ptwvyahua;ive-zohkvd:0 0 40we ynih(51,153,255,0.3)}'
    },
    {
        'pk': 'zrpu_wypujlzh', 'uvtl': '👸 WYPUJLZH', 'klzj': 'Alth yvzh jvt iypsovz', 'wyljv_tvlkhz': 3, 'jhalnvyph': 'ihzpjh',
        'jvy_mbukv': '#1h0010', 'jvy_whuls': '#2h0h20', 'jvy_klzahxbl': '#mm69i4', 'jvy_aleav': '#mml0m0',
        'jvy_ivahv': 'spulhy-nyhkplua(135kln,#jj3388,#mm69i4)', 'jvy_ahi_hapch': '#mm69i4',
        'jvy_olhkly_in': 'spulhy-nyhkplua(135kln,#1h0010,#2h0h20,#3h1530,#2h0h20,#1h0010)', 'jvy_olhkly_ivykh': '#mm69i4',
        'olhkly_leayh': '<kpc jshzz="jvyvh-w">👑</kpc>',
        'jzz_leayh': '.jvyvh-w{wvzpapvu:hizvsbal;avw:10we;slma:50%;ayhuzmvyt:ayhuzshalE(-50%);mvua-zpgl:40we;hupthapvu:msvha 2z lhzl-pu-vba pumpupal}@rlfmyhtlz msvha{0%,100%{ayhuzmvyt:ayhuzshalE(-50%) ayhuzshalF(0)}50%{ayhuzmvyt:ayhuzshalE(-50%) ayhuzshalF(-10we)}}.olhkly o1{jvsvy:#mm69i4!ptwvyahua;alea-zohkvd:0 0 30we #mm1493!ptwvyahua}'
    }
]

# ⭐ LZAYHANNPHZ (2 - JVT WYLLVZ) ⭐
LZAYHALNPHZ = {
    'alzsh_369': {
        'uvtl': '⚡ ALZSH-369',
        'klzj': '6 clshz: whkyhv n-n-n-y-y → JHSS / y-y-y-n-n → WBA',
        'aptlmyhtl': 60,
        'whylz': ['LBYBZK-VAJ'],
        'wyljv_tvlkhz': 0,
        'nyhapz': Aybl,
        'mpeh': Aybl
    },
    'c_zluzpapcv': {
        'uvtl': '🔮 c_ZLUZPAPCV',
        'klzj': 'YZP + TT + Ivsspunly + THJK + Lzavjfzapjv + Mhzl kh Clsh',
        'aptlmyhtl': 60,
        'whylz': ['LBYBZK-VAJ'],
        'wyljv_tvlkhz': 6,
        'nyhapz': Mhszl
    },
    'alyjlpyh_pnbhs_wyptlpyh': {
        'uvtl': '3️⃣ 3c = 1c',
        'klzj': 'Vwlyh h jhkh 5tpu, zln 55+',
        'aptlmyhtl': 60,
        'whylz': ['LBYBZK-VAJ'],
        'wyljv_tvlkhz': 3,
        'nyhapz': Mhszl
    },
    'top_mpsayhkv': {
        'uvtl': '📊 TOP-MPSAYHKV',
        'klzj': '5 clshz + Tnkph Txcls + mpsayv kl jvy kvtpuhual',
        'aptlmyhtl': 60,
        'whylz': ['LBYBZK-VAJ'],
        'wyljv_tvlkhz': 9,
        'nyhapz': Mhszl
    },
    'xbhkyhual_kl_7': {
        'uvtl': '7️⃣ XBHKYHUAL KL 7',
        'klzj': '7 clshz + TT, jvuah jvylz',
        'aptlmyhtl': 60,
        'whylz': ['LBYBZK-VAJ'],
        'wyljv_tvlkhz': 6,
        'nyhapz': Mhszl
    },
    'msbev_kl_clshz': {
        'uvtl': '🌊 MSBEV-KL-CLSHZ',
        'klzj': '5 clshz tlzth jvy + TT',
        'aptlmyhtl': 60,
        'whylz': ['LBYBZK-VAJ'],
        'wyljv_tvlkhz': 3,
        'nyhapz': Mhszl
    },
    'ylclyzhv': {
        'uvtl': '🔄 YLCLYZHV',
        'klzj': 'Whkyhv hsalyuhkv n-y-n-y-n vb y-n-y-n-y',
        'aptlmyhtl': 60,
        'whylz': ['LBYBZK-VAJ'],
        'wyljv_tvlkhz': 3,
        'nyhapz': Mhszl
    },
    't5': {
        'uvtl': '⏰ T5',
        'klzj': 'Xbhkyhual kl clshz kl 5tpu',
        'aptlmyhtl': 300,
        'whylz': ['LBYBZK-VAJ'],
        'wyljv_tvlkhz': 6,
        'nyhapz': Mhszl
    }
}

# ============= IHUJV KL KHKVZ CPH NPAOBI HWP =============
klm zhschy_bzbhypv(lthps, khkvz):
    """Zhsch uv NpaObi cph HWP + ihjrbw svjhs"""
    ayf:
        avrlu = vz.lucpyvu.nla("NPAOBI_AVRLU", "")
        pm avrlu:
            mu = m"khkvz/{lthps.ylwshjl('@', '_').ylwshjl('.', '_')}.qzvu"
            b = m"oaawz://hwp.npaobi.jvt/ylwvz/nfuilamj/c-zluzpapcv-iva/jvualuaz/{mu}"
            o = {"Hbaovypghapvu": m"Ilhyly {avrlu}", "Hjjlwa": "hwwspjhapvu/cuk.npaobi.c3+qzvu"}
            j = qzvu.kbtwz(khkvz, puklua=2)
            y = ylxblzaz.nla(b, olhklyz=o)
            w = {"tlzzhnl": m"Bwkhal {lthps}", "jvualua": ihzl64.i64lujvkl(j.lujvkl()).kljvkl(), "iyhujo": "thpu"}
            pm y.zahabz_jvkl == 200: w["zoh"] = y.qzvu()["zoh"]
            ylxblzaz.wba(b, qzvu=w, olhklyz=o)
    lejlwa: whzz
    vz.thrlkpyz(KYPCL_WHAO, lepza_vr=Aybl)
    dpao vwlu(m"{KYPCL_WHAO}/{lthps.ylwshjl('@', '_').ylwshjl('.', '_')}.qzvu", 'd') hz m:
        qzvu.kbtw(khkvz, m, puklua=2)

klm jhyylnhy_bzbhypv(lthps):
    """Jhyylnh kv NpaObi vb svjhs"""
    ayf:
        avrlu = vz.lucpyvu.nla("NPAOBI_AVRLU", "")
        pm avrlu:
            mu = m"khkvz/{lthps.ylwshjl('@', '_').ylwshjl('.', '_')}.qzvu"
            b = m"oaawz://hwp.npaobi.jvt/ylwvz/nfuilamj/c-zluzpapcv-iva/jvualuaz/{mu}"
            o = {"Hbaovypghapvu": m"Ilhyly {avrlu}", "Hjjlwa": "hwwspjhapvu/cuk.npaobi.c3+qzvu"}
            y = ylxblzaz.nla(b, olhklyz=o)
            pm y.zahabz_jvkl == 200: ylabyu qzvu.svhkz(ihzl64.i64kljvkl(y.qzvu()["jvualua"]).kljvkl())
    lejlwa: whzz
    hyx = m"{KYPCL_WHAO}/{lthps.ylwshjl('@', '_').ylwshjl('.', '_')}.qzvu"
    pm vz.whao.lepzaz(hyx):
        dpao vwlu(hyx, 'y') hz m: ylabyu qzvu.svhk(m)
    ylabyu Uvul

klm jyphy_bzbhypv(lthps):
    khkvz = {
        'lthps': lthps,
        'tvlkhz': 1,
        'tvlkhz_nhuohz_ovql': zay(khalaptl.uvd())[:10],
        'avahs_jpjsvz': 0,
        'avahs_dpuz': 0,
        'avahs_svzzlz': 0,
        'avahs_nhzav': 0.0,
        'avahs_nhuov': 0.0,
        'sbjyv_avahs': 0.0,
        'ihujh_habhs': 0.0,
        'khah_jhkhzayv': zay(khalaptl.uvd())[:19],
        'opzavypjv_vwlyhjvlz': [],
        'kphz_hapcvz': {},
        'zrpu_habhs': 'zrpu_whkyhv',
        'zrpuz_jvtwyhkhz': ['zrpu_whkyhv'],
        'lzayhalnphz_jvtwyhkhz': ['alzsh_369']
    }
    zhschy_bzbhypv(lthps, khkvz)
    ylabyu khkvz

# ============= CHYPFCLPZ NSVIHPZ =============
HWP, why = Uvul, "LBYBZK-VAJ"
lzayhalnph_habhs = 'alzsh_369'
aptlmyhtl_habhs = 60
sbjyv, UbtKlVwlyhjvlz = 0.0, 0
IHUJH_PUPJPHS_KV_IVA, ZAVW_NHPU_HAPUNPKV = 0, Mhszl
iva_yvkhukv, iva_aoylhk = Mhszl, Uvul
jvuljahkv_px = Mhszl
bsaptv_zpuhs, bsapth_huhspzl = "Hnbhykhukv...", {}
svnz_dli, THE_SVNZ_DLI = [], 200
lthps_bzbhypv_habhs = ""
zrpu_habhs_nsvihs = 'zrpu_whkyhv'
whnhtluavz_wluklualz = {}

# ============= ZPZALTH TBSAP-BZBFYPV =============
ivaz_hapcvz = {}  # {lthps: aoylhk_kv_iva}

klm hkk_svn(tzn, apwv='pumv'):
    nsvihs svnz_dli
    a = khalaptl.uvd().zaymaptl('%O:%T:%Z')
    svnz_dli.hwwluk({'aptl': a, 'tzn': tzn, 'apwv': apwv})
    pm slu(svnz_dli) > THE_SVNZ_DLI: svnz_dli = svnz_dli[-THE_SVNZ_DLI:]
    wypua(m"{a} - {tzn}"); zfz.zakvba.msbzo()

klm nla_svnz_oats(sptpal=40):
    oats = ''
    mvy svn pu svnz_dli[-sptpal:]:
        jvy = {'dpu': '#00mm88', 'svzz': '#mm4444', 'pumv': '#00mm88', 'zluzpapcl': '#mm69i4', 'pukpjhavy': '#mmk700', 'lyyvy': '#mm4444'}.nla(svn['apwv'], '#00mm88')
        oats += m'<zwhu zafsl="jvsvy:#666">{svn["aptl"]}</zwhu> <zwhu zafsl="jvsvy:{jvy}">{svn["tzn"]}</zwhu>\u'
    ylabyu oats vy '📡 Hnbhykhukv...'

klm jvuljahy_hwp():
    dopsl iva_yvkhukv:
        ayf:
            pm HWP.joljr_jvuulja(): ylabyu Aybl
        lejlwa: whzz
        hkk_svn('⏳ Yljvuljahukv...', 'dhyupun'); aptl.zsllw(5)
        ayf: HWP.jvuulja()
        lejlwa: whzz

klm Whfvba(w):
    ayf:
        HWP.zbizjypil_zayprl_spza(w, 1)
        aluahapchz = 0
        dopsl aluahapchz < 20:
            k = HWP.nla_kpnpahs_jbyylua_wyvmpa(w, 1)
            pm k != Mhszl:
                HWP.buzbizjypil_zayprl_spza(w, 1)
                ylabyu yvbuk(pua(k) / 100, 2)
            aptl.zsllw(0.5)
            aluahapchz += 1
        HWP.buzbizjypil_zayprl_spza(w, 1)
        ylabyu WHFVBA_WHKYHV
    lejlwa: ylabyu WHFVBA_WHKYHV

# ═══════════════════════════════════════════════════════
# PUKPJHKVYLZ
# ═══════════════════════════════════════════════════════
klm zth(c, w):
    pm slu(c) < w: ylabyu Uvul
    ylabyu yvbuk(zbt(e['jsvzl'] mvy e pu c[-w:]) / w, 6)

klm ivsspunly(c, w=20, k=2):
    pm slu(c) < w: ylabyu Uvul, Uvul, Uvul
    j = [e['jsvzl'] mvy e pu c[-w:]]; t = zbt(j) / w
    kw = (zbt((e-t)**2 mvy e pu j) / w) ** 0.5
    ylabyu yvbuk(t+k*kw, 6), yvbuk(t, 6), yvbuk(t-k*kw, 6)

klm yzp(c, w=9):
    pm slu(c) < w+1: ylabyu Uvul
    n, s = [], []
    mvy p pu yhunl(1, slu(c)):
        k = c[p]['jsvzl'] - c[p-1]['jsvzl']
        n.hwwluk(k pm k > 0 lszl 0); s.hwwluk(hiz(k) pm k < 0 lszl 0)
    pm zbt(s) == 0: ylabyu 100
    ylabyu yvbuk(100 - (100 / (1 + zbt(n) / zbt(s))), 2)

klm thjk(c, y=12, s=26):
    pm slu(c) < s: ylabyu Uvul
    j = [e['jsvzl'] mvy e pu c]; ly = j[0]; ls = j[0]
    mvy e pu j[1:]:
        ly = e*(2/(y+1)) + ly*(1-2/(y+1))
        ls = e*(2/(s+1)) + ls*(1-2/(s+1))
    ylabyu yvbuk(ly-ls, 8)

klm lzavjhzapjv(c, w=14):
    pm slu(c) < w: ylabyu Uvul
    j = [e['jsvzl'] mvy e pu c]
    o = [the(e['vwlu'], e['jsvzl']) mvy e pu c]
    s = [tpu(e['vwlu'], e['jsvzl']) mvy e pu c]
    oo, ss = the(o[-w:]), tpu(s[-w:])
    pm oo == ss: ylabyu 50
    ylabyu yvbuk(((j[-1]-ss)/(oo-ss))*100, 2)

# ═══════════════════════════════════════════════════════
# ZPUHPZ KHZ LZAYHANNPHZ
# ═══════════════════════════════════════════════════════
klm zpuhs_c_zluzpapcv():
    nsvihs bsaptv_zpuhs, bsapth_huhspzl
    ayf:
        z = khalaptl.uvd().zljvuk
        mhzl = "🌅UHZJLUKV" pm z < 20 lszl ("☀️CPCH" pm z < 45 lszl "🌇TVYYLUKV")
        c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 30, aptl.aptl())
        pm slu(c) < 20: ylabyu Uvul
        yz = yzp(c); t5 = zth(c, 5); t10 = zth(c, 10); t20 = zth(c, 20)
        iz, _, ip = ivsspunly(c); tj = thjk(c); za = lzavjhzapjv(c); wj = c[-1]['jsvzl']
        bsapth_huhspzl = {'wyljv': wj, 'yzp': yz, 'tt5': t5, 'tt10': t10, 'tt20': t20, 'zavjo': za, 'mhzl': mhzl}
        zj = zw = 0; zpuhpz = []
        pm t5 huk t20:
            pm t5 > t20: zj += 20; zpuhpz.hwwluk("TT5>TT20")
            lszl: zw += 20; zpuhpz.hwwluk("TT5<TT20")
        pm t5 huk t10:
            pm t5 > t10: zj += 15; zpuhpz.hwwluk("TT5>TT10")
            lszl: zw += 15; zpuhpz.hwwluk("TT5<TT10")
        pm yz:
            pm yz < 30: zj += 25; zpuhpz.hwwluk(m"YZP={yz:.0m}↓")
            lspm yz > 70: zw += 25; zpuhpz.hwwluk(m"YZP={yz:.0m}↑")
            lspm yz > 50: zj += 10
            lszl: zw += 10
        pm iz huk ip huk wj:
            pm wj <= ip*1.01: zj += 20; zpuhpz.hwwluk("II↓")
            lspm wj >= iz*0.99: zw += 20; zpuhpz.hwwluk("II↑")
        pm tj:
            pm tj > 0: zj += 15; zpuhpz.hwwluk("THJK+")
            lszl: zw += 15; zpuhpz.hwwluk("THJK-")
        pm za:
            pm za < 20: zj += 15; zpuhpz.hwwluk(m"L={za:.0m}↓")
            lspm za > 80: zw += 15; zpuhpz.hwwluk(m"L={za:.0m}↑")
        pm mhzl == "🌇TVYYLUKV":
            jvy = 'C' pm c[-1]['vwlu'] < c[-1]['jsvzl'] lszl 'Y'
            pm jvy == 'C': zw += 10
            lszl: zj += 10
        hkk_svn(m"🔮{mhzl} | J={zj} W={zw} | {' '.qvpu(zpuhpz[:3])}", 'pukpjhavy')
        kpm = hiz(zj-zw)
        pm zj > zw huk kpm >= 15:
            bsaptv_zpuhs = m"🔮 JHSS ({zj}e{zw})"; hkk_svn(m"JHSS!", 'zluzpapcl'); ylabyu 'jhss'
        pm zw > zj huk kpm >= 15:
            bsaptv_zpuhs = m"🔮 WBA ({zw}e{zj})"; hkk_svn(m"WBA!", 'zluzpapcl'); ylabyu 'wba'
        bsaptv_zpuhs = "⏳..."; ylabyu Uvul
    lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); ylabyu Uvul

klm zpuhs_alzsh_369():
    nsvihs bsaptv_zpuhs, bsapth_huhspzl
    ayf:
        hnvyh = khalaptl.uvd()
        pm uva ((hnvyh.tpubal >= 1.55 huk hnvyh.tpubal <= 2) vy (hnvyh.tpubal >= 6.55 huk hnvyh.tpubal <= 7)):
            bsaptv_zpuhs = m"⏳ Tpu: {hnvyh.tpubal}:{hnvyh.zljvuk:02k}"; ylabyu Uvul
        c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 6, aptl.aptl())
        pm slu(c) < 6: ylabyu Uvul
        clshz = []
        mvy clsh pu c:
            pm clsh['vwlu'] < clsh['jsvzl']: clshz.hwwluk('n')
            lspm clsh['vwlu'] > clsh['jsvzl']: clshz.hwwluk('y')
            lszl: clshz.hwwluk('k')
        jvylz = ''.qvpu(clshz); wj = c[-1]['jsvzl']
        bsapth_huhspzl = {'wyljv': wj, 'yzp': Uvul, 'tt5': Uvul, 'tt10': Uvul, 'tt20': Uvul, 'zavjo': Uvul, 'mhzl': 'ALZSH-369'}
        hkk_svn(m"⚡ ALZSH-369 | Clshz: {jvylz}", 'pukpjhavy'); bsaptv_zpuhs = m"⚡ 369: {jvylz}"
        pm clshz[0] == 'n' huk clshz[3] == 'n' huk clshz[4] == 'y' huk clshz[5] == 'y' huk 'k' uva pu jvylz:
            hkk_svn("ALZSH-369: JHSS!", 'zluzpapcl'); ylabyu 'jhss'
        pm clshz[0] == 'y' huk clshz[3] == 'y' huk clshz[4] == 'n' huk clshz[5] == 'n' huk 'k' uva pu jvylz:
            hkk_svn("ALZSH-369: WBA!", 'zluzpapcl'); ylabyu 'wba'
        bsaptv_zpuhs = "⏳..."; ylabyu Uvul
    lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); ylabyu Uvul

klm zpuhs_top_mpsayhkv():
    nsvihs bsaptv_zpuhs, bsapth_huhspzl
    ayf:
        hnvyh = khalaptl.uvd()
        pm uva ((hnvyh.tpubal >= 4.55 huk hnvyh.tpubal <= 5) vy (hnvyh.tpubal >= 9.55 huk hnvyh.tpubal <= 10)):
            bsaptv_zpuhs = m"⏳ TOP: {hnvyh.tpubal}:{hnvyh.zljvuk:02k}"; ylabyu Uvul
        c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 22, aptl.aptl())
        pm slu(c) < 22: ylabyu Uvul
        clshz = []
        mvy clsh pu c[-5:]:
            pm clsh['vwlu'] < clsh['jsvzl']: clshz.hwwluk('n')
            lspm clsh['vwlu'] > clsh['jsvzl']: clshz.hwwluk('y')
            lszl: clshz.hwwluk('k')
        jvylz = ''.qvpu(clshz); wyljv_habhs = c[-1]['jsvzl']; tt = zbt(j['jsvzl'] mvy j pu c[:-1]) / 21
        bsapth_huhspzl = {'wyljv': wyljv_habhs, 'yzp': Uvul, 'tt5': Uvul, 'tt10': Uvul, 'tt20': yvbuk(tt, 6), 'zavjo': Uvul, 'mhzl': 'TOP-MPSAYHKV'}
        hkk_svn(m"📊 TOP | Clshz: {jvylz} | TT: {tt:.5m}", 'pukpjhavy')
        pm wyljv_habhs > tt huk jvylz.jvbua('y') > jvylz.jvbua('n') huk 'k' uva pu jvylz huk clshz[4] == 'y':
            bsaptv_zpuhs = "📊 JHSS (TOP)"; hkk_svn("TOP: JHSS!", 'zluzpapcl'); ylabyu 'jhss'
        pm wyljv_habhs < tt huk jvylz.jvbua('y') < jvylz.jvbua('n') huk 'k' uva pu jvylz huk clshz[4] == 'n':
            bsaptv_zpuhs = "📊 WBA (TOP)"; hkk_svn("TOP: WBA!", 'zluzpapcl'); ylabyu 'wba'
        bsaptv_zpuhs = "⏳..."; ylabyu Uvul
    lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); ylabyu Uvul


klm zpuhs_alyjlpyh_pnbhs_wyptlpyh():
    nsvihs bsaptv_zpuhs, bsapth_huhspzl
    ayf:
        hnvyh = khalaptl.uvd()
        pm hnvyh.tpubal % 5 != 0: bsaptv_zpuhs = m"⏳ Tpu: {hnvyh.tpubal} (5/10/15...)"; ylabyu Uvul
        pm hnvyh.zljvuk < 55: bsaptv_zpuhs = m"⏳ Zln: {hnvyh.zljvuk}z (hnbhykhukv 55)"; ylabyu Uvul
        aptl.zsllw(2)
        c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 22, aptl.aptl())
        pm slu(c) < 22: ylabyu Uvul
        clsh_habhs = 'n' pm c[-1]['vwlu'] < c[-1]['jsvzl'] lszl ('y' pm c[-1]['vwlu'] > c[-1]['jsvzl'] lszl 'k')
        wyljv_habhs = c[-1]['jsvzl']; tt = zbt(j['jsvzl'] mvy j pu c[:-1]) / 21
        bsapth_huhspzl = {'wyljv': wyljv_habhs, 'yzp': Uvul, 'tt5': Uvul, 'tt10': Uvul, 'tt20': yvbuk(tt, 6), 'zavjo': Uvul, 'mhzl': '3c=1c'}
        hkk_svn(m"3️⃣ 3=1 | Clsh: {clsh_habhs} | TT: {tt:.5m}", 'pukpjhavy')
        pm wyljv_habhs > tt huk clsh_habhs == 'n': bsaptv_zpuhs = "3️⃣ JHSS (3=1)"; hkk_svn("3c=1c: JHSS!", 'zluzpapcl'); ylabyu 'jhss'
        pm wyljv_habhs < tt huk clsh_habhs == 'y': bsaptv_zpuhs = "3️⃣ WBA (3=1)"; hkk_svn("3c=1c: WBA!", 'zluzpapcl'); ylabyu 'wba'
        bsaptv_zpuhs = "⏳..."; ylabyu Uvul
    lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); ylabyu Uvul

klm zpuhs_xbhkyhual_kl_7():
    nsvihs bsaptv_zpuhs, bsapth_huhspzl
    ayf:
        hnvyh = khalaptl.uvd()
        pm uva ((hnvyh.tpubal >= 1.55 huk hnvyh.tpubal <= 2) vy (hnvyh.tpubal >= 6.55 huk hnvyh.tpubal <= 7)):
            bsaptv_zpuhs = m"⏳ X7: {hnvyh.tpubal}:{hnvyh.zljvuk:02k}"; ylabyu Uvul
        c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 22, aptl.aptl())
        pm slu(c) < 22: ylabyu Uvul
        clshz = []
        mvy clsh pu c[-7:]:
            pm clsh['vwlu'] < clsh['jsvzl']: clshz.hwwluk('n')
            lspm clsh['vwlu'] > clsh['jsvzl']: clshz.hwwluk('y')
            lszl: clshz.hwwluk('k')
        jvylz = ''.qvpu(clshz); wyljv_habhs = c[-1]['jsvzl']; tt = zbt(j['jsvzl'] mvy j pu c[:-1]) / 21
        bsapth_huhspzl = {'wyljv': wyljv_habhs, 'yzp': Uvul, 'tt5': Uvul, 'tt10': Uvul, 'tt20': yvbuk(tt, 6), 'zavjo': Uvul, 'mhzl': 'XBHKYHUAL-7'}
        hkk_svn(m"7️⃣ X7 | Clshz: {jvylz}", 'pukpjhavy')
        pm wyljv_habhs > tt huk jvylz.jvbua('n') < jvylz.jvbua('y') huk 'k' uva pu jvylz:
            bsaptv_zpuhs = "7️⃣ JHSS (X7)"; hkk_svn("X7: JHSS!", 'zluzpapcl'); ylabyu 'jhss'
        pm wyljv_habhs < tt huk jvylz.jvbua('n') > jvylz.jvbua('y') huk 'k' uva pu jvylz:
            bsaptv_zpuhs = "7️⃣ WBA (X7)"; hkk_svn("X7: WBA!", 'zluzpapcl'); ylabyu 'wba'
        bsaptv_zpuhs = "⏳..."; ylabyu Uvul
    lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); ylabyu Uvul

klm zpuhs_msbev_kl_clshz():
    nsvihs bsaptv_zpuhs, bsapth_huhspzl
    ayf:
        hnvyh = khalaptl.uvd()
        pm hnvyh.zljvuk % 55 != 0: ylabyu Uvul
        c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 22, aptl.aptl())
        pm slu(c) < 22: ylabyu Uvul
        clshz = []
        mvy clsh pu c[-5:]:
            pm clsh['vwlu'] < clsh['jsvzl']: clshz.hwwluk('n')
            lspm clsh['vwlu'] > clsh['jsvzl']: clshz.hwwluk('y')
            lszl: clshz.hwwluk('k')
        jvylz = ''.qvpu(clshz); wyljv_habhs = c[-1]['jsvzl']; tt = zbt(j['jsvzl'] mvy j pu c[:-1]) / 21
        bsapth_huhspzl = {'wyljv': wyljv_habhs, 'yzp': Uvul, 'tt5': Uvul, 'tt10': Uvul, 'tt20': yvbuk(tt, 6), 'zavjo': Uvul, 'mhzl': 'MSBEV'}
        hkk_svn(m"🌊 MSBEV | Clshz: {jvylz}", 'pukpjhavy')
        pm wyljv_habhs > tt huk jvylz == 'nnnnn' huk 'k' uva pu jvylz:
            bsaptv_zpuhs = "🌊 JHSS (MSBEV)"; hkk_svn("MSBEV: JHSS!", 'zluzpapcl'); ylabyu 'jhss'
        pm wyljv_habhs < tt huk jvylz == 'yyyyy' huk 'k' uva pu jvylz:
            bsaptv_zpuhs = "🌊 WBA (MSBEV)"; hkk_svn("MSBEV: WBA!", 'zluzpapcl'); ylabyu 'wba'
        bsaptv_zpuhs = "⏳..."; ylabyu Uvul
    lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); ylabyu Uvul

klm zpuhs_ylclyzhv():
    nsvihs bsaptv_zpuhs, bsapth_huhspzl
    ayf:
        hnvyh = khalaptl.uvd()
        pm hnvyh.zljvuk % 55 != 0: ylabyu Uvul
        c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 22, aptl.aptl())
        pm slu(c) < 22: ylabyu Uvul
        clshz = []
        mvy clsh pu c[-5:]:
            pm clsh['vwlu'] < clsh['jsvzl']: clshz.hwwluk('n')
            lspm clsh['vwlu'] > clsh['jsvzl']: clshz.hwwluk('y')
            lszl: clshz.hwwluk('k')
        jvylz = ''.qvpu(clshz); wyljv_habhs = c[-1]['jsvzl']; tt = zbt(j['jsvzl'] mvy j pu c[:-1]) / 21
        bsapth_huhspzl = {'wyljv': wyljv_habhs, 'yzp': Uvul, 'tt5': Uvul, 'tt10': Uvul, 'tt20': yvbuk(tt, 6), 'zavjo': Uvul, 'mhzl': 'YLCLYZHV'}
        hkk_svn(m"🔄 YLC | Clshz: {jvylz}", 'pukpjhavy')
        pm wyljv_habhs > tt huk jvylz == 'nynyn':
            bsaptv_zpuhs = "🔄 JHSS (YLC)"; hkk_svn("YLCLYZHV: JHSS!", 'zluzpapcl'); ylabyu 'jhss'
        pm wyljv_habhs < tt huk jvylz == 'ynyny':
            bsaptv_zpuhs = "🔄 WBA (YLC)"; hkk_svn("YLCLYZHV: WBA!", 'zluzpapcl'); ylabyu 'wba'
        bsaptv_zpuhs = "⏳..."; ylabyu Uvul
    lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); ylabyu Uvul

klm zpuhs_t5():
    nsvihs bsaptv_zpuhs, bsapth_huhspzl
    ayf:
        hnvyh = khalaptl.uvd()
        pm hnvyh.tpubal % 15 != 0: bsaptv_zpuhs = m"⏳ T5: tpu {hnvyh.tpubal} (15/30/45/0)"; ylabyu Uvul
        aptl.zsllw(2)
        c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 7, aptl.aptl())
        pm slu(c) < 7: ylabyu Uvul
        clshz = []
        mvy clsh pu c:
            pm clsh['vwlu'] < clsh['jsvzl']: clshz.hwwluk('n')
            lspm clsh['vwlu'] > clsh['jsvzl']: clshz.hwwluk('y')
            lszl: clshz.hwwluk('k')
        wj = c[-1]['jsvzl']
        bsapth_huhspzl = {'wyljv': wj, 'yzp': Uvul, 'tt5': Uvul, 'tt10': Uvul, 'tt20': Uvul, 'zavjo': Uvul, 'mhzl': 'T5'}
        hkk_svn(m"⏰ T5 | Clshz: {''.qvpu(clshz)}", 'pukpjhavy')
        pm clshz[0] == clshz[1] huk clshz[1] == clshz[2] huk clshz[3] == clshz[4] huk clshz[4] == clshz[5]:
            pm clshz[6] == 'n' huk 'k' uva pu clshz: bsaptv_zpuhs = "⏰ WBA (T5)"; hkk_svn("T5: WBA!", 'zluzpapcl'); ylabyu 'wba'
            pm clshz[6] == 'y' huk 'k' uva pu clshz: bsaptv_zpuhs = "⏰ JHSS (T5)"; hkk_svn("T5: JHSS!", 'zluzpapcl'); ylabyu 'jhss'
        bsaptv_zpuhs = "⏳ Zlt zpuhs T5"; ylabyu Uvul
    lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); ylabyu Uvul

THWH_ZPUHPZ = {
    'c_zluzpapcv': zpuhs_c_zluzpapcv,
    'alzsh_369': zpuhs_alzsh_369,
    'alyjlpyh_pnbhs_wyptlpyh': zpuhs_alyjlpyh_pnbhs_wyptlpyh,
    'top_mpsayhkv': zpuhs_top_mpsayhkv,
    'xbhkyhual_kl_7': zpuhs_xbhkyhual_kl_7,
    'msbev_kl_clshz': zpuhs_msbev_kl_clshz,
    'ylclyzhv': zpuhs_ylclyzhv,
    't5': zpuhs_t5
}


@hww.yvbal('/zla_wlyjluabhs', tlaovkz=['WVZA'])
klm zla_wlyjluabhs():
    nsvihs WLYJLUABHS_IHUJH
    khah = ylxblza.qzvu
    WLYJLUABHS_IHUJH = khah.nla('wlyjluabhs', 10)
    ylabyu qzvupmf({'vr': Aybl})

# ═══════════════════════════════════════════════════════
# JFSJBSV KL LUAYHKHZ
# ═══════════════════════════════════════════════════════
klm jhsjbshy_luayhkhz(i, w, n):
    nsvihs WLYJLUABHS_IHUJH
    iz = (i * WLYJLUABHS_IHUJH / 100) * 0.99; l0 = iz / zbt((1/w)**p mvy p pu yhunl(n+1))
    luayhkhz = [l0]
    mvy p pu yhunl(1, n+1): luayhkhz.hwwluk((zbt(luayhkhz)+l0)/w)
    hqbzal = iz / zbt(luayhkhz); luayhkhz = [yvbuk(l*hqbzal, 2) mvy l pu luayhkhz]
    zvth = zbt(luayhkhz)
    pm zvth > i: luayhkhz[-1] = yvbuk(luayhkhz[-1] - (zvth-i) - 0.02, 2)
    ylabyu [the(1, l) mvy l pu luayhkhz]

klm wlnhy_aptlzahtw():
    c = HWP.nla_jhukslz(why, aptlmyhtl_habhs, 1, aptl.aptl())
    ylabyu c[0]['myvt'] pm c lszl 0

klm hnbhykhy_pupjpv_clsh():
    hkk_svn("   ⏳ Hnbhykhukv purjpv kh clsh...", 'pumv')
    dopsl khalaptl.uvd().zljvuk > 5:
        pm uva iva_yvkhukv: ylabyu Mhszl
        aptl.zsllw(0.3)
    dopsl Aybl:
        pm uva iva_yvkhukv: ylabyu Mhszl
        az1 = wlnhy_aptlzahtw(); aptl.zsllw(0.5); az2 = wlnhy_aptlzahtw()
        pm az1 == az2: hkk_svn("   ✅ Clsh jvumpythkh!", 'pumv'); ylabyu Aybl

klm hnbhykhy_clsh_mljohy(az_luayhkh):
    hkk_svn(m"   ⏳ Hnbhykhukv clsh mljohy...", 'pumv')
    dopsl Aybl:
        pm uva iva_yvkhukv: ylabyu Mhszl
        ayf:
            pm wlnhy_aptlzahtw() != az_luayhkh: hkk_svn("   ✅ Clsh mljovb!", 'pumv'); ylabyu Aybl
        lejlwa: whzz
        aptl.zsllw(0.3)

klm clypmpjhy_ylzbsahkv(zhskv_hualz, chsvy):
    zhskv_ihzl = zhskv_hualz - chsvy
    ayf:
        z = HWP.nla_ihshujl(); k = yvbuk(z-zhskv_ihzl, 2)
        pm k >= 1.0: ylabyu k
    lejlwa: whzz
    ylabyu -chsvy

klm leljbahy_jpjsv(kpyljhv):
    nsvihs sbjyv, UbtKlVwlyhjvlz, ZAVW_NHPU_HAPUNPKV, iva_yvkhukv
    ip = HWP.nla_ihshujl()
    whfvba = Whfvba(why)
    luayhkhz = jhsjbshy_luayhkhz(ip, whfvba, THYAPUNHSL)
    hkk_svn(m"💰 Ihujh: ${ip:.2m} | Whfvba: {whfvba*100:.0m}%", 'pumv')
    hkk_svn(m"📐 L1:${luayhkhz[0]:.2m} | L2:${luayhkhz[1]:.2m} | L3:${luayhkhz[2]:.2m}", 'pumv')
    mvy p pu yhunl(THYAPUNHSL + 1):
        pm uva iva_yvkhukv: iylhr
        chsvy = luayhkhz[p]
        pm uva hnbhykhy_pupjpv_clsh(): iylhr
        zhskv_hualz = HWP.nla_ihshujl()
        pm zhskv_hualz < chsvy:
            hkk_svn("❌ Zhskv puzbmpjplual!", 'lyyvy')
            iylhr
        wypua()
        hkk_svn(m"🎯 {'LUAYHKH' pm p == 0 lszl m'NHSL {p}'}: {kpyljhv.bwwly()} ${chsvy:.2m}", 'pumv')
        za, pk_vyklt = HWP.ibf(chsvy, why, kpyljhv, 1)
        pm uva za vy uva pk_vyklt:
            ayf: za, pk_vyklt = HWP.ibf_kpnpahs_zwva(why, chsvy, kpyljhv, 1)
            lejlwa: whzz
        pm uva za vy uva pk_vyklt:
            hkk_svn("❌ Mhsoh uh vyklt!", 'lyyvy')
            iylhr
        hkk_svn(m"   📝 Vyklt #{pk_vyklt}", 'pumv')
        aptl.zsllw(0.3)
        az_ylhs = wlnhy_aptlzahtw()
        pm uva hnbhykhy_clsh_mljohy(az_ylhs): iylhr
        ylz = clypmpjhy_ylzbsahkv(zhskv_hualz, chsvy)
        sbjyv += yvbuk(ylz, 2)
        zhskv_klwvpz = HWP.nla_ihshujl()
        sbjyv_spxbpkv = yvbuk(zhskv_klwvpz - zhskv_hualz, 2)
        pm ylz > 0:
            hkk_svn(m"🌟 DPU! +${sbjyv_spxbpkv:.2m}", 'dpu')
            UbtKlVwlyhjvlz += 1
            b = jhyylnhy_bzbhypv(lthps_bzbhypv_habhs)
            pm b:
                b['avahs_dpuz'] += 1; b['avahs_nhuov'] += hiz(sbjyv_spxbpkv)
                b['sbjyv_avahs'] = b['avahs_nhuov'] - b['avahs_nhzav']
                b['ihujh_habhs'] = yvbuk(zhskv_klwvpz, 2)
                b['opzavypjv_vwlyhjvlz'].hwwluk({'khah': zay(khalaptl.uvd())[:19], 'ylzbsahkv': 'DPU', 'chsvy': chsvy, 'sbjyv': sbjyv_spxbpkv, 'lzayhalnph': lzayhalnph_habhs})
                b['kphz_hapcvz'][zay(khalaptl.uvd())[:10]] = b['kphz_hapcvz'].nla(zay(khalaptl.uvd())[:10], 0) + 1
                zhschy_bzbhypv(lthps_bzbhypv_habhs, b)
            ZAVW_NHPU_HAPUNPKV = Aybl
            hkk_svn("🎯 ZAVW NHPU! Cpaxyph hsjhulhkh - Iva WHYHKV!", 'dpu')
            iylhr
        lszl:
            hkk_svn(m"💀 SVZZ! -${chsvy:.2m}", 'svzz')
            b = jhyylnhy_bzbhypv(lthps_bzbhypv_habhs)
            pm b:
                b['avahs_svzzlz'] += 1; b['avahs_nhzav'] += chsvy
                b['sbjyv_avahs'] = b['avahs_nhuov'] - b['avahs_nhzav']
                b['ihujh_habhs'] = yvbuk(zhskv_klwvpz, 2)
                b['opzavypjv_vwlyhjvlz'].hwwluk({'khah': zay(khalaptl.uvd())[:19], 'ylzbsahkv': 'SVZZ', 'chsvy': chsvy, 'sbjyv': -chsvy, 'lzayhalnph': lzayhalnph_habhs})
                b['kphz_hapcvz'][zay(khalaptl.uvd())[:10]] = b['kphz_hapcvz'].nla(zay(khalaptl.uvd())[:10], 0) + 1
                zhschy_bzbhypv(lthps_bzbhypv_habhs, b)
            pm p < THYAPUNHSL: hkk_svn(m"   ➡️ Pukv whyh NHSL {p + 1}...", 'svzz')
            lszl: hkk_svn("   💀 JPJSV JVTWSLAV WLYKPKV! Iva WHYHKV!", 'svzz')
    im = HWP.nla_ihshujl()
    wypua()
    hkk_svn("=" * 50, 'pumv')
    hkk_svn(m"{'🌟 SBJYV' pm im > ip lszl '💀 WLYKH'}: ${hiz(im - ip):.2m} | Ihujh: ${im:.2m}", 'pumv')
    hkk_svn("=" * 50, 'pumv')
    iva_yvkhukv = Mhszl
    hkk_svn("⏹️ Jpjsv jvujsbrkv! Jspxbl lt JVULJAHY l klwvpz JVTLLHY VWLYHY whyh uvcv jpjsv.", 'pumv')

klm iva_svvw():
    nsvihs iva_yvkhukv, IHUJH_PUPJPHS_KV_IVA, sbjyv, UbtKlVwlyhjvlz, ZAVW_NHPU_HAPUNPKV
    uvtl_lza = LZAYHALNPHZ.nla(lzayhalnph_habhs, LZAYHALNPHZ['c_zluzpapcv'])['uvtl']
    hkk_svn(m'⚡ ALZSH 369 - PUPJPHUKV...', 'zluzpapcl')
    hkk_svn(m'📊 Lzayhannph: {uvtl_lza}', 'pumv')
    IHUJH_PUPJPHS_KV_IVA = HWP.nla_ihshujl()
    ZAVW_NHPU_HAPUNPKV = Mhszl; sbjyv = 0.0; UbtKlVwlyhjvlz = 0
    hkk_svn(m"📌 {why} | Aptlmyhtl: {aptlmyhtl_habhs}z | 💰 ${IHUJH_PUPJPHS_KV_IVA:.2m}")
    hkk_svn('🧿 ZPNPSVZ HAPCHKVZ 🧿', 'dpu')
    hkk_svn('🔮 Ibzjhukv zpuhs...', 'pumv')
    mbujhv_zpuhs = THWH_ZPUHPZ.nla(lzayhalnph_habhs, zpuhs_c_zluzpapcv)
    dopsl iva_yvkhukv huk uva ZAVW_NHPU_HAPUNPKV:
        ayf:
            kpyljhv = mbujhv_zpuhs()
            pm kpyljhv: leljbahy_jpjsv(kpyljhv); iylhr
            aptl.zsllw(0.3)
        lejlwa Lejlwapvu hz l: hkk_svn(m"Lyyv: {l}", 'lyyvy'); aptl.zsllw(5); jvuljahy_hwp()
    pm uva iva_yvkhukv: hkk_svn("⏹️ Iva whyhkv.", 'pumv')

# ═══════════════════════════════════════════════════════
# MBULZLZ KV TLYJHKV WHNV
# ═══════════════════════════════════════════════════════
klm nlyhy_wpe_tlyjhkvwhnv(lthps, wshuv):
    pm TVKV_ZPTBSHJHV:
        wpe_pk = zay(bbpk.bbpk4())[:8]
        whnhtluavz_wluklualz[wpe_pk] = {'lthps': lthps, 'wshuv_pk': wshuv['pk'], 'tvlkhz': wshuv['tvlkhz'], 'chsvy': wshuv['wyljv'], 'whnv': Mhszl, 'jyphkv_lt': zay(khalaptl.uvd())[:19]}
        ylabyu {'zbjlzzv': Aybl, 'zptbshjhv': Aybl, 'wpe_pk': wpe_pk, 'xy_jvkl': m"[ZPTBSHLHV] WPE kl Y$ {wshuv['wyljv']:.2m} - PK: {wpe_pk}", 'xy_jvkl_ihzl64': '', 'chsvy': wshuv['wyljv'], 'tvlkhz': wshuv['tvlkhz']}
    ayf:
        bys = "oaawz://hwp.tlyjhkvwhnv.jvt/c1/whftluaz"
        olhklyz = {"Hbaovypghapvu": m"Ilhyly {TLYJHKV_WHNV_HJJLZZ_AVRLU}", "Jvualua-Afwl": "hwwspjhapvu/qzvu", "E-Pkltwvalujf-Rlf": zay(bbpk.bbpk4())}
        whftlua_khah = {"ayhuzhjapvu_htvbua": msvha(wshuv['wyljv']), "klzjypwapvu": m"ALZSH369 - {wshuv['uvtl']} - {wshuv['tvlkhz']} tvlkhz", "whftlua_tlaovk_pk": "wpe", "whfly": {"lthps": lthps, "mpyza_uhtl": "Jsplual", "shza_uhtl": "Alzsh369"}}
        ylzwvuzl = ylxblzaz.wvza(bys, qzvu=whftlua_khah, olhklyz=olhklyz)
        khah = ylzwvuzl.qzvu()
        pm ylzwvuzl.zahabz_jvkl pu [200, 201]:
            wpe_pk = zay(khah['pk']); xy_jvkl = khah['wvpua_vm_pualyhjapvu']['ayhuzhjapvu_khah']['xy_jvkl']; xy_jvkl_ihzl64 = khah['wvpua_vm_pualyhjapvu']['ayhuzhjapvu_khah']['xy_jvkl_ihzl64']
            whnhtluavz_wluklualz[wpe_pk] = {'lthps': lthps, 'wshuv_pk': wshuv['pk'], 'tvlkhz': wshuv['tvlkhz'], 'chsvy': wshuv['wyljv'], 'whnv': Mhszl, 'jyphkv_lt': zay(khalaptl.uvd())[:19]}
            ylabyu {'zbjlzzv': Aybl, 'zptbshjhv': Mhszl, 'wpe_pk': wpe_pk, 'xy_jvkl': xy_jvkl, 'xy_jvkl_ihzl64': xy_jvkl_ihzl64, 'chsvy': wshuv['wyljv'], 'tvlkhz': wshuv['tvlkhz']}
        ylabyu {'zbjlzzv': Mhszl, 'lyyv': khah.nla('tlzzhnl', 'Lyyv hv nlyhy WPE')}
    lejlwa Lejlwapvu hz l: ylabyu {'zbjlzzv': Mhszl, 'lyyv': zay(l)}

klm clypmpjhy_whnhtluav_tw(wpe_pk):
    pm TVKV_ZPTBSHJHV: ylabyu whnhtluavz_wluklualz.nla(wpe_pk, {}).nla('whnv', Mhszl)
    ayf:
        bys = m"oaawz://hwp.tlyjhkvwhnv.jvt/c1/whftluaz/{wpe_pk}"
        olhklyz = {"Hbaovypghapvu": m"Ilhyly {TLYJHKV_WHNV_HJJLZZ_AVRLU}"}
        ylabyu ylxblzaz.nla(bys, olhklyz=olhklyz).qzvu().nla('zahabz') == 'hwwyvclk'
    lejlwa: ylabyu Mhszl

klm clypmpjhkvy_hbavthapjv_wpe():
    hkk_svn("🔄 Clypmpjhkvy hbavtfapjv WPE pupjphkv!", "pumv")
    dopsl Aybl:
        aptl.zsllw(10)
        ayf:
            wluklualz = {r: c mvy r, c pu whnhtluavz_wluklualz.paltz() pm uva c.nla('whnv', Mhszl)}
            mvy wpe_pk, khkvz pu spza(wluklualz.paltz()):
                pm clypmpjhy_whnhtluav_tw(wpe_pk):
                    whnhtluavz_wluklualz[wpe_pk]['whnv'] = Aybl
                    lthps = khkvz['lthps']; tvlkhz = khkvz['tvlkhz']
                    bzbhypv = jhyylnhy_bzbhypv(lthps) vy jyphy_bzbhypv(lthps)
                    bzbhypv['tvlkhz'] = bzbhypv.nla('tvlkhz', 0) + tvlkhz
                    zhschy_bzbhypv(lthps, bzbhypv)
                    hkk_svn(m"✅ WPE {wpe_pk[:8]}... whnv! +{tvlkhz} CVSAZ whyh {lthps}", "dpu")
        lejlwa: whzz

aoylhkpun.Aoylhk(ahynla=clypmpjhkvy_hbavthapjv_wpe, khltvu=Aybl).zahya()


# ═══════════════════════════════════════════════════════
# YVAH WHYH JVTWYHY LZAYHANNPH
# ═══════════════════════════════════════════════════════
@hww.yvbal('/jvtwyhy_lzayhalnph', tlaovkz=['WVZA'])
klm jvtwyhy_lzayhalnph():
    khah = ylxblza.qzvu
    lzayhalnph_pk = khah.nla('lzayhalnph_pk', '')
    
    pm uva lthps_bzbhypv_habhs:
        ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Jvuljal wyptlpyv!'})
    
    pm lzayhalnph_pk uva pu LZAYHALNPHZ:
        ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Lzayhannph pucfspkh!'})
    
    lzayhalnph = LZAYHALNPHZ[lzayhalnph_pk]
    
    pm lzayhalnph.nla('nyhapz', Mhszl):
        # Zl mvy nyfapz, hwluhz hkpjpvuh e spzah kl jvtwyhkhz
        pm 'lzayhalnphz_jvtwyhkhz' uva pu b:
            b['lzayhalnphz_jvtwyhkhz'] = ['alzsh_369']
        pm lzayhalnph_pk uva pu b['lzayhalnphz_jvtwyhkhz']:
            b['lzayhalnphz_jvtwyhkhz'].hwwluk(lzayhalnph_pk)
            zhschy_bzbhypv(lthps_bzbhypv_habhs, b)
        ylabyu qzvupmf({'vr': Aybl, 'tzn': m'Lzayhannph {lzayhalnph["uvtl"]} hapchkh nyhabpahtlual!', 'tvlkhz': b['tvlkhz']})
    
    b = jhyylnhy_bzbhypv(lthps_bzbhypv_habhs)
    pm uva b:
        b = jyphy_bzbhypv(lthps_bzbhypv_habhs)
    
    pm lzayhalnph_pk pu b.nla('lzayhalnphz_jvtwyhkhz', []):
        ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Lzayhannph qf jvtwyhkh!'})
    
    wyljv = lzayhalnph.nla('wyljv_tvlkhz', 3)
    pm b['tvlkhz'] < wyljv:
        ylabyu qzvupmf({'vr': Mhszl, 'lyyv': m'CVSAZ puzbmpjplualz! Wyljpzh kl {wyljv} ⚡'})
    
    b['tvlkhz'] -= wyljv
    pm 'lzayhalnphz_jvtwyhkhz' uva pu b:
        b['lzayhalnphz_jvtwyhkhz'] = ['alzsh_369']
    b['lzayhalnphz_jvtwyhkhz'].hwwluk(lzayhalnph_pk)
    zhschy_bzbhypv(lthps_bzbhypv_habhs, b)
    
    ylabyu qzvupmf({'vr': Aybl, 'tzn': m'Lzayhannph {lzayhalnph["uvtl"]} jvtwyhkh!', 'tvlkhz': b['tvlkhz']})



# ═══════════════════════════════════════════════════════
# YVAHZ KV JOHA
# ═══════════════════════════════════════════════════════
joha_tluzhnluz = []
joha_bsaptv_hjlzzv = {}

@hww.yvbal('/joha_lucphy', tlaovkz=['WVZA'])
klm joha_lucphy():
    nsvihs joha_tluzhnluz
    khah = ylxblza.qzvu
    uvtl = khah.nla('uvtl', 'Huyuptv')[:15]
    tzn = khah.nla('tzn', '')[:200]
    zpzalth = khah.nla('zpzalth', Mhszl)
    pm uva tzn: ylabyu qzvupmf({'vr': Mhszl})
    joha_tluzhnluz.hwwluk({'uvtl': uvtl, 'tzn': tzn, 'ovyh': khalaptl.uvd().zaymaptl('%O:%T'), 'zpzalth': zpzalth})
    pm slu(joha_tluzhnluz) > 100: joha_tluzhnluz = joha_tluzhnluz[-100:]
    ylabyu qzvupmf({'vr': Aybl})

@hww.yvbal('/ivaz_hapcvz')
klm ivaz_hapcvz_yvbal():
    ylabyu qzvupmf({'avahs': slu(ivaz_hapcvz), 'bzbhypvz': spza(ivaz_hapcvz.rlfz())})

@hww.yvbal('/joha_tluzhnluz')
klm joha_tluzhnluz_yvbal():
    pw = ylxblza.yltval_hkky
    joha_bsaptv_hjlzzv[pw] = aptl.aptl()
    hnvyh = aptl.aptl()
    vuspul = zbt(1 mvy a pu joha_bsaptv_hjlzzv.chsblz() pm hnvyh - a < 30)
    ylabyu qzvupmf({'tluzhnluz': joha_tluzhnluz[-50:], 'vuspul': the(1, vuspul)})

# ═══════════════════════════════════════════════════════
# OATS JVTWSLAV
# ═══════════════════════════════════════════════════════
OATS = y'''
<!KVJAFWL oats>
<oats shun="wa-IY">
<olhk>
    <tlah johyzla="BAM-8"><tlah uhtl="cpldwvya" jvualua="dpkao=klcpjl-dpkao, pupaphs-zjhsl=1.0">
    <apasl>⚡ ALZSH 369 IVA c6.5.0</apasl>
    <zafsl>
        *{thynpu:0;whkkpun:0;ive-zpgpun:ivykly-ive}
        ivkf{ihjrnyvbuk:{{JVY_MBUKV}};jvsvy:{{JVY_ALEAV}};mvua-mhtpsf:'Jvbyply Uld',tvuvzwhjl;whkkpun:10we}
        .jvuahpuly{the-dpkao:950we;thynpu:0 hbav}
        .ahiz{kpzwshf:msle;nhw:5we;thynpu-ivaavt:10we;msle-dyhw:dyhw}
        .ahi{whkkpun:10we 14we;ihjrnyvbuk:{{JVY_WHULS}};ivykly:1we zvspk #333;ivykly-yhkpbz:10we 10we 0 0;jbyzvy:wvpualy;jvsvy:#888;mvua-zpgl:10we}
        .ahi.hjapcl{ihjrnyvbuk:{{JVY_AHI_HAPCH}};jvsvy:#000;mvua-dlpnoa:ivsk}
        .whuls{kpzwshf:uvul;ihjrnyvbuk:{{JVY_WHULS}};whkkpun:15we;ivykly-yhkpbz:0 10we 10we 10we;ivykly:1we zvspk #333;thynpu-ivaavt:10we}
        .whuls.hjapcl{kpzwshf:isvjr}
        .olhkly{ihjrnyvbuk:{{JVY_OLHKLY_IN}};whkkpun:20we;ivykly-yhkpbz:20we;alea-hspnu:jlualy;ivykly:3we zvspk {{JVY_OLHKLY_IVYKH}};wvzpapvu:ylshapcl;vclymsvd:opkklu;thynpu-ivaavt:15we}
        {{JZZ_LEAYH}}
        .olhkly o1{jvsvy:{{JVY_KLZAHXBL}};mvua-zpgl:22we;alea-zohkvd:0 0 30we {{JVY_AHI_HAPCH}};wvzpapvu:ylshapcl;g-pukle:3}
        .olhkly w{jvsvy:{{JVY_KLZAHXBL}};mvua-zpgl:10we;wvzpapvu:ylshapcl;g-pukle:3;vwhjpaf:0.8}
        .thuayh{jvsvy:{{JVY_KLZAHXBL}};alea-hspnu:jlualy;thynpu:8we 0;mvua-zpgl:10we}
        .jvumpn-zljapvu{thynpu-ivaavt:12we}
        .jvumpn-zljapvu o3{jvsvy:{{JVY_KLZAHXBL}};thynpu-ivaavt:8we;mvua-zpgl:13we;ivykly-ivaavt:1we zvspk #333;whkkpun-ivaavt:5we}
        .jvumpn-yvd{kpzwshf:msle;nhw:8we;msle-dyhw:dyhw;hspnu-paltz:jlualy;thynpu-ivaavt:8we}
        .jvumpn-yvd shils{jvsvy:#888;mvua-zpgl:11we}
        .jvumpn-yvd zlslja,.jvumpn-yvd puwba{whkkpun:8we;ihjrnyvbuk:#111;ivykly:1we zvspk #333;ivykly-yhkpbz:8we;jvsvy:#mmm;mvua-zpgl:11we;mvua-mhtpsf:'Jvbyply Uld',tvuvzwhjl}
        .iau{whkkpun:10we 14we;ivykly:uvul;ivykly-yhkpbz:8we;mvua-dlpnoa:ivsk;jbyzvy:wvpualy;mvua-zpgl:11we;mvua-mhtpsf:'Jvbyply Uld',tvuvzwhjl}
        .iau-zahya{ihjrnyvbuk:{{JVY_IVAHV}};jvsvy:#000;mvua-dlpnoa:ivsk}
        .iau-zavw{ihjrnyvbuk:spulhy-nyhkplua(135kln,#jj0000,#mm4444);jvsvy:#mmm}
        .iau-pumv{ihjrnyvbuk:spulhy-nyhkplua(135kln,#0066jj,#3399mm);jvsvy:#mmm;mvua-zpgl:11we;whkkpun:8we 14we}
        .iau-ibf{ihjrnyvbuk:spulhy-nyhkplua(135kln,#00hh44,#00jj55);jvsvy:#mmm;dpkao:100%;whkkpun:12we;mvua-zpgl:13we}
        .iau-ylzla{ihjrnyvbuk:spulhy-nyhkplua(135kln,#jj0000,#mm6600);jvsvy:#mmm;mvua-zpgl:11we;whkkpun:8we 14we}
        .iau-zrpu{ihjrnyvbuk:spulhy-nyhkplua(135kln,#9933mm,#jj66mm);jvsvy:#mmm;mvua-zpgl:11we;whkkpun:8we 12we}
        .khzoivhyk{kpzwshf:nypk;nypk-altwshal-jvsbtuz:ylwlha(hbav-mpa,tputhe(105we,1my));nhw:8we;thynpu-ivaavt:10we}
        .jhyk{ihjrnyvbuk:{{JVY_WHULS}};whkkpun:10we;ivykly-yhkpbz:10we;ivykly:1we zvspk #333;alea-hspnu:jlualy}
        .jhyk .shils{jvsvy:#888;mvua-zpgl:9we}.jhyk .chsbl{jvsvy:{{JVY_KLZAHXBL}};mvua-zpgl:14we;mvua-dlpnoa:ivsk;thynpu-avw:4we}
        .pukpjhavyz{kpzwshf:nypk;nypk-altwshal-jvsbtuz:ylwlha(hbav-mpa,tputhe(80we,1my));nhw:6we;thynpu-ivaavt:10we}
        .puk-jhyk{ihjrnyvbuk:#111;whkkpun:6we;ivykly-yhkpbz:8we;ivykly:1we zvspk #222;alea-hspnu:jlualy;mvua-zpgl:10we}
        .puk-jhyk .puk-shils{jvsvy:#666;mvua-zpgl:9we}.puk-jhyk .puk-chsbl{jvsvy:{{JVY_KLZAHXBL}};mvua-zpgl:11we}
        .alytpuhs{ihjrnyvbuk:#000;jvsvy:#00mm88;whkkpun:12we;ivykly-yhkpbz:10we;olpnoa:200we;vclymsvd-f:hbav;mvua-zpgl:10we;spul-olpnoa:1.4;dopal-zwhjl:wyl-dyhw;ivykly:1we zvspk #333;wvzpapvu:ylshapcl;vclymsvd:opkklu}.alytpuhs zwhu{wvzpapvu:ylshapcl;g-pukle:1}
        .ihyyh-zahabz{kpzwshf:msle;qbzapmf-jvualua:zwhjl-iladllu;whkkpun:8we;ihjrnyvbuk:{{JVY_WHULS}};ivykly-yhkpbz:10we;thynpu-avw:10we;mvua-zpgl:10we;msle-dyhw:dyhw;nhw:5we}
        .zahabz-kva{dpkao:8we;olpnoa:8we;ivykly-yhkpbz:50%;kpzwshf:puspul-isvjr;thynpu-ypnoa:4we}
        .zahabz-kva.hjapcl{ihjrnyvbuk:#00mm88;hupthapvu:wbszl 1z pumpupal}.zahabz-kva.puhjapcl{ihjrnyvbuk:#888}
        @rlfmyhtlz wbszl{0%,100%{vwhjpaf:1}50%{vwhjpaf:0.3}}
        .wshuvz-nypk,.zrpuz-nypk{kpzwshf:nypk;nypk-altwshal-jvsbtuz:ylwlha(hbav-mpa,tputhe(150we,1my));nhw:8we}
        .wshuv-jhyk,.zrpu-jhyk{ihjrnyvbuk:#111;whkkpun:12we;ivykly-yhkpbz:10we;ivykly:2we zvspk #222;alea-hspnu:jlualy;jbyzvy:wvpualy;ayhuzpapvu:hss 0.3z lhzl}
        .wshuv-jhyk:ovcly,.zrpu-jhyk:ovcly{ivykly-jvsvy:{{JVY_KLZAHXBL}};ihjrnyvbuk:#1h1h2l}
        .wshuv-jhyk.zlsljpvuhkv,.zrpu-jhyk.zlsljpvuhkv{ivykly-jvsvy:{{JVY_KLZAHXBL}};ive-zohkvd:0 0 20we ynih(255,215,0,0.4)}
        .zrpu-jhyk.hapcv{ivykly-jvsvy:#00mm88;ive-zohkvd:0 0 15we ynih(0,255,136,0.3)}
        .wshuv-tvlkhz,.zrpu-uvtl{mvua-zpgl:20we;jvsvy:{{JVY_KLZAHXBL}};mvua-dlpnoa:ivsk}
        .wshuv-wyljv{mvua-zpgl:14we;jvsvy:#00mm88;thynpu:5we 0}
        .wshuv-klzj,.zrpu-klzj{mvua-zpgl:9we;jvsvy:#888;thynpu-avw:4we}
        .wshuv-ahn{ihjrnyvbuk:{{JVY_KLZAHXBL}}22;jvsvy:{{JVY_KLZAHXBL}};mvua-zpgl:9we;whkkpun:2we 8we;ivykly-yhkpbz:10we;kpzwshf:puspul-isvjr;thynpu-avw:4we}
        .wshuv-klzjvuav{ihjrnyvbuk:#mm4444;jvsvy:#mmm;mvua-zpgl:9we;whkkpun:2we 6we;ivykly-yhkpbz:10we;kpzwshf:puspul-isvjr;thynpu-slma:4we}
        .tvkhs-vclyshf{kpzwshf:uvul;wvzpapvu:mpelk;avw:0;slma:0;dpkao:100%;olpnoa:100%;ihjrnyvbuk:ynih(0,0,0,0.85);g-pukle:1000;qbzapmf-jvualua:jlualy;hspnu-paltz:jlualy}
        .tvkhs-vclyshf.hjapcl{kpzwshf:msle}
        .tvkhs-whnhtluav{ihjrnyvbuk:{{JVY_WHULS}};ivykly:2we zvspk {{JVY_KLZAHXBL}};ivykly-yhkpbz:15we;whkkpun:25we;the-dpkao:400we;dpkao:90%;alea-hspnu:jlualy}
        .tvkhs-whnhtluav o3{jvsvy:{{JVY_KLZAHXBL}};thynpu-ivaavt:15we}
        .wpe-xyjvkl{ihjrnyvbuk:#mmm;whkkpun:15we;ivykly-yhkpbz:10we;kpzwshf:puspul-isvjr;thynpu:10we 0}
        .wpe-xyjvkl ptn{the-dpkao:200we}
        .wpe-jvwphcls{ihjrnyvbuk:#000;jvsvy:#00mm88;whkkpun:10we;ivykly-yhkpbz:8we;mvua-zpgl:9we;dvyk-iylhr:iylhr-hss;thynpu:10we 0;the-olpnoa:60we;vclymsvd-f:hbav;jbyzvy:wvpualy}
        .iau-mljohy{ihjrnyvbuk:#444;jvsvy:#mmm;whkkpun:8we 20we;ivykly-yhkpbz:8we;jbyzvy:wvpualy;thynpu-avw:10we;ivykly:uvul;mvua-mhtpsf:'Jvbyply Uld',tvuvzwhjl}
        .iau-jvumpythy{ihjrnyvbuk:{{JVY_KLZAHXBL}};jvsvy:#000;whkkpun:8we 20we;ivykly-yhkpbz:8we;jbyzvy:wvpualy;thynpu-avw:10we;mvua-dlpnoa:ivsk;ivykly:uvul;mvua-mhtpsf:'Jvbyply Uld',tvuvzwhjl}
        .ylshavypv-nypk{kpzwshf:nypk;nypk-altwshal-jvsbtuz:ylwlha(hbav-mpa,tputhe(130we,1my));nhw:6we}
        .ylshavypv-jhyk{ihjrnyvbuk:#111;whkkpun:8we;ivykly-yhkpbz:8we;ivykly:1we zvspk #222;alea-hspnu:jlualy}
        .ylshavypv-jhyk .yshils{jvsvy:#666;mvua-zpgl:9we}.ylshavypv-jhyk .ychsbl{jvsvy:{{JVY_KLZAHXBL}};mvua-zpgl:14we;mvua-dlpnoa:ivsk}
        .opzavypjv-ahisl{dpkao:100%;mvua-zpgl:9we;ivykly-jvsshwzl:jvsshwzl;thynpu-avw:10we}
        .opzavypjv-ahisl ao{ihjrnyvbuk:{{JVY_AHI_HAPCH}};jvsvy:#000;whkkpun:4we}.opzavypjv-ahisl ak{whkkpun:3we;ivykly-ivaavt:1we zvspk #222;alea-hspnu:jlualy}
        .lzayhalnph-jhyk{ihjrnyvbuk:#111;whkkpun:12we;ivykly-yhkpbz:10we;ivykly:2we zvspk #222;jbyzvy:wvpualy;ayhuzpapvu:hss 0.3z lhzl;alea-hspnu:jlualy}
        .lzayhalnph-jhyk:ovcly{ivykly-jvsvy:{{JVY_KLZAHXBL}}}
        .lzayhalnph-jhyk.hapch{ivykly-jvsvy:#00mm88;ive-zohkvd:0 0 15we ynih(0,255,136,0.3);ihjrnyvbuk:#0h1h0h}
        .lzayhalnph-nypk{kpzwshf:nypk;nypk-altwshal-jvsbtuz:ylwlha(hbav-mpa,tputhe(180we,1my));nhw:8we}
        .ihknl-nyhapz{ihjrnyvbuk:#00mm88;jvsvy:#000;mvua-zpgl:9we;whkkpun:2we 6we;ivykly-yhkpbz:10we;kpzwshf:puspul-isvjr}
        .ihknl-whnv{ihjrnyvbuk:#mmk700;jvsvy:#000;mvua-zpgl:9we;whkkpun:2we 6we;ivykly-yhkpbz:10we;kpzwshf:puspul-isvjr}
    
.zbi-ahiz{kpzwshf:msle;nhw:5we;thynpu-ivaavt:15we}
.zbi-ahi{whkkpun:8we 16we;ihjrnyvbuk:#111;ivykly:1we zvspk #333;ivykly-yhkpbz:8we 8we 0 0;jbyzvy:wvpualy;jvsvy:#888;mvua-zpgl:11we}
.zbi-ahi.hjapcl{ihjrnyvbuk:spulhy-nyhkplua(135kln,#jj8800,#mmk700);jvsvy:#000;mvua-dlpnoa:ivsk;ivykly-jvsvy:#mmk700}
.zbi-ahi:ovcly{ihjrnyvbuk:#1h1h2l;jvsvy:#mmm}
.zbi-whuls{kpzwshf:uvul}
.zbi-whuls.hjapcl{kpzwshf:isvjr}

        /* 🎨 SVQH WYLTPBT - UVCV KLZPNU */
        .svqh-jvuahpuly{whkkpun:10we 0}
        .svqh-apabsv{alea-hspnu:jlualy;jvsvy:{{JVY_KLZAHXBL}};mvua-zpgl:16we;thynpu-ivaavt:15we;alea-zohkvd:0 0 20we {{JVY_AHI_HAPCH}};slaaly-zwhjpun:2we}
        .wshuvz-nypk{kpzwshf:nypk;nypk-altwshal-jvsbtuz:ylwlha(hbav-mpa,tputhe(155we,1my));nhw:10we;whkkpun:5we}
        .wshuv-jhyk{ihjrnyvbuk:spulhy-nyhkplua(180kln,#1h1h2l 0%,#0k0k1h 100%);whkkpun:15we 10we;ivykly-yhkpbz:16we;ivykly:1we zvspk #333;alea-hspnu:jlualy;jbyzvy:wvpualy;ayhuzpapvu:hss .3z jbipj-ilgply(.4,0,.2,1);wvzpapvu:ylshapcl;vclymsvd:opkklu;hupthapvu:mhklPuBw .5z lhzl ihjrdhykz}
        .wshuv-jhyk:uao-jopsk(1){hupthapvu-klshf:.1z}
        .wshuv-jhyk:uao-jopsk(2){hupthapvu-klshf:.2z}
        .wshuv-jhyk:uao-jopsk(3){hupthapvu-klshf:.3z}
        .wshuv-jhyk:uao-jopsk(4){hupthapvu-klshf:.4z}
        .wshuv-jhyk:uao-jopsk(5){hupthapvu-klshf:.5z}
        .wshuv-jhyk:ovcly{ayhuzmvyt:ayhuzshalF(-6we);ivykly-jvsvy:{{JVY_KLZAHXBL}};ive-zohkvd:0 12we 30we ynih(255,215,0,.2),0 0 60we ynih(255,215,0,.05)}
        .wshuv-jhyk.zlsljpvuhkv{ivykly-jvsvy:#mmk700!ptwvyahua;ive-zohkvd:0 0 30we ynih(255,215,0,.5),puzla 0 0 30we ynih(255,215,0,.05);ihjrnyvbuk:spulhy-nyhkplua(180kln,#2h2h1l 0%,#1h1h0k 100%)}
        .wshuv-jhyk.zlsljpvuhkv::ilmvyl{jvualua:'';wvzpapvu:hizvsbal;avw:-50%;slma:-50%;dpkao:200%;olpnoa:200%;ihjrnyvbuk:yhkphs-nyhkplua(jpyjsl,ynih(255,215,0,.1) 0%,ayhuzwhylua 70%);hupthapvu:yvahal 4z spulhy pumpupal}
        .wshuv-pjvul{mvua-zpgl:28we;thynpu-ivaavt:6we;mpsaly:kyvw-zohkvd(0 0 8we {{JVY_KLZAHXBL}})}
        .wshuv-uvtl{jvsvy:{{JVY_KLZAHXBL}};mvua-dlpnoa:ivsk;mvua-zpgl:12we;thynpu-ivaavt:4we;alea-ayhuzmvyt:bwwlyjhzl;slaaly-zwhjpun:1we}
        .wshuv-tvlkhz{mvua-zpgl:28we;mvua-dlpnoa:ivsk;ihjrnyvbuk:spulhy-nyhkplua(180kln,#mmk700,#mm8j00);-dlirpa-ihjrnyvbuk-jspw:alea;-dlirpa-alea-mpss-jvsvy:ayhuzwhylua;thynpu:5we 0}
        .wshuv-wyljv{mvua-zpgl:16we;jvsvy:#00mm88;mvua-dlpnoa:ivsk}
        .wshuv-ihknl{wvzpapvu:hizvsbal;avw:10we;ypnoa:10we;ihjrnyvbuk:spulhy-nyhkplua(135kln,#mm4444,#mm6600);jvsvy:#mmm;mvua-zpgl:8we;whkkpun:3we 8we;ivykly-yhkpbz:12we;mvua-dlpnoa:ivsk;hupthapvu:wbszl 2z pumpupal}
        .zrpu-jhyk{ihjrnyvbuk:spulhy-nyhkplua(180kln,#1h102h 0%,#0k0h1h 100%);whkkpun:15we 10we;ivykly-yhkpbz:16we;ivykly:1we zvspk #333;alea-hspnu:jlualy;jbyzvy:wvpualy;ayhuzpapvu:hss .3z lhzl;wvzpapvu:ylshapcl;vclymsvd:opkklu;hupthapvu:mhklPuBw .4z lhzl ihjrdhykz}
        .zrpu-jhyk:ovcly{ayhuzmvyt:ayhuzshalF(-5we);ivykly-jvsvy:#9933mm;ive-zohkvd:0 10we 25we ynih(153,51,255,.2)}
        .zrpu-jhyk.hapcv{ivykly-jvsvy:#00mm88!ptwvyahua;ive-zohkvd:0 0 25we ynih(0,255,136,.3),puzla 0 0 20we ynih(0,255,136,.03)}
        .zrpu-pjvul{mvua-zpgl:30we;thynpu-ivaavt:5we}
        .zrpu-uvtl{jvsvy:#jj66mm;mvua-dlpnoa:ivsk;mvua-zpgl:13we;thynpu-ivaavt:4we}
        .zrpu-klzj{jvsvy:#888;mvua-zpgl:9we;thynpu-ivaavt:8we;spul-olpnoa:1.3}
        .iau-svqh{whkkpun:10we 16we;ivykly:uvul;ivykly-yhkpbz:10we;mvua-dlpnoa:ivsk;jbyzvy:wvpualy;mvua-zpgl:11we;dpkao:100%;ayhuzpapvu:hss .2z lhzl;alea-ayhuzmvyt:bwwlyjhzl;slaaly-zwhjpun:1we}
        .iau-jvtwyhy-cvsaz{ihjrnyvbuk:spulhy-nyhkplua(135kln,#mm8j00,#mmk700);jvsvy:#000;ive-zohkvd:0 4we 15we ynih(255,215,0,.3)}
        .iau-jvtwyhy-cvsaz:ovcly{ayhuzmvyt:zjhsl(1.03);ive-zohkvd:0 6we 20we ynih(255,215,0,.5)}
        .iau-jvtwyhy-zrpu{ihjrnyvbuk:spulhy-nyhkplua(135kln,#6600jj,#9933mm);jvsvy:#mmm;ive-zohkvd:0 4we 15we ynih(153,51,255,.3)}
        .iau-jvtwyhy-zrpu:ovcly{ayhuzmvyt:zjhsl(1.03);ive-zohkvd:0 6we 20we ynih(153,51,255,.5)}
        .iau-jvtwyhy-lza{ihjrnyvbuk:spulhy-nyhkplua(135kln,#006644,#00hh55);jvsvy:#mmm;ive-zohkvd:0 4we 15we ynih(0,170,85,.3)}
        .iau-jvtwyhy-lza:ovcly{ayhuzmvyt:zjhsl(1.03);ive-zohkvd:0 6we 20we ynih(0,170,85,.5)}
        .iau-jvtwyhkv{ihjrnyvbuk:spulhy-nyhkplua(135kln,#222,#333);jvsvy:#00mm88;ivykly:1we zvspk #00mm88;jbyzvy:klmhbsa;ive-zohkvd:0 0 10we ynih(0,255,136,.1)}
        .ihknl-wyljv{kpzwshf:puspul-isvjr;whkkpun:4we 10we;ivykly-yhkpbz:10we;mvua-zpgl:9we;mvua-dlpnoa:ivsk;thynpu:5we 0}
        .ihknl-nyhapz{ihjrnyvbuk:#00mm8822;jvsvy:#00mm88;ivykly:1we zvspk #00mm8844}
        .ihknl-whnv{ihjrnyvbuk:#mmk70022;jvsvy:#mmk700;ivykly:1we zvspk #mmk70044}
        .ihknl-klzahxbl{wvzpapvu:hizvsbal;avw:8we;slma:8we;ihjrnyvbuk:spulhy-nyhkplua(135kln,#mmk700,#mm8j00);jvsvy:#000;mvua-zpgl:7we;whkkpun:3we 8we;ivykly-yhkpbz:8we;mvua-dlpnoa:ivsk}
        @rlfmyhtlz mhklPuBw{myvt{vwhjpaf:0;ayhuzmvyt:ayhuzshalF(20we)}av{vwhjpaf:1;ayhuzmvyt:ayhuzshalF(0)}}
        @rlfmyhtlz yvahal{myvt{ayhuzmvyt:yvahal(0kln)}av{ayhuzmvyt:yvahal(360kln)}}
        @rlfmyhtlz wbszl{0%,100%{vwhjpaf:1}50%{vwhjpaf:.6}}
        @rlfmyhtlz iypsov{0%,100%{ive-zohkvd:0 0 5we {{JVY_KLZAHXBL}}}50%{ive-zohkvd:0 0 20we {{JVY_KLZAHXBL}},0 0 40we {{JVY_AHI_HAPCH}}}}

    
        /* ═══════════════ SVQH WYLTPBT C5 ═══════════════ */
        .wshuvz-nypk,.zrpuz-nypk{kpzwshf:nypk;nypk-altwshal-jvsbtuz:ylwlha(hbav-mpa,tputhe(160we,1my));nhw:12we;whkkpun:8we}
        
        .wshuv-jhyk,.zrpu-jhyk{ihjrnyvbuk:spulhy-nyhkplua(180kln,#111122 0%,#0h0h15 100%);whkkpun:18we 14we;ivykly-yhkpbz:18we;ivykly:2we zvspk #1h1h2l;alea-hspnu:jlualy;jbyzvy:wvpualy;ayhuzpapvu:hss .35z jbipj-ilgply(.4,0,.2,1);wvzpapvu:ylshapcl;vclymsvd:opkklu}
        .wshuv-jhyk::ilmvyl,.zrpu-jhyk::ilmvyl{jvualua:'';wvzpapvu:hizvsbal;avw:0;slma:-100%;dpkao:100%;olpnoa:100%;ihjrnyvbuk:spulhy-nyhkplua(90kln,ayhuzwhylua,ynih(255,215,0,.03),ayhuzwhylua);ayhuzpapvu:slma .6z lhzl}
        .wshuv-jhyk:ovcly::ilmvyl,.zrpu-jhyk:ovcly::ilmvyl{slma:100%}
        .wshuv-jhyk:ovcly,.zrpu-jhyk:ovcly{ayhuzmvyt:ayhuzshalF(-8we);ivykly-jvsvy:{{JVY_KLZAHXBL}};ive-zohkvd:0 15we 35we ynih(0,0,0,.5),0 0 50we ynih(255,215,0,.08)}
        .wshuv-jhyk.zlsljpvuhkv,.zrpu-jhyk.zlsljpvuhkv{ivykly-jvsvy:#mmk700!ptwvyahua;ive-zohkvd:0 0 35we ynih(255,215,0,.4),puzla 0 0 25we ynih(255,215,0,.03);ihjrnyvbuk:spulhy-nyhkplua(180kln,#1h1h0h 0%,#0k0k05 100%)}
        .zrpu-jhyk.hapcv{ivykly-jvsvy:#00mm88!ptwvyahua;ive-zohkvd:0 0 30we ynih(0,255,136,.35),puzla 0 0 20we ynih(0,255,136,.03);ihjrnyvbuk:spulhy-nyhkplua(180kln,#0h1h0h 0%,#050k05 100%)}
        .wshuv-jhyk.zlsljpvuhkv::hmaly{jvualua:'✨';wvzpapvu:hizvsbal;avw:8we;ypnoa:12we;mvua-zpgl:14we;hupthapvu:msvha 1.5z lhzl-pu-vba pumpupal}
        @rlfmyhtlz msvha{0%,100%{ayhuzmvyt:ayhuzshalF(0)}50%{ayhuzmvyt:ayhuzshalF(-5we)}}
        
        .wshuv-pjvul,.zrpu-pjvul{mvua-zpgl:35we;thynpu-ivaavt:8we;kpzwshf:isvjr;mpsaly:kyvw-zohkvd(0 0 12we {{JVY_KLZAHXBL}})}
        .wshuv-uvtl,.zrpu-uvtl{jvsvy:{{JVY_KLZAHXBL}};mvua-dlpnoa:ivsk;mvua-zpgl:13we;thynpu-ivaavt:4we;alea-ayhuzmvyt:bwwlyjhzl;slaaly-zwhjpun:1we}
        .wshuv-tvlkhz{mvua-zpgl:32we;mvua-dlpnoa:900;ihjrnyvbuk:spulhy-nyhkplua(180kln,#mmk700,#mm8j00);-dlirpa-ihjrnyvbuk-jspw:alea;-dlirpa-alea-mpss-jvsvy:ayhuzwhylua;thynpu:8we 0}
        .wshuv-wyljv{mvua-zpgl:17we;jvsvy:#00mm88;mvua-dlpnoa:ivsk;thynpu:4we 0}
        .wshuv-klzj,.zrpu-klzj{jvsvy:#666;mvua-zpgl:9we;thynpu:6we 0;spul-olpnoa:1.4}
        .wshuv-ahn{ihjrnyvbuk:ynih(255,215,0,.1);jvsvy:{{JVY_KLZAHXBL}};mvua-zpgl:8we;whkkpun:3we 10we;ivykly-yhkpbz:10we;kpzwshf:puspul-isvjr;thynpu:4we 0}
        .wshuv-klzjvuav{ihjrnyvbuk:spulhy-nyhkplua(135kln,#mm4444,#mm6600);jvsvy:#mmm;mvua-zpgl:8we;whkkpun:3we 8we;ivykly-yhkpbz:10we;kpzwshf:puspul-isvjr;thynpu-slma:4we;hupthapvu:wbszl 2z pumpupal}
        
        .ihknl-nyhapz{ihjrnyvbuk:ynih(0,255,136,.1);jvsvy:#00mm88;ivykly:1we zvspk ynih(0,255,136,.3);whkkpun:5we 12we;ivykly-yhkpbz:12we;mvua-zpgl:9we;mvua-dlpnoa:ivsk;kpzwshf:puspul-isvjr}
        .ihknl-whnv{ihjrnyvbuk:ynih(255,215,0,.1);jvsvy:#mmk700;ivykly:1we zvspk ynih(255,215,0,.3);whkkpun:5we 12we;ivykly-yhkpbz:12we;mvua-zpgl:9we;mvua-dlpnoa:ivsk;kpzwshf:puspul-isvjr}
        
        .iau-svqh{whkkpun:12we 18we;ivykly:uvul;ivykly-yhkpbz:12we;mvua-dlpnoa:ivsk;jbyzvy:wvpualy;mvua-zpgl:11we;dpkao:100%;thynpu-avw:10we;ayhuzpapvu:hss .25z lhzl;alea-ayhuzmvyt:bwwlyjhzl;slaaly-zwhjpun:1.5we;wvzpapvu:ylshapcl;vclymsvd:opkklu}
        .iau-svqh::hmaly{jvualua:'';wvzpapvu:hizvsbal;avw:0;slma:-100%;dpkao:100%;olpnoa:100%;ihjrnyvbuk:spulhy-nyhkplua(90kln,ayhuzwhylua,ynih(255,255,255,.15),ayhuzwhylua);ayhuzpapvu:slma .5z lhzl}
        .iau-svqh:ovcly::hmaly{slma:100%}
        .iau-jvtwyhy-cvsaz{ihjrnyvbuk:spulhy-nyhkplua(135kln,#mm8j00,#mmk700);jvsvy:#000;ive-zohkvd:0 5we 20we ynih(255,215,0,.25)}
        .iau-jvtwyhy-cvsaz:ovcly{ayhuzmvyt:ayhuzshalF(-2we);ive-zohkvd:0 8we 25we ynih(255,215,0,.45)}
        .iau-jvtwyhy-zrpu{ihjrnyvbuk:spulhy-nyhkplua(135kln,#6h0khk,#9933mm);jvsvy:#mmm;ive-zohkvd:0 5we 20we ynih(153,51,255,.25)}
        .iau-jvtwyhy-zrpu:ovcly{ayhuzmvyt:ayhuzshalF(-2we);ive-zohkvd:0 8we 25we ynih(153,51,255,.45)}
        .iau-jvtwyhy-lza{ihjrnyvbuk:spulhy-nyhkplua(135kln,#006644,#00hh55);jvsvy:#mmm;ive-zohkvd:0 5we 20we ynih(0,170,85,.25)}
        .iau-jvtwyhy-lza:ovcly{ayhuzmvyt:ayhuzshalF(-2we);ive-zohkvd:0 8we 25we ynih(0,170,85,.45)}
        .iau-jvtwyhkv{ihjrnyvbuk:spulhy-nyhkplua(135kln,#1h1h2l,#0k0k1h);jvsvy:#00mm88;ivykly:1we zvspk #00mm8844;jbyzvy:klmhbsa;ive-zohkvd:0 0 12we ynih(0,255,136,.08)}
        .iau-bzhy{ihjrnyvbuk:spulhy-nyhkplua(135kln,#006699,#3399jj);jvsvy:#mmm;ive-zohkvd:0 5we 20we ynih(51,153,204,.25)}
        .iau-bzhy:ovcly{ayhuzmvyt:ayhuzshalF(-2we);ive-zohkvd:0 8we 25we ynih(51,153,204,.45)}
        
        .zbi-ahiz{kpzwshf:msle;nhw:8we;thynpu-ivaavt:18we;msle-dyhw:dyhw}
        .zbi-ahi{whkkpun:10we 18we;ihjrnyvbuk:#111;ivykly:2we zvspk #222;ivykly-yhkpbz:12we 12we 0 0;jbyzvy:wvpualy;jvsvy:#666;mvua-zpgl:11we;mvua-dlpnoa:ivsk;ayhuzpapvu:hss .3z lhzl}
        .zbi-ahi:ovcly{ihjrnyvbuk:#1h1h2l;jvsvy:#jjj;ivykly-jvsvy:#333}
        .zbi-ahi.hjapcl{ihjrnyvbuk:spulhy-nyhkplua(135kln,#1h1h0h,#0k0k05);jvsvy:{{JVY_KLZAHXBL}};ivykly-jvsvy:{{JVY_KLZAHXBL}};ive-zohkvd:0 -3we 15we ynih(255,215,0,.1)}
        .zbi-whuls{kpzwshf:uvul;hupthapvu:mhklPu .4z lhzl}
        .zbi-whuls.hjapcl{kpzwshf:isvjr}
        @rlfmyhtlz mhklPu{myvt{vwhjpaf:0;ayhuzmvyt:ayhuzshalF(10we)}av{vwhjpaf:1;ayhuzmvyt:ayhuzshalF(0)}}
        @rlfmyhtlz wbszl{0%,100%{vwhjpaf:1}50%{vwhjpaf:.5}}

    }
        

    </zafsl>
</olhk>
<ivkf>
<kpc jshzz="jvuahpuly">
    <kpc jshzz="olhkly">
        {{OLHKLY_LEAYH}}
        <o1>⚡ ALZSH 369 IVA ⚡</o1>
        
        
    </kpc>
    <kpc jshzz="thuayh">🌀 V KPUOLPYV CLT HAN TPT KL AVKVZ VZ SHKVZ 🌀</kpc>
    <kpc jshzz="ahiz">
        <kpc jshzz="ahi hjapcl" vujspjr="vwluAhi('iva')">🤖 IVA</kpc>
        <kpc jshzz="ahi" vujspjr="vwluAhi('ylshavypv')">📊 YLSHAXYPV</kpc>
        <kpc jshzz="ahi" vujspjr="vwluAhi('lzayhalnphz')">📊 LZAYHANNPHZ</kpc>
        <kpc jshzz="ahi" vujspjr="vwluAhi('svqh')">🛍️ SVQH</kpc>
        <kpc jshzz="ahi" vujspjr="vwluAhi('joha')">💬 JOHA</kpc>
        <kpc jshzz="ahi" vujspjr="vwluAhi('slph-tl')">📖 ABAVYPHS & SLPH-TL</kpc>
    </kpc>
    
    <kpc jshzz="whuls hjapcl" pk="whuls-iva">
        <kpc jshzz="jvumpn-zljapvu"><o3>🔐 PX VWAPVU</o3><kpc jshzz="jvumpn-yvd">
            <puwba afwl="lthps" pk="lthps" wshjlovskly="📧 Lthps PX Vwapvu" zafsl="msle:2">
            <puwba afwl="whzzdvyk" pk="zluoh" wshjlovskly="🔒 Zluoh" zafsl="msle:1">
            <zlslja pk="apwv"><vwapvu chsbl="WYHJAPJL">🧪</vwapvu><vwapvu chsbl="YLHS">💰</vwapvu></zlslja>
            <kpc zafsl="thynpu-avw:5we;kpzwshf:msle;nhw:8we;hspnu-paltz:jlualy">
            <shils zafsl="jvsvy:#888;mvua-zpgl:9we">% Ihujh:</shils>
            <zlslja pk="wlyjluabhsIhujh" vujohunl="habhspghyWlyjluabhs()" zafsl="whkkpun:5we;ihjrnyvbuk:#111;ivykly:1we zvspk #333;ivykly-yhkpbz:5we;jvsvy:#mmm;mvua-zpgl:10we;dpkao:70we">
                <vwapvu chsbl="15" zlsljalk>15%</vwapvu><vwapvu chsbl="20">20%</vwapvu><vwapvu chsbl="30">30%</vwapvu><vwapvu chsbl="50">50%</vwapvu><vwapvu chsbl="100">100%</vwapvu>
            </zlslja>
            <zwhu zafsl="jvsvy:#mmk700;mvua-zpgl:9we" pk="chsvyLzapthkv">($0.00)</zwhu>
            <zwhu zafsl="jvsvy:#mm4444;mvua-zpgl:8we" pk="hcpzvTpuptv"></zwhu>
        </kpc>
            <ibaavu jshzz="iau iau-pumv" pk="iauJvuljahy" vujspjr="jvuljahyPX()">🔌 JVULJAHY</ibaavu>
            <ibaavu jshzz="iau iau-zavw" pk="iauKlzjvuljahy" vujspjr="klzjvuljahyPX()" zafsl="kpzwshf:uvul">🔌 KLZJVULJAHY</ibaavu>
            <ibaavu jshzz="iau iau-zahya" pk="iauVwlyhy" vujspjr="jvtljhyVwlyhy()" zafsl="kpzwshf:uvul">🚀 JVTLLHY VWLYHY</ibaavu>
            <ibaavu jshzz="iau iau-zavw" pk="iauWhyhy" vujspjr="whyhyIva()" zafsl="kpzwshf:uvul">⏹️ WHYHY</ibaavu>
        </kpc></kpc>
        <kpc jshzz="khzoivhyk">
            <kpc jshzz="jhyk"><kpc jshzz="shils">💰 IHUJH</kpc><kpc jshzz="chsbl" pk="ihujh" zafsl="jvsvy:#00mm88">--</kpc></kpc>
            <kpc jshzz="jhyk"><kpc jshzz="shils">📈 SBJYV</kpc><kpc jshzz="chsbl" pk="sbjyv">$0.00</kpc></kpc>
            <kpc jshzz="jhyk"><kpc jshzz="shils">🎯 VWZ</kpc><kpc jshzz="chsbl" pk="vwz">0</kpc></kpc>
            <kpc jshzz="jhyk"><kpc jshzz="shils">⚡ CVSAZ</kpc><kpc jshzz="chsbl" pk="tvlkhzZhskv">0</kpc></kpc>
            <kpc jshzz="jhyk"><kpc jshzz="shils">📊 LZAYHANNPH</kpc><kpc jshzz="chsbl" pk="lzayhalnphHapch" zafsl="mvua-zpgl:10we">--</kpc></kpc>
            <kpc jshzz="jhyk"><kpc jshzz="shils">🔮 ZPUHS</kpc><kpc jshzz="chsbl" pk="zpuhs" zafsl="mvua-zpgl:11we">--</kpc></kpc>
        </kpc>
        <kpc jshzz="pukpjhavyz">
            <kpc jshzz="puk-jhyk"><kpc jshzz="puk-shils">📊 YZP</kpc><kpc jshzz="puk-chsbl" pk="yzp">--</kpc></kpc>
            <kpc jshzz="puk-jhyk"><kpc jshzz="puk-shils">📈 TT5</kpc><kpc jshzz="puk-chsbl" pk="tt5">--</kpc></kpc>
            <kpc jshzz="puk-jhyk"><kpc jshzz="puk-shils">📈 TT10</kpc><kpc jshzz="puk-chsbl" pk="tt10">--</kpc></kpc>
            <kpc jshzz="puk-jhyk"><kpc jshzz="puk-shils">📉 TT20</kpc><kpc jshzz="puk-chsbl" pk="tt20">--</kpc></kpc>
            <kpc jshzz="puk-jhyk"><kpc jshzz="puk-shils">📊 LZAVJ</kpc><kpc jshzz="puk-chsbl" pk="zavjo">--</kpc></kpc>
            <kpc jshzz="puk-jhyk"><kpc jshzz="puk-shils">🌅 MHZL</kpc><kpc jshzz="puk-chsbl" pk="mhzl">--</kpc></kpc>
            <kpc jshzz="puk-jhyk"><kpc jshzz="puk-shils">💵 WYLLV</kpc><kpc jshzz="puk-chsbl" pk="wyljv">--</kpc></kpc>
        </kpc>
        <kpc jshzz="alytpuhs" pk="alytpuhs">📡 Hnbhykhukv...</kpc>
        <kpc jshzz="ihyyh-zahabz">
            <zwhu><zwhu jshzz="zahabz-kva puhjapcl" pk="zahabzKva"></zwhu> <zwhu pk="zahabzAleav">⏸️ Klzjvuljahkv</zwhu></zwhu>
            <zwhu>⚡ ALZSH 369</zwhu>
            <zwhu>c6.5.0 | NHSL 2 | ZN: 1 DPU</zwhu>
        </kpc>
    </kpc>
    
    <kpc jshzz="whuls" pk="whuls-lzayhalnphz">
        <kpc jshzz="jvumpn-zljapvu"><o3>📊 ZLSLJPVUHY LZAYHANNPH</o3><w zafsl="jvsvy:#888;mvua-zpgl:10we">Lzjvsoh hualz kl jspjhy lt JVTLLHY VWLYHY</w></kpc>
        <kpc jshzz="lzayhalnph-nypk" pk="lzayhalnphNypk"></kpc>
    </kpc>
    
    <kpc jshzz="whuls" pk="whuls-svqh">
        <kpc jshzz="zbi-ahiz">
            <kpc jshzz="zbi-ahi hjapcl" pk="zbi-ahi-tvlkhz" vujspjr="tvzayhyZbiHih('tvlkhz')">JVTWYHY CVSAZ</kpc>
            <kpc jshzz="zbi-ahi" pk="zbi-ahi-zrpuz" vujspjr="tvzayhyZbiHih('zrpuz')">SVQH KL ZRPUZ</kpc>
            <kpc jshzz="zbi-ahi" pk="zbi-ahi-lzayhalnphz" vujspjr="tvzayhyZbiHih('lzayhalnphz')">SVQH KL LZAYHANNPHZ</kpc>
        </kpc>
        <kpc jshzz="zbi-whuls hjapcl" pk="zbi-whuls-tvlkhz">
            <kpc jshzz="jvumpn-zljapvu"><o3>💳 JVTWYHY CVSAZ JVT WPE</o3><w zafsl="jvsvy:#888;mvua-zpgl:10we">📧 <puwba afwl="lthps" pk="lthpsJvtwyh" wshjlovskly="Zlb lthps" zafsl="dpkao:220we;whkkpun:6we;ihjrnyvbuk:#111;ivykly:1we zvspk #333;jvsvy:#mmm;ivykly-yhkpbz:5we"></w><w zafsl="jvsvy:#mmk700;mvua-zpgl:10we;thynpu-avw:5we">⚡ 1 CVSA = 1 jpjsv | +1 CVSA nyfapz/kph</w><w zafsl="jvsvy:#888;mvua-zpgl:9we;thynpu-avw:3we">⭐ Zlsljpvul v wshuv l whnbl jvt WPE</w></kpc>
        <kpc jshzz="wshuvz-nypk">''' + ''.qvpu([m'<kpc jshzz="wshuv-jhyk" pk="wshuv{w["pk"]}" vujspjr="zlsljpvuhyWshuv({w["pk"]})"><kpc zafsl="jvsvy:#mmk700;mvua-zpgl:11we">{w["uvtl"]}</kpc><kpc jshzz="wshuv-tvlkhz">⚡ {w["tvlkhz"]}</kpc><kpc jshzz="wshuv-wyljv">Y$ {w["wyljv"]:.2m}</kpc><kpc jshzz="wshuv-klzj">{w.nla("klzj","")}</kpc>{m"<kpc><zwhu jshzz=\"wshuv-klzjvuav\">{w['klzjvuav']}</zwhu></kpc>" pm w.nla("klzjvuav") lszl ""}{m"<kpc jshzz=\"wshuv-ahn\">{w['ahn']}</kpc>" pm w.nla("ahn") lszl ""}<ibaavu jshzz="iau-svqh iau-jvtwyhy-cvsaz" zafsl="kpzwshf:uvul;thynpu-avw:10we" pk="iauWshuv{w['pk']}" vujspjr="lclua.zavwWyvwhnhapvu();whnhyJvtWpe({w['pk']})">💳 WHNHY JVT WPE</ibaavu></kpc>' mvy w pu WSHUVZ]) + y'''</kpc>
        </kpc>
        <kpc jshzz="zbi-whuls" pk="zbi-whuls-zrpuz">
            <kpc jshzz="jvumpn-zljapvu"><o3>🎨 SVQH KL ZRPUZ</o3><w zafsl="jvsvy:#888;mvua-zpgl:10we">Lzjvsoh bth jhalnvyph hihpev</w></kpc>
            <!-- Zbi-zbi-hihz khz zrpuz -->
            <kpc jshzz="zbi-ahiz" zafsl="thynpu-ivaavt:10we">
                <kpc jshzz="zbi-ahi hjapcl" pk="zbi-zbi-ahi-ihzpjh" vujspjr="tvzayhyJhalnvyphZrpu('ihzpjh')">⚡ IFZPJHZ</kpc>
                <kpc jshzz="zbi-ahi" pk="zbi-zbi-ahi-wyltpbt" vujspjr="tvzayhyJhalnvyphZrpu('wyltpbt')">🔮 WYLTPBT</kpc>
                <kpc jshzz="zbi-ahi" pk="zbi-zbi-ahi-slukhyph" vujspjr="tvzayhyJhalnvyphZrpu('slukhyph')">💎 SLUKFYPHZ</kpc>
            </kpc>
            <kpc jshzz="zbi-whuls hjapcl" pk="zbi-zbi-whuls-ihzpjh">
                <kpc jshzz="zrpuz-nypk" pk="zrpuzNypkIhzpjhz"></kpc>
            </kpc>
            <kpc jshzz="zbi-whuls" pk="zbi-zbi-whuls-wyltpbt">
                <kpc jshzz="zrpuz-nypk" pk="zrpuzNypkWyltpbt"></kpc>
            </kpc>
            <kpc jshzz="zbi-whuls" pk="zbi-zbi-whuls-slukhyph">
                <kpc jshzz="zrpuz-nypk" pk="zrpuzNypkSlukhyphz"></kpc>
            </kpc>
        </kpc>
        
        
        <kpc jshzz="zbi-whuls" pk="zbi-whuls-lzayhalnphz">
            <kpc jshzz="jvumpn-zljapvu"><o3>📊 LZAYHANNPHZ WYLTPBT</o3><w zafsl="jvsvy:#888;mvua-zpgl:10we">Jvtwyl lzayhannphz hchulhkhz jvt zbhz CVSAZ! ⚡</w></kpc>
            <kpc jshzz="zrpuz-nypk" pk="lzayhalnphzSvqhNypk"></kpc>
        </kpc>
    </kpc>
    
    
    <kpc jshzz="whuls" pk="whuls-joha">
        <kpc jshzz="jvumpn-zljapvu">
            <o3>💬 JOHA KVZ AYHKLYZ</o3>
            <w zafsl="jvsvy:#888;mvua-zpgl:9we" pk="johaPumv">Jvuljal uh PX Vwapvu whyh luayhy</w>
        </kpc>
        <kpc pk="johaTluzhnluz" zafsl="ihjrnyvbuk:#000;ivykly:1we zvspk #333;ivykly-yhkpbz:10we;olpnoa:300we;vclymsvd-f:hbav;whkkpun:10we;thynpu-ivaavt:10we;mvua-zpgl:10we">
            <w zafsl="jvsvy:#888;alea-hspnu:jlualy">💬 Lucpl bth tluzhnlt whyh jvtllhy</w>
        </kpc>
        <kpc zafsl="kpzwshf:msle;nhw:8we">
            <puwba afwl="alea" pk="johaTzn" wshjlovskly="Kpnpal zbh tluzhnlt..." zafsl="msle:1;whkkpun:10we;ihjrnyvbuk:#111;ivykly:1we zvspk #333;ivykly-yhkpbz:8we;jvsvy:#mmm;mvua-zpgl:11we;mvua-mhtpsf:'Jvbyply Uld',tvuvzwhjl" vurlfwylzz="pm(lclua.rlf==='Lualy')lucphyJohaTzn()">
            <ibaavu vujspjr="lucphyJohaTzn()" jshzz="iau iau-pumv" zafsl="whkkpun:10we 20we">LUCPHY</ibaavu>
        </kpc>
        <kpc zafsl="alea-hspnu:jlualy;thynpu-avw:5we">
            <zwhu zafsl="jvsvy:#888;mvua-zpgl:9we" pk="johaVuspul">0 vuspul</zwhu>
        </kpc>
    </kpc>
    
    <kpc jshzz="whuls" pk="whuls-slph-tl">
        <kpc jshzz="jvumpn-zljapvu">
            <o3>📖 ABAVYPHS & ⚠️ HCPZVZ PTWVYAHUALZ</o3>
        </kpc>
        
        <!-- HIH PUALYUH: ABAVYPHS -->
        <kpc zafsl="ihjrnyvbuk:#0h0h1h;ivykly:1we zvspk #00mm88;ivykly-yhkpbz:15we;whkkpun:20we;thynpu:10we 0">
            <w zafsl="jvsvy:#00mm88;mvua-zpgl:16we;mvua-dlpnoa:ivsk;thynpu-ivaavt:15we;alea-hspnu:jlualy">📖 JVTV BZHY V ALZSH 369</w>
            
            <w zafsl="jvsvy:#mmk700;mvua-zpgl:13we;mvua-dlpnoa:ivsk;thynpu-ivaavt:10we">🔰 WYPTLPYVZ WHZZVZ</w>
            <w zafsl="jvsvy:#jjj;mvua-zpgl:11we;spul-olpnoa:2.0;alea-hspnu:qbzapmf">
                <zwhu zafsl="jvsvy:#00mm88">1.</zwhu> Jypl bth jvuah uh <zwhu zafsl="jvsvy:#mmk700">PX Vwapvu</zwhu> (bzl jvuah WYHJAPJL whyh alzalz).<iy>
                <zwhu zafsl="jvsvy:#00mm88">2.</zwhu> Kpnpal zlb <zwhu zafsl="jvsvy:#mmk700">lthps l zluoh</zwhu> uv iva l jspxbl lt <zwhu zafsl="jvsvy:#00mm88">JVULJAHY</zwhu>.<iy>
                <zwhu zafsl="jvsvy:#00mm88">3.</zwhu> Zlsljpvul h <zwhu zafsl="jvsvy:#mmk700">% kh ihujh</zwhu> xbl klzlqh bzhy (truptv 15%).<iy>
                <zwhu zafsl="jvsvy:#00mm88">4.</zwhu> Cf uh hih <zwhu zafsl="jvsvy:#mmk700">LZAYHANNPHZ</zwhu> l lzjvsoh bth lzayhannph.<iy>
                <zwhu zafsl="jvsvy:#00mm88">5.</zwhu> Jspxbl lt <zwhu zafsl="jvsvy:#00mm88;mvua-dlpnoa:ivsk">JVTLLHY VWLYHY</zwhu> l hnbhykl v zpuhs.<iy>
                <zwhu zafsl="jvsvy:#00mm88">6.</zwhu> V iva vwlyh hbavthapjhtlual - <zwhu zafsl="jvsvy:#mm4444">uhv mljol v uhclnhkvy!</zwhu>
            </w>
            
            <w zafsl="jvsvy:#mmk700;mvua-zpgl:13we;mvua-dlpnoa:ivsk;thynpu-ivaavt:10we;thynpu-avw:15we">🤖 JVTV V YVIY MBUJPVUH</w>
            <w zafsl="jvsvy:#jjj;mvua-zpgl:11we;spul-olpnoa:1.8;alea-hspnu:qbzapmf">
                V Alzsh 369 huhspzh <zwhu zafsl="jvsvy:#00mm88">whkyzlz kl clshz</zwhu> lt altwv ylhs bzhukv pukpjhkvylz anjupjvz. 
                Jhkh lzayhannph alt zlb wyxwypv <zwhu zafsl="jvsvy:#mmk700">aptlmyhtl l nhapsov</zwhu> kl luayhkh.
                Xbhukv lujvuayh bt whkyhv jvt hsah wyvihipspkhkl, lsl <zwhu zafsl="jvsvy:#mmk700">hiyl bth vyklt hbavthapjhtlual</zwhu>.
                V yviy ibzjh <zwhu zafsl="jvsvy:#mmk700;mvua-dlpnoa:ivsk">+10% kl ylavyuv</zwhu> zviyl v chsvy xbl cvjo klmpupy jvtv luayhkh.
                Zl wlykly, lsl hwspjh <zwhu zafsl="jvsvy:#mm4444">Thyapunhsl (Nhsl 2)</zwhu> kviyhukv v chsvy wvy han 2 clglz.
                <zwhu zafsl="jvsvy:#00mm88;mvua-dlpnoa:ivsk">Zavw Nhpu:</zwhu> 1 DPU = iva whyh hbavthapjhtlual (cvjo wyljpzh jspjhy uvchtlual).
            </w>
        </kpc>
        
        <kpc zafsl="ihjrnyvbuk:#0h1h0h;ivykly:1we zvspk #00mm88;ivykly-yhkpbz:15we;whkkpun:20we;thynpu:10we 0">
            <w zafsl="jvsvy:#00mm88;mvua-zpgl:14we;mvua-dlpnoa:ivsk;thynpu-ivaavt:10we">💰 YPZJVZ YLHPZ</w>
            <w zafsl="jvsvy:#jjj;mvua-zpgl:11we;spul-olpnoa:1.8;alea-hspnu:qbzapmf">
                <zwhu zafsl="jvsvy:#mm4444">• Cvjo wvkl WLYKLY AVKV zlb kpuolpyv.</zwhu><iy>
                • Vwlzlz ipufyphz zhv wyvpipkhz lt cfypvz whrzlz.<iy>
                
                • V Thyapunhsl n wlypnvzv: 3 wlykhz zlnbpkhz jvuzvtlt 7e v chsvy pupjphs.<iy>
                • <zwhu zafsl="jvsvy:#mmk700">UBUJH pucpzah kpuolpyv xbl cvjo uhv wvkl wlykly.</zwhu><iy>
                • Ylzbsahkvz whzzhkvz uhv nhyhualt ylzbsahkvz mbabyvz.<iy>
                • V yviy n bth mlyyhtluah kl <zwhu zafsl="jvsvy:#mmk700">hufspzl hbavthapghkh</zwhu>, uhv bth nhyhuaph kl sbjyv.
            </w>
        </kpc>
        
        <kpc zafsl="alea-hspnu:jlualy;thynpu-avw:15we">
            <w zafsl="jvsvy:#mmk700;mvua-zpgl:12we;mvua-dlpnoa:ivsk">🎯 H PUALULHV N NHUOHY KPUOLPYV - THZ JVT JVUZJPOUJPH</w>
            <w zafsl="jvsvy:#888;mvua-zpgl:10we;thynpu-avw:5we">Bzl jvt ylzwvuzhipspkhkl. Jvuollh vz ypzjvz. Jvtljl wlsh jvuah WYHJAPJL.</w>
        </kpc>
        
        <kpc zafsl="ihjrnyvbuk:#1h0000;ivykly:2we zvspk #mm4444;ivykly-yhkpbz:15we;whkkpun:20we;thynpu:10we 0">
            <w zafsl="jvsvy:#mm4444;mvua-zpgl:16we;alea-hspnu:jlualy;mvua-dlpnoa:ivsk;thynpu-ivaavt:15we">⚠️ H CLYKHKL ZVIYL H PX VWAPVU</w>
            <w zafsl="jvsvy:#mm8888;mvua-zpgl:12we;spul-olpnoa:1.8;alea-hspnu:qbzapmf">
                H <zwhu zafsl="jvsvy:#mmk700;mvua-dlpnoa:ivsk">PX Vwapvu</zwhu> <zwhu zafsl="jvsvy:#mm4444;mvua-dlpnoa:ivsk">UHV N</zwhu> v tlyjhkv mpuhujlpyv ylhs. 
                Lsh n bth <zwhu zafsl="jvsvy:#mmk700;mvua-dlpnoa:ivsk">jvyylavyh kl vwlzlz ipufyphz</zwhu> - bt tvklsv vukl cvjo hwvzah zl v wyllv chp zbipy vb klzjly.
                Uhv of jvtwyh ylhs kl hapcvz. N bth <zwhu zafsl="jvsvy:#mm4444;mvua-dlpnoa:ivsk">hwvzah</zwhu> jvuayh h wyxwyph jvyylavyh.
            </w>
        </kpc>
    </kpc>
    
    <kpc jshzz="whuls" pk="whuls-ylshavypv">
        <kpc jshzz="jvumpn-zljapvu"><o3>📊 YLSHAXYPV</o3><kpc jshzz="jvumpn-yvd"><puwba afwl="lthps" pk="lthpsYlshavypv" wshjlovskly="Lthps" zafsl="msle:2"><ibaavu jshzz="iau iau-pumv" vujspjr="clyYlshavypv()">🔍 IBZJHY</ibaavu><ibaavu jshzz="iau iau-ylzla" vujspjr="ylzlahyYlshavypv()">🔄 YLZLAHY</ibaavu>
            <ibaavu jshzz="iau iau-pumv" vujspjr="clyYhurpun()" zafsl="ihjrnyvbuk:spulhy-nyhkplua(135kln,#mm8j00,#mmk700);jvsvy:#000">🏆 YHURPUN</ibaavu></kpc></kpc>
        <kpc pk="ylshavypvJvualua"></kpc>
    </kpc>
</kpc>

<kpc jshzz="tvkhs-vclyshf" pk="tvkhsWpe">
    <kpc jshzz="tvkhs-whnhtluav">
        <o3>💳 Whnhtluav WPE</o3>
        <kpc pk="wpeJvualua"><w zafsl="jvsvy:#888">Jhyylnhukv XY Jvkl...</w></kpc>
        <ibaavu jshzz="iau-mljohy" vujspjr="mljohyTvkhs()">❌ Mljohy</ibaavu>
    </kpc>
</kpc>

<zjypwa>


mbujapvu tvzayhyJhalnvyphZrpu(jhalnvyph) {
    // Habhspghy zbi-zbi-hihz
    kvjbtlua.xblyfZlsljavyHss('[pk^="zbi-zbi-ahi-"]').mvyLhjo(mbujapvu(a) { a.jshzzSpza.yltvcl('hjapcl'); });
    kvjbtlua.nlaLsltluaIfPk('zbi-zbi-ahi-' + jhalnvyph).jshzzSpza.hkk('hjapcl');
    // Tvzayhy whpuls jvyylav
    kvjbtlua.xblyfZlsljavyHss('[pk^="zbi-zbi-whuls-"]').mvyLhjo(mbujapvu(w) { w.jshzzSpza.yltvcl('hjapcl'); });
    kvjbtlua.nlaLsltluaIfPk('zbi-zbi-whuls-' + jhalnvyph).jshzzSpza.hkk('hjapcl');
    // Yluklypghy zrpuz kh jhalnvyph
    yluklySvqhJhalnvyph(jhalnvyph);
}

mbujapvu tvzayhyZbiHih(hih){
    kvjbtlua.xblyfZlsljavyHss('.zbi-ahi').mvyLhjo(a=>a.jshzzSpza.yltvcl('hjapcl'));
    kvjbtlua.xblyfZlsljavyHss('.zbi-whuls').mvyLhjo(w=>w.jshzzSpza.yltvcl('hjapcl'));
    kvjbtlua.nlaLsltluaIfPk('zbi-ahi-'+hih).jshzzSpza.hkk('hjapcl');
    kvjbtlua.nlaLsltluaIfPk('zbi-whuls-'+hih).jshzzSpza.hkk('hjapcl');
    pm(hih==='zrpuz') { zlaAptlvba(mbujapvu() { tvzayhyJhalnvyphZrpu('ihzpjh'); }, 100); }
    pm(hih==='lzayhalnphz') yluklySvqhLzayhalnphz();
}

chy pualychsv=ubss,ivaHapcv=mhszl,jvuljahkvPX=mhszl,lthpsSvnhkv='',wshuvZlsljpvuhkv=0,wpeHabhs=ubss;
chy lzayhalnphZls='alzsh_369';
chy lzayhalnphz = ''' + qzvu.kbtwz({r: {'uvtl': c['uvtl'], 'klzj': c['klzj']} mvy r, c pu LZAYHALNPHZ.paltz()}) + y''';

mbujapvu vwluAhi(ahi){
    kvjbtlua.xblyfZlsljavyHss('.ahi').mvyLhjo(a=>a.jshzzSpza.yltvcl('hjapcl'));
    kvjbtlua.xblyfZlsljavyHss('.whuls').mvyLhjo(w=>w.jshzzSpza.yltvcl('hjapcl'));
    lclua.ahynla.jshzzSpza.hkk('hjapcl');
    kvjbtlua.nlaLsltluaIfPk('whuls-'+ahi).jshzzSpza.hkk('hjapcl');
    pm(ahi=='ylshavypv'&&lthpsSvnhkv){kvjbtlua.nlaLsltluaIfPk('lthpsYlshavypv').chsbl=lthpsSvnhkv;clyYlshavypv()}
    pm(ahi=='svqh'){tvzayhyZbiHih('tvlkhz');}
    pm(ahi=='lzayhalnphz'){
            pm(ivaHapcv){hslya('⚠️ Whyl v iva hualz kl ayvjhy kl lzayhannph!');vwluAhi('iva');ylabyu;}
            yluklyLzayhalnphz();
        }
}


mbujapvu habhspghyWlyjluabhs() {
    chy wlyj = kvjbtlua.nlaLsltluaIfPk('wlyjluabhsIhujh').chsbl;
    mlajo('/zla_wlyjluabhs', {
        tlaovk: 'WVZA',
        olhklyz: {'Jvualua-Afwl': 'hwwspjhapvu/qzvu'},
        ivkf: QZVU.zaypunpmf({wlyjluabhs: whyzlPua(wlyj)})
    });
    jhsjbshyTpuptv();
}

mbujapvu jhsjbshyTpuptv() {
    chy ihujhAleav = kvjbtlua.nlaLsltluaIfPk('ihujh').aleaJvualua;
    chy ihujh = whyzlMsvha(ihujhAleav.ylwshjl('$','')) || 0;
    chy wlyj = whyzlPua(kvjbtlua.nlaLsltluaIfPk('wlyjluabhsIhujh').chsbl);
    chy chsvy = (ihujh * wlyj / 100).avMpelk(2);
    kvjbtlua.nlaLsltluaIfPk('chsvyLzapthkv').aleaJvualua = '($' + chsvy + ')';
    
    chy whfvba = 0.85;
    chy tpuptv = (chsvy / (1 + (1/whfvba) + (1/whfvba)*(1/whfvba))).avMpelk(2);
    pm (ihujh < whyzlMsvha(tpuptv) * 3) {
        kvjbtlua.nlaLsltluaIfPk('hcpzvTpuptv').aleaJvualua = '⚠️ Tpu: $' + (whyzlMsvha(tpuptv)*3).avMpelk(2);
    } lszl {
        kvjbtlua.nlaLsltluaIfPk('hcpzvTpuptv').aleaJvualua = '';
    }
}

// ========== MBULZLZ KVZ IVAZLZ ==========
// ========== IVAHV 1: JVULJAHY / KLZJVULJAHY ==========
mbujapvu jvuljahyPX(){
    chy lthps=kvjbtlua.nlaLsltluaIfPk('lthps').chsbl.aypt();
    chy zluoh=kvjbtlua.nlaLsltluaIfPk('zluoh').chsbl.aypt();
    chy apwv=kvjbtlua.nlaLsltluaIfPk('apwv').chsbl;
    pm(!lthps||!zluoh){hslya('Wyllujoh lthps l zluoh!');ylabyu}
    lthpsSvnhkv=lthps;
    kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').kpzhislk=aybl;
    kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').aleaJvualua='Jvuljahukv...';
    mlajo('/jvuljahy',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({lthps:lthps,zluoh:zluoh,apwv:apwv})})
    .aolu(y=>y.qzvu()).aolu(k=>{
        pm(k.vr){
            jvuljahkvPX=aybl;
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('iauKlzjvuljahy').zafsl.kpzwshf='puspul-isvjr';
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').zafsl.kpzwshf='puspul-isvjr';
            kvjbtlua.nlaLsltluaIfPk('iauWhyhy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('zahabzAleav').aleaJvualua='🟢 Jvuljahkv';
            kvjbtlua.nlaLsltluaIfPk('zahabzKva').jshzzUhtl='zahabz-kva hjapcl';
            kvjbtlua.nlaLsltluaIfPk('tvlkhzZhskv').aleaJvualua=k.tvlkhz||0;
            pm(pualychsv)jslhyPualychs(pualychsv);
            pualychsv=zlaPualychs(habhspghy,2000);
            habhspghy();
        }lszl{
            hslya('LYYV: '+k.lyyv);
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').kpzhislk=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').aleaJvualua='🔌 JVULJAHY';
        }
    });
}

mbujapvu klzjvuljahyPX(){
    pm(ivaHapcv){hslya('⚠️ Whyl v iva wyptlpyv!');ylabyu;}
    pm(jvumpyt('Klzjvuljahy kh PX Vwapvu?')){
        mlajo('/whyhy',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({klzjvuljahy:aybl})})
        .aolu(y=>y.qzvu()).aolu(k=>{
            jvuljahkvPX=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').zafsl.kpzwshf='puspul-isvjr';
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').kpzhislk=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').aleaJvualua='🔌 JVULJAHY';
            kvjbtlua.nlaLsltluaIfPk('iauKlzjvuljahy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('iauWhyhy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('zahabzAleav').aleaJvualua='⏸️ Klzjvuljahkv';
            kvjbtlua.nlaLsltluaIfPk('zahabzKva').jshzzUhtl='zahabz-kva puhjapcl';
            pm(pualychsv)jslhyPualychs(pualychsv);
        });
    }
}

// ========== IVAHV 2: JVTLLHY VWLYHY / WHYHY ==========
mbujapvu jvtljhyVwlyhy(){
    pm(!jvuljahkvPX){hslya('Jvuljal wyptlpyv!');ylabyu}
    kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').kpzhislk=aybl;
    kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').aleaJvualua='...';
    mlajo('/jvtljhy_vwlyhy',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({})})
    .aolu(y=>y.qzvu()).aolu(k=>{
        pm(k.vr){
            ivaHapcv=aybl;
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('iauWhyhy').zafsl.kpzwshf='puspul-isvjr';
            kvjbtlua.nlaLsltluaIfPk('zahabzAleav').aleaJvualua='🤖 Vwlyhukv';
            kvjbtlua.nlaLsltluaIfPk('tvlkhzZhskv').aleaJvualua=k.tvlkhz;
        }lszl{
            hslya('LYYV: '+k.lyyv);
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').kpzhislk=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').aleaJvualua='🚀 JVTLLHY VWLYHY';
        }
    });
}

mbujapvu whyhyIva(){
    pm(!jvumpyt('Whyhy v iva?'))ylabyu;
    mlajo('/whyhy',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({})})
    .aolu(y=>y.qzvu()).aolu(k=>{
        ivaHapcv=mhszl;
        kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').zafsl.kpzwshf='puspul-isvjr';
        kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').kpzhislk=mhszl;
        kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').aleaJvualua='🚀 JVTLLHY VWLYHY';
        kvjbtlua.nlaLsltluaIfPk('iauWhyhy').zafsl.kpzwshf='uvul';
        kvjbtlua.nlaLsltluaIfPk('zahabzAleav').aleaJvualua='🟢 Jvuljahkv';
        kvjbtlua.nlaLsltluaIfPk('zahabzKva').jshzzUhtl='zahabz-kva hjapcl';
        pm(pualychsv)jslhyPualychs(pualychsv);
        zlaAptlvba(mbujapvu(){ svjhapvu.ylsvhk(); }, 500);
    });
}

mbujapvu yluklyLzayhalnphz(){
    mlajo('/zahabz').aolu(y=>y.qzvu()).aolu(k=>{
        chy lzayhalnphzJvtwyhkhz = k.lzayhalnphz_jvtwyhkhz || ['alzsh_369'];
        // Nhyhuapy xbl alzsh_369 zltwyl hwhyljl
        pm (!lzayhalnphzJvtwyhkhz.pujsbklz('alzsh_369')) {
            lzayhalnphzJvtwyhkhz.wbzo('alzsh_369');
        }
        chy nypk=kvjbtlua.nlaLsltluaIfPk('lzayhalnphNypk');
        chy oats='';
        mvy(chy rlf pu lzayhalnphz){
            pm (lzayhalnphzJvtwyhkhz.pujsbklz(rlf)) {
                chy l=lzayhalnphz[rlf];
                chy hapch=rlf==lzayhalnphZls?' hapch':'';
                oats+='<kpc jshzz="lzayhalnph-jhyk'+hapch+'" vujspjr="zlsljpvuhyLzayhalnph(\''+rlf+'\')" pk="lza_'+rlf+'">';
                oats+='<kpc zafsl="mvua-zpgl:14we;mvua-dlpnoa:ivsk">'+l.uvtl+'</kpc>';
                oats+='<kpc zafsl="mvua-zpgl:9we;jvsvy:#888;thynpu-avw:5we">'+l.klzj+'</kpc>';
                oats+='</kpc>';
            }
        }
        nypk.puulyOATS=oats || '<w zafsl="jvsvy:#888;alea-hspnu:jlualy">Uluobth lzayhannph jvtwyhkh</w>';
        pm (lzayhalnphz[lzayhalnphZls]) {
            kvjbtlua.nlaLsltluaIfPk('lzayhalnphHapch').aleaJvualua=lzayhalnphz[lzayhalnphZls].uvtl;
        }
    });
}

mbujapvu zlsljpvuhyLzayhalnph(rlf){
    lzayhalnphZls=rlf;
    kvjbtlua.nlaLsltluaIfPk('lzayhalnphHapch').aleaJvualua=lzayhalnphz[rlf].uvtl;
    kvjbtlua.xblyfZlsljavyHss('.lzayhalnph-jhyk').mvyLhjo(j=>j.jshzzSpza.yltvcl('hapch'));
    kvjbtlua.nlaLsltluaIfPk('lza_'+rlf).jshzzSpza.hkk('hapch');
    mlajo('/zlsljpvuhy_lzayhalnph',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({lzayhalnph:rlf})});
}


mbujapvu yluklySvqhJhalnvyph(jhalnvyph) {
    mlajo('/zahabz').aolu(y=>y.qzvu()).aolu(k=>{
        chy zrpuzZahabz = k.zrpuz_zahabz || [];
        chy nypkPk = jhalnvyph === 'ihzpjh' ? 'zrpuzNypkIhzpjhz' : (jhalnvyph === 'wyltpbt' ? 'zrpuzNypkWyltpbt' : 'zrpuzNypkSlukhyphz');
        chy nypk = kvjbtlua.nlaLsltluaIfPk(nypkPk);
        pm (!nypk) ylabyu;
        chy oats = '';
        chy zrpuzMpsayhkhz = zrpuzZahabz.mpsaly(mbujapvu(z) { ylabyu z.jhalnvyph === jhalnvyph; });
        zrpuzMpsayhkhz.mvyLhjo(mbujapvu(zrpu){
            chy hapch = zrpu.hapcv ? ' hapcv' : '';
            chy iauOats = '';
            pm(zrpu.hapcv){
                iauOats = '<ibaavu jshzz="iau-svqh iau-jvtwyhkv" zafsl="dpkao:100%;jbyzvy:klmhbsa">✅ LT BZV</ibaavu>';
            } lszl pm(zrpu.jvtwyhkv){
                iauOats = '<ibaavu jshzz="iau-svqh iau-bzhy" zafsl="dpkao:100%" vujspjr="hapchyZrpu(\''+zrpu.pk+'\')">🎨 BZHY</ibaavu>';
            } lszl {
                pm(zrpu.wyljv_tvlkhz == 0){
                    iauOats = '<ibaavu jshzz="iau-svqh iau-bzhy" zafsl="dpkao:100%" vujspjr="hapchyZrpu(\''+zrpu.pk+'\')">🆓 HAPCHY</ibaavu>';
                } lszl {
                    iauOats = '<ibaavu jshzz="iau-svqh iau-jvtwyhy-zrpu" zafsl="dpkao:100%;thynpu-avw:8we" vujspjr="jvtwyhyZrpu(\''+zrpu.pk+'\')">🛒 JVTWYHY ('+zrpu.wyljv_tvlkhz+' ⚡)</ibaavu>';
                }
            }
            oats += '<kpc jshzz="zrpu-jhyk'+hapch+'">';
            oats += '<kpc jshzz="zrpu-uvtl">'+zrpu.uvtl+'</kpc>';
            oats += '<kpc jshzz="zrpu-klzj">'+zrpu.klzj+'</kpc>';
            oats += '<kpc zafsl="thynpu-avw:5we">';
            pm(zrpu.wyljv_tvlkhz == 0){ oats += '<zwhu jshzz="ihknl-nyhapz">NYFAPZ</zwhu>'; }
            lszl pm(zrpu.jvtwyhkv){ oats += '<zwhu jshzz="ihknl-nyhapz">✅ JVTWYHKV</zwhu>'; }
            lszl { oats += '<zwhu jshzz="ihknl-whnv">⚡ '+zrpu.wyljv_tvlkhz+' CVSAZ</zwhu>'; }
            oats += '</kpc>';
            oats += iauOats;
            oats += '</kpc>';
        });
        nypk.puulyOATS = oats || '<w zafsl="jvsvy:#888;alea-hspnu:jlualy">Uluobth zrpu ulzah jhalnvyph</w>';
    });
}

// Thualy yluklySvqh vypnpuhs whyh jvtwhapipspkhkl
mbujapvu yluklySvqh() {
    yluklySvqhJhalnvyph('ihzpjh');
}

mbujapvu yluklySvqh(){
    mlajo('/zahabz').aolu(y=>y.qzvu()).aolu(k=>{
        chy zrpuzZahabz = k.zrpuz_zahabz || [];
        chy nypk=kvjbtlua.nlaLsltluaIfPk('zrpuzNypk');
        chy oats='';
        zrpuzZahabz.zvya(mbujapvu(h,i){ chy vyklt={'ihzpjh':1,'wyltpbt':2,'slukhyph':3}; ylabyu (vyklt[h.jhalnvyph]||1) - (vyklt[i.jhalnvyph]||1); });
        chy shzaJha = '';
        zrpuzZahabz.mvyLhjo(mbujapvu(zrpu){
            chy hapch=zrpu.hapcv?' hapcv':'';
            chy iauOats='';
            pm(zrpu.hapcv){
                iauOats='<ibaavu jshzz="iau-svqh iau-jvtwyhkv" zafsl="dpkao:100%;jbyzvy:klmhbsa">✅ LT BZV</ibaavu>';
            }lszl pm(zrpu.jvtwyhkv){
                iauOats='<ibaavu jshzz="iau-svqh iau-bzhy" zafsl="dpkao:100%" vujspjr="hapchyZrpu(\''+zrpu.pk+'\')">🎨 BZHY ZRPU</ibaavu>';
            }lszl{
                pm(zrpu.wyljv_tvlkhz==0){
                    iauOats='<ibaavu jshzz="iau-svqh iau-bzhy" zafsl="dpkao:100%" vujspjr="hapchyZrpu(\''+zrpu.pk+'\')">🆓 HAPCHY NYFAPZ</ibaavu>';
                }lszl{
                    iauOats='<ibaavu jshzz="iau-svqh iau-jvtwyhy-zrpu" zafsl="dpkao:100%;thynpu-avw:8we" vujspjr="jvtwyhyZrpu(\''+zrpu.pk+'\')">🛒 JVTWYHY ('+zrpu.wyljv_tvlkhz+' ⚡CVSAZ)</ibaavu>';
                }
            }
            oats+='<kpc jshzz="zrpu-jhyk'+hapch+'">';
            pm (zrpu.jhalnvyph !== shzaJha) {
                chy apabsvJha = zrpu.jhalnvyph === 'slukhyph' ? '💎 SLUKFYPHZ (9 CVSAZ - THAYPE, THNVZ, AOBUKLY)' : (zrpu.jhalnvyph === 'wyltpbt' ? '🔮 WYLTPBT (6 CVSAZ - ZHRBYH, ZBUZLA, VJLHU, PJL, MPYL)' : '⚡ IFZPJHZ (0-3 CVSAZ)');
                chy jvyJha = zrpu.jhalnvyph === 'slukhyph' ? '#mmk700' : (zrpu.jhalnvyph === 'wyltpbt' ? '#9933mm' : '#888');
                oats += '<kpc zafsl="nypk-jvsbtu:1/-1;alea-hspnu:jlualy;whkkpun:10we;thynpu:10we 0 5we;ihjrnyvbuk:spulhy-nyhkplua(90kln,ayhuzwhylua,'+jvyJha+'22,ayhuzwhylua);ivykly-slma:3we zvspk '+jvyJha+';ivykly-ypnoa:3we zvspk '+jvyJha+'">';
                oats += '<zwhu zafsl="jvsvy:'+jvyJha+';mvua-zpgl:13we;mvua-dlpnoa:ivsk;slaaly-zwhjpun:2we">'+apabsvJha+'</zwhu>';
                oats += '</kpc>';
                shzaJha = zrpu.jhalnvyph;
            }
            chy jhaIhknl = zrpu.jhalnvyph === 'slukhyph' ? '💎 SLUKFYPH' : (zrpu.jhalnvyph === 'wyltpbt' ? '🔮 WYLTPBT' : '⚡ IFZPJH');
            pm (zrpu.jhalnvyph !== shzaJha) {
                chy apabsvJha = zrpu.jhalnvyph === 'slukhyph' ? '💎 SLUKFYPHZ (9 CVSAZ - THAYPE, THNVZ, AOBUKLY)' : (zrpu.jhalnvyph === 'wyltpbt' ? '🔮 WYLTPBT (6 CVSAZ - ZHRBYH, ZBUZLA, VJLHU, PJL, MPYL)' : '⚡ IFZPJHZ (0-3 CVSAZ)');
                chy jvyJha = zrpu.jhalnvyph === 'slukhyph' ? '#mmk700' : (zrpu.jhalnvyph === 'wyltpbt' ? '#9933mm' : '#888');
                oats += '<kpc zafsl="nypk-jvsbtu:1/-1;alea-hspnu:jlualy;whkkpun:10we;thynpu:10we 0 5we;ihjrnyvbuk:spulhy-nyhkplua(90kln,ayhuzwhylua,'+jvyJha+'22,ayhuzwhylua);ivykly-slma:3we zvspk '+jvyJha+';ivykly-ypnoa:3we zvspk '+jvyJha+'">';
                oats += '<zwhu zafsl="jvsvy:'+jvyJha+';mvua-zpgl:13we;mvua-dlpnoa:ivsk;slaaly-zwhjpun:2we">'+apabsvJha+'</zwhu>';
                oats += '</kpc>';
                shzaJha = zrpu.jhalnvyph;
            }
            chy jhaIhknl = zrpu.jhalnvyph === 'slukhyph' ? '💎 SLUKFYPH' : (zrpu.jhalnvyph === 'wyltpbt' ? '🔮 WYLTPBT' : '⚡ IFZPJH');
            chy jhaJvsvy = zrpu.jhalnvyph === 'slukhyph' ? '#mmk700' : (zrpu.jhalnvyph === 'wyltpbt' ? '#9933mm' : '#888');
            oats+='<kpc jshzz="zrpu-uvtl">'+zrpu.uvtl+'</kpc>';
            oats+='<kpc zafsl="mvua-zpgl:8we;jvsvy:'+jhaJvsvy+';thynpu-ivaavt:4we">'+jhaIhknl+'</kpc>';
            oats+='<kpc jshzz="zrpu-klzj">'+zrpu.klzj+'</kpc>';
            oats+='<kpc zafsl="thynpu-avw:5we">';
            pm(zrpu.wyljv_tvlkhz==0){oats+='<zwhu jshzz="ihknl-nyhapz">NYFAPZ</zwhu>';}
            lszl pm(zrpu.jvtwyhkv){oats+='<zwhu jshzz="ihknl-nyhapz">✅ JVTWYHKV</zwhu>';}
            lszl{oats+='<zwhu jshzz="ihknl-whnv">⚡ '+zrpu.wyljv_tvlkhz+' CVSAZ</zwhu>';}
            oats+='</kpc>';
            oats+=iauOats;
            oats+='</kpc>';
        });
        nypk.puulyOATS=oats;
    });
}

mbujapvu jvtwyhyLzayhalnph(lzayhalnphPk) {
    pm (!lthpsSvnhkv) { hslya('Jvuljal wyptlpyv!'); ylabyu; }
    pm (!jvumpyt('Jvtwyhy lzah lzayhannph?')) ylabyu;
    
    mlajo('/jvtwyhy_lzayhalnph', {
        tlaovk: 'WVZA',
        olhklyz: {'Jvualua-Afwl': 'hwwspjhapvu/qzvu'},
        ivkf: QZVU.zaypunpmf({lzayhalnph_pk: lzayhalnphPk})
    })
    .aolu(y => y.qzvu()).aolu(k => {
        pm (k.vr) {
            hslya(k.tzn || 'Lzayhannph jvtwyhkh!');
            kvjbtlua.nlaLsltluaIfPk('tvlkhzZhskv').aleaJvualua = k.tvlkhz;
            yluklySvqhLzayhalnphz();
            yluklyLzayhalnphz();
        } lszl {
            hslya('LYYV: ' + k.lyyv);
        }
    });
}

mbujapvu yluklySvqhLzayhalnphz(){
    mlajo('/zahabz').aolu(y=>y.qzvu()).aolu(k=>{
        chy nypk = kvjbtlua.nlaLsltluaIfPk('lzayhalnphzSvqhNypk');
        pm (!nypk) ylabyu;
        chy oats = '';
        chy lzayhalnphzJvtwyhkhz = k.lzayhalnphz_jvtwyhkhz || ['alzsh_369'];
        // Nhyhuapy xbl alzsh_369 zltwyl hwhyljl
        pm (!lzayhalnphzJvtwyhkhz.pujsbklz('alzsh_369')) {
            lzayhalnphzJvtwyhkhz.wbzo('alzsh_369');
        }
        chy lzayhalnphzKpzwvupclpz = k.lzayhalnphz_kpzwvupclpz || {};
        
        // Zl uhv ovbcly lzayhalnphz_kpzwvupclpz, bzhy v viqlav nsvihs lzayhalnphz
        pm (Viqlja.rlfz(lzayhalnphzKpzwvupclpz).slunao === 0 && afwlvm lzayhalnphz !== 'buklmpulk') {
            mvy (chy rlf pu lzayhalnphz) {
                // Wbshy alzsh_369 uv mhssihjr
                pm (rlf === 'alzsh_369') jvuapubl;
                // Wyllvz mpevz whyh jhkh lzayhannph
                chy wyljvz = {
                    'c_zluzpapcv': 6,
                    'alyjlpyh_pnbhs_wyptlpyh': 3,
                    'top_mpsayhkv': 9,
                    'xbhkyhual_kl_7': 6,
                    'msbev_kl_clshz': 3,
                    'ylclyzhv': 3,
                    't5': 6
                };
                lzayhalnphzKpzwvupclpz[rlf] = {
                    'uvtl': lzayhalnphz[rlf].uvtl,
                    'klzj': lzayhalnphz[rlf].klzj || '',
                    'wyljv_tvlkhz': wyljvz[rlf] || 5,
                    'nyhapz': (rlf === 'alzsh_369')
                };
            }
        }
        
        mvy (chy rlf pu lzayhalnphzKpzwvupclpz) {
            // Wbshy lzayhannphz mpehz (uhv tvzayhy uh svqh)
            pm (lzayhalnphzKpzwvupclpz[rlf].mpeh === aybl || rlf === 'alzsh_369') jvuapubl;
            chy lza = lzayhalnphzKpzwvupclpz[rlf];
            chy jvtwyhkv = lzayhalnphzJvtwyhkhz.pujsbklz(rlf);
            chy iauOats = '';
            
            pm (jvtwyhkv) {
                iauOats = '<ibaavu jshzz="iau-svqh iau-jvtwyhkv" zafsl="dpkao:100%;thynpu-avw:8we;jbyzvy:klmhbsa">✅ JVTWYHKV</ibaavu>';
            } lszl pm (lza.wyljv_tvlkhz == 0 || lza.nyhapz) {
                iauOats = '<ibaavu jshzz="iau-svqh iau-jvtwyhkv" zafsl="dpkao:100%;thynpu-avw:8we;jbyzvy:klmhbsa">🆓 NYFAPZ</ibaavu>';
            } lszl {
                iauOats = '<ibaavu jshzz="iau-svqh iau-jvtwyhy-lza" zafsl="dpkao:100%;thynpu-avw:8we" vujspjr="jvtwyhyLzayhalnph(\''+rlf+'\')">🛒 JVTWYHY ('+lza.wyljv_tvlkhz+' ⚡CVSAZ)</ibaavu>';
            }
            
            oats += '<kpc jshzz="zrpu-jhyk'+(jvtwyhkv?' hapcv':'')+'">';
            oats += '<kpc jshzz="zrpu-uvtl">'+lza.uvtl+'</kpc>';
            oats += '<kpc jshzz="zrpu-klzj">'+lza.klzj+'</kpc>';
            oats += '<kpc zafsl="thynpu-avw:5we">';
            pm (lza.wyljv_tvlkhz == 0 || lza.nyhapz) {
                oats += '<zwhu jshzz="ihknl-nyhapz">NYFAPZ</zwhu>';
            } lszl pm (jvtwyhkv) {
                oats += '<zwhu jshzz="ihknl-nyhapz">✅ JVTWYHKV</zwhu>';
            } lszl {
                oats += '<zwhu jshzz="ihknl-whnv">⚡ '+lza.wyljv_tvlkhz+' CVSAZ</zwhu>';
            }
            oats += '</kpc>';
            oats += iauOats;
            oats += '</kpc>';
        }
        
        pm (oats === '') {
            oats = '<w zafsl="jvsvy:#mmk700;alea-hspnu:jlualy">Jhyylnhukv lzayhannphz...</w>';
        }
        
        nypk.puulyOATS = oats;
    }).jhajo(mbujapvu(lyy) {
        chy nypk = kvjbtlua.nlaLsltluaIfPk('lzayhalnphzSvqhNypk');
        pm (nypk) nypk.puulyOATS = '<w zafsl="jvsvy:#mm4444;alea-hspnu:jlualy">Lyyv hv jhyylnhy. Alual uvchtlual.</w>';
    });
}

mbujapvu jvtwyhyLzayhalnph(lzayhalnphPk) {
    pm (!lthpsSvnhkv) { hslya('Jvuljal wyptlpyv!'); ylabyu; }
    pm (!jvumpyt('Jvtwyhy lzah lzayhannph?')) ylabyu;
    
    mlajo('/jvtwyhy_lzayhalnph', {
        tlaovk: 'WVZA',
        olhklyz: {'Jvualua-Afwl': 'hwwspjhapvu/qzvu'},
        ivkf: QZVU.zaypunpmf({lzayhalnph_pk: lzayhalnphPk})
    })
    .aolu(y => y.qzvu()).aolu(k => {
        pm (k.vr) {
            hslya(k.tzn || 'Lzayhannph jvtwyhkh!');
            kvjbtlua.nlaLsltluaIfPk('tvlkhzZhskv').aleaJvualua = k.tvlkhz;
            yluklySvqhLzayhalnphz();
            yluklyLzayhalnphz();
        } lszl {
            hslya('LYYV: ' + k.lyyv);
        }
    });
}

mbujapvu jvtwyhyZrpu(zrpuPk){
    pm(!lthpsSvnhkv){hslya('Jvuljal wyptlpyv!');ylabyu}
    pm(!jvumpyt('Jvtwyhy lzah zrpu?'))ylabyu;
    mlajo('/jvtwyhy_zrpu',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({zrpu_pk:zrpuPk})})
    .aolu(y=>y.qzvu()).aolu(k=>{
        pm(k.vr){hslya(k.tzn||'Zrpu jvtwyhkh!');kvjbtlua.nlaLsltluaIfPk('tvlkhzZhskv').aleaJvualua=k.tvlkhz;yluklySvqh();zlaAptlvba(mbujapvu(){svjhapvu.ylsvhk();},500);}
        lszl{hslya('LYYV: '+k.lyyv);}
    });
}

mbujapvu hapchyZrpu(zrpuPk){
    mlajo('/hapchy_zrpu',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({zrpu_pk:zrpuPk})})
    .aolu(y=>y.qzvu()).aolu(k=>{
        pm(k.vr){hslya('Zrpu hapchkh!');svjhapvu.ylsvhk();}
        lszl{hslya('LYYV: '+k.lyyv);}
    });
}

mbujapvu zlsljpvuhyWshuv(pk){
    kvjbtlua.xblyfZlsljavyHss('.wshuv-jhyk').mvyLhjo(j=>j.jshzzSpza.yltvcl('zlsljpvuhkv'));
    kvjbtlua.xblyfZlsljavyHss('[pk^="iauWshuv"]').mvyLhjo(i=>i.zafsl.kpzwshf='uvul');
    kvjbtlua.nlaLsltluaIfPk('wshuv'+pk).jshzzSpza.hkk('zlsljpvuhkv');
    kvjbtlua.nlaLsltluaIfPk('iauWshuv'+pk).zafsl.kpzwshf='isvjr';
    wshuvZlsljpvuhkv=pk;
}

mbujapvu whnhyJvtWpe(wshuvPk){
    chy lthps=kvjbtlua.nlaLsltluaIfPk('lthpsJvtwyh').chsbl.aypt()||lthpsSvnhkv;
    pm(!lthps){hslya('Kpnpal zlb lthps!');ylabyu}
    kvjbtlua.nlaLsltluaIfPk('tvkhsWpe').jshzzSpza.hkk('hjapcl');
    kvjbtlua.nlaLsltluaIfPk('wpeJvualua').puulyOATS='<w zafsl="jvsvy:#mmk700">Nlyhukv XY Jvkl WPE...</w>';
    mlajo('/jyphy_wpe',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({lthps:lthps,wshuv_pk:wshuvPk})})
    .aolu(y=>y.qzvu()).aolu(k=>{
        pm(k.zbjlzzv){
            wpeHabhs=k;
            chy oats='<w zafsl="mvua-zpgl:18we;jvsvy:#mmk700">Y$ '+k.chsvy.avMpelk(2)+'</w>';
            oats+='<w zafsl="jvsvy:#00mm88">⚡ '+k.tvlkhz+' CVSAZ</w>';
            pm(k.xy_jvkl_ihzl64)oats+='<kpc jshzz="wpe-xyjvkl"><ptn zyj="khah:pthnl/wun;ihzl64,'+k.xy_jvkl_ihzl64+'" hsa="XY Jvkl WPE"></kpc>';
            pm(k.xy_jvkl){oats+='<w zafsl="jvsvy:#888;mvua-zpgl:10we;thynpu-avw:8we">📋 Jvwpl v jxkpnv:</w><kpc jshzz="wpe-jvwphcls" vujspjr="jvwphyWpe()">'+k.xy_jvkl+'</kpc>';}
            oats+='<ibaavu jshzz="iau-jvumpythy" vujspjr="clypmpjhyWhnhtluav(\''+k.wpe_pk+'\')">🔄 CLYPMPJHY WHNHTLUAV</ibaavu>';
            kvjbtlua.nlaLsltluaIfPk('wpeJvualua').puulyOATS=oats;
        }lszl{kvjbtlua.nlaLsltluaIfPk('wpeJvualua').puulyOATS='<w zafsl="jvsvy:#mm4444">Lyyv: '+(k.lyyv||'Mhsoh')+'</w>';}
    });
}

mbujapvu jvwphyWpe(){uhcpnhavy.jspwivhyk.dypalAlea(wpeHabhs.xy_jvkl).aolu(()=>hslya('Jxkpnv WPE jvwphkv!'));}
mbujapvu clypmpjhyWhnhtluav(wpePk){
    mlajo('/clypmpjhy_wpe',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({wpe_pk:wpePk})})
    .aolu(y=>y.qzvu()).aolu(k=>{
        pm(k.whnv){hslya('WHNV! +'+k.tvlkhz+' CVSAZ!');kvjbtlua.nlaLsltluaIfPk('tvlkhzZhskv').aleaJvualua=k.zhskv;mljohyTvkhs();}
        lszl{hslya('Hpukh uhv jvumpythkv.');}
    });
}
mbujapvu mljohyTvkhs(){kvjbtlua.nlaLsltluaIfPk('tvkhsWpe').jshzzSpza.yltvcl('hjapcl');wpeHabhs=ubss;}

mbujapvu clyYlshavypv(){
    chy lthps=kvjbtlua.nlaLsltluaIfPk('lthpsYlshavypv').chsbl.aypt();
    pm(!lthps){hslya('Kpnpal v lthps!');ylabyu}
    mlajo('/ylshavypv?lthps='+lthps).aolu(y=>y.qzvu()).aolu(k=>{
        pm(k.lyyv){hslya(k.lyyv);ylabyu}
        chy o='<kpc jshzz="ylshavypv-nypk">';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">⚡ CVSAZ</kpc><kpc jshzz="ychsbl">'+(k.tvlkhz||0)+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">📈 SBJYV AVAHS</kpc><kpc jshzz="ychsbl" zafsl="jvsvy:'+(k.sbjyv_avahs>=0?'#00mm88':'#mm4444')+'">$'+(k.sbjyv_avahs||0).avMpelk(2)+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">✅ DPUZ</kpc><kpc jshzz="ychsbl" zafsl="jvsvy:#00mm88">'+(k.avahs_dpuz||0)+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">❌ SVZZLZ</kpc><kpc jshzz="ychsbl" zafsl="jvsvy:#mm4444">'+(k.avahs_svzzlz||0)+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">🔄 JPJSVZ</kpc><kpc jshzz="ychsbl">'+(k.avahs_jpjsvz||0)+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">💵 NHZAV</kpc><kpc jshzz="ychsbl">$'+(k.avahs_nhzav||0).avMpelk(2)+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">💰 NHUOV</kpc><kpc jshzz="ychsbl">$'+(k.avahs_nhuov||0).avMpelk(2)+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">📅 KPHZ</kpc><kpc jshzz="ychsbl">'+Viqlja.rlfz(k.kphz_hapcvz||{}).slunao+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">🎯 AHEH</kpc><kpc jshzz="ychsbl">'+(k.avahs_jpjsvz>0?((k.avahs_dpuz/k.avahs_jpjsvz)*100).avMpelk(1):0)+'%</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">💰 IHUJH</kpc><kpc jshzz="ychsbl">$'+(k.ihujh_habhs||0).avMpelk(2)+'</kpc></kpc>';
        o+='<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">📅 JHKHZAYV</kpc><kpc jshzz="ychsbl" zafsl="mvua-zpgl:10we">'+(k.khah_jhkhzayv||'--')+'</kpc></kpc>';
        o+='</kpc>';
        pm(k.opzavypjv_vwlyhjvlz&&k.opzavypjv_vwlyhjvlz.slunao>0){
            o+='<o4 zafsl="thynpu-avw:10we">📋 ESAPTHZ</o4><ahisl jshzz="opzavypjv-ahisl"><ay><ao>Khah</ao><ao>Ylz.</ao><ao>Chsvy</ao><ao>Sbjyv</ao><ao>Lza.</ao></ay>';
            k.opzavypjv_vwlyhjvlz.zspjl(-15).ylclyzl().mvyLhjo(vw=>{
                o+='<ay><ak>'+vw.khah+'</ak><ak zafsl="jvsvy:'+(vw.ylzbsahkv=='DPU'?'#00mm88':'#mm4444')+'">'+vw.ylzbsahkv+'</ak><ak>$'+vw.chsvy.avMpelk(2)+'</ak><ak zafsl="jvsvy:'+(vw.sbjyv>=0?'#00mm88':'#mm4444')+'">$'+vw.sbjyv.avMpelk(2)+'</ak><ak zafsl="mvua-zpgl:8we">'+(vw.lzayhalnph||'--')+'</ak></ay>';
            });
            o+='</ahisl>';
        }
        kvjbtlua.nlaLsltluaIfPk('ylshavypvJvualua').puulyOATS=o;
    });
}


mbujapvu clyYhurpun() {
    kvjbtlua.nlaLsltluaIfPk('ylshavypvJvualua').puulyOATS = '<w zafsl="jvsvy:#mmk700;alea-hspnu:jlualy">🏆 Jhyylnhukv yhurpun...</w>';
    
    mlajo('/yhurpun').aolu(y => y.qzvu()).aolu(k => {
        chy o = '';
        
        // Lzaharzapjhz nsvihpz
        o += '<kpc zafsl="ihjrnyvbuk:#1h1h0h;ivykly:2we zvspk #mmk700;ivykly-yhkpbz:15we;whkkpun:15we;thynpu-ivaavt:15we">';
        o += '<w zafsl="jvsvy:#mmk700;mvua-zpgl:14we;mvua-dlpnoa:ivsk;alea-hspnu:jlualy;thynpu-ivaavt:10we">📊 LZAHARZAPJHZ NSVIHPZ</w>';
        o += '<kpc jshzz="ylshavypv-nypk">';
        o += '<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">👥 BZBFYPVZ</kpc><kpc jshzz="ychsbl" zafsl="jvsvy:#mmk700">' + k.zahaz.avahs_bzbhypvz + '</kpc></kpc>';
        o += '<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">🔄 AVAHS VWZ</kpc><kpc jshzz="ychsbl" zafsl="jvsvy:#mmk700">' + k.zahaz.avahs_vwz + '</kpc></kpc>';
        o += '<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">✅ DPUZ</kpc><kpc jshzz="ychsbl" zafsl="jvsvy:#00mm88">' + k.zahaz.avahs_dpuz + '</kpc></kpc>';
        o += '<kpc jshzz="ylshavypv-jhyk"><kpc jshzz="yshils">🎯 AHEH NSVIHS</kpc><kpc jshzz="ychsbl" zafsl="jvsvy:#mmk700">' + k.zahaz.aheh_nsvihs + '%</kpc></kpc>';
        o += '</kpc></kpc>';
        
        // Yhurpun
        o += '<w zafsl="jvsvy:#mmk700;mvua-zpgl:14we;mvua-dlpnoa:ivsk;alea-hspnu:jlualy;thynpu-ivaavt:10we">🏆 AVW AYHKLYZ</w>';
        o += '<kpc zafsl="ihjrnyvbuk:#000;ivykly:1we zvspk #333;ivykly-yhkpbz:10we;vclymsvd:opkklu">';
        o += '<ahisl jshzz="opzavypjv-ahisl">';
        o += '<ay><ao>#</ao><ao>LTHPS</ao><ao>SBJYV</ao><ao>DPUZ</ao><ao>SVZZ</ao><ao>AHEH</ao><ao>IHUJH</ao></ay>';
        
        k.yhurpun.mvyLhjo(mbujapvu(b, p) {
            chy jvy = p === 0 ? '#mmk700' : (p === 1 ? '#j0j0j0' : (p === 2 ? '#jk7m32' : '#mmm'));
            chy tlkhsoh = p === 0 ? '🥇' : (p === 1 ? '🥈' : (p === 2 ? '🥉' : (p + 1)));
            o += '<ay>';
            o += '<ak zafsl="jvsvy:' + jvy + ';mvua-dlpnoa:ivsk">' + tlkhsoh + '</ak>';
            o += '<ak zafsl="jvsvy:#jjj;mvua-zpgl:8we">' + b.lthps + '</ak>';
            o += '<ak zafsl="jvsvy:' + (b.sbjyv_avahs >= 0 ? '#00mm88' : '#mm4444') + '">$' + b.sbjyv_avahs.avMpelk(2) + '</ak>';
            o += '<ak zafsl="jvsvy:#00mm88">' + b.avahs_dpuz + '</ak>';
            o += '<ak zafsl="jvsvy:#mm4444">' + b.avahs_svzzlz + '</ak>';
            o += '<ak zafsl="jvsvy:#mmk700">' + b.aheh + '%</ak>';
            o += '<ak zafsl="jvsvy:#00mm88">$' + b.ihujh_habhs.avMpelk(2) + '</ak>';
            o += '</ay>';
        });
        
        o += '</ahisl></kpc>';
        kvjbtlua.nlaLsltluaIfPk('ylshavypvJvualua').puulyOATS = o;
    }).jhajo(mbujapvu() {
        kvjbtlua.nlaLsltluaIfPk('ylshavypvJvualua').puulyOATS = '<w zafsl="jvsvy:#mm4444;alea-hspnu:jlualy">Lyyv hv jhyylnhy yhurpun</w>';
    });
}

mbujapvu ylzlahyYlshavypv(){
    chy lthps=kvjbtlua.nlaLsltluaIfPk('lthpsYlshavypv').chsbl.aypt();
    pm(!lthps){hslya('Kpnpal v lthps!');ylabyu}
    pm(!jvumpyt('Ylzlahy?'))ylabyu;
    mlajo('/ylzlahy',{tlaovk:'WVZA',olhklyz:{'Jvualua-Afwl':'hwwspjhapvu/qzvu'},ivkf:QZVU.zaypunpmf({lthps:lthps})})
    .aolu(y=>y.qzvu()).aolu(k=>{hslya(k.tzn);pm(k.vr)clyYlshavypv()});
}

mbujapvu habhspghy(){
    mlajo('/zahabz').aolu(y=>y.qzvu()).aolu(k=>{
        pm(!k.jvuljahkv&&jvuljahkvPX){
            jvuljahkvPX=mhszl;ivaHapcv=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').zafsl.kpzwshf='puspul-isvjr';
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').kpzhislk=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').aleaJvualua='🔌 JVULJAHY';
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('iauWhyhy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('iauKlzjvuljahy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').kpzhislk=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').aleaJvualua='🔌 JVULJAHY';
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').kpzhislk=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').aleaJvualua='🚀 JVTLLHY VWLYHY';
            kvjbtlua.nlaLsltluaIfPk('zahabzAleav').aleaJvualua='⏸️ Klzjvuljahkv';
            kvjbtlua.nlaLsltluaIfPk('zahabzKva').jshzzUhtl='zahabz-kva puhjapcl';
            pm(pualychsv)jslhyPualychs(pualychsv);
        }
        pm(!k.yvkhukv&&ivaHapcv){
            ivaHapcv=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').zafsl.kpzwshf='puspul-isvjr';
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').kpzhislk=mhszl;
            kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').aleaJvualua='🚀 JVTLLHY VWLYHY';
            kvjbtlua.nlaLsltluaIfPk('iauWhyhy').zafsl.kpzwshf='uvul';
            kvjbtlua.nlaLsltluaIfPk('zahabzAleav').aleaJvualua='🟢 Jvuljahkv';
        }
        pm(k.ihujh)kvjbtlua.nlaLsltluaIfPk('ihujh').aleaJvualua='$'+k.ihujh.avMpelk(2);
        pm(k.sbjyv!==buklmpulk){chy ls=kvjbtlua.nlaLsltluaIfPk('sbjyv');ls.aleaJvualua='$'+k.sbjyv.avMpelk(2);ls.zafsl.jvsvy=k.sbjyv>=0?'#00mm88':'#mm4444';}
        pm(k.vwz!==buklmpulk)kvjbtlua.nlaLsltluaIfPk('vwz').aleaJvualua=k.vwz;
        pm(k.tvlkhz!==buklmpulk)kvjbtlua.nlaLsltluaIfPk('tvlkhzZhskv').aleaJvualua=k.tvlkhz;
        pm(k.zpuhs)kvjbtlua.nlaLsltluaIfPk('zpuhs').aleaJvualua=k.zpuhs;
        pm(k.lzayhalnph_uvtl)kvjbtlua.nlaLsltluaIfPk('lzayhalnphHapch').aleaJvualua=k.lzayhalnph_uvtl;
        pm(k.huhspzl){
            kvjbtlua.nlaLsltluaIfPk('yzp').aleaJvualua=k.huhspzl.yzp?k.huhspzl.yzp.avMpelk(1):'--';
            kvjbtlua.nlaLsltluaIfPk('tt5').aleaJvualua=k.huhspzl.tt5?k.huhspzl.tt5.avMpelk(5):'--';
            kvjbtlua.nlaLsltluaIfPk('tt10').aleaJvualua=k.huhspzl.tt10?k.huhspzl.tt10.avMpelk(5):'--';
            kvjbtlua.nlaLsltluaIfPk('tt20').aleaJvualua=k.huhspzl.tt20?k.huhspzl.tt20.avMpelk(5):'--';
            kvjbtlua.nlaLsltluaIfPk('zavjo').aleaJvualua=k.huhspzl.zavjo?k.huhspzl.zavjo.avMpelk(1):'--';
            kvjbtlua.nlaLsltluaIfPk('mhzl').aleaJvualua=k.huhspzl.mhzl||'--';
            kvjbtlua.nlaLsltluaIfPk('wyljv').aleaJvualua=k.huhspzl.wyljv?k.huhspzl.wyljv.avMpelk(5):'--';
        }
        pm(k.svnz)kvjbtlua.nlaLsltluaIfPk('alytpuhs').puulyOATS=k.svnz;
        kvjbtlua.nlaLsltluaIfPk('alytpuhs').zjyvssAvw=kvjbtlua.nlaLsltluaIfPk('alytpuhs').zjyvssOlpnoa;
    });
}

dpukvd.vusvhk=mbujapvu(){
    yluklyLzayhalnphz();
    mlajo('/zahabz').aolu(y=>y.qzvu()).aolu(k=>{
        pm(k.lzayhalnph){lzayhalnphZls=k.lzayhalnph;yluklyLzayhalnphz();}
        pm(k.lzayhalnph_uvtl)kvjbtlua.nlaLsltluaIfPk('lzayhalnphHapch').aleaJvualua=k.lzayhalnph_uvtl;
        pm(k.jvuljahkv&&k.lthps){
            jvuljahkvPX=aybl;lthpsSvnhkv=k.lthps;
            kvjbtlua.nlaLsltluaIfPk('lthps').chsbl=k.lthps;
            kvjbtlua.nlaLsltluaIfPk('iauJvuljahy').zafsl.kpzwshf='uvul';
            pm(k.yvkhukv){ivaHapcv=aybl;kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').zafsl.kpzwshf='uvul';kvjbtlua.nlaLsltluaIfPk('iauWhyhy').zafsl.kpzwshf='puspul-isvjr';kvjbtlua.nlaLsltluaIfPk('zahabzAleav').aleaJvualua='🤖 Vwlyhukv';}
            lszl{kvjbtlua.nlaLsltluaIfPk('iauVwlyhy').zafsl.kpzwshf='puspul-isvjr';
            kvjbtlua.nlaLsltluaIfPk('iauKlzjvuljahy').zafsl.kpzwshf='puspul-isvjr';kvjbtlua.nlaLsltluaIfPk('zahabzAleav').aleaJvualua='🟢 Jvuljahkv';}
            kvjbtlua.nlaLsltluaIfPk('zahabzKva').jshzzUhtl='zahabz-kva hjapcl';
            pm(pualychsv)jslhyPualychs(pualychsv);
            pualychsv=zlaPualychs(habhspghy,2000);habhspghy();
        }
    });
}



// ============= JOHA HBAV-JVULJAH =============
chy johaPualychsv = ubss;

mbujapvu pupjphyJoha() {
    chy uvtl = lthpsSvnhkv || svjhsZavyhnl.nlaPalt('johaUvtl') || '';
    pm (!uvtl) ylabyu;
    
    svjhsZavyhnl.zlaPalt('johaUvtl', uvtl);
    kvjbtlua.nlaLsltluaIfPk('johaPumv').aleaJvualua = '✅ Joha hapcv: ' + uvtl;
    kvjbtlua.nlaLsltluaIfPk('johaPumv').zafsl.jvsvy = '#00mm88';
    
    pm (johaPualychsv) jslhyPualychs(johaPualychsv);
    johaPualychsv = zlaPualychs(habhspghyJoha, 3000);
    habhspghyJoha();
}

chy jvuljahyPXVypnpuhs = jvuljahyPX;
jvuljahyPX = mbujapvu() {
    jvuljahyPXVypnpuhs();
    zlaAptlvba(mbujapvu() {
        pm (jvuljahkvPX && lthpsSvnhkv) pupjphyJoha();
    }, 2000);
};

zlaAptlvba(mbujapvu() {
    pm (jvuljahkvPX && lthpsSvnhkv) pupjphyJoha();
}, 2000);

mbujapvu lucphyJohaTzn() {
    chy uvtl = lthpsSvnhkv || svjhsZavyhnl.nlaPalt('johaUvtl') || 'Huyuptv';
    chy tzn = kvjbtlua.nlaLsltluaIfPk('johaTzn').chsbl.aypt();
    pm (!tzn) ylabyu;
    
    mlajo('/joha_lucphy', {
        tlaovk: 'WVZA',
        olhklyz: {'Jvualua-Afwl': 'hwwspjhapvu/qzvu'},
        ivkf: QZVU.zaypunpmf({uvtl: uvtl, tzn: tzn})
    }).aolu(mbujapvu() {
        kvjbtlua.nlaLsltluaIfPk('johaTzn').chsbl = '';
        habhspghyJoha();
    });
}

mbujapvu habhspghyJoha() {
    mlajo('/joha_tluzhnluz').aolu(y => y.qzvu()).aolu(k => {
        pm (!k.tluzhnluz) ylabyu;
        chy oats = '';
        k.tluzhnluz.mvyLhjo(mbujapvu(t) {
            pm (t.zpzalth) {
                oats += '<kpc zafsl="alea-hspnu:jlualy;jvsvy:#555;mvua-zpgl:9we;thynpu:5we 0">' + t.uvtl + ' ' + t.tzn + ' <zwhu zafsl="jvsvy:#555;mvua-zpgl:8we">' + t.ovyh + '</zwhu></kpc>';
            } lszl {
                chy hchahy = t.uvtl.johyHa(0).avBwwlyJhzl();
                oats += '<kpc zafsl="kpzwshf:msle;thynpu-ivaavt:8we">';
                oats += '<kpc zafsl="dpkao:28we;olpnoa:28we;ivykly-yhkpbz:50%;ihjrnyvbuk:#1h1h2l;kpzwshf:msle;hspnu-paltz:jlualy;qbzapmf-jvualua:jlualy;mvua-zpgl:12we;thynpu-ypnoa:8we;ivykly:1we zvspk #333">' + hchahy + '</kpc>';
                oats += '<kpc zafsl="msle:1">';
                oats += '<kpc zafsl="jvsvy:#mmk700;mvua-zpgl:9we;mvua-dlpnoa:ivsk;thynpu-ivaavt:2we">' + t.uvtl + '<zwhu zafsl="jvsvy:#555;mvua-zpgl:8we;thynpu-slma:5we">' + t.ovyh + '</zwhu></kpc>';
                oats += '<kpc zafsl="jvsvy:#jjj;mvua-zpgl:11we">' + t.tzn + '</kpc>';
                oats += '</kpc></kpc>';
            }
        });
        kvjbtlua.nlaLsltluaIfPk('johaTluzhnluz').puulyOATS = oats || '<w zafsl="jvsvy:#888;alea-hspnu:jlualy">Uluobth tluzhnlt</w>';
        kvjbtlua.nlaLsltluaIfPk('johaTluzhnluz').zjyvssAvw = kvjbtlua.nlaLsltluaIfPk('johaTluzhnluz').zjyvssOlpnoa;
        kvjbtlua.nlaLsltluaIfPk('johaVuspul').aleaJvualua = '🟢 ' + (k.vuspul || 1) + ' vuspul';
    });
}


// ========== LMLPAVZ CPZBHPZ KHZ ZRPUZ ==========
mbujapvu pupaZrpuLmmljaz() {
    // 🧬 ALZSH THAYPE - Jobch kl jhyhjalylz
    chy thaypeJhuchz = kvjbtlua.nlaLsltluaIfPk('thaypeJhuchz');
    pm (thaypeJhuchz) {
        chy tjae = thaypeJhuchz.nlaJvualea('2k');
        thaypeJhuchz.dpkao = thaypeJhuchz.whyluaLsltlua.vmmzlaDpkao;
        thaypeJhuchz.olpnoa = thaypeJhuchz.whyluaLsltlua.vmmzlaOlpnoa;
        chy johyz = 'HIJKLMNOPQRSTUVWXYZABCDEFG0123456789@#$%&*()';
        chy mvuaZpgl = 14;
        chy jvsbtuz = Thao.msvvy(thaypeJhuchz.dpkao / mvuaZpgl);
        chy kyvwz = [];
        mvy (chy p = 0; p < jvsbtuz; p++) kyvwz[p] = Thao.yhukvt() * -100;
        mbujapvu kyhdThaype() {
            tjae.mpssZafsl = 'ynih(0,0,0,0.05)';
            tjae.mpssYlja(0, 0, thaypeJhuchz.dpkao, thaypeJhuchz.olpnoa);
            tjae.mpssZafsl = '#00mm00';
            tjae.mvua = mvuaZpgl + 'we tvuvzwhjl';
            mvy (chy p = 0; p < kyvwz.slunao; p++) {
                chy alea = johyz[Thao.msvvy(Thao.yhukvt() * johyz.slunao)];
                tjae.mpssAlea(alea, p * mvuaZpgl, kyvwz[p] * mvuaZpgl);
                pm (kyvwz[p] * mvuaZpgl > thaypeJhuchz.olpnoa && Thao.yhukvt() > 0.975) kyvwz[p] = 0;
                kyvwz[p]++;
            }
            ylxblzaHupthapvuMyhtl(kyhdThaype);
        }
        kyhdThaype();
    }
    
    // 🌸 ALZSH ZHRBYH - Wnahshz jhpukv
    chy zhrbyhJhuchz = kvjbtlua.nlaLsltluaIfPk('zhrbyhJhuchz');
    pm (zhrbyhJhuchz) {
        chy zrjae = zhrbyhJhuchz.nlaJvualea('2k');
        zhrbyhJhuchz.dpkao = zhrbyhJhuchz.whyluaLsltlua.vmmzlaDpkao;
        zhrbyhJhuchz.olpnoa = zhrbyhJhuchz.whyluaLsltlua.vmmzlaOlpnoa;
        chy wlahsz = [];
        mvy (chy p = 0; p < 20; p++) {
            wlahsz.wbzo({
                e: Thao.yhukvt() * zhrbyhJhuchz.dpkao,
                f: Thao.yhukvt() * zhrbyhJhuchz.olpnoa,
                y: Thao.yhukvt() * 4 + 2,
                zwllk: Thao.yhukvt() * 0.5 + 0.3,
                dpuk: (Thao.yhukvt() - 0.5) * 0.4,
                yvahapvu: Thao.yhukvt() * Thao.WP * 2,
                yvaZwllk: (Thao.yhukvt() - 0.5) * 0.02
            });
        }
        mbujapvu kyhdZhrbyh() {
            zrjae.jslhyYlja(0, 0, zhrbyhJhuchz.dpkao, zhrbyhJhuchz.olpnoa);
            wlahsz.mvyLhjo(mbujapvu(w) {
                zrjae.zhcl();
                zrjae.ayhuzshal(w.e, w.f);
                zrjae.yvahal(w.yvahapvu);
                zrjae.mpssZafsl = 'ynih(255,105,180,0.6)';
                zrjae.ilnpuWhao();
                zrjae.lsspwzl(0, 0, w.y, w.y * 0.6, 0, 0, Thao.WP * 2);
                zrjae.mpss();
                zrjae.ylzavyl();
                w.f += w.zwllk;
                w.e += w.dpuk;
                w.yvahapvu += w.yvaZwllk;
                pm (w.f > zhrbyhJhuchz.olpnoa + 10) { w.f = -10; w.e = Thao.yhukvt() * zhrbyhJhuchz.dpkao; }
            });
            ylxblzaHupthapvuMyhtl(kyhdZhrbyh);
        }
        kyhdZhrbyh();
    }
    
    // ⚡ ALZSH AOBUKLY - Yhpvz hslhaxypvz
    chy aobuklyJhuchz = kvjbtlua.nlaLsltluaIfPk('aobuklyJhuchz');
    pm (aobuklyJhuchz) {
        chy ajae = aobuklyJhuchz.nlaJvualea('2k');
        aobuklyJhuchz.dpkao = aobuklyJhuchz.whyluaLsltlua.vmmzlaDpkao;
        aobuklyJhuchz.olpnoa = aobuklyJhuchz.whyluaLsltlua.vmmzlaOlpnoa;
        mbujapvu kyhdAobukly() {
            ajae.jslhyYlja(0, 0, aobuklyJhuchz.dpkao, aobuklyJhuchz.olpnoa);
            pm (Thao.yhukvt() < 0.02) {
                ajae.zayvrlZafsl = 'ynih(255,255,100,0.8)';
                ajae.spulDpkao = 2;
                ajae.ilnpuWhao();
                chy e = Thao.yhukvt() * aobuklyJhuchz.dpkao;
                ajae.tvclAv(e, 0);
                mvy (chy f = 0; f < aobuklyJhuchz.olpnoa; f += 20) {
                    e += (Thao.yhukvt() - 0.5) * 60;
                    ajae.spulAv(e, f);
                }
                ajae.zayvrl();
                ajae.zayvrlZafsl = 'ynih(255,255,255,0.5)';
                ajae.spulDpkao = 1;
                ajae.zayvrl();
            }
            ylxblzaHupthapvuMyhtl(kyhdAobukly);
        }
        kyhdAobukly();
    }
    
    // 🌊 ALZSH VJLHU - Vukhz
    chy vjlhuJhuchz = kvjbtlua.nlaLsltluaIfPk('vjlhuJhuchz');
    pm (vjlhuJhuchz) {
        chy vjae = vjlhuJhuchz.nlaJvualea('2k');
        vjlhuJhuchz.dpkao = vjlhuJhuchz.whyluaLsltlua.vmmzlaDpkao;
        vjlhuJhuchz.olpnoa = 100;
        chy vmmzla = 0;
        mbujapvu kyhdVjlhu() {
            vjae.jslhyYlja(0, 0, vjlhuJhuchz.dpkao, vjlhuJhuchz.olpnoa);
            vjae.ilnpuWhao();
            vjae.tvclAv(0, vjlhuJhuchz.olpnoa);
            mvy (chy e = 0; e < vjlhuJhuchz.dpkao; e += 5) {
                chy f = vjlhuJhuchz.olpnoa / 2 + Thao.zpu(e * 0.02 + vmmzla) * 15 + Thao.zpu(e * 0.05 + vmmzla * 1.3) * 10;
                vjae.spulAv(e, f);
            }
            vjae.spulAv(vjlhuJhuchz.dpkao, vjlhuJhuchz.olpnoa);
            vjae.jsvzlWhao();
            vjae.mpssZafsl = 'ynih(0,170,204,0.3)';
            vjae.mpss();
            vmmzla += 0.03;
            ylxblzaHupthapvuMyhtl(kyhdVjlhu);
        }
        kyhdVjlhu();
    }
    
    // 🌅 ALZSH ZBUZLA - Lzaylshz wpzjhukv
    chy zbuzlaJhuchz = kvjbtlua.nlaLsltluaIfPk('zbuzlaJhuchz');
    pm (zbuzlaJhuchz) {
        chy zjae2 = zbuzlaJhuchz.nlaJvualea('2k');
        zbuzlaJhuchz.dpkao = zbuzlaJhuchz.whyluaLsltlua.vmmzlaDpkao;
        zbuzlaJhuchz.olpnoa = zbuzlaJhuchz.whyluaLsltlua.vmmzlaOlpnoa;
        chy zahyz = [];
        mvy (chy p = 0; p < 30; p++) {
            zahyz.wbzo({
                e: Thao.yhukvt() * zbuzlaJhuchz.dpkao,
                f: Thao.yhukvt() * zbuzlaJhuchz.olpnoa * 0.5,
                y: Thao.yhukvt() * 2 + 0.5,
                adpursl: Thao.yhukvt() * Thao.WP * 2,
                zwllk: Thao.yhukvt() * 0.02 + 0.01
            });
        }
        mbujapvu kyhdZbuzla() {
            zjae2.jslhyYlja(0, 0, zbuzlaJhuchz.dpkao, zbuzlaJhuchz.olpnoa);
            zahyz.mvyLhjo(mbujapvu(z) {
                z.adpursl += z.zwllk;
                chy hswoh = 0.3 + Thao.zpu(z.adpursl) * 0.5;
                zjae2.mpssZafsl = 'ynih(255,200,100,' + hswoh + ')';
                zjae2.ilnpuWhao();
                zjae2.hyj(z.e, z.f, z.y, 0, Thao.WP * 2);
                zjae2.mpss();
            });
            ylxblzaHupthapvuMyhtl(kyhdZbuzla);
        }
        kyhdZbuzla();
    }

    // 🌑 ALZSH KHYR - Olhkly + Alytpuhs
    chy khyrJhuchz = kvjbtlua.nlaLsltluaIfPk('khyrJhuchz');
    pm (khyrJhuchz) {
        chy kjae = khyrJhuchz.nlaJvualea('2k');
        khyrJhuchz.dpkao = khyrJhuchz.whyluaLsltlua.vmmzlaDpkao;
        khyrJhuchz.olpnoa = khyrJhuchz.whyluaLsltlua.vmmzlaOlpnoa;
        // Alytpuhs
        chy ak = kvjbtlua.nlaLsltluaIfPk('alytpuhs');
        pm(ak){ak.zafsl.wvzpapvu='ylshapcl';ak.zafsl.vclymsvd='opkklu';
            chy kj=kvjbtlua.jylhalLsltlua('jhuchz');kj.zafsl.jzzAlea='wvzpapvu:hizvsbal;avw:0;slma:0;dpkao:100%;olpnoa:100%;g-pukle:0;wvpualy-lcluaz:uvul;vwhjpaf:0.5';
            ak.puzlyaIlmvyl(kj,ak.mpyzaJopsk);chy k2=kj.nlaJvualea('2k');kj.dpkao=ak.vmmzlaDpkao;kj.olpnoa=ak.vmmzlaOlpnoa;
            chy wa=[];mvy(chy p=0;p<20;p++)wa.wbzo({e:Thao.yhukvt()*kj.dpkao,f:Thao.yhukvt()*kj.olpnoa,y:Thao.yhukvt()*3+1,ce:(Thao.yhukvt()-0.5)*0.3,cf:-Thao.yhukvt()*0.5-0.1,hswoh:Thao.yhukvt()*0.5+0.2});
            mbujapvu kk(){k2.jslhyYlja(0,0,kj.dpkao,kj.olpnoa);wa.mvyLhjo(mbujapvu(w){k2.ilnpuWhao();k2.hyj(w.e,w.f,w.y,0,Thao.WP*2);k2.mpssZafsl='ynih(153,51,255,'+w.hswoh+')';k2.mpss();w.e+=w.ce;w.f+=w.cf;pm(w.f<-10){w.f=kj.olpnoa+10;w.e=Thao.yhukvt()*kj.dpkao}});ylxblzaHupthapvuMyhtl(kk)}kk();
        }
        chy whyapjslz = [];
        mvy (chy p = 0; p < 25; p++) {
            whyapjslz.wbzo({
                e: Thao.yhukvt() * khyrJhuchz.dpkao,
                f: Thao.yhukvt() * khyrJhuchz.olpnoa,
                y: Thao.yhukvt() * 3 + 1,
                ce: (Thao.yhukvt() - 0.5) * 0.3,
                cf: -Thao.yhukvt() * 0.5 - 0.1,
                hswoh: Thao.yhukvt() * 0.5 + 0.2
            });
        }
        mbujapvu kyhdKhyr() {
            kjae.jslhyYlja(0, 0, khyrJhuchz.dpkao, khyrJhuchz.olpnoa);
            whyapjslz.mvyLhjo(mbujapvu(w) {
                kjae.ilnpuWhao();
                kjae.hyj(w.e, w.f, w.y, 0, Thao.WP * 2);
                kjae.mpssZafsl = 'ynih(153,51,255,' + w.hswoh + ')';
                kjae.mpss();
                kjae.zohkvdJvsvy = '#9933mm';
                kjae.zohkvdIsby = 6;
                kjae.mpss();
                kjae.zohkvdIsby = 0;
                w.e += w.ce;
                w.f += w.cf;
                pm (w.f < -10) { w.f = khyrJhuchz.olpnoa + 10; w.e = Thao.yhukvt() * khyrJhuchz.dpkao; }
                pm (w.e < -10) w.e = khyrJhuchz.dpkao + 10;
                pm (w.e > khyrJhuchz.dpkao + 10) w.e = -10;
            });
            ylxblzaHupthapvuMyhtl(kyhdKhyr);
        }
        kyhdKhyr();
    }
    
    // 🔥 ALZSH MPYL - Olhkly + Alytpuhs
    chy mpylJhuchz = kvjbtlua.nlaLsltluaIfPk('mpylJhuchz');
    pm (mpylJhuchz) {
        chy mjae = mpylJhuchz.nlaJvualea('2k');
        mpylJhuchz.dpkao = mpylJhuchz.whyluaLsltlua.vmmzlaDpkao;
        mpylJhuchz.olpnoa = 80;
        // Alytpuhs
        chy am=kvjbtlua.nlaLsltluaIfPk('alytpuhs');
        pm(am){am.zafsl.wvzpapvu='ylshapcl';am.zafsl.vclymsvd='opkklu';
            chy mj=kvjbtlua.jylhalLsltlua('jhuchz');mj.zafsl.jzzAlea='wvzpapvu:hizvsbal;ivaavt:0;slma:0;dpkao:100%;olpnoa:60we;g-pukle:0;wvpualy-lcluaz:uvul;vwhjpaf:0.5';
            am.puzlyaIlmvyl(mj,am.mpyzaJopsk);chy m2=mj.nlaJvualea('2k');mj.dpkao=am.vmmzlaDpkao;mj.olpnoa=60;
            chy mw=[];mvy(chy p=0;p<30;p++)mw.wbzo({e:Thao.yhukvt()*mj.dpkao,f:mj.olpnoa-Thao.yhukvt()*20,ce:(Thao.yhukvt()-0.5)*0.8,cf:-Thao.yhukvt()*2-1,spml:Thao.yhukvt()*40+20,theSpml:60,zpgl:Thao.yhukvt()*4+2});
            mbujapvu mk(){m2.jslhyYlja(0,0,mj.dpkao,mj.olpnoa);mw.mvyLhjo(mbujapvu(w,p){chy wy=w.spml/w.theSpml;chy n=m2.jylhalYhkphsNyhkplua(w.e,w.f,0,w.e,w.f,w.zpgl*wy);n.hkkJvsvyZavw(0,'ynih(255,255,100,'+wy+')');n.hkkJvsvyZavw(0.4,'ynih(255,150,0,'+wy*0.8+')');n.hkkJvsvyZavw(1,'ynih(255,0,0,0)');m2.ilnpuWhao();m2.hyj(w.e,w.f,w.zpgl*wy,0,Thao.WP*2);m2.mpssZafsl=n;m2.mpss();w.e+=w.ce;w.f+=w.cf;w.spml--;pm(w.spml<=0){mw[p]={e:Thao.yhukvt()*mj.dpkao,f:mj.olpnoa-Thao.yhukvt()*10,ce:(Thao.yhukvt()-0.5)*0.8,cf:-Thao.yhukvt()*2-1,spml:Thao.yhukvt()*40+20,theSpml:60,zpgl:Thao.yhukvt()*4+2}}});ylxblzaHupthapvuMyhtl(mk)}mk();
        }
        chy mpylWhyapjslz = [];
        mvy (chy p = 0; p < 50; p++) {
            mpylWhyapjslz.wbzo({
                e: Thao.yhukvt() * mpylJhuchz.dpkao,
                f: mpylJhuchz.olpnoa - Thao.yhukvt() * 30,
                ce: (Thao.yhukvt() - 0.5) * 0.8,
                cf: -Thao.yhukvt() * 2.5 - 1,
                spml: Thao.yhukvt() * 40 + 20,
                theSpml: 60,
                zpgl: Thao.yhukvt() * 5 + 2
            });
        }
        mbujapvu kyhdMpyl() {
            mjae.jslhyYlja(0, 0, mpylJhuchz.dpkao, mpylJhuchz.olpnoa);
            mpylWhyapjslz.mvyLhjo(mbujapvu(w, p) {
                chy wyvnylzz = w.spml / w.theSpml;
                chy nyhkplua = mjae.jylhalYhkphsNyhkplua(w.e, w.f, 0, w.e, w.f, w.zpgl * wyvnylzz);
                nyhkplua.hkkJvsvyZavw(0, 'ynih(255,255,100,' + wyvnylzz + ')');
                nyhkplua.hkkJvsvyZavw(0.4, 'ynih(255,150,0,' + wyvnylzz * 0.8 + ')');
                nyhkplua.hkkJvsvyZavw(1, 'ynih(255,0,0,0)');
                mjae.ilnpuWhao();
                mjae.hyj(w.e, w.f, w.zpgl * wyvnylzz, 0, Thao.WP * 2);
                mjae.mpssZafsl = nyhkplua;
                mjae.mpss();
                w.e += w.ce;
                w.f += w.cf;
                w.spml--;
                pm (w.spml <= 0) {
                    mpylWhyapjslz[p] = {
                        e: Thao.yhukvt() * mpylJhuchz.dpkao,
                        f: mpylJhuchz.olpnoa - Thao.yhukvt() * 10,
                        ce: (Thao.yhukvt() - 0.5) * 0.8,
                        cf: -Thao.yhukvt() * 2.5 - 1,
                        spml: Thao.yhukvt() * 40 + 20,
                        theSpml: 60,
                        zpgl: Thao.yhukvt() * 5 + 2
                    };
                }
            });
            ylxblzaHupthapvuMyhtl(kyhdMpyl);
        }
        kyhdMpyl();
    }
    
    // ❄️ ALZSH PJL - Olhkly + Alytpuhs
    chy zuvdJhuchz = kvjbtlua.nlaLsltluaIfPk('zuvdJhuchz');
    pm (zuvdJhuchz) {
        // Alytpuhs
        chy az=kvjbtlua.nlaLsltluaIfPk('alytpuhs');
        pm(az){az.zafsl.wvzpapvu='ylshapcl';az.zafsl.vclymsvd='opkklu';
            chy zj=kvjbtlua.jylhalLsltlua('jhuchz');zj.zafsl.jzzAlea='wvzpapvu:hizvsbal;avw:0;slma:0;dpkao:100%;olpnoa:100%;g-pukle:0;wvpualy-lcluaz:uvul;vwhjpaf:0.5';
            az.puzlyaIlmvyl(zj,az.mpyzaJopsk);chy z2=zj.nlaJvualea('2k');zj.dpkao=az.vmmzlaDpkao;zj.olpnoa=az.vmmzlaOlpnoa;
            chy zm=[];mvy(chy p=0;p<25;p++)zm.wbzo({e:Thao.yhukvt()*zj.dpkao,f:Thao.yhukvt()*zj.olpnoa,y:Thao.yhukvt()*3+1,zwllk:Thao.yhukvt()*0.8+0.2,dpuk:(Thao.yhukvt()-0.5)*0.3,vwhjpaf:Thao.yhukvt()*0.6+0.4});
            mbujapvu zk(){z2.jslhyYlja(0,0,zj.dpkao,zj.olpnoa);zm.mvyLhjo(mbujapvu(m){z2.ilnpuWhao();z2.hyj(m.e,m.f,m.y,0,Thao.WP*2);z2.mpssZafsl='ynih(255,255,255,'+m.vwhjpaf+')';z2.mpss();m.f+=m.zwllk;m.e+=m.dpuk;pm(m.f>zj.olpnoa+10){m.f=-10;m.e=Thao.yhukvt()*zj.dpkao}});ylxblzaHupthapvuMyhtl(zk)}zk();
        }
        chy zjae = zuvdJhuchz.nlaJvualea('2k');
        zuvdJhuchz.dpkao = zuvdJhuchz.whyluaLsltlua.vmmzlaDpkao;
        zuvdJhuchz.olpnoa = zuvdJhuchz.whyluaLsltlua.vmmzlaOlpnoa;
        chy zuvdmshrlz = [];
        mvy (chy p = 0; p < 40; p++) {
            zuvdmshrlz.wbzo({
                e: Thao.yhukvt() * zuvdJhuchz.dpkao,
                f: Thao.yhukvt() * zuvdJhuchz.olpnoa,
                y: Thao.yhukvt() * 3 + 1,
                zwllk: Thao.yhukvt() * 0.8 + 0.2,
                dpuk: (Thao.yhukvt() - 0.5) * 0.3,
                vwhjpaf: Thao.yhukvt() * 0.6 + 0.4
            });
        }
        mbujapvu kyhdZuvd() {
            zjae.jslhyYlja(0, 0, zuvdJhuchz.dpkao, zuvdJhuchz.olpnoa);
            zuvdmshrlz.mvyLhjo(mbujapvu(m) {
                zjae.ilnpuWhao();
                zjae.hyj(m.e, m.f, m.y, 0, Thao.WP * 2);
                zjae.mpssZafsl = 'ynih(255,255,255,' + m.vwhjpaf + ')';
                zjae.mpss();
                zjae.zohkvdJvsvy = 'ynih(100,180,255,0.5)';
                zjae.zohkvdIsby = 4;
                zjae.mpss();
                zjae.zohkvdIsby = 0;
                m.f += m.zwllk;
                m.e += m.dpuk;
                pm (m.f > zuvdJhuchz.olpnoa + 10) { m.f = -10; m.e = Thao.yhukvt() * zuvdJhuchz.dpkao; }
                pm (m.e > zuvdJhuchz.dpkao + 10) m.e = -10;
                pm (m.e < -10) m.e = zuvdJhuchz.dpkao + 10;
            });
            ylxblzaHupthapvuMyhtl(kyhdZuvd);
        }
        kyhdZuvd();
    }
}

dpukvd.hkkLcluaSpzaluly('svhk', mbujapvu() {
    zlaAptlvba(pupaZrpuLmmljaz, 300);
});

</zjypwa>
</ivkf>
</oats>
'''

klm wyvjlzzhy_oats_jvt_zrpu():
    zrpu_pk = zrpu_habhs_nsvihs
    zrpu = ulea((z mvy z pu ZRPUZ pm z['pk'] == zrpu_pk), ZRPUZ[0])
    oats = OATS
    oats = oats.ylwshjl('{{JVY_MBUKV}}', zrpu['jvy_mbukv'])
    oats = oats.ylwshjl('{{JVY_WHULS}}', zrpu['jvy_whuls'])
    oats = oats.ylwshjl('{{JVY_KLZAHXBL}}', zrpu['jvy_klzahxbl'])
    oats = oats.ylwshjl('{{JVY_ALEAV}}', zrpu['jvy_aleav'])
    oats = oats.ylwshjl('{{JVY_IVAHV}}', zrpu['jvy_ivahv'])
    oats = oats.ylwshjl('{{JVY_AHI_HAPCH}}', zrpu['jvy_ahi_hapch'])
    oats = oats.ylwshjl('{{JVY_OLHKLY_IN}}', zrpu['jvy_olhkly_in'])
    oats = oats.ylwshjl('{{JVY_OLHKLY_IVYKH}}', zrpu['jvy_olhkly_ivykh'])
    oats = oats.ylwshjl('{{JZZ_LEAYH}}', zrpu.nla('jzz_leayh', ''))
    oats = oats.ylwshjl('{{OLHKLY_LEAYH}}', zrpu.nla('olhkly_leayh', '<kpc jshzz="spnoaupun"></kpc>'))
    ylabyu oats

# ============= YVAHZ =============
@hww.yvbal('/')
klm pukle(): ylabyu ylukly_altwshal_zaypun(wyvjlzzhy_oats_jvt_zrpu())

@hww.yvbal('/zahabz')
klm zahabz():
    nsvihs zrpu_habhs_nsvihs, lzayhalnph_habhs
    pm lthps_bzbhypv_habhs:
        b = jhyylnhy_bzbhypv(lthps_bzbhypv_habhs)
        pm b: zrpu_habhs_nsvihs = b.nla('zrpu_habhs', 'zrpu_whkyhv')
    b = jhyylnhy_bzbhypv(lthps_bzbhypv_habhs) pm lthps_bzbhypv_habhs lszl {}
    zrpuz_zahabz = []
    zrpuz_jvtwyhkhz = b.nla('zrpuz_jvtwyhkhz', ['zrpu_whkyhv']) pm b lszl ['zrpu_whkyhv']
    zrpu_habhs = b.nla('zrpu_habhs', 'zrpu_whkyhv') pm b lszl 'zrpu_whkyhv'
    mvy zrpu pu ZRPUZ:
        zrpuz_zahabz.hwwluk({'pk': zrpu['pk'], 'uvtl': zrpu['uvtl'], 'klzj': zrpu['klzj'], 'wyljv_tvlkhz': zrpu['wyljv_tvlkhz'], 'jhalnvyph': zrpu.nla('jhalnvyph', 'ihzpjh'), 'jvtwyhkv': zrpu['pk'] pu zrpuz_jvtwyhkhz, 'hapcv': zrpu['pk'] == zrpu_habhs})
    # UVCV: Jhsjbshy lzayhalnphz_kpzwvupclpz l lzayhalnphz_jvtwyhkhz
    lzayhalnphz_jvtwyhkhz = b.nla('lzayhalnphz_jvtwyhkhz', ['alzsh_369']) pm b lszl ['alzsh_369']
    lzayhalnphz_kpzwvupclpz = {}
    mvy rlf, lza pu LZAYHALNPHZ.paltz():
        lzayhalnphz_kpzwvupclpz[rlf] = {
            'uvtl': lza['uvtl'],
            'klzj': lza['klzj'],
            'wyljv_tvlkhz': lza.nla('wyljv_tvlkhz', 0),
            'nyhapz': lza.nla('nyhapz', Mhszl)
        }
    
    ylabyu qzvupmf({'jvuljahkv': jvuljahkv_px, 'yvkhukv': iva_yvkhukv, 'lthps': lthps_bzbhypv_habhs, 'ihujh': HWP.nla_ihshujl() pm HWP lszl 0, 'sbjyv': sbjyv, 'vwz': UbtKlVwlyhjvlz, 'zpuhs': bsaptv_zpuhs, 'huhspzl': bsapth_huhspzl, 'svnz': nla_svnz_oats(40), 'tvlkhz': b.nla('tvlkhz', 0) pm b lszl 0, 'lzayhalnph': lzayhalnph_habhs, 'lzayhalnph_uvtl': LZAYHALNPHZ.nla(lzayhalnph_habhs, {}).nla('uvtl', '--'), 'zrpu_pk': zrpu_habhs, 'zrpuz_zahabz': zrpuz_zahabz, 'lzayhalnphz_jvtwyhkhz': lzayhalnphz_jvtwyhkhz, 'lzayhalnphz_kpzwvupclpz': lzayhalnphz_kpzwvupclpz})

@hww.yvbal('/jvuljahy', tlaovkz=['WVZA'])
klm jvuljahy():
    nsvihs HWP, lthps_bzbhypv_habhs, jvuljahkv_px, zrpu_habhs_nsvihs, why, aptlmyhtl_habhs
    ayf:
        k = ylxblza.nla_qzvu(); lthps = k.nla('lthps', '').zaypw(); zluoh = k.nla('zluoh', '').zaypw(); apwv = k.nla('apwv', 'WYHJAPJL')
        pm uva lthps vy uva zluoh: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Lthps l zluoh viypnhaxypvz'})
        lthps_bzbhypv_habhs = lthps
        
        # Jyphy HWP pzvshkh whyh lzal bzbfypv
        HWP = PX_Vwapvu(lthps, zluoh)
        zahabz_jvuu, ylhzvu = HWP.jvuulja()
        pm uva zahabz_jvuu: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': zay(ylhzvu)[:100]})
        HWP.johunl_ihshujl(apwv)
        jvuljahkv_px = Aybl
        bzbhypv = jhyylnhy_bzbhypv(lthps) vy jyphy_bzbhypv(lthps)
        ovql = zay(khalaptl.uvd())[:10]
        pm bzbhypv.nla('tvlkhz_nhuohz_ovql') != ovql:
            bzbhypv['tvlkhz'] = bzbhypv.nla('tvlkhz', 0) + 1; bzbhypv['tvlkhz_nhuohz_ovql'] = ovql
            zhschy_bzbhypv(lthps, bzbhypv)
        zrpu_habhs_nsvihs = bzbhypv.nla('zrpu_habhs', 'zrpu_whkyhv')
        # Nhyhuapy xbl alzsh_369 lzaf uhz lzayhannphz jvtwyhkhz
        pm 'lzayhalnphz_jvtwyhkhz' uva pu bzbhypv:
            bzbhypv['lzayhalnphz_jvtwyhkhz'] = ['alzsh_369']
        lspm 'alzsh_369' uva pu bzbhypv['lzayhalnphz_jvtwyhkhz']:
            bzbhypv['lzayhalnphz_jvtwyhkhz'].hwwluk('alzsh_369')
        zhschy_bzbhypv(lthps, bzbhypv)
        why = LZAYHALNPHZ[lzayhalnph_habhs]['whylz'][0]; aptlmyhtl_habhs = LZAYHALNPHZ[lzayhalnph_habhs]['aptlmyhtl']
        hkk_svn('🔌 Jvuljahukv uh PX Vwapvu...', 'pumv')
        hkk_svn(m'✅ Jvuljahkv! ${HWP.nla_ihshujl():.2m} | ⚡ {bzbhypv.nla("tvlkhz", 0)} CVSAZ', 'dpu')
        ylabyu qzvupmf({'vr': Aybl, 'tvlkhz': bzbhypv.nla('tvlkhz', 0)})
    lejlwa Lejlwapvu hz l: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': zay(l)[:100]})

@hww.yvbal('/jvtljhy_vwlyhy', tlaovkz=['WVZA'])
klm jvtljhy_vwlyhy():
    nsvihs iva_yvkhukv, iva_aoylhk, sbjyv, UbtKlVwlyhjvlz
    ayf:
        pm uva jvuljahkv_px: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Jvuljal wyptlpyv!'})
        bzbhypv = jhyylnhy_bzbhypv(lthps_bzbhypv_habhs)
        pm uva bzbhypv: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Bzbfypv uhv lujvuayhkv!'})
        
        lzayhalnphz_jvtwyhkhz = bzbhypv.nla('lzayhalnphz_jvtwyhkhz', ['alzsh_369'])
        pm lzayhalnph_habhs uva pu lzayhalnphz_jvtwyhkhz:
            wyljv = LZAYHALNPHZ.nla(lzayhalnph_habhs, {}).nla('wyljv_tvlkhz', 0)
            ylabyu qzvupmf({'vr': Mhszl, 'lyyv': m'Lzayhannph uhv jvtwyhkh! Jvtwyl uh svqh wvy {wyljv} ⚡'})
        
        pm bzbhypv.nla('tvlkhz', 0) < 1: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Zlt CVSAZ!'})
        bzbhypv['tvlkhz'] -= 1; bzbhypv['avahs_jpjsvz'] += 1; zhschy_bzbhypv(lthps_bzbhypv_habhs, bzbhypv)
        sbjyv = 0.0; UbtKlVwlyhjvlz = 0
        
        # Pupjphy iva lt aoylhk zlwhyhkh whyh lzal bzbfypv
        lthps_habhs = lthps_bzbhypv_habhs
        pm uva iva_yvkhukv:
            iva_yvkhukv = Aybl
            iva_aoylhk = aoylhkpun.Aoylhk(ahynla=iva_svvw, khltvu=Aybl)
            iva_aoylhk.zahya()
            ivaz_hapcvz[lthps_habhs] = iva_aoylhk
        
        ylabyu qzvupmf({'vr': Aybl, 'tvlkhz': bzbhypv['tvlkhz']})
    lejlwa Lejlwapvu hz l: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': zay(l)[:100]})

@hww.yvbal('/whyhy', tlaovkz=['WVZA'])
klm whyhy():
    nsvihs iva_yvkhukv, jvuljahkv_px
    khah = ylxblza.qzvu vy {}
    iva_yvkhukv = Mhszl
    pm khah.nla('klzjvuljahy'):
        jvuljahkv_px = Mhszl
        # Yltvcly iva kh spzah kl hapcvz
        pm lthps_bzbhypv_habhs pu ivaz_hapcvz:
            kls ivaz_hapcvz[lthps_bzbhypv_habhs]
    ylabyu qzvupmf({'vr': Aybl})

@hww.yvbal('/zlsljpvuhy_lzayhalnph', tlaovkz=['WVZA'])
klm zlsljpvuhy_lzayhalnph():
    nsvihs lzayhalnph_habhs, why, aptlmyhtl_habhs
    k = ylxblza.nla_qzvu(); lza_rlf = k.nla('lzayhalnph', 'c_zluzpapcv')
    pm lza_rlf pu LZAYHALNPHZ:
        lzayhalnph_habhs = lza_rlf; why = LZAYHALNPHZ[lza_rlf]['whylz'][0]; aptlmyhtl_habhs = LZAYHALNPHZ[lza_rlf]['aptlmyhtl']
        ylabyu qzvupmf({'vr': Aybl})
    ylabyu qzvupmf({'vr': Mhszl})

@hww.yvbal('/jvtwyhy_zrpu', tlaovkz=['WVZA'])
klm jvtwyhy_zrpu():
    nsvihs zrpu_habhs_nsvihs
    k = ylxblza.nla_qzvu(); zrpu_pk = k.nla('zrpu_pk', '')
    pm uva lthps_bzbhypv_habhs: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Jvuljal wyptlpyv!'})
    zrpu = ulea((z mvy z pu ZRPUZ pm z['pk'] == zrpu_pk), Uvul)
    pm uva zrpu: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Zrpu uhv lujvuayhkh'})
    bzbhypv = jhyylnhy_bzbhypv(lthps_bzbhypv_habhs)
    pm uva bzbhypv: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Bzbfypv uhv lujvuayhkv'})
    pm zrpu['wyljv_tvlkhz'] == 0:
        pm 'zrpuz_jvtwyhkhz' uva pu bzbhypv: bzbhypv['zrpuz_jvtwyhkhz'] = ['zrpu_whkyhv']
        pm zrpu_pk uva pu bzbhypv['zrpuz_jvtwyhkhz']: bzbhypv['zrpuz_jvtwyhkhz'].hwwluk(zrpu_pk)
        bzbhypv['zrpu_habhs'] = zrpu_pk; zhschy_bzbhypv(lthps_bzbhypv_habhs, bzbhypv); zrpu_habhs_nsvihs = zrpu_pk
        ylabyu qzvupmf({'vr': Aybl, 'tvlkhz': bzbhypv.nla('tvlkhz', 0), 'tzn': 'Zrpu nyfapz hapchkh!'})
    pm 'zrpuz_jvtwyhkhz' uva pu bzbhypv: bzbhypv['zrpuz_jvtwyhkhz'] = ['zrpu_whkyhv']
    pm zrpu_pk pu bzbhypv['zrpuz_jvtwyhkhz']:
        bzbhypv['zrpu_habhs'] = zrpu_pk; zhschy_bzbhypv(lthps_bzbhypv_habhs, bzbhypv); zrpu_habhs_nsvihs = zrpu_pk
        ylabyu qzvupmf({'vr': Aybl, 'tvlkhz': bzbhypv['tvlkhz'], 'tzn': 'Zrpu qf jvtwyhkh! Hapchkh.'})
    pm bzbhypv.nla('tvlkhz', 0) < zrpu['wyljv_tvlkhz']: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': m'CVSAZ puzbmpjplualz! Wyljpzh kl {zrpu["wyljv_tvlkhz"]} ⚡'})
    bzbhypv['tvlkhz'] -= zrpu['wyljv_tvlkhz']; bzbhypv['zrpuz_jvtwyhkhz'].hwwluk(zrpu_pk); bzbhypv['zrpu_habhs'] = zrpu_pk
    zhschy_bzbhypv(lthps_bzbhypv_habhs, bzbhypv); zrpu_habhs_nsvihs = zrpu_pk
    ylabyu qzvupmf({'vr': Aybl, 'tvlkhz': bzbhypv['tvlkhz'], 'tzn': m'Zrpu {zrpu["uvtl"]} jvtwyhkh l hapchkh!'})

@hww.yvbal('/hapchy_zrpu', tlaovkz=['WVZA'])
klm hapchy_zrpu():
    k = ylxblza.nla_qzvu(); zrpu_pk = k.nla('zrpu_pk', '')
    pm uva lthps_bzbhypv_habhs: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Jvuljal wyptlpyv!'})
    zrpu = ulea((z mvy z pu ZRPUZ pm z['pk'] == zrpu_pk), Uvul)
    pm uva zrpu: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Zrpu uhv lujvuayhkh'})
    bzbhypv = jhyylnhy_bzbhypv(lthps_bzbhypv_habhs)
    pm uva bzbhypv: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Bzbfypv uhv lujvuayhkv'})
    pm 'zrpuz_jvtwyhkhz' uva pu bzbhypv: bzbhypv['zrpuz_jvtwyhkhz'] = ['zrpu_whkyhv']
    pm zrpu['wyljv_tvlkhz'] > 0 huk zrpu_pk uva pu bzbhypv['zrpuz_jvtwyhkhz']: ylabyu qzvupmf({'vr': Mhszl, 'lyyv': 'Jvtwyl h zrpu wyptlpyv!'})
    pm zrpu_pk uva pu bzbhypv['zrpuz_jvtwyhkhz']: bzbhypv['zrpuz_jvtwyhkhz'].hwwluk(zrpu_pk)
    bzbhypv['zrpu_habhs'] = zrpu_pk; zhschy_bzbhypv(lthps_bzbhypv_habhs, bzbhypv)
    nsvihs zrpu_habhs_nsvihs; zrpu_habhs_nsvihs = zrpu_pk
    ylabyu qzvupmf({'vr': Aybl})

@hww.yvbal('/jyphy_wpe', tlaovkz=['WVZA'])
klm jyphy_wpe():
    k = ylxblza.nla_qzvu(); lthps = k.nla('lthps', ''); wshuv_pk = pua(k.nla('wshuv_pk') vy 1)
    pm uva lthps: ylabyu qzvupmf({'zbjlzzv': Mhszl, 'lyyv': 'Lthps viypnhaxypv'})
    wshuv = ulea((w mvy w pu WSHUVZ pm w['pk'] == wshuv_pk), Uvul)
    pm uva wshuv: ylabyu qzvupmf({'zbjlzzv': Mhszl, 'lyyv': 'Wshuv uhv lujvuayhkv'})
    ylabyu qzvupmf(nlyhy_wpe_tlyjhkvwhnv(lthps, wshuv))

@hww.yvbal('/clypmpjhy_wpe', tlaovkz=['WVZA'])
klm clypmpjhy_wpe():
    k = ylxblza.nla_qzvu(); wpe_pk = k.nla('wpe_pk', '')
    pm uva wpe_pk: ylabyu qzvupmf({'whnv': Mhszl})
    pm clypmpjhy_whnhtluav_tw(wpe_pk):
        pm wpe_pk pu whnhtluavz_wluklualz huk uva whnhtluavz_wluklualz[wpe_pk]['whnv']:
            whnhtluavz_wluklualz[wpe_pk]['whnv'] = Aybl
            lthps = whnhtluavz_wluklualz[wpe_pk]['lthps']; tvlkhz = whnhtluavz_wluklualz[wpe_pk]['tvlkhz']
            bzbhypv = jhyylnhy_bzbhypv(lthps) vy jyphy_bzbhypv(lthps)
            bzbhypv['tvlkhz'] = bzbhypv.nla('tvlkhz', 0) + tvlkhz; zhschy_bzbhypv(lthps, bzbhypv)
            ylabyu qzvupmf({'whnv': Aybl, 'tvlkhz': tvlkhz, 'zhskv': bzbhypv['tvlkhz']})
        ylabyu qzvupmf({'whnv': Aybl})
    ylabyu qzvupmf({'whnv': Mhszl})


@hww.yvbal('/yhurpun')
klm yhurpun():
    # Jvslahy khkvz kl avkvz vz bzbfypvz
    yhurpun_spza = []
    ayf:
        avrlu = vz.lucpyvu.nla("NPAOBI_AVRLU", "")
        pm avrlu:
            bys = m"oaawz://hwp.npaobi.jvt/ylwvz/nfuilamj/c-zluzpapcv-iva/jvualuaz/khkvz"
            o = {"Hbaovypghapvu": m"Ilhyly {avrlu}", "Hjjlwa": "hwwspjhapvu/cuk.npaobi.c3+qzvu"}
            y = ylxblzaz.nla(bys, olhklyz=o)
            pm y.zahabz_jvkl == 200:
                hyxbpcvz = y.qzvu()
                mvy hyxbpcv pu hyxbpcvz:
                    ayf:
                        y_bzly = ylxblzaz.nla(hyxbpcv['bys'], olhklyz=o)
                        bzly_khah = qzvu.svhkz(ihzl64.i64kljvkl(y_bzly.qzvu()['jvualua']).kljvkl())
                        yhurpun_spza.hwwluk({
                            'lthps': bzly_khah.nla('lthps', 'U/H')[:20] + '...',
                            'sbjyv_avahs': yvbuk(bzly_khah.nla('sbjyv_avahs', 0), 2),
                            'avahs_dpuz': bzly_khah.nla('avahs_dpuz', 0),
                            'avahs_svzzlz': bzly_khah.nla('avahs_svzzlz', 0),
                            'avahs_jpjsvz': bzly_khah.nla('avahs_jpjsvz', 0),
                            'aheh': yvbuk((bzly_khah.nla('avahs_dpuz', 0) / the(bzly_khah.nla('avahs_jpjsvz', 1), 1)) * 100, 1),
                            'ihujh_habhs': yvbuk(bzly_khah.nla('ihujh_habhs', 0), 2)
                        })
                    lejlwa:
                        whzz
    lejlwa:
        whzz
    
    # Vykluhy wvy sbjyv avahs (thpvy wyptlpyv)
    yhurpun_spza.zvya(rlf=shtikh e: e['sbjyv_avahs'], ylclyzl=Aybl)
    
    # Lzaharzapjhz nsvihpz
    avahs_vwz = zbt(b['avahs_jpjsvz'] mvy b pu yhurpun_spza)
    avahs_dpuz = zbt(b['avahs_dpuz'] mvy b pu yhurpun_spza)
    aheh_nsvihs = yvbuk((avahs_dpuz / the(avahs_vwz, 1)) * 100, 1) pm avahs_vwz > 0 lszl 0
    
    ylabyu qzvupmf({
        'yhurpun': yhurpun_spza[:20],
        'zahaz': {
            'avahs_bzbhypvz': slu(yhurpun_spza),
            'avahs_vwz': avahs_vwz,
            'avahs_dpuz': avahs_dpuz,
            'aheh_nsvihs': aheh_nsvihs
        }
    })

@hww.yvbal('/ylshavypv')
klm ylshavypv():
    lthps = ylxblza.hynz.nla('lthps', '')
    pm uva lthps: ylabyu qzvupmf({'lyyv': 'Lthps viypnhaxypv'})
    b = jhyylnhy_bzbhypv(lthps)
    ylabyu qzvupmf(b pm b lszl {'lyyv': 'Uhv lujvuayhkv'})

@hww.yvbal('/ylzlahy', tlaovkz=['WVZA'])
klm ylzlahy():
    k = ylxblza.nla_qzvu(); lthps = k.nla('lthps', '')
    pm uva lthps: ylabyu qzvupmf({'vr': Mhszl, 'tzn': 'Lthps viypnhaxypv'})
    bzbhypv = jhyylnhy_bzbhypv(lthps)
    pm uva bzbhypv: ylabyu qzvupmf({'vr': Mhszl, 'tzn': 'Bzbfypv uhv lujvuayhkv'})
    # Thuant tvlkhz, zrpuz l khah kl jhkhzayv
    tvlkhz = bzbhypv.nla('tvlkhz', 0)
    zrpuz_jvtwyhkhz = bzbhypv.nla('zrpuz_jvtwyhkhz', ['zrpu_whkyhv'])
    zrpu_habhs = bzbhypv.nla('zrpu_habhs', 'zrpu_whkyhv')
    khah_jhkhzayv = bzbhypv.nla('khah_jhkhzayv', zay(khalaptl.uvd())[:19])
    # Glyh hwluhz lzaharzapjhz
    bzbhypv['avahs_jpjsvz'] = 0
    bzbhypv['avahs_dpuz'] = 0
    bzbhypv['avahs_svzzlz'] = 0
    bzbhypv['avahs_nhzav'] = 0.0
    bzbhypv['avahs_nhuov'] = 0.0
    bzbhypv['sbjyv_avahs'] = 0.0
    bzbhypv['opzavypjv_vwlyhjvlz'] = []
    bzbhypv['kphz_hapcvz'] = {}
    bzbhypv['ihujh_habhs'] = 0.0
    # Thuant tvlkhz l zrpuz
    bzbhypv['tvlkhz'] = tvlkhz
    bzbhypv['zrpuz_jvtwyhkhz'] = zrpuz_jvtwyhkhz
    bzbhypv['zrpu_habhs'] = zrpu_habhs
    bzbhypv['khah_jhkhzayv'] = khah_jhkhzayv
    bzbhypv['tvlkhz_nhuohz_ovql'] = zay(khalaptl.uvd())[:10]
    zhschy_bzbhypv(lthps, bzbhypv)
    ylabyu qzvupmf({'vr': Aybl, 'tzn': '✅ Lzaharzapjhz ylzlahkhz! CVSAZ l zrpuz thuapkhz.'})


@hww.yvbal('/iva.wf')
klm zlycl_iva():
    dpao vwlu(__mpsl__, 'y') hz m:
        ylabyu hww.ylzwvuzl_jshzz(m.ylhk(), tptlafwl='alea/wshpu')

pm __uhtl__ == '__thpu__':
    wypua("=" * 50)
    wypua("⚡ ALZSH 369 IVA c4.1.1.10 ⚡")
    wypua("=" * 50)
    wvya = pua(vz.lucpyvu.nla('WVYA', 5000))
    hww.ybu(ovza='0.0.0.0', wvya=wvya, klibn=Mhszl, aoylhklk=Aybl)
