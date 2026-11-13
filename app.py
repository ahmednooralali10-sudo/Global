# -*- coding: utf-8 -*-
import json, base64, datetime, re, http.client, ssl, gzip, asyncio, gc, sys, os, time
import threading, queue, socket, struct, traceback, uuid, codecs, hmac, hashlib, string, random
from io import BytesIO
from datetime import datetime, timedelta

import jwt, urllib3, requests
from protobuf_decoder.protobuf_decoder import Parser
from google.protobuf.timestamp_pb2 import Timestamp
from rich.console import Console
from cfonts import render, say
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

import keys
from xAlInAs import *

ACCOUNTS_FILE = "accounts.txt"
TCPOB_FILE = "xAlInAs.json"
TG = "@xAlInAs_sAnIlAx"
RCD = 1
RDT = .1
RES = 20000
OBV = "ob55"
RF = False
RAF = {"ME": ACCOUNTS_FILE}
ADMIN_UID = "7909163333"

xAlInAs_enc  = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
xAlInAs_enc1 = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
xAlInAs_key  = b"Yg&tc%DEuh6%Zc^8"
xAlInAs_iv   = b"6oyZDr22E3ychjM%"

LOGIN_SERVERS = [
    "https://loginbp.ppmainecoonghj.com/"
]

console = Console()
lock = threading.Lock()
sem = threading.Semaphore(10000)
connected_bots = {}
connected_lock = threading.Lock()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

login_url = LOGIN_SERVERS[0]
ob = "OB55"
verr = None
host = "loginbp.ppmainecoonghj.com"
active_count = 0

GRANT_URL = "https://ffmconnect.ppmainecoonghj.com/api/v2/oauth/guest/token:grant"
API_HEX_KEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
API_SECRET_KEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
AES_KEY_G = b'Yg&tc%DEuh6%Zc^8'
AES_IV_G = b'6oyZDr22E3ychjM%'

REGION_LANG = {
    "BD": "bn", "IND": "hi", "PK": "ur", "SG": "en", "ID": "id",
    "ME": "ar", "VN": "vi", "TW": "zh", "CIS": "ru", "TH": "th",
    "EU": "en", "US": "en", "SAC": "es", "LK": "en", "BR": "pt",
}

GHOST_MAX_TRIES = 1000000000
GHOST_RETRY_DELAY = 0.0001
MSG_TRIES = 1000000000
MSG_DELAY = 0.05
BURST_TIME = 12.0

CHAT_AUTH_WAIT   = 0.20
CHAT_JOIN_WAIT   = 0.30
CHAT_RETRY_DELAY = 0.10

JOIN_TIMEOUT = 2.0
JOIN_REFRESH = 0.005
CYCLE_RETRY_DELAY = 0.1
JOIN_MAX_TRIES = 100
PACKET_RESEND = 50

AUTH_RETRY_DELAY = 3.0
BOT_CRASH_RESTART_DELAY = 2.0

INSTAGRAM = "@xAlInAs_sAnIlAx"
TELEGRAM = "@xAlInAs_sAnIlAx"
OWNER_NAME = "xAlInAs"

HR = {
    "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
    "Accept": "*/*",
    "Accept-Encoding": "deflate, gzip",
    "X-GA-SV": "1790797445",
    "Authorization": "Bearer",
    "X-GA": "v1 1",
    "ReleaseVersion": ob,
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Unity-Version": "2018.4.12f1",
}

COLORS = [
    "32CD32", "00BFFF", "00FA9A", "90EE90", "FF4500", "FF6347", "FF69B4",
    "FF8C00", "FFD700", "FFDAB9", "F0F0F0", "F0E68C", "D3D3D3", "A9A9A9",
    "D2691E", "CD853F", "BC8F8F", "6A5ACD", "483D8B", "4682B4", "9370DB",
    "C71585", "FFA07A", "FF0000", "00FF00", "0000FF", "FFFF00", "FF00FF",
    "00FFFF", "FFFFFF", "FF1493", "7CFC00", "DC143C", "00CED1", "9400D3",
    "F08080", "20B2AA", "B22222", "DAA520", "00FF7F", "6495ED", "DDA0DD",
    "2E8B57", "3CB371", "6B8E23", "808000", "B8860B", "CD5C5C", "8B0000",
]

def ArA_CoLor():
    return random.choice(COLORS)

def xAlInAs_add_bot(b, o, r):
    with connected_lock:
        connected_bots[b] = {
            'bot_uid': b, 'original_uid': o, 'region': r,
            'time': datetime.now().strftime("%H:%M:%S"),
        }

def xAlInAs_remove_bot(b):
    with connected_lock:
        connected_bots.pop(b, None)

def xAlInAs_find_proto_start(d):
    if not d:
        return 0
    for i, x in enumerate(d):
        if x == 0x08:
            return i
    return 0

def xAlInAs_read_varint(d, p):
    v = 0
    s = 0
    while True:
        if p >= len(d):
            raise ValueError("truncated")
        b = d[p]
        p += 1
        v |= (b & 0x7F) << s
        if not b & 0x80:
            return v, p
        s += 7
        if s > 70:
            raise ValueError("too long")

def xAlInAs_is_printable(t):
    return all(c.isprintable() or c in "\r\n\t" for c in t)

def xAlInAs_put_field(r, k, v):
    if k in r:
        if type(r[k]) is not list:
            r[k] = [r[k]]
        r[k].append(v)
    else:
        r[k] = v

def xAlInAs_proto_decode(d, depth=0):
    r = {}
    p = 0
    try:
        while p < len(d):
            tag, p = xAlInAs_read_varint(d, p)
            f = tag >> 3
            w = tag & 7
            if f <= 0:
                raise ValueError("bad")
            if w == 0:
                v, p = xAlInAs_read_varint(d, p)
            elif w == 1:
                if p + 8 > len(d):
                    raise ValueError("trunc")
                v = struct.unpack("<Q", d[p:p + 8])[0]
                p += 8
            elif w == 2:
                ln, p = xAlInAs_read_varint(d, p)
                if p + ln > len(d):
                    raise ValueError("trunc")
                raw = d[p:p + ln]
                p += ln
                try:
                    tx = raw.decode("utf-8")
                    if xAlInAs_is_printable(tx):
                        v = tx
                    else:
                        n = xAlInAs_proto_decode(raw, depth + 1)
                        v = n if n else raw.hex()
                except:
                    try:
                        n = xAlInAs_proto_decode(raw, depth + 1)
                        v = n if n else raw.hex()
                    except:
                        v = raw.hex()
            elif w == 5:
                if p + 4 > len(d):
                    raise ValueError("trunc")
                v = struct.unpack("<I", d[p:p + 4])[0]
                p += 4
            else:
                raise ValueError("bad wire")
            xAlInAs_put_field(r, str(f), v)
        return r
    except:
        return r

def xAlInAs_get_raw_field(d, tf):
    try:
        p = 0
        while p < len(d):
            tag, p = xAlInAs_read_varint(d, p)
            f = tag >> 3
            w = tag & 7
            if w == 0:
                v, p = xAlInAs_read_varint(d, p)
            elif w == 1:
                if p + 8 > len(d):
                    return None
                v = d[p:p + 8]
                p += 8
            elif w == 2:
                ln, p = xAlInAs_read_varint(d, p)
                if p + ln > len(d):
                    return None
                v = d[p:p + ln]
                p += ln
            elif w == 5:
                if p + 4 > len(d):
                    return None
                v = d[p:p + 4]
                p += 4
            else:
                return None
            if f == tf:
                return v
        return None
    except:
        return None

def xAlInAs_to_text(v):
    if type(v) is str:
        return v
    if type(v) is bytes:
        return v.decode("utf-8", errors="ignore")
    return str(v)

def xAlInAs_varint_encode(v):
    o = bytearray()
    v = int(v)
    while v > 127:
        o.append((v & 127) | 128)
        v >>= 7
    o.append(v)
    return bytes(o)

def xAlInAs_proto_encode(fields):
    o = bytearray()
    for f, v in fields.items():
        if type(v) is dict:
            n = xAlInAs_proto_encode(v)
            o.extend(xAlInAs_varint_encode((f << 3) | 2))
            o.extend(xAlInAs_varint_encode(len(n)))
            o.extend(n)
        elif type(v) is int:
            o.extend(xAlInAs_varint_encode(f << 3))
            o.extend(xAlInAs_varint_encode(v))
        elif type(v) is str:
            e = v.encode()
            o.extend(xAlInAs_varint_encode((f << 3) | 2))
            o.extend(xAlInAs_varint_encode(len(e)))
            o.extend(e)
        elif type(v) is bytes:
            o.extend(xAlInAs_varint_encode((f << 3) | 2))
            o.extend(xAlInAs_varint_encode(len(v)))
            o.extend(v)
    return bytes(o)

def xAlInAs_update_version():
    global login_url, ob, verr, host
    try:
        from google_play_scraper import app as gp
        d = gp("com.dts.freefireth", lang="en", country="ME")
        version = d["version"]
    except Exception:
        version = "1.132.1"
    try:
        x = requests.get(
            "https://version.ggwhitehawk.com/live/ver.php"
            f"?version={version}&lang=en&device=android&channel=android"
            f"&appsttore=googleplay&region=en&whitelist_version=1.3.0"
            f"&whitelist_sp_version=1.0.0&device_name=google%20G011A"
            f"&device_CPU=ARMv7%20VFPv3%20NEON%20VMH"
            f"&device_GPU=Adreno%20(TM)%20640&device_mem=1993",
            timeout=10,
        ).json()
        login_url = x["server_url"]
        ob = x["latest_release_version"]
        verr = x["remote_version"]
        host = login_url.split("https://", 1)[1].split("/", 1)[0]
    except Exception:
        login_url = LOGIN_SERVERS[0]
        ob = "OB55"
        verr = version
        host = "loginbp.ppmainecoonghj.com"
    return login_url, ob, verr

login_url, ob, version = xAlInAs_update_version()
HR["ReleaseVersion"] = ob

# ==================== AUTH & LOGIN FUNCTIONS ====================
def EnV_VaRiAnT(n):
	d=[]
	while True:
		b=n&0x7F;n>>=7
		if n:b|=0x80
		d.append(b)
		if not n:break
	return bytes(d)

def ProToBuF(Fields):
	p=bytearray()
	for f,v in Fields.items():
		if isinstance(v,bool):
			p.extend(EnV_VaRiAnT((f<<3)|0));p.extend(EnV_VaRiAnT(1 if v else 0))
		elif isinstance(v,int):
			p.extend(EnV_VaRiAnT((f<<3)|0));p.extend(EnV_VaRiAnT(v))
		elif isinstance(v,str):
			d=v.encode();p.extend(EnV_VaRiAnT((f<<3)|2));p.extend(EnV_VaRiAnT(len(d)));p.extend(d)
		elif isinstance(v,(bytes,bytearray)):
			d=bytes(v);p.extend(EnV_VaRiAnT((f<<3)|2));p.extend(EnV_VaRiAnT(len(d)));p.extend(d)
	return bytes(p)

def Read_VaRiAnT(data,pos):
	result=0;shift=0
	while pos<len(data):
		b=data[pos];pos+=1
		result|=(b&0x7F)<<shift
		if not (b&0x80):break
		shift+=7
	return result,pos

def Parse_ProToBuF(data):
	fields={};pos=0;n=len(data)
	while pos<n:
		try:key,pos=Read_VaRiAnT(data,pos)
		except:break
		fn=key>>3;wt=key&0x07
		try:
			if wt==0:val,pos=Read_VaRiAnT(data,pos)
			elif wt==2:
				ln,pos=Read_VaRiAnT(data,pos);val=data[pos:pos+ln];pos+=ln
			elif wt==5:val=data[pos:pos+4];pos+=4
			elif wt==1:val=data[pos:pos+8];pos+=8
			else:break
		except:break
		fields.setdefault(fn,[]).append(val)
	return fields

def Ua():
	versions=['4.0.18P6','4.0.19P7','4.0.20P1','4.1.0P3','4.1.5P2','4.2.1P8','4.2.3P1','5.0.1B2','5.0.2P4','5.1.0P1','5.2.0B1','5.2.5P3','5.3.0B1','5.3.2P2','5.4.0P1','5.4.3B2','5.5.0P1','5.5.2P3']
	return random.choice(versions)

def xAlInAs_build_login_payload(access_token,open_id):
	PyL={}
	PyL[3]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	PyL[4]="free fire"
	PyL[5]=1
	PyL[7]=verr or "1.132.9"
	PyL[8]="Android OS 14 / API-34 (UP1A.231005.007/V816.0.15.0.UNQMIXM)"
	PyL[9]="Handheld"
	PyL[10]="Grameenphone"
	PyL[11]="CarrierDataNetwork"
	PyL[12]=1666
	PyL[13]=750
	PyL[14]="352"
	PyL[15]="ARM64 FP ASIMD AES | 2400 | 8"
	PyL[16]=5563
	PyL[17]="Mali-G57 MC2"
	PyL[18]="OpenGL ES 3.2 v1.r32p1-01eac0.0a0b917d9265b4c01be9925306306139"
	PyL[19]="Google|9cc73f7a-91f6-40f6-87ec-5b67e597eb8c"
	PyL[20]="59.152.5.188"
	PyL[21]="en"
	PyL[22]=open_id
	PyL[23]="8"
	PyL[24]="Handheld"
	PyL[25]="Xiaomi 2312DRAABI"
	PyL[26]="ME"
	PyL[29]=access_token
	PyL[30]=1
	PyL[41]="Grameenphone"
	PyL[42]="Cellular"
	PyL[57]="7428b253defc164018c604a1ebbfebdf"
	PyL[60]=109685
	PyL[61]=58294
	PyL[62]=797
	PyL[63]=18000
	PyL[64]=58818
	PyL[65]=109685
	PyL[66]=58818
	PyL[67]=109685
	PyL[73]=2
	PyL[74]="/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/lib/arm64"
	PyL[76]=1
	PyL[77]="b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/base.apk"
	PyL[78]=3
	PyL[79]=2
	PyL[81]="64"
	PyL[83]="2019121229"
	PyL[85]=3
	PyL[86]="OpenGLES2"
	PyL[87]=4095
	PyL[88]=8
	PyL[89]=b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
	PyL[90]="Dhaka"
	PyL[91]="C"
	PyL[92]=8043
	PyL[93]="android"
	PyL[94]="KqsHT4XbSZhqerDNUhjbS3DxG/4+I62zQU2tZFJN91kBUICAlZ5yujshLKvjlk/KiShfKfis8EeB1PMhFHIodWPncZC4fCHYF3TcTwNj95aWY/S3"
	PyL[95]=111207
	PyL[96]='{"cur_rate":[60,90,120],"support_etc2":false}'
	PyL[97]=1
	PyL[98]=1
	PyL[99]="4"
	PyL[100]="4"
	PyL[102]="GQ]        e"
	PyL[103]=1
	PyL[104]=45174
	PyL[105]=1
	PyL[106]="https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a"
	PyL[107]="1.9393e7b8e53e8aeb"
	return AES.new(xAlInAs_key,AES.MODE_CBC,xAlInAs_iv).encrypt(pad(ProToBuF(PyL),16))

def Strip_MajorLogin_Prefix(body):
	if len(body)<=64:return body
	try:
		if 8 in Parse_ProToBuF(body):return body
	except:pass
	try:
		if 8 in Parse_ProToBuF(body[64:]):return body[64:]
	except:pass
	return body[64:]

def GeT_AccEss(uid,password):
	url="https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
	headers={"User-Agent":Ua(),"Content-Type":"application/json; charset=utf-8"}
	R=requests.post(url,headers=headers,json={"client_id":100067,"client_secret":"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3","client_type":2,"device_id":"","password":password,"response_type":"token","uid":int(uid)},verify=False,timeout=15)
	if R.status_code not in (200,201):return None
	try:J=R.json()
	except:return None
	if J.get("code")!=0:return None
	data=J.get("data",{})
	return {"access_token":data.get("access_token"),"open_id":data.get("open_id")}

def xAlInAs_decrypt_major_login(resp):
	class A: pass
	a = A()
	body = Strip_MajorLogin_Prefix(resp)
	ld = Parse_ProToBuF(body)
	if not ld: return None
	au = ld.get("8") or ld.get(8)
	if type(au) is list: au = au[0]
	if isinstance(au, bytes):
		try: tok = au.decode("utf-8")
		except: tok = ""
	else: tok = str(au or "")
	if not tok.startswith("eyJ"): return None
	
	ub = ld.get("10") or ld.get(10)
	if type(ub) is list: ub = ub[0]
	url = ub.decode("utf-8") if isinstance(ub, bytes) else str(ub or "")
	if not url: return None
	
	ts_raw = ld.get("21") or ld.get(21)
	if type(ts_raw) is list: ts_raw = ts_raw[0]
	ts = int(ts_raw) if ts_raw else int(time.time())
	
	kb = xAlInAs_get_raw_field(body, 22)
	ib = xAlInAs_get_raw_field(body, 23)
	if not kb or not ib: kb, ib = xAlInAs_key, xAlInAs_iv
	
	acc_uid = ld.get("1") or ld.get(1)
	if type(acc_uid) is list: acc_uid = acc_uid[0]
	if isinstance(acc_uid, bytes):
		try: acc_uid = int(acc_uid.hex(), 16)
		except: acc_uid = 0
	
	a.token = tok
	a.account_uid = acc_uid or 0
	a.key = kb
	a.iv = ib
	a.timestamp = ts
	a.url = url
	return a

def xAlInAs_decrypt_login_data(data):
	class P: pass
	p = P()
	pd = Parse_ProToBuF(data)
	if not pd: return None
	
	def get_val(k):
		v = pd.get(k)
		if not v: return None
		if isinstance(v, list): v = v[0]
		return v.decode("utf-8", errors="ignore") if isinstance(v, bytes) else str(v)

	op = get_val("14") or get_val(14)
	cp_ = get_val("32") or get_val(32)
	if not op or not cp_: return None
	p.Online_IP_Port = op
	p.AccountIP_Port = cp_
	return p

def xAlInAs_build_auth_token(uid, token, ts, key, iv, mode="online"):
	ah = f"{int(uid):x}".zfill(16)
	enc = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(token.encode(), 16)).hex()
	th = f"{int(ts):x}"
	if len(th) % 2: th = "0" + th
	tsz = f"{len(enc)//2:02x}"
	pad_ = "00000" if mode == "chat" else "0000000000000"
	return f"9015{ah}{th}{pad_}{tsz}{enc}"

def xAlInAs_online_keepalive(ip, port, auth_online, key, iv, bot_uid):
    while True:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(20)
            s.connect((ip, int(port)))
            s.sendall(bytes.fromhex(auth_online))
            lk = time.time()
            while True:
                try:
                    s.settimeout(3)
                    d = s.recv(8192)
                    if not d:
                        break
                except socket.timeout:
                    pass
                if time.time() - lk > 20:
                    try:
                        s.sendall(send_keep_alive(key, iv))
                        lk = time.time()
                    except:
                        break
        except:
            pass
        try:
            if s:
                s.close()
        except:
            pass
        time.sleep(10)

class xAlInAsClient:
    def __init__(self, uid, password, region):
        self.uid = uid
        self.password = password
        self.region = region
        self.bot_uid = "Unknown"
        self.running = True
        self.target_found = False
        self.login_success = False

    def xAlInAs_all(self):
        global active_count, RF
        with sem:
            with lock:
                active_count += 1

            auth = None
            auth_online = None
            ip = None
            port = None
            ip2 = None
            port2 = None
            key = None
            iv = None

            while self.running and not RF:
                auth_attempts = 0
                saved_data = None
                while self.running and not RF:
                    auth_attempts += 1
                    try:
                        td = GeT_AccEss(self.uid, self.password)
                        if td and td.get("access_token") and td.get("open_id"):
                            atk = td["access_token"]
                            oid = td["open_id"]
                            pyl = xAlInAs_build_login_payload(atk, oid)
                            
                            url_ml = f"{login_url.rstrip('/')}/MajorLogin"
                            headers_ml = {
                                "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
                                "Accept-Encoding": "identity",
                                "X-GA-SV": str(int(time.time())),
                                "Authorization": "Bearer",
                                "X-GA": "v1 1",
                                "ReleaseVersion": ob,
                                "Content-Type": "application/x-www-form-urlencoded",
                                "X-Unity-Version": "2018.4.12f1",
                                "Host": host,
                            }
                            r_ml = requests.post(url_ml, headers=headers_ml, data=pyl, verify=False, timeout=15)
                            if r_ml.status_code in (200, 201) and r_ml.content:
                                ad = xAlInAs_decrypt_major_login(r_ml.content)
                                if ad:
                                    client_url = ad.url.rstrip("/")
                                    if not client_url.startswith(("http://", "https://")):
                                        client_url = "https://" + client_url
                                    
                                    url_gld = f"{client_url}/GetLoginData"
                                    headers_gld = {
                                        "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
                                        "Accept": "*/*",
                                        "Accept-Encoding": "deflate, gzip",
                                        "X-GA-SV": str(int(time.time())),
                                        "Authorization": f"Bearer {ad.token}",
                                        "X-GA": "v1 1",
                                        "ReleaseVersion": ob,
                                        "Content-Type": "application/x-www-form-urlencoded",
                                        "X-Unity-Version": "2018.4.12f1"
                                    }
                                    r_gld = requests.post(url_gld, headers=headers_gld, data=pyl, verify=False, timeout=15)
                                    if r_gld.status_code == 200 and r_gld.content:
                                        ports = xAlInAs_decrypt_login_data(r_gld.content)
                                        if ports:
                                            op = ports.Online_IP_Port
                                            cp_ = ports.AccountIP_Port
                                            if op and cp_:
                                                oip, oport = op.split(":")
                                                cip, cport = cp_.split(":")
                                                ac = xAlInAs_build_auth_token(int(ad.account_uid), ad.token, int(ad.timestamp), ad.key, ad.iv, mode="chat")
                                                ao = xAlInAs_build_auth_token(int(ad.account_uid), ad.token, int(ad.timestamp), ad.key, ad.iv, mode="online")
                                                saved_data = {
                                                    'auth': ac, 'auth_online': ao,
                                                    'ip': oip, 'port': oport, 'ip2': cip, 'port2': cport,
                                                    'key': ad.key, 'iv': ad.iv, 'bot_uid': str(ad.account_uid),
                                                }
                                                break
                    except Exception as e:
                        pass
                    with lock:
                        console.print(f"[red]{self.uid} {self.region} Auth Failed (attempt {auth_attempts}), retry in {AUTH_RETRY_DELAY}s...[/red]")
                    time.sleep(AUTH_RETRY_DELAY)

                if not saved_data:
                    with lock:
                        active_count -= 1
                    return

                auth = saved_data['auth']
                auth_online = saved_data['auth_online']
                ip = saved_data['ip']
                port = saved_data['port']
                ip2 = saved_data['ip2']
                port2 = saved_data['port2']
                key = saved_data['key']
                iv = saved_data['iv']
                self.bot_uid = saved_data['bot_uid']

                with lock:
                    console.print(f"[green]Bot {self.bot_uid} {self.region} LOGGED IN[/green]")
                self.login_success = True

                try:
                    t = threading.Thread(
                        target=xAlInAs_online_keepalive,
                        args=(ip, int(port), auth_online, key, iv, self.bot_uid),
                        daemon=True,
                    )
                    t.start()
                    xAlInAs_add_bot(self.bot_uid, str(self.uid), self.region)
                except:
                    pass

                try:
                    b64 = auth.split(".")[1] + "=" * ((4 - len(auth.split(".")[1]) % 4) % 4)
                    bot_info = json.loads(base64.urlsafe_b64decode(b64).decode())
                    bot_uid_real = bot_info.get("account_id", "0")
                except:
                    bot_uid_real = self.bot_uid

                cycle_num = 0
                while self.running and not RF:
                    cycle_num += 1
                    sock = None
                    target_uid = None
                    squad_code = None
                    code = None
                    try:
                        for attempt in range(JOIN_MAX_TRIES):
                            if RF or not self.running:
                                break
                            try:
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 524288)
                                sock.settimeout(0.4)
                                sock.connect((ip, int(port)))
                                sock.sendall(bytes.fromhex(auth_online))
                                time.sleep(0.001)
                                deadline = time.time() + JOIN_TIMEOUT
                                last_send = 0
                                while time.time() < deadline:
                                    if RF or not self.running:
                                        break
                                    if time.time() - last_send > JOIN_REFRESH:
                                        try:
                                            sock.sendall(Join_Sq(key, iv))
                                            last_send = time.time()
                                        except:
                                            break
                                    try:
                                        sock.settimeout(0.1)
                                        data = sock.recv(65536)
                                        if not data:
                                            break
                                        hex_data = data.hex()
                                        if hex_data.startswith('0500') and len(hex_data) > 100:
                                            try:
                                                js = DeCode_PackEt(hex_data[10:])
                                                if js:
                                                    packet = json.loads(js)
                                                    try:
                                                        t_uid = packet.get('5', {}).get('data', {}).get('1', {}).get('data')
                                                        sq = packet.get('5', {}).get('data', {}).get('31', {}).get('data')
                                                        ch = packet.get('5', {}).get('data', {}).get('17', {}).get('data')
                                                    except:
                                                        t_uid, sq, ch = None, None, None
                                                    if t_uid and sq and ch:
                                                        target_uid = t_uid
                                                        squad_code = sq
                                                        code = ch
                                                        break
                                            except:
                                                pass
                                    except socket.timeout:
                                        continue
                                    except (ConnectionResetError, OSError):
                                        break
                                    except:
                                        continue
                                if target_uid:
                                    break
                                try:
                                    sock.close()
                                except:
                                    pass
                                sock = None
                                time.sleep(CYCLE_RETRY_DELAY)
                            except:
                                try:
                                    if sock:
                                        sock.close()
                                except:
                                    pass
                                sock = None
                                time.sleep(CYCLE_RETRY_DELAY)

                        if not sock or not target_uid:
                            time.sleep(0.01)
                            continue

                        self.target_found = True
                        with lock:
                            console.print(f"[cyan]{self.bot_uid} JOINED cycle {cycle_num} -> {target_uid}[/cyan]")

                        try:
                            sock.close()
                        except:
                            pass
                        sock = None

                        ghost_count = 0
                        msg_count = 0
                        inv_count = 0
                        sock_online = None
                        sock_chat = None

                        try:
                            sock_online = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock_online.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                            sock_online.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 524288)
                            sock_online.settimeout(0.4)
                            sock_online.connect((ip, int(port)))
                            sock_online.sendall(bytes.fromhex(auth_online))
                            time.sleep(0.001)
                        except:
                            sock_online = None

                        for _ in range(4):
                            try:
                                sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock_chat.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                                sock_chat.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 524288)
                                sock_chat.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                                sock_chat.settimeout(6.0)
                                sock_chat.connect((ip2, int(port2)))
                                sock_chat.sendall(bytes.fromhex(auth))
                                time.sleep(CHAT_AUTH_WAIT)
                                sock_chat.sendall(dance(code, target_uid, key, iv))
                                time.sleep(CHAT_JOIN_WAIT)
                                try:
                                    sock_chat.settimeout(0.05)
                                    while True:
                                        d = sock_chat.recv(4096)
                                        if not d:
                                            break
                                except socket.timeout:
                                    pass
                                sock_chat.settimeout(6.0)
                                break
                            except:
                                try:
                                    if sock_chat:
                                        sock_chat.close()
                                except:
                                    pass
                                sock_chat = None
                                time.sleep(CHAT_RETRY_DELAY)

                        if sock_online:
                            try:
                                sock_online.sendall(xAlInAs_SendInv(bot_uid_real, target_uid, key, iv))
                                inv_count += 1
                            except:
                                pass

                            for _ in range(3):
                                try:
                                    sock_online.sendall(Join_Sq(key, iv))
                                    time.sleep(0.002)
                                except:
                                    break

                            start = time.time()
                            while self.running and time.time() - start < BURST_TIME:
                                try:
                                    color = ArA_CoLor()
                                    pkt = Send_GhosTs(target_uid, f"[C][b][{color}]TG : [ffffff]{TELEGRAM}", squad_code, key, iv)
                                    sock_online.sendall(pkt)
                                    ghost_count += 1
                                    if ghost_count % 10 == 0:
                                        try:
                                            sock_online.sendall(Join_Sq(key, iv))
                                        except:
                                            pass
                                    time.sleep(GHOST_RETRY_DELAY)
                                except (ConnectionResetError, BrokenPipeError, OSError):
                                    break
                                except:
                                    continue

                        if sock_chat:
                            i = 0
                            msgs = [
                                f"The game has been hacked by {OWNER_NAME}",
                                "DoNe By xAlInAs To BuY GL SYSTEM JUST DM",
                                f"Instagram : {INSTAGRAM}",
                                f"Telegram : {TELEGRAM}",
                                f"FOLLOW ME PR I'WILL BAND YOU {OWNER_NAME}",
                                "EvErYThiNg It AvAiBLe",
                                f"IG : {INSTAGRAM}",
                                f"TL : {TELEGRAM}",
                                f"{OWNER_NAME} DoNe GLobAL SySTeM HaS BeeN HaCKeD",
                                "To BuY UR BoTs JuSt Dm Me",
                                f"Contact me on Instagram : {INSTAGRAM}",
                                f"Contact me on Telegram : {TELEGRAM}",
                            ]
                            start = time.time()
                            while self.running and time.time() - start < BURST_TIME:
                                try:
                                    color = ArA_CoLor()
                                    tpl = msgs[i % len(msgs)]
                                    pkt = xAlInAs_Msg(f"[b][c][{color}]{tpl}", target_uid, bot_uid_real, key, iv)
                                    try:
                                        sock_chat.sendall(pkt)
                                        msg_count += 1
                                        i += 1
                                        time.sleep(MSG_DELAY)
                                    except (ConnectionResetError, BrokenPipeError, OSError):
                                        try:
                                            sock_chat.close()
                                        except:
                                            pass
                                        sock_chat = None
                                        for _ in range(4):
                                            try:
                                                sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                sock_chat.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                                                sock_chat.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 524288)
                                                sock_chat.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                                                sock_chat.settimeout(6.0)
                                                sock_chat.connect((ip2, int(port2)))
                                                sock_chat.sendall(bytes.fromhex(auth))
                                                time.sleep(CHAT_AUTH_WAIT)
                                                sock_chat.sendall(dance(code, target_uid, key, iv))
                                                time.sleep(CHAT_JOIN_WAIT)
                                                break
                                            except:
                                                try:
                                                    if sock_chat:
                                                        sock_chat.close()
                                                except:
                                                    pass
                                                sock_chat = None
                                                time.sleep(CHAT_RETRY_DELAY)
                                        if not sock_chat:
                                            break
                                        time.sleep(0.20)
                                except:
                                    continue

                        if sock_online:
                            try:
                                sock_online.sendall(ExiT(key, iv))
                                time.sleep(0.001)
                            except:
                                pass

                        try:
                            if sock_online:
                                sock_online.close()
                        except:
                            pass
                        try:
                            if sock_chat:
                                sock_chat.close()
                        except:
                            pass

                        with lock:
                            console.print(f"[magenta]{self.bot_uid} CYCLE {cycle_num} -> ghost={ghost_count} msg={msg_count} inv={inv_count}[/magenta]")
                        with lock:
                            console.print(f"[yellow]{self.bot_uid} LEFT cycle {cycle_num}[/yellow]")

                        time.sleep(0.01)

                    except Exception as e:
                        with lock:
                            console.print(f"[red]{self.bot_uid} cycle err: {type(e).__name__}[/red]")
                        try:
                            if sock:
                                sock.close()
                        except:
                            pass
                        time.sleep(0.01)

                xAlInAs_remove_bot(self.bot_uid)
                return

def xAlInAs_load_file(fp):
    accs = []
    try:
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        u = parts[0].strip()
                        p = ':'.join(parts[1:]).strip()
                        if u and p:
                            accs.append((u, p))
    except:
        pass
    return accs

def xAlInAs_load_all():
    all_ = []
    for region, fp in RAF.items():
        for u, p in xAlInAs_load_file(fp):
            all_.append((u, p, region))
    random.shuffle(all_)
    return all_

def xAlInAs_run_bot(uid, password, region):
    while True:
        try:
            xAlInAsClient(uid, password, region).xAlInAs_all()
        except Exception as e:
            print(f"[{uid}] BOT CRASH: {type(e).__name__}: {e}, restart in {BOT_CRASH_RESTART_DELAY}s")
        time.sleep(BOT_CRASH_RESTART_DELAY)

def xAlInAs_start_all():
    accs = xAlInAs_load_all()
    if not accs:
        console.print("[red]No accounts found in accounts.txt[/red]")
        return
    console.print(f"[green]Total Accounts {len(accs)}[/green]")
    threads = []
    for u, p, r in accs:
        t = threading.Thread(target=xAlInAs_run_bot, args=(u, p, r), daemon=True)
        t.start()
        threads.append(t)
    return threads

def xAlInAs_restart_loop():
    while True:
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=xAlInAs_restart_loop, daemon=True).start()

    console.print("[bold green]SCRIPT STARTED (Ctrl+C to stop)[/bold green]")
    try:
        xAlInAs_start_all()
    except KeyboardInterrupt:
        console.print("[yellow]Stopped by user.[/yellow]")
        os._exit(0)
    except Exception:
        traceback.print_exc()

    console.print("[bold cyan]Main loop alive - Ctrl+C to stop[/bold cyan]")
    while True:
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            console.print("[yellow]Stopped by user.[/yellow]")
            os._exit(0)
        except Exception:
            time.sleep(5)
