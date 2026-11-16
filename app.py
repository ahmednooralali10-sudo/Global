# -*- coding: utf-8 -*-
import json, base64, datetime, re, http.client, ssl, gzip, asyncio, gc, sys, os, time
import threading, queue, socket, struct, traceback, uuid, codecs, hmac, hashlib, string, random
import subprocess
import tempfile
import shutil
from io import BytesIO
from datetime import datetime, timedelta

import jwt, urllib3, requests
from protobuf_decoder.protobuf_decoder import Parser
from google.protobuf.timestamp_pb2 import Timestamp
from rich.console import Console
from cfonts import render, say
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from fastapi import FastAPI
import uvicorn

import keys
from xAlInAs import *

# ==================== محاولة استيراد كود الأشباح ====================
try:
    from xCoRe import (
        MaJoRLoGiN, CrAuThTK, xGetFNLToKeN, 
        DecodeWhisperMessage, SEndMsG, GhosTCMD, loginbp, Parser as GhostParser
    )
    HAS_GHOST_MODULE = True
    print("[+] Ghost module (xCoRe) loaded successfully.")
except ImportError:
    HAS_GHOST_MODULE = False
    print("[-] WARNING: xCoRe.py not found. Ghost will not work properly!")

# ==================== استيراد نظام الصوت من HELLX ====================
# تأكد أن هذه الملفات موجودة في نفس المجلد
try:
    from auth import (
        HELLXgenerate_access, HELLXbuild_major_login, HELLXmajor_login, HELLXget_login_data,
        HELLXdecode_major_login, HELLXdecode_login_data, HELLXbuild_auth_startup,
        HELLXbuild_post_auth_packets, HELLXbuild_ping_packet, HELLXbuild_accept_invite,
        HELLXbuild_voice_step1, HELLXbuild_voice_auth, HELLXbuild_voice_auth_device,
        HELLXbuild_voice_ping, HELLXbuild_voice_stat_report, HELLXbuild_voice_broadcast_sub,
        HELLXbuild_voice_join, HELLXbuild_voice_custom, HELLXparse_voice_custom_response,
        HELLXbuild_voice_redirect, HELLXbuild_chat_auth, HELLXbuild_chat_global_auth,
        HELLXbuild_chat_message, HELLXbuild_leave_team, HELLXbuild_chat_close,
        HELLXfetch_version, HELLXfetch_city, _VOICE_BASE_HEX, HELLXbuild_emote,
        HELLXbuild_create_squad, HELLXbuild_change_squad_size, HELLXbuild_squad_info_request,
        HELLXbuild_ghost_msg, HELLXbuild_dm_message, HELLXbuild_join_sq, HELLXequip_emote,
    )
    from voice import HELLXextract_garena_voice_data, HELLXextract_voice_from_tcp
    from network import HELLXconnect_online, HELLXping_loop, HELLXread_loop
    from proto import HELLXdecode_proto, HELLXcreate_proto, HELLXgenerate_packet, HELLXenc_varint
    from utils import HELLXload_accounts, HELLXdefault_headers, HELLXlog
    HAS_VOICE_MODULE = True
    print("[+] Voice module (HELLX) loaded successfully.")
except ImportError as e:
    HAS_VOICE_MODULE = False
    print(f"[-] WARNING: Voice module not found: {e}. Voice will not work.")

# ==================== الإعدادات ====================
ACCOUNTS_FILE = "accounts.txt"
TCPOB_FILE = "xAlInAs.json"
TG = "@xxmahdipy"
RCD = 1
RDT = .1
RES = 20000
OBV = "ob55"
RF = False
RAF = {"ME": ACCOUNTS_FILE}
ADMIN_UID = "11877711994"

CURRENT_GHOST_NAME = "[C][b][FF00FF]insta:37_rl"

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

INSTAGRAM = "37_rl"
TELEGRAM = "xxmahdipy"
OWNER_NAME = "XxMAHDI.py"

YOUTUBE_URL = "https://youtu.be/P0uaLRO6V1U?si=XiR792eTXFlDHuic"

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

# ==================== VOICE SYSTEM (from HELLX) ====================
class VoiceStreamer:
    def __init__(self, uid, password, region, youtube_url):
        self.uid = uid
        self.password = password
        self.region = region
        self.youtube_url = youtube_url
        self.key = xAlInAs_key
        self.iv = xAlInAs_iv
        self.token = None
        self.login_url = None
        self.timestamp = None
        self.online_ip = "98.98.162.30"
        self.online_port = 39699
        self.chat_ip = None
        self.chat_port = None
        self.voice_ip = None
        self.voice_port = None
        self.voice_region_id = None
        self.voice_secret = None
        self.voice_chat_key = None
        self.chat_region_id = None
        self.team_owner_uid = None
        self.region_prefix = "ME"
        self.ext_region = "ME"
        self._sdk_verify_domain = "ff.rtc.grtc.garenanow.com"
        self.writer = None
        self._voice_writer = None
        self._voice_reader = None
        self._voice_ping_task = None
        self._voice_connect_task = None
        self._processed_invite_code = None
        self.voice_candidates = []
        self.opus_bitrate = 18000
        self.opus_samplerate = 16000
        self.opus_channels = 1
        self.voice_ssrc = b'\x0c\x43\x03\x3e'
        self._voice_f5 = 0
        self._voice_f3 = 0x13e6
        self._voice_heartbeat_interval = 5.0
        self._voice_ip = None
        self._voice_port = None
        self._udp_task = None
        self._current_ogg = None
        self._track_title = ""
        self._track_channel = ""
        self._track_total_frames = 0
        self._track_current_frame = 0
        self._progress_task = None
        self._stopped_frame = 0
        self._volume = 100
        self._lyrics_enabled = False
        self._lyrics_data = []
        self._lyrics_task = None

    async def _handle_tcp_data(self, data):
        buffer = bytearray(data)
        pos = 0
        while pos < len(buffer) - 5:
            opcode = buffer[pos]
            length = struct.unpack('>I', buffer[pos+1:pos+5])[0]
            if 0 < length < 200000 and pos + 5 + length <= len(buffer):
                payload = bytes(buffer[pos+5:pos+5+length])
                try:
                    proto_data = HELLXdecode_proto(payload)
                    if not proto_data:
                        pos += 5 + length
                        continue
                    field5 = proto_data.get('5')
                    if isinstance(field5, dict):
                        code = field5.get('8')
                        owner_uid = field5.get('1', self.uid)
                        if code and isinstance(code, str) and '_' in code:
                            if code != self._processed_invite_code:
                                self._processed_invite_code = code
                                accept_pkt = HELLXbuild_accept_invite(owner_uid, code, self.key, self.iv)
                                if self.writer:
                                    self.writer.write(accept_pkt)
                                    await self.writer.drain()
                                    HELLXlog("TEAM", f"Invitation accepted. code={code}")
                    if not self.voice_region_id and isinstance(field5, dict):
                        region_id = field5.get('17')
                        if region_id:
                            self.voice_region_id = int(region_id)
                            self.chat_region_id = int(self.voice_region_id / 256 + 0.5) * 256
                            self.team_owner_uid = int(field5.get('1', self.uid))
                            HELLXlog("TEAM", f"region_id={self.voice_region_id} owner={self.team_owner_uid}")
                            chat_key = field5.get('31')
                            if chat_key:
                                self.voice_chat_key = str(chat_key)
                            if getattr(self, '_joining', False):
                                self._join_success = True
                            asyncio.create_task(self._connect_chat())
                            if not self._voice_connect_task or self._voice_connect_task.done():
                                self._voice_connect_task = asyncio.create_task(self._voice_connect())
                    if isinstance(field5, dict):
                        sender_uid_online = str(field5.get('1', ''))
                        message_online = field5.get('4', '')
                        if isinstance(message_online, str) and message_online.strip() and sender_uid_online != str(self.uid):
                            HELLXlog("CHAT", f"[online][{sender_uid_online}]: {message_online}")
                except Exception:
                    pass
                pos += 5 + length
            else:
                pos += 1

    async def _voice_connect(self):
        if not self.voice_region_id:
            HELLXlog("VOICE", "ERROR: No region_id")
            return
        self._voice_f5 = 0
        self._voice_f3 = 0x13e6
        import re as _re
        import aiohttp as _aiohttp
        import struct as _st2

        async def _read_voice_frame(reader, timeout):
            header = await asyncio.wait_for(reader.readexactly(4), timeout)
            frame_length = _st2.unpack('>I', header)[0]
            if frame_length <= 0 or frame_length > 65536:
                raise ValueError(f"invalid voice frame length: {frame_length}")
            return await asyncio.wait_for(reader.readexactly(frame_length), timeout)

        sdk_token = None
        redirect_ip, redirect_port = None, None
        SDK_VERIFY_URL = f"https://{self._sdk_verify_domain}/sdk/sdk_verify"
        _SDK_VERIFY_PAYLOAD = bytes.fromhex(
            '0a8e010800100b180122074f6e65506c75732a013930cc80868c023a0961726d3634'
            '2d76386142004a2439313864346563382d383733332d343930622d626334362d643132'
            '666139396337383238522a464644353846423446373646363438433241354532314542'
            '4346413341414538314234433942374439375a05766f69636562064e45323231316802'
            '720471636f6d12800160ad4251d2f821e2701e5e1d8b607d2b34dcb0c512300ac3e5839'
            '6155780dc64686b20d05581c038ae28539fc3bc21ced330e31721e18e6c626972829f'
            '6878cb8ec7d95f2f7391bd25f9d7296f09f56f9bc5bccabaf10f09b58c39dc02c08995'
            'd6abe727d93bcea4123da86ad42f6500fa68e74ddc2ed2cb7af0aadd22d2ec93180120'
            '063800'
        )

        def _parse_sdk_response(data):
            nonlocal sdk_token, redirect_ip, redirect_port
            if len(data) < 4:
                return
            _vproto = HELLXdecode_proto(data)
            _f5 = _vproto.get('5')
            _candidates = _f5 if isinstance(_f5, list) else ([_f5] if _f5 else [])
            for _r in _candidates:
                if isinstance(_r, bytes):
                    _r = HELLXdecode_proto(_r)
                if isinstance(_r, dict):
                    _rip = _r.get('1')
                    _rport = _r.get('2')
                    if isinstance(_rip, str) and '.' in _rip and _rport:
                        redirect_ip = _rip
                        redirect_port = int(_rport)
                        HELLXlog("VOICE", f"SDK verify redirect: {redirect_ip}:{redirect_port}")
                        break
            import re as _re2
            if not redirect_ip:
                m_ip = _re2.search(rb'([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})', data)
                m_port = _re2.search(rb'\x10([\x80-\xff]?.)', data[data.find(b'\x0a\x0d') + 15:] if b'\x0a\x0d' in data else b'')
                if m_ip:
                    redirect_ip = m_ip.group(1).decode()
                    HELLXlog("VOICE", f"SDK verify redirect (regex): {redirect_ip}")
                if not redirect_port and m_port:
                    _pb = m_port.group(1)
                    if len(_pb) == 1:
                        redirect_port = _pb[0]
                    elif len(_pb) == 2 and _pb[0] & 0x80:
                        redirect_port = (_pb[0] & 0x7f) | (_pb[1] << 7)
            m_opus = _re2.search(rb'OPUS_BITRATE[\x00-\x20]{0,8}(\d{4,6})', data)
            if m_opus:
                _brate = int(m_opus.group(1).decode())
                if 8000 <= _brate <= 64000:
                    self.opus_bitrate = _brate
                    HELLXlog("VOICE", f"OPUS_BITRATE from server: {_brate}")
            _pos = 0
            while _pos < len(data) - 2:
                if data[_pos] == 0x12:
                    _p2 = _pos + 1; _vlen = 0; _shift = 0
                    while _p2 < len(data):
                        _b = data[_p2]; _vlen |= (_b & 0x7F) << _shift; _p2 += 1; _shift += 7
                        if not (_b & 0x80): break
                    if _vlen == 128 and _p2 + 128 <= len(data):
                        sdk_token = data[_p2:_p2 + 128]
                        break
                _pos += 1
            HELLXlog("VOICE", f"SDK token: {sdk_token.hex()[:32] if sdk_token else 'None'}")

        try:
            _ssl_ctx = __import__('ssl').create_default_context()
            _ssl_ctx.check_hostname = False
            _ssl_ctx.verify_mode = __import__('ssl').CERT_NONE
            async with _aiohttp.ClientSession() as _sess:
                async with _sess.post(
                    SDK_VERIFY_URL,
                    data=_SDK_VERIFY_PAYLOAD,
                    headers={
                        "Host": self._sdk_verify_domain,
                        "Accept": "*/*",
                        "Accept-Encoding": "identity",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Content-Length": str(len(_SDK_VERIFY_PAYLOAD)),
                    },
                    ssl=_ssl_ctx,
                    timeout=_aiohttp.ClientTimeout(total=8)
                ) as _resp:
                    _rbody = await _resp.read()
                    HELLXlog("VOICE", f"SDK verify HTTPS: status={_resp.status} len={len(_rbody)}")
                    if _resp.status == 200 and len(_rbody) > 4:
                        _parse_sdk_response(_rbody)
        except Exception as e:
            HELLXlog("VOICE", f"SDK verify HTTPS failed: {e}, trying TCP fallback...")

        if not redirect_ip:
            try:
                import socket as _sock
                import struct as _st3
                _infos = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: _sock.getaddrinfo(self._sdk_verify_domain, 8012, _sock.AF_INET)
                )
                _tcp_ips = list(dict.fromkeys(info[4][0] for info in _infos))
                HELLXlog("VOICE", f"SDK verify TCP fallback: DNS={_tcp_ips}")
                _tcp_pkt = _st3.pack('>I', len(_SDK_VERIFY_PAYLOAD)) + _SDK_VERIFY_PAYLOAD
                for _tip in _tcp_ips:
                    try:
                        _tr, _tw = await asyncio.wait_for(
                            asyncio.open_connection(_tip, 8012), timeout=5.0)
                        _tw.write(_tcp_pkt)
                        await _tw.drain()
                        _tbody = b""
                        try:
                            _chunk = await asyncio.wait_for(_tr.read(65536), timeout=8.0)
                            if _chunk:
                                _tbody = _chunk
                                while True:
                                    try:
                                        _more = await asyncio.wait_for(_tr.read(65536), timeout=2.0)
                                        if not _more: break
                                        _tbody += _more
                                    except asyncio.TimeoutError:
                                        break
                        except asyncio.TimeoutError:
                            pass
                        try:
                            _tw.close()
                        except Exception:
                            pass
                        if _tbody:
                            HELLXlog("VOICE", f"SDK verify TCP: {_tip}:8012 RX {len(_tbody)}B")
                            _parse_sdk_response(_tbody[4:] if len(_tbody) > 4 else _tbody)
                            if redirect_ip:
                                break
                    except Exception as _te:
                        HELLXlog("VOICE", f"SDK verify TCP {_tip} failed: {_te}")
            except Exception as e:
                HELLXlog("VOICE", f"SDK verify TCP fallback failed: {e}")

        if not redirect_ip or not redirect_port:
            HELLXlog("VOICE", "ERROR: No redirect from SDK verify")
            return
        HELLXlog("VOICE", f"Step2: {redirect_ip}:{redirect_port}")
        try:
            r2, w2 = await asyncio.wait_for(
                asyncio.open_connection(redirect_ip, redirect_port), timeout=5.0)
        except Exception as e:
            HELLXlog("VOICE", f"Step2 failed: {e}")
            return
        redir_pkt = HELLXbuild_voice_redirect(self.uid, self.voice_region_id, self.region_prefix, self.ext_region)
        HELLXlog("VOICE", f"Step2 TCP CONNECT: {redirect_ip}:{redirect_port}")
        HELLXlog("VOICE", f"Step2 REQUEST ({len(redir_pkt)}B): {redir_pkt.hex()}")
        w2.write(redir_pkt)
        await w2.drain()
        HELLXlog("VOICE", "Step2: TX sent")
        voice_ip, voice_port = None, None
        try:
            header2 = await asyncio.wait_for(r2.readexactly(4), timeout=5.0)
            response_length = struct.unpack('>I', header2)[0]
            if response_length <= 0 or response_length > 65536:
                raise ValueError(f"invalid Step2 response length: {response_length}")
            resp2 = header2 + await asyncio.wait_for(
                r2.readexactly(response_length), timeout=5.0
            )
            if resp2:
                HELLXlog("VOICE", f"Step2 RESPONSE ({len(resp2)}B): {resp2.hex()}")
                data = resp2[4:]
                proto = HELLXdecode_proto(data)
                ip_val = proto.get('1')
                port_val = proto.get('2')
                if isinstance(ip_val, str) and '.' in ip_val:
                    voice_ip = ip_val
                if isinstance(port_val, int):
                    voice_port = port_val
                HELLXlog("VOICE", f"UDP VOICE TARGET: {voice_ip}:{voice_port} (audio UDP port={voice_port + 2 if voice_port else None})")
        except asyncio.TimeoutError:
            HELLXlog("VOICE", "Step2: timeout")
        w2.close()
        if not voice_ip or not voice_port:
            HELLXlog("VOICE", "ERROR: No voice IP from redirect")
            return
        HELLXlog("VOICE", f"Step3: {voice_ip}:{voice_port}")
        try:
            r3, w3 = await asyncio.wait_for(
                asyncio.open_connection(voice_ip, voice_port), timeout=5.0)
        except Exception as e:
            HELLXlog("VOICE", f"Step3 failed: {e}")
            return
        self._voice_writer = w3
        self._voice_reader = r3
        auth3 = HELLXbuild_voice_auth(self.uid, self.voice_region_id, voice_port, self.region_prefix)
        w3.write(auth3[:4])
        await w3.drain()
        w3.write(auth3[4:])
        await w3.drain()
        HELLXlog("VOICE", "Step3: TX auth type=7")
        try:
            resp3 = await _read_voice_frame(r3, 3.0)
            if resp3:
                _p = HELLXdecode_proto(resp3)
                HELLXlog("VOICE", f"Step3 resp: {_p}")
                self._voice_f3 = int(_p.get('3', 0x13e6))
                f5_value = _p.get('5', _p.get('13', 0))
                if isinstance(f5_value, dict):
                    f5_value = f5_value.get('1', 0)
                if isinstance(f5_value, list):
                    f5_value = f5_value[0] if f5_value else 0
                self._voice_f5 = int(f5_value) & 0xFFFFFFFF
                HELLXlog("VOICE", f"f5=0x{self._voice_f5:08x} f3=0x{self._voice_f3:04x}")
        except (asyncio.TimeoutError, TypeError, ValueError):
            pass
        if self._voice_f5 == 0:
            HELLXlog("VOICE", "f5=0 detected, wrong MCU session. Sending warning to chat...")
            asyncio.create_task(self._send_chat_message(
                "[F52727]Wrong IPs detected, please wait, i will handle!\n"
                "[A627F5]If voice still not coming, please contact:\n"
                "[27EBF5]Make bot leave and create a new team -> invite it.\n"
                "[F227F5]Leave command => !leave or /help"
            ))
            try:
                w3.close()
                await w3.wait_closed()
            except Exception:
                pass
            self._voice_writer = None
            self._voice_reader = None
            await asyncio.sleep(3)
            self._voice_connect_task = asyncio.create_task(self._voice_connect())
            return
        custom = HELLXbuild_voice_custom(self.uid, self.voice_region_id, mcu_ip=voice_ip, region_prefix=self.region_prefix)
        w3.write(custom[:4])
        await w3.drain()
        w3.write(custom[4:])
        await w3.drain()
        HELLXlog("VOICE", "Step3: TX custom binary")
        try:
            resp4 = await _read_voice_frame(r3, 3.0)
            if resp4:
                HELLXlog("VOICE", f"Custom resp: {resp4.hex()[:80]}")
                raw = resp4[4:] if resp4[:4] != b'\xfe\xff\xff\x7f' else resp4
                idx = raw.find(b'\xfe\xff\xff\x7f')
                if idx != -1:
                    ts_idx = raw.find(b'\x17\x76', idx)
                    if ts_idx != -1 and ts_idx + 6 <= len(raw):
                        self.voice_session_ts = raw[ts_idx+2:ts_idx+6]
                        HELLXlog("VOICE", f"session_ts: {self.voice_session_ts.hex()}")
        except asyncio.TimeoutError:
            pass
        if self._voice_ping_task:
            self._voice_ping_task.cancel()
        self._voice_ping_task = asyncio.create_task(
            self._voice_ping_loop(w3, r3)
        )
        self._voice_ip = voice_ip
        self._voice_port = voice_port
        async def _voice_tcp_reader():
            try:
                while True:
                    try:
                        data = await _read_voice_frame(r3, 30.0)
                    except (asyncio.IncompleteReadError, ConnectionError):
                        HELLXlog("VOICE", "TCP: Server closed connection!")
                        if self._udp_task and not self._udp_task.done():
                            self._udp_task.cancel()
                        break
                    HELLXlog("VOICE", f"TCP RX: {len(data)}B hex={data.hex()}")
                    try:
                        p = HELLXdecode_proto(data)
                        inner = p.get('1', {})
                        pkt_type = inner.get('1', 0) if isinstance(inner, dict) else 0
                        field2 = p.get('2', 0)
                        if pkt_type == 0x0b and field2:
                            HELLXlog("VOICE", f"TCP: 0x0b received, re-sending auth type=7")
                            self._voice_ssrc_refresh = True
                            async def _do_reauth():
                                auth3 = HELLXbuild_voice_auth(self.uid, self.voice_region_id, voice_port, self.region_prefix)
                                w3.write(auth3[:4]); await w3.drain()
                                w3.write(auth3[4:]); await w3.drain()
                                custom = HELLXbuild_voice_custom(self.uid, self.voice_region_id, mcu_ip=voice_ip, region_prefix=self.region_prefix)
                                w3.write(custom[:4]); await w3.drain()
                                w3.write(custom[4:]); await w3.drain()
                                HELLXlog("VOICE", "TCP: Re-auth sent")
                            asyncio.create_task(_do_reauth())
                    except Exception:
                        pass
            except Exception as e:
                HELLXlog("VOICE", f"TCP reader error: {e}")
        asyncio.create_task(_voice_tcp_reader())
        HELLXlog("VOICE", f"Step3: Done. Streaming to {voice_ip}:{voice_port+2}")
        asyncio.create_task(self._play_yt(self.youtube_url))

    async def _leave_team(self):
        HELLXlog("TEAM", "Leaving team...")
        if self.writer:
            leave_pkt = HELLXbuild_leave_team(int(self.uid), self.key, self.iv)
            self.writer.write(leave_pkt)
            await self.writer.drain()
        if self._chat_writer:
            try:
                close_pkt = HELLXbuild_chat_close(int(self.uid), self.key, self.iv)
                self._chat_writer.write(close_pkt)
                await self._chat_writer.drain()
            except Exception:
                pass
        if self._udp_task and not self._udp_task.done():
            self._udp_task.cancel()
        if self._progress_task and not self._progress_task.done():
            self._progress_task.cancel()
        if self._voice_ping_task and not self._voice_ping_task.done():
            self._voice_ping_task.cancel()
        if self._voice_connect_task and not self._voice_connect_task.done():
            self._voice_connect_task.cancel()
        self.voice_region_id = None
        self.chat_region_id = None
        self.team_owner_uid = None
        self.voice_chat_key = None
        self._processed_invite_code = None
        self._voice_ip = None
        self._voice_port = None
        self._voice_writer = None
        self._voice_reader = None
        self._current_ogg = None
        self._track_title = ""
        self._track_channel = ""
        self._track_total_frames = 0
        self._track_current_frame = 0
        self._stopped_frame = 0
        HELLXlog("TEAM", "Left team. Waiting for new invite...")

    async def _connect_chat(self):
        if not self._chat_writer or self._chat_writer.transport.is_closing():
            HELLXlog("CHAT", "No chat connection!")
            return
        if not self.voice_region_id:
            return
        try:
            w = self._chat_writer
            owner = self.team_owner_uid if self.team_owner_uid else int(self.uid)
            auth_pkt = HELLXbuild_chat_auth(owner, str(self.chat_region_id), self.key, self.iv)
            w.write(auth_pkt)
            await w.drain()
            HELLXlog("CHAT", f"Auth sent (owner={owner} region={self.chat_region_id})")
        except Exception as e:
            HELLXlog("CHAT", f"Chat auth failed: {e}")

    async def _chat_read_loop(self, reader):
        try:
            while True:
                data = await reader.read(16384)
                if not data:
                    HELLXlog("CHAT", "Disconnected — reconnecting...")
                    asyncio.create_task(self._reconnect_chat())
                    break
                await self._handle_chat_data(data)
        except Exception as e:
            HELLXlog("CHAT", f"Error: {e} — reconnecting...")
            asyncio.create_task(self._reconnect_chat())

    async def _reconnect_chat(self):
        await asyncio.sleep(2)
        if not self.chat_ip or not self.chat_port:
            return
        try:
            auth_hex = HELLXbuild_auth_startup(self.uid, self.token, self.timestamp, self.key, self.iv)
            cr, cw = await asyncio.wait_for(
                asyncio.open_connection(self.chat_ip, self.chat_port), timeout=5.0)
            self._chat_reader = cr
            self._chat_writer = cw
            cw.write(bytes.fromhex(auth_hex))
            await cw.drain()
            HELLXlog("CHAT", "Reconnected")
            if self.voice_region_id and self.team_owner_uid:
                owner = self.team_owner_uid
                auth_pkt = HELLXbuild_chat_auth(owner, str(self.chat_region_id), self.key, self.iv)
                cw.write(auth_pkt)
                await cw.drain()
            asyncio.create_task(self._chat_read_loop(cr))
            asyncio.create_task(self._chat_keepalive_loop(cw))
        except Exception as e:
            HELLXlog("CHAT", f"Reconnect failed: {e}")

    async def _handle_chat_data(self, data: bytes):
        self._chat_buffer.extend(data)
        buffer = self._chat_buffer
        pos = 0
        while len(buffer) - pos >= 5:
            length = struct.unpack('>I', buffer[pos+1:pos+5])[0]
            if 0 < length < 200000 and pos + 5 + length <= len(buffer):
                payload = bytes(buffer[pos+5:pos+5+length])
                try:
                    proto_data = HELLXdecode_proto(payload)
                    if proto_data:
                        field5 = proto_data.get('5')
                        if isinstance(field5, dict):
                            sender_uid = str(field5.get('1', ''))
                            message = field5.get('4', '')
                            msg_type = field5.get('3', 0)
                            sender_name = ""
                            f9 = field5.get('9', {})
                            if isinstance(f9, dict):
                                sender_name = str(f9.get('1', ''))
                            if isinstance(message, str) and message.strip() and sender_uid != str(self.uid):
                                HELLXlog("CHAT", f"[{sender_name}|{sender_uid}]: {message}")
                                if str(msg_type) == '2':
                                    asyncio.create_task(self._handle_dm(message.strip(), sender_name, sender_uid))
                                else:
                                    asyncio.create_task(self._handle_command(message.strip(), sender_name, sender_uid))
                        self._scan_for_commands(proto_data)
                except Exception as e:
                    HELLXlog("CHAT", f"Parse error: {e}")
                pos += 5 + length
            else:
                if length <= 0 or length >= 200000:
                    pos += 1
                else:
                    break
        if pos:
            del buffer[:pos]

    def _scan_for_commands(self, obj, depth=0):
        if depth > 5:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and v.strip().lower() == '/leave':
                    asyncio.create_task(self._leave_team())
                elif isinstance(v, (dict, list)):
                    self._scan_for_commands(v, depth+1)
        elif isinstance(obj, list):
            for item in obj:
                self._scan_for_commands(item, depth+1)

    async def _chat_keepalive_loop(self, writer):
        try:
            while writer and not writer.transport.is_closing():
                await asyncio.sleep(5)
                try:
                    writer.write(bytes.fromhex('0201'))
                    await writer.drain()
                except Exception:
                    break
        except asyncio.CancelledError:
            pass

    async def _send_chat_message(self, message: str):
        if not self._chat_writer:
            HELLXlog("CHAT", "No writer!")
            return
        try:
            import time as _t
            ts = int(_t.time())
            owner = self.team_owner_uid if self.team_owner_uid else int(self.uid)
            pkt = await HELLXbuild_chat_message(int(self.uid), owner, message, ts, self.key, self.iv)
            self._chat_writer.write(pkt)
            await self._chat_writer.drain()
            HELLXlog("CHAT", f"Sent: {message[:60]}")
        except Exception as e:
            import traceback
            HELLXlog("CHAT", f"Send error: {e} | {traceback.format_exc()[-200:]}")

    async def _voice_ping_loop(self, writer, reader):
        try:
            counter = 0
            while writer and not writer.transport.is_closing():
                await asyncio.sleep(5)
                try:
                    session_id = getattr(self, '_voice_f3', 0x0b)
                    ping_pkt = HELLXbuild_voice_ping(self.uid, self.voice_region_id, self.voice_port, session_id)
                    writer.write(ping_pkt)
                    await writer.drain()
                    counter += 1
                except Exception as e:
                    HELLXlog("VOICE", f"TCP ping error: {e}")
                    break
        except asyncio.CancelledError:
            pass

    async def _play_yt(self, url: str, lyrics: bool = False):
        import subprocess, tempfile as _tmp, os as _os
        if self._udp_task and not self._udp_task.done():
            self._udp_task.cancel()
            await asyncio.sleep(0.5)
        if not self._voice_ip or not self._voice_port:
            await self._send_chat_message("[27EBF5]Voice connection is still starting, please wait...")
            deadline = asyncio.get_running_loop().time() + 20.0
            while (not self._voice_ip or not self._voice_port) and asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(0.25)
            if not self._voice_ip or not self._voice_port:
                await self._send_chat_message("[F52727]Voice connection failed or timed out.")
                return
        wav_path = _tmp.mktemp(suffix='.wav')
        ogg_path = _tmp.mktemp(suffix='.opus')
        volume_val = self._volume / 100.0
        def _encode():
            import glob as _glob
            raw_path = _tmp.mktemp()
            ffmpeg_path = _ffmpeg_executable()
            subprocess.run([
                *_yt_dlp_command(), "-x",
                "--audio-format", "wav",
                "--audio-quality", "0",
                "--ffmpeg-location", ffmpeg_path,
                "-o", raw_path + ".%(ext)s",
                "--no-playlist", url
            ], check=True, capture_output=True, text=True)
            matches = _glob.glob(raw_path + ".*")
            if not matches:
                raise Exception("yt-dlp produced no output file")
            raw_file = matches[0]
            HELLXlog("VOICE", f"Downloaded: {raw_file} ({_os.path.getsize(raw_file)} bytes)")
            subprocess.run([
                _ffmpeg_executable(), "-loglevel", "quiet", "-y",
                "-i", raw_file,
                "-ar", "16000", "-ac", "1",
                "-af", f"volume={volume_val},loudnorm=I=-16:TP=-1.5:LRA=11",
                wav_path
            ], check=True)
            HELLXlog("VOICE", f"Resampled: {wav_path} ({_os.path.getsize(wav_path)} bytes)")
            try: _os.unlink(raw_file)
            except: pass
            subprocess.run([
                r"C:\Users\axira\Documents\LVL UP\opus\opus\opusenc.exe",
                "--speech", "--bitrate", str(self.opus_bitrate // 1000), "--hard-cbr",
                "--framesize", "20", "--quiet", wav_path, ogg_path
            ], check=True)
            data = open(ogg_path, 'rb').read()
            HELLXlog("VOICE", f"Encoded: {len(data)} bytes opus")
            try: _os.unlink(wav_path)
            except: pass
            try: _os.unlink(ogg_path)
            except: pass
            return data
        loop = asyncio.get_event_loop()
        try:
            ogg_data = await loop.run_in_executor(None, _encode)
        except Exception as e:
            await self._send_chat_message(f"[F52727]Download failed: {str(e)[:60]}")
            return
        self._current_ogg = ogg_data
        self._track_total_frames = len(list(_ogg_opus_frames_bytes(ogg_data)))
        self._track_current_frame = 0
        self._udp_task = asyncio.create_task(
            self._voice_udp_loop(self._voice_ip, self._voice_port, ogg_data=ogg_data)
        )
        if self._progress_task and not self._progress_task.done():
            self._progress_task.cancel()
        self._progress_task = asyncio.create_task(self._auto_progress_loop())

    async def _auto_progress_loop(self):
        try:
            await asyncio.sleep(15)
            while self._udp_task and not self._udp_task.done():
                if self._track_total_frames > 0:
                    frame = self._track_current_frame
                    total = self._track_total_frames
                    elapsed_s = int(frame * 0.02)
                    total_s = int(total * 0.02)
                    pct = min(frame / total, 1.0)
                    bar_len = 16
                    filled = int(bar_len * pct)
                    bar = "[27EBF5]" + "\u25a0" * filled + "[5427F5]" + "\u25a1" * (bar_len - filled)
                    elapsed_str = f"{elapsed_s//60}:{elapsed_s%60:02d}"
                    total_str = f"{total_s//60}:{total_s%60:02d}"
                    playing = not self._udp_task.done()
                    status = "[27EBF5]\u25b6" if playing else "[F52727]\u23f8"
                    await self._send_chat_message(
                        f"{status} [5427F5]{self._track_title[:38]}\n"
                        f"[A627F5]{self._track_channel[:30]}\n"
                        f"{bar}\n"
                        f"[27EBF5]{elapsed_str} [F227F5]/ [27EBF5]{total_str}  "
                        f"[A627F5]Vol:{self._volume}%"
                    )
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            pass

    async def _voice_udp_loop(self, ip: str, port: int, encode_task=None, ogg_data: bytes = None, start_frame: int = 0):
        import socket as _sock
        import struct as _st
        import time as _time
        udp_port = port + 2
        if ogg_data is None and encode_task is not None:
            ogg_data = await encode_task
        if not ogg_data:
            HELLXlog("VOICE", "UDP: No audio data")
            return
        frames = list(_ogg_opus_frames_bytes(ogg_data))
        converted = []
        for f in frames:
            if f[0] == 0x78:
                continue
            if f[0] == 0x4b and len(f) > 2 and f[1] == 0x01:
                converted.append(bytes([0x48]) + f[2:])
            else:
                converted.append(f)
        frames = converted
        HELLXlog("VOICE", f"UDP: Streaming {len(frames)} frames from {start_frame} to {ip}:{udp_port}")
        udp = _sock.socket(_sock.AF_INET, _sock.SOCK_DGRAM)
        magic = b'\x41\x6f'
        import random as _random
        seq = _random.randint(0, 0xFFFF)
        ts = _random.randint(0, 0xFFFFFFFF)
        FRAME_SAMPLES = 0x3c0
        FRAME_DURATION = 0.020
        f3_val = getattr(self, '_voice_f3', 0x13e6)
        FIXED_2 = b'\x00\x00' + f3_val.to_bytes(2, 'big')
        mic_open = b'\x71\x5c\x35\x07\x00\x00\x00\x00\x80\x02\x00\x00\x00\x00' + f3_val.to_bytes(2, 'big')
        udp.setblocking(False)
        loop = asyncio.get_running_loop()
        udp_rx_count = 0

        async def _udp_receiver():
            nonlocal udp_rx_count
            try:
                while True:
                    packet, address = await loop.sock_recvfrom(udp, 4096)
                    udp_rx_count += 1
                    if udp_rx_count <= 5 or udp_rx_count % 100 == 0:
                        HELLXlog(
                            "VOICE",
                            f"UDP RX: #{udp_rx_count} {len(packet)}B from {address} hex={packet[:32].hex()}"
                        )
            except asyncio.CancelledError:
                pass
            except (ConnectionError, OSError) as e:
                HELLXlog("VOICE", f"UDP receiver stopped: {e}")

        udp_rx_task = asyncio.create_task(_udp_receiver())
        try:
            udp.sendto(mic_open, (ip, udp_port))
        except OSError as e:
            HELLXlog("VOICE", f"UDP: Failed to open voice stream: {e}")
        try:
            while True:
                seq_loop = seq
                ts_loop = ts
                loop_start = start_frame if seq_loop == seq else 0
                self._track_current_frame = loop_start
                next_send = _time.monotonic()
                for i in range(loop_start, len(frames)):
                    opus_frame = frames[i]
                    f5_val = getattr(self, '_voice_f5', 0)
                    FIXED_1 = f5_val.to_bytes(4, 'big')
                    header = _st.pack('>2sHI4s4s', magic, seq_loop & 0xFFFF, ts_loop & 0xFFFFFFFF, FIXED_1, FIXED_2)
                    try:
                        udp.sendto(header + opus_frame, (ip, udp_port))
                    except Exception:
                        pass
                    if i == loop_start:
                        HELLXlog("VOICE", f"UDP: Streaming started (frame {i})")
                    if i % 500 == 0 and i > loop_start:
                        HELLXlog("VOICE", f"UDP: Frame {i}/{len(frames)}")
                    self._track_current_frame = i
                    seq_loop = (seq_loop + 1) & 0xFFFF
                    ts_loop = (ts_loop + FRAME_SAMPLES) & 0xFFFFFFFF
                    next_send += FRAME_DURATION
                    sleep_time = next_send - _time.monotonic()
                    if sleep_time > 0:
                        try:
                            await asyncio.sleep(sleep_time)
                        except asyncio.CancelledError:
                            self._stopped_frame = i
                            HELLXlog("VOICE", f"UDP: Stopped at frame {i}")
                            raise
                seq = seq_loop
                ts = ts_loop
                start_frame = 0
                HELLXlog("VOICE", "UDP: Track finished, restarting...")
        except asyncio.CancelledError:
            HELLXlog("VOICE", "UDP: Stopped (cancelled)")
        except Exception as e:
            HELLXlog("VOICE", f"UDP: FATAL ERROR {type(e).__name__}: {e}")
        finally:
            udp_rx_task.cancel()
            try:
                await udp_rx_task
            except asyncio.CancelledError:
                pass
            udp.close()

    async def run(self):
        HELLXlog("AUTH", f"Logging in {self.uid}...")
        headers = HELLXdefault_headers()
        current_version, server_url, client_ip = await HELLXfetch_version()
        if not current_version:
            current_version = "1.126.7"
        if not server_url:
            server_url = "https://loginbp.ggpolarbear.com/"
        if not client_ip:
            client_ip = "129.45.8.219"
        HELLXlog("AUTH", f"Version={current_version} server_url={server_url} client_ip={client_ip}")
        self._current_version = current_version
        city = await HELLXfetch_city(client_ip)
        if not city:
            city = "Oran"
        HELLXlog("AUTH", f"GeoCity={city}")
        open_id, access_token = await HELLXgenerate_access(self.uid, self.password, headers['User-Agent'])
        if not open_id:
            HELLXlog("AUTH", "OAuth Failed")
            return
        HELLXlog("AUTH", "OAuth Success. Sending MajorLogin...")
        major_payload = HELLXbuild_major_login(open_id, access_token, version=current_version, client_ip=client_ip, city=city)
        major_resp = await HELLXmajor_login(major_payload, headers, server_url=server_url)
        if not major_resp:
            HELLXlog("AUTH", "MajorLogin Failed")
            return
        major_proto = HELLXdecode_major_login(major_resp)
        HELLXlog("AUTH", f"MajorLogin raw: {major_resp.hex()[:80]}")
        _raw_p = HELLXdecode_proto(major_resp)
        HELLXlog("AUTH", f"MajorLogin proto keys: {list(_raw_p.keys())}")
        self.token = getattr(major_proto, 'token', None) or _raw_p.get('8') or None
        self.login_url = getattr(major_proto, 'url', None) or _raw_p.get('10') or None
        proto_ts = getattr(major_proto, 'timestamp', None) or _raw_p.get('21')
        self.timestamp = int(proto_ts) if proto_ts else int(time.time())
        account_uid = getattr(major_proto, 'account_uid', None) or _raw_p.get('1')
        if account_uid:
            self.uid = str(account_uid)
        new_key = getattr(major_proto, 'key', None) or (_raw_p.get('22') if isinstance(_raw_p.get('22'), bytes) else None)
        new_iv = getattr(major_proto, 'iv', None) or (_raw_p.get('23') if isinstance(_raw_p.get('23'), bytes) else None)
        if new_key and len(new_key) == 16:
            self.key = new_key
            HELLXlog("AUTH", f"Dynamic KEY extracted: {self.key.hex()}")
        if new_iv and len(new_iv) == 16:
            self.iv = new_iv
            HELLXlog("AUTH", f"Dynamic IV extracted: {self.iv.hex()}")
        HELLXlog("AUTH", f"MajorLogin OK. uid={self.uid} url={self.login_url}")
        login_data_resp = await HELLXget_login_data(self.login_url, open_id, access_token, self.token, headers, version=current_version, client_ip=client_ip, city=city)
        if not login_data_resp:
            HELLXlog("AUTH", "GetLoginData Failed")
            return
        self.voice_candidates = []  
        voice_data = HELLXextract_garena_voice_data(login_data_resp)
        for entry in voice_data["idc_servers"]:
            parts = entry['ip_port'].split(':')
            ip, port = parts[0], int(parts[1])
            HELLXlog("VOICE", f"IDC Server => region={entry['region']} idc={entry['idc']} ip_port={entry['ip_port']}")
            if entry['idc'] == 'IDC2':
                self.voice_ip = ip
                self.voice_port = port
                self.voice_candidates.insert(0, (ip, port))
            else:
                self.voice_candidates.append((ip, port))
        if voice_data["webrtc"]:
            w = voice_data["webrtc"]
            HELLXlog("VOICE", f"WebRTC Fallback => domains={w['domains']} ips={w['ips']}")
            sdk_domains = w.get('domains', [])
            if sdk_domains:
                first_domain = sdk_domains[0]
                self._sdk_verify_domain = first_domain
        region_val = _raw_p.get('2') or _raw_p.get('3')
        if region_val and isinstance(region_val, str) and region_val.isalpha():
            self.region_prefix = region_val.upper()
            _region_to_ext = {
                'EUROPE': 'eu', 'VN': 'vn', 'SA': 'sa', 'BR': 'br',
                'ID': 'id', 'TW': 'tw', 'TH': 'th', 'SG': 'sg',
                'ME': 'me', 'IND': 'in', 'NA': 'na', 'LATAM': 'la',
            }
            _region_to_sdk_domain = {
                'EUROPE': 'ff.rtc.grtc.garenanow.com',
                'VN': 'ff.rtc.grtc.garenanow.com',
                'SA': 'ff.rtc.grtc.garenanow.com',
                'BR': 'ff.rtc.grtc.garenanow.com',
                'ID': 'ff.rtc.grtc.garenanow.com',
                'TW': 'ff.rtc.grtc.garenanow.com',
                'TH': 'ff.rtc.grtc.garenanow.com',
                'SG': 'ff.rtc.grtc.garenanow.com',
                'ME': 'ff.rtc.grtc.garenanow.com',
                'IND': 'ff.rtc.grtc.garenanow.com',
            }
            self.ext_region = _region_to_ext.get(self.region_prefix, self.region_prefix.lower()[:2])
            if not voice_data.get("webrtc"):
                self._sdk_verify_domain = _region_to_sdk_domain.get(self.region_prefix, 'ff.rtc.grtc.garenanow.com')
            HELLXlog("AUTH", f"Region prefix: {self.region_prefix} ext: {self.ext_region} sdk_domain: {self._sdk_verify_domain}")
        ld_proto = HELLXdecode_login_data(login_data_resp)
        online_port_str = getattr(ld_proto, 'Online_IP_Port', None) or getattr(ld_proto, 'online_ip_port', None)
        account_port_str = getattr(ld_proto, 'AccountIP_Port', None) or getattr(ld_proto, 'account_ip_port', None)
        if online_port_str and ':' in online_port_str:
            parts = online_port_str.split(":")
            self.online_ip = parts[0]
            self.online_port = int(parts[1])
            HELLXlog("NETWORK", f"Online Server from GetLoginData: {self.online_ip}:{self.online_port}")
        if account_port_str and ':' in account_port_str:
            parts = account_port_str.split(":")
            self.chat_ip = parts[0]
            self.chat_port = int(parts[1])
            HELLXlog("NETWORK", f"Chat Server from GetLoginData: {self.chat_ip}:{self.chat_port}")
        auth_hex = HELLXbuild_auth_startup(self.uid, self.token, self.timestamp, self.key, self.iv)
        if self.chat_ip and self.chat_port:
            try:
                cr, cw = await asyncio.wait_for(
                    asyncio.open_connection(self.chat_ip, self.chat_port), timeout=5.0)
                self._chat_reader = cr
                self._chat_writer = cw
                cw.write(bytes.fromhex(auth_hex))
                await cw.drain()
                HELLXlog("CHAT", f"Early connect + startup auth sent ({self.chat_ip}:{self.chat_port})")
                asyncio.create_task(self._chat_read_loop(cr))
                asyncio.create_task(self._chat_keepalive_loop(cw))
            except Exception as e:
                HELLXlog("CHAT", f"Early connect failed: {e}")
        HELLXlog("NETWORK", f"Connecting to Online Server ({self.online_ip}:{self.online_port})...")
        reader, writer = await HELLXconnect_online(self.online_ip, self.online_port, auth_hex)
        if not writer:
            return
        self.writer = writer
        asyncio.create_task(HELLXping_loop(writer, HELLXbuild_ping_packet, self.key, self.iv))
        await HELLXread_loop(reader, self._handle_tcp_data, self.key, self.iv)

# ==================== END VOICE SYSTEM ====================

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
                                last_send = 1
                                while time.time() < deadline:
                                    if RF or not self)
.running:
                                        break
                                    if time.time()                                - last_send > JOIN_REFRESH:
                                        try sock:
                                            sock.sendall(Join_Sq(key, iv_ch))
                                            last_send = time.time()
                                        except:
                                            breakat
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
                                sock_chat.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, .settimeout(6.0)
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

                            # ==================== [تعديل] تشغيل الصوت ====================
                            if HAS_VOICE_MODULE:
                                try:
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                    voice_bot = VoiceStreamer(self.uid, self.password, self.region, YOUTUBE_URL)
                                    loop.run_until_complete(voice_bot.run())
                                except Exception as e:
                                    with lock: console.print(f"[red]VOICE MODULE ERROR: {e}[/red]")
                            # ====================================================================

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

# ==================== سيرفر الويب (Render) ====================
app = FastAPI()

@app.get("/")
def index():
    return {"status": "Ghost Server is Running on Render"}

@app.on_event("startup")
def startup_event():
    console.print("[bold green]SCRIPT STARTED ON RENDER[/bold green]")
    threading.Thread(target=xAlInAs_restart_loop, daemon=True).start()
    threading.Thread(target=xAlInAs_start_all, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
