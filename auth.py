import aiohttp
import ssl
import random
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from encrypt import HELLXenc_packet
from proto import HELLXcreate_proto, HELLXgenerate_packet, HELLXgenerate_packet_plain, HELLXenc_varint
from Pb2 import MajoRLoGinrEs_pb2, PorTs_pb2


async def HELLXfetch_version():
    url = (
        "https://version.common.redflamenco.com/live/ver.php"
        "?version=1.129.1&lang=tr&device=android&channel=android"
        "&appstore=googleplay&region=EUROPE&release_version=OB54"
        "&whitelist_version=1.6.0&whitelist_sp_version=1.0.0"
        "&device_name=samsung%20SM-S9210"
        "&device_CPU=x86-64%20SSE3%20SSE4.1%20SSE4.2%20AVX%20AVX2"
        "&device_GPU=Adreno%20%28TM%29%20640&device_mem=1999"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    ver = data.get("remote_version", "")
                    server_url = data.get("server_url", "")
                    client_ip = data.get("client_ip", "")
                    return ver, server_url, client_ip
    except Exception as e:
        print(f"HELLX => [VERSION]: {e}")
    return "", "", ""

async def HELLXfetch_city(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,city"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("status") == "success":
                        return data.get("city", "")
    except Exception as e:
        print(f"HELLX => [GEOIP]: {e}")
    return ""


async def HELLXgenerate_access(uid, password, user_agent):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={
            "Host": "100067.connect.garena.com",
            "User-Agent": user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close"
        }, data=data) as response:
            if response.status != 200:
                return None, None
            res_data = await response.json()
            return res_data.get("open_id"), res_data.get("access_token")
def HELLXbuild_major_login(open_id, access_token, version, client_ip, city):
    fields = {
        3: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        4: "free fire",
        5: 1,
        7: version,
        8: "Android OS 9 / API-28 (PQ3B.190801.03250903/G9650ZHU2ARC6)",
        9: "Handheld",
        10: "Verizon",
        11: "WIFI",
        12: 1600,
        13: 900,
        14: "240",
        15: "x86-64 SSE3 SSE4.1 SSE4.2 AVX | 2865 | 3",
        16: 3946,
        17: "Adreno (TM) 640",
        18: "OpenGL ES 3.1 v1",
        19: "Google|b3767319-e502-42db-863e-0eafd4beb3cd",
        20: client_ip,
        21: "en",
        22: open_id,
        23: "4",
        24: "Handheld",
        25: "OnePlus NE2210",
        29: access_token,
        30: 1,
        41: "Verizon",
        42: "WIFI",
        57: "7428b253defc164018c604a1ebbfebdf",
        60: 56882,
        61: 50521,
        62: 2519,
        63: 734,
        64: 24757,
        65: 28108,
        66: 53002,
        67: 56882,
        73: 3,
        74: "/data/app/com.dts.freefireth-DyYEGJRFB_Wufw2ceipWLA==/lib/arm64",
        76: 1,
        77: "17e6a447803a17e4f59e3fd734efc5ae|/data/app/com.dts.freefireth-DyYEGJRFB_Wufw2ceipWLA==/base.apk",
        78: 3,
        79: 2,
        81: "64",
        83: "2019120816",
        85: 3,
        86: "OpenGLES2",
        87: 255,
        88: 4,
        90: city,
        91: "31",
        92: 98752,
        93: "android",
        94: "KqsHTxi8NTI80hue8OYkMmXjneb2kl6Wo6xIUjCxACYxyAgAfyJGjPbYv0QOmhyvPcfYQ/GeihoVwOSzZGpCrfHOh+E=",
        96: "{\"cur_rate\":null,\"support_etc2\":false}",
        97: 1,
        98: 1,
        99: "4",
        100: "4",
        102: "\x13\x06MG\x04\\Y\x04\x18\x01\\C\\Q\x10\x0eBg\nU\\R\x04}\x01Pp\nVZhY\x010",
    }
    proto_bytes = HELLXcreate_proto(fields)
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(proto_bytes, AES.block_size))
def HELLXbuild_get_login_data_payload(open_id, access_token, version="1.126.7", client_ip="129.45.8.219", city="Oran"):
    fields = {
        3: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        4: "free fire",
        5: 1,
        7: version,
        8: "Android OS 9 / API-28 (PQ3B.190801.03250903/G9650ZHU2ARC6)",
        9: "Handheld",
        10: "Verizon",
        11: "WIFI",
        12: 1600,
        13: 900,
        14: "240",
        15: "x86-64 SSE3 SSE4.1 SSE4.2 AVX | 2865 | 3",
        16: 3946,
        17: "Adreno (TM) 640",
        18: "OpenGL ES 3.1 v1",
        19: "Google|b3767319-e502-42db-863e-0eafd4beb3cd",
        20: client_ip,
        21: "en",
        22: open_id,
        23: "4",
        24: "Handheld",
        25: "OnePlus NE2210",
        29: access_token,
        30: 1,
        41: "Verizon",
        42: "WIFI",
        57: "7428b253defc164018c604a1ebbfebdf",
        60: 56882,
        61: 50521,
        62: 2519,
        63: 734,
        64: 24757,
        65: 28108,
        66: 53002,
        67: 56882,
        73: 3,
        74: "/data/app/com.dts.freefireth-DyYEGJRFB_Wufw2ceipWLA==/lib/arm64",
        76: 1,
        77: "17e6a447803a17e4f59e3fd734efc5ae|/data/app/com.dts.freefireth-DyYEGJRFB_Wufw2ceipWLA==/base.apk",
        78: 3,
        79: 2,
        81: "64",
        83: "2019120816",
        85: 3,
        86: "OpenGLES2",
        87: 255,
        88: 4,
        90: city,
        91: "31",
        92: 98752,
        93: "android",
        94: "KqsHTxi8NTI80hue8OYkMmXjneb2kl6Wo6xIUjCxACYxyAgAfyJGjPbYv0QOmhyvPcfYQ/GeihoVwOSzZGpCrfHOh+E=",
        96: "{\"cur_rate\":null,\"support_etc2\":false}",
        97: 1,
        98: 1,
        99: "0",
        100: "4",
        102: "\x13\x06MG\x04\\Y\x04\x18\x01\\C\\Q\x10\x0eBg\nU\\R\x04}\x01Pp\nVZhY\x010",
        103: 1,
    }
    proto_bytes = HELLXcreate_proto(fields)
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(proto_bytes, AES.block_size))
async def HELLXmajor_login(payload, headers, server_url="https://loginbp.ggpolarbear.com/"):
    if not server_url.startswith("http"):
        server_url = "https://" + server_url
    url = server_url.rstrip("/") + "/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None
async def HELLXget_login_data(base_url, open_id, access_token, token, headers, version="1.126.7", client_ip="129.45.8.219", city="Oran"):
    if not base_url:
        print(f"HELLX => [AUTH]: GetLoginData FAILED - Invalid URL: '{base_url}'")
        return None
    if not base_url.startswith("http"):
        base_url = "https://" + base_url
    url = f"{base_url}/GetLoginData"
    payload = HELLXbuild_get_login_data_payload(open_id, access_token, version, client_ip, city)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    current_headers = headers.copy()
    current_headers['Authorization'] = f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=payload, headers=current_headers, ssl=ssl_context, timeout=30) as response:
                if response.status == 200:
                    return await response.read()
                print(f"HELLX => [AUTH]: GetLoginData HTTP {response.status} from {url}")
                return None
        except Exception as e:
            print(f"HELLX => [AUTH]: GetLoginData Exception: {e}")
            return None
def HELLXdecode_major_login(response_bytes):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(response_bytes)
    return proto
def HELLXdecode_login_data(response_bytes):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(response_bytes)
    return proto
def HELLXbuild_auth_startup(uid, token, timestamp, key, iv):
    uid_hex = hex(int(uid))[2:]
    uid_length = len(uid_hex)
    r = hex(timestamp)
    f = str(r)[2:]
    if len(f) == 1:
        f = "0" + f
    encrypted_timestamp = f
    encrypted_account_token = token.encode().hex()
    encrypted_packet = HELLXenc_packet(encrypted_account_token, key, iv)
    length_val = len(encrypted_packet) // 2
    length_hex = hex(length_val)[2:].zfill(4)
    if uid_length == 9:
        headers = '0000000'
    elif uid_length == 8:
        headers = '00000000'
    elif uid_length == 10:
        headers = '000000'
    elif uid_length == 7:
        headers = '000000000'
    else:
        headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}0000{length_hex}{encrypted_packet}"
_PKT2_INNER_BLOB = bytes.fromhex(
    '6db490eb03aadf4f1901d5762b2a15959a10cd867a845c4105a27aed4faad29b'
    '6889119641a5e0ec13d3a25855acfc12635979c40be6d74ab1c3023b9c664eaf'
    '3e4d75d02cf7233a056713efa599142bffa45cb0e1a3b8099ec0cd50ce3a5544'
    '69559bf663164e1a3577aa6e3f019a7103ef6d153ef39d18525499628c76cf5a'
    '0cdb0ea3001a6080bd5caf27684934e656eec792ca6096a57e9f0091ed07b78b'
    '2f2dc58993c2fdad15bf0b001c26d8dfd28cd217407d7e04bac5651d75cfeb60'
    '94213583a836566fa7425881bdfd915f25c00e469de2ffcaf975d799547101bd'
    'a95b4a9b38bb5555e37cce84fc515596f03f6f513b4e6332b4283fc68543fe35'
    '96272093a1bf4989438a99272b482addabd7910dad1031efa836d3bfdfb26cb6'
    'd9a718fb7852820722507692393161f747d74e1e95874911f3334f9e5ac6bd17'
    '998d094696e736db326314b4301644717e22a280a0aa33b5a07e7609e127b9ad'
    '803afa3291407088d76e35eac163f951a0fc1349d3db022e63b0670fea37585c'
    '15151c4f032174cbcf01ffc9656d14846123ab1c37df3b4960c3c37234bb7d97'
    '0ec8085337e1c7f6dc3aa7761352c9257f7a00461a4cac9840918308084851e0'
    '0160a84494b2f1067711725f4b711f3140578e826a28ce142abe11871b9064a3'
    'eecffe4bae380a66bed4d20ec6'
)

def HELLXbuild_post_auth_packets(uid, jwt_token, key, iv):
    uid_hex = hex(int(uid))[2:]
    uid_len = len(uid_hex)
    if uid_len <= 8:
        uid_pad = uid_hex.zfill(8)
    elif uid_len == 9:
        uid_pad = uid_hex
    elif uid_len == 10:
        uid_pad = uid_hex
    elif uid_len == 11:
        uid_pad = uid_hex
    else:
        uid_pad = uid_hex

    jwt_bytes = jwt_token.encode()
    cipher1 = AES.new(key, AES.MODE_CBC, iv)
    enc_jwt = cipher1.encrypt(pad(jwt_bytes, AES.block_size))
    enc_len_hex = hex(len(enc_jwt))[2:].zfill(8)
    pkt1 = bytes.fromhex('830c' + enc_len_hex + uid_pad) + enc_jwt

    inner = _PKT2_INNER_BLOB
    inner_len_varint = HELLXenc_varint(len(inner))
    field1_tag = b'\x0a'
    inner_wrapped = field1_tag + inner_len_varint + inner
    field2_content = HELLXenc_varint(2) + HELLXenc_varint(len(inner_wrapped)) + inner_wrapped
    pkt2_proto = b'\x08\x02\x12' + HELLXenc_varint(len(inner_wrapped)) + inner_wrapped
    cipher2 = AES.new(key, AES.MODE_CBC, iv)
    enc2 = cipher2.encrypt(pad(pkt2_proto, AES.block_size))
    enc2_len_hex = hex(len(enc2))[2:].zfill(8)
    pkt2 = bytes.fromhex('280c' + enc2_len_hex) + enc2

    fields_pkt3 = {1: 6, 2: {1: 3, 2: "2019120816", 3: 1}}
    proto3 = HELLXcreate_proto(fields_pkt3)
    cipher3 = AES.new(key, AES.MODE_CBC, iv)
    enc3 = cipher3.encrypt(pad(proto3, AES.block_size))
    enc3_len_hex = hex(len(enc3))[2:].zfill(8)
    pkt3 = bytes.fromhex('1d0c' + enc3_len_hex) + enc3

    fields_pkt4 = {1: 7, 2: b''}
    proto4 = HELLXcreate_proto(fields_pkt4)
    cipher4 = AES.new(key, AES.MODE_CBC, iv)
    enc4 = cipher4.encrypt(pad(proto4, AES.block_size))
    enc4_len_hex = hex(len(enc4))[2:].zfill(8)
    pkt4 = bytes.fromhex('280c' + enc4_len_hex) + enc4

    return pkt1, pkt2, pkt3, pkt4
def HELLXbuild_ping_packet(key, iv):
    fields = {
        1: 15,
        2: {
            1: 804266360,
            2: 1
        }
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)
def HELLXbuild_accept_invite(owner_uid, code, key, iv):
    fields = {
        1: 4,
        2: {
            1: int(owner_uid),
            3: int(owner_uid),
            4: bytes.fromhex("01030407090a0b1216191a201d27"),
            8: 1,
            9: {
                1: "088ED288AA30EE9402010100000000120013000100000001B8B110CD0F0000004676251400000000000000000000000000000000000000ff00000000cacfa16d",
                2: 53,
                4: "~[YP",
                6: 11,
                8: "1.129.15",
                9: 6,
                10: 2
            },
            10: str(code),
            11: [
                {1: "IDC1", 2: 68, 3: "EUROPE"},
                {1: "IDC2", 2: 25, 3: "EUROPE"},
            ],
            13: "tr",
            16: bytes.fromhex("374f5219"),
            20: [
                {1: 3, 2: 357},
                {1: 4, 2: 385},
                {1: 5, 2: 156},
                {1: 29, 2: 204},
                {1: 22, 2: 115},
                {1: 14, 2: 139},
                {1: 21},
            ],
        }
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)
def HELLXbuild_join_sq(uid: int, code: str, key: bytes, iv: bytes) -> bytes:
    _F9_RAW = bytes.fromhex(
        "0a800130383846443242384141333045453934303230313031303030303030303030433030313530303031"
        "30303038303030313136423530454636304630303030303034363736323531343030303030303030303030"
        "30303030303030303030303030303030303030303030303030303066663030303030303030636163666131"
        "366410401a8f03725e5954140204480809515703510955030d5100085601010d54070a060d000000570204"
        "01070b001708004c715a45454e1b04180818130505491a45637e585e4174755953486270441f505e480155"
        "42426d5f6565041201481c005e701c66054b780557604263751c59514b444a435566010607091708024c7b"
        "474258704b587d6b7d445f454c62515d595272746a047c1e41540e170c455e486c0e7a470e710661685a56"
        "5c007058475a5e4e48794a615c460c1401487254764444534262666006404e090745001e49795c4e674d72"
        "41790a16084b54724e436542057f07610001616c5367774d5f7b706461710470700d17060d4d5f6202716e"
        "5b456c545f557142701f6d6352754f707645057e5e5a0c13074b5e78436462015503425a5f025376187542"
        "5548577b6d1e597e7247091a054c055d0367705d655c691e48000e6c624607737075607f6d010477540e17"
        "06094d7e470254430402621f4904057b78010100751b02687f784e1c5d680a1001484f5371476f7457795c"
        "0702775e5343550374647a6c7a08457672500822047e5b5950300b3a1a140544464205000607081514607f"
        "7c63736c785d5b725851545e4208312e3132332e3135480650025ad104036262535136393676524d527541"
        "6456324b796f566c63796661584f6548564d77696639476f78355758532f77785a4a426c55334d66336b59"
        "64307a5045483571785335596f385452325453585832496f5a4a565574444f6c4c74564f73526d676f5953"
        "6f33346a66574e2b724b4a2f345973424b41525a5a66324a464a4957506153635747594f684956464c5833"
        "4b7a693965324c50516d34366e49565965657950596b794b4d7263376f684d474b59574479443650317264"
        "3636706456704d6d5238663051524737506f45546577785a715a554a502f366961597562574a612f313853"
        "2b705239546b5839747073464f31666d564b595265764c347178367362544c435a316b4555767041365073"
        "54576a4e513161352f572b776a482f2b45554b4c7446597a4a515741757451786e6c653766533132475030"
        "6667712f70442b555a78477568663845646c556f4c434969706c6333795174664d474841696b7061575a75"
        "706371536f783764425072565179344d7276444353432f543876534c566a7976537958586c335948684c49"
        "322f6855627a6c39453871563554556965656947567946625768714d6f2b5472636d777a414e776c434c37"
        "5861514f6c74684c6b2f436d664f48594b4234366b35557449373142346f6f30545376674b456349704e51"
        "4575796d46506457703051477071755279426d7a4371463150724d59586336677947416e2f4d7043436669"
        "6d78364d304a4b554f417274454557506c4278724c4f2b6741357132624f64484b61782b784478376a2b61"
        "393432672f7541735a42354e5879653974513d3d"
    )
    fields = {
        1: 4,
        2: {
            4: bytes.fromhex("01030407090a0b1216191a201d27"),
            5: str(code),
            6: 6,
            8: 1,
            9: _F9_RAW,
            11: [
                {1: "IDC1", 2: 67, 3: "EUROPE"},
                {1: "IDC2", 2: 24, 3: "EUROPE"}
            ],
            13: "tr",
            16: bytes.fromhex("374f5219"),
            20: [
                {1: 3, 2: 357},
                {1: 4, 2: 385},
                {1: 5, 2: 156},
                {1: 29, 2: 204},
                {1: 22, 2: 115},
                {1: 14, 2: 139},
                {1: 21}
            ]
        }
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)
import struct as _struct
_VOICE_BASE_HEX = (
    '0a8e01'
    '0811100b180122'
    '04534f4e59'
    '2a013930cc80868c02'
    '3a0b61726d65616269'
    '2d763761'
    '4200'
    '4a2438323934386166322d313737392d346438372d613864352d356237363962376365623934'
    '522a464644353846423446373646363438433241354532314542434641334141453831423443394237443937'
    '5a05766f696365'
    '62075851'
    '2d42453432'
    '6802'
    '720471636f6d'
    '100b'
)
_STEP1_FIXED128_HEX = (
    '69839458c071310bbc7e2eede4101c55f0e8c682102c5b100c79'
    '291ae9800ad21d16f7a4e484d4c09f5960f58d00a576128a7bad'
    '036fe886b369e6e2e07ad339be2d93f40eb37e640790972809ea'
    '078b24540912ca6dd3f54183ac721db4c50cd3703941'
    '9f467a430d9429eeee04ead8b83073e54e45a51e0d33b9b273fd2942'
)
def _make_voice_packet(pkt_type: int, region_id: int, uid: str) -> bytes:
    RAW = bytearray(bytes.fromhex(_VOICE_BASE_HEX))
    RAW[4] = pkt_type
    return _struct.pack('>I', len(RAW)) + bytes(RAW)
def HELLXbuild_voice_step1(uid: str, region_id: int) -> bytes:
    base = bytearray(bytes.fromhex(_VOICE_BASE_HEX))
    base[4] = 0x00
    fixed128 = bytes.fromhex(_STEP1_FIXED128_HEX)
    payload = bytes(base) + b'\x12\x80\x01' + fixed128 + b'\x18\x01\x20\x06\x38\x01'
    return _struct.pack('>I', len(payload)) + payload
def HELLXbuild_voice_auth(uid: str, region_id: int, voice_port: int, region_prefix: str = "EUROPE") -> bytes:
    base = bytearray(bytes.fromhex(_VOICE_BASE_HEX))
    base[4] = 0x07
    device_id = "FFD58FB4F76F648C2A5E21EBCFA3AAE81B4C9B7D97"
    region_str = f"{region_prefix}_{region_id}"
    field2_str = (device_id + region_str).encode()
    uid_b = uid.encode()
    field2_len = len(field2_str)
    field2_len_varint = bytes([field2_len]) if field2_len < 128 else bytes([0x80 | (field2_len & 0x7F), field2_len >> 7])
    payload = (
        bytes(base) +
        b'\x12' + field2_len_varint + field2_str +
        bytes.fromhex('20052801' '30d008' '380040005001') +
        b'\x5a' + bytes([len(uid_b)]) + uid_b +
        bytes.fromhex('60007000800101')
    )
    return _struct.pack('>I', len(payload)) + payload
def HELLXbuild_voice_ping(uid: str, region_id: int, voice_port: int, session_id: int = 0x0b) -> bytes:
    base = bytearray(bytes.fromhex(_VOICE_BASE_HEX))
    base[4] = 0x09
    base_bytes = bytes(base[:-2])
    session_varint = HELLXenc_varint(session_id)
    payload = base_bytes + b'\x10' + session_varint
    return _struct.pack('>I', len(payload)) + payload
def HELLXbuild_voice_stat_report(uid: str, region_id: int, session_id: int, region_prefix: str = "EUROPE") -> bytes:
    base = bytearray(bytes.fromhex(_VOICE_BASE_HEX))
    base[4] = 0x38
    base_bytes = bytes(base[:-2])
    region_str = f"{region_prefix}_{region_id}".encode()
    session_varint = HELLXenc_varint(session_id)
    payload = (
        base_bytes +
        b'\x10' + session_varint +
        b'\x1a\x40' + b'FFD58FB4F76F648C2A5E21EBCFA3AAE81B4C9B7D97'.encode() +
        region_str
    )
    return _struct.pack('>I', len(payload)) + payload
def HELLXbuild_voice_broadcast_sub(uid: str, region_id: int, session_id: int, region_prefix: str = "EUROPE") -> bytes:
    base = bytearray(bytes.fromhex(_VOICE_BASE_HEX))
    base[4] = 0x37
    base_bytes = bytes(base[:-2])
    region_str = f"{region_prefix}_{region_id}".encode()
    session_varint = HELLXenc_varint(session_id)
    payload = (
        base_bytes +
        b'\x10' + session_varint +
        b'\x1a\x40' + b'FFD58FB4F76F648C2A5E21EBCFA3AAE81B4C9B7D97'.encode() +
        region_str +
        b'\x22\x03all'
    )
    return _struct.pack('>I', len(payload)) + payload
def HELLXbuild_voice_join(uid: str, region_id: int, counter: int, voice_secret: str, chat_key: str, region_prefix: str = "EUROPE") -> bytes:
    base = bytearray(bytes.fromhex(_VOICE_BASE_HEX))
    base[4] = 0x18
    device_id = "FFD58FB4F76F648C2A5E21EBCFA3AAE81B4C9B7D97"
    region_str = f"{region_prefix}_{region_id}"
    field2_str = (device_id + region_str).encode()
    uid_b = uid.encode()
    uid_last3 = uid.zfill(11)[-3:].encode()
    field2_len = len(field2_str)
    field2_len_varint = bytes([field2_len]) if field2_len < 128 else bytes([0x80 | (field2_len & 0x7F), field2_len >> 7])
    flag = b'\x01' if counter == 0 else b'\x00'
    payload = (
        bytes(base) +
        b'\x12' + field2_len_varint + field2_str +
        bytes.fromhex('20052801' '30d008' '380040005001') +
        b'\x5a' + bytes([len(uid_b)]) + uid_b +
        bytes.fromhex('60007000800101') +
        b'\x1a\x0b' + uid_last3 +
        bytes([0x20, counter & 0xFF, 0x28]) + flag
    )
    return _struct.pack('>I', len(payload)) + payload
def HELLXbuild_voice_auth_device(uid: str, region_id: int) -> bytes:
    payload = bytearray()
    payload.append(0x01)
    payload.append(0x0a)
    device_model = b"samsung"
    payload.append(len(device_model))
    payload.extend(device_model)
    payload.append(0x12)
    device_info = b"SM-S9210"
    payload.append(len(device_info))
    payload.extend(device_info)
    length = len(payload)
    return _struct.pack('>I', length) + bytes(payload)
import time as _time
_VOICE_CUSTOM_MAGIC = bytes.fromhex('feffffff04b50001')
def HELLXbuild_voice_custom(uid: str, region_id: int, uuid: str = "f687ba460e-9b6b8bc39",
                              device_id: str = "F76F648CCFA3AAE897",
                              mcu_ip: str = "0.0.0.0",
                              region_prefix: str = "EUROPE") -> bytes:
    uid_str = uid.zfill(11)
    uid_last3 = uid_str[-3:].encode()
    region_str = f"{region_prefix}_{region_id}".encode()
    uuid_b = uuid.encode()
    device_b = device_id.encode()
    local_ip = b"0.0.0.0"
    mcu_ip_b = mcu_ip.encode()
    ts = int(_time.time()) & 0xFFFFFFFF
    pkt = bytearray()
    pkt.extend(_VOICE_CUSTOM_MAGIC)
    pkt.extend(b'\x00\x24')
    pkt.extend(uuid_b); pkt.append(0)
    pkt.extend(b'\x00\x2a')
    pkt.extend(device_b); pkt.append(0)
    pkt.extend(b'\x00\x1a')
    pkt.extend(region_str); pkt.append(0)
    pkt.extend(b'\x00\x0b')
    pkt.extend(uid_last3); pkt.extend(b'\x00\x00\x00\x00')
    pkt.extend(b'\x28\x2e\x30\x00')
    pkt.append(0x07)
    pkt.extend(local_ip); pkt.extend(b'\x00')
    pkt.append(0x0d)
    pkt.extend(mcu_ip_b); pkt.extend(b'\x00')
    pkt.extend(b'\x17\x76')
    pkt.extend(_struct.pack('>I', ts))
    pkt.extend(b'\x00\x00\x00\x00')
    return _struct.pack('>I', len(pkt)) + bytes(pkt)
def HELLXparse_voice_custom_response(data: bytes):
    if len(data) > 4 and data[4:8] == b'\xfe\xff\xff\x7f':
        data = data[4:]
    if not data.startswith(b'\xfe\xff\xff\x7f'):
        return None
    import re
    matches = re.findall(rb'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', data)
    for m in matches:
        parts = m.split(b'.')
        if all(0 <= int(p) <= 255 for p in parts) and parts[0] not in (b'0', b'1'):
            return m.decode()
    return None
def HELLXbuild_chat_auth(uid: int, region_id, key, iv) -> bytes:
    # fields = {
    #     1: 3,
    #     2: {
    #         1: uid,
    #         3: "en",
    #         4: str(region_id),
    #     }
    # }
    fields = {1: 3, 2: {1: int(uid), 3: 'en', 4: str(region_id)}}
    print(fields)
    print("________________________________________________________________________________________________")
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '1215', key, iv)
def HELLXbuild_chat_global_auth(key, iv) -> bytes:
    fields = {
        1: 3,
        2: {
            2: 5,
            3: "en",
        }
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '1215', key, iv)
async def get_randm_avatar():
    avatars = [902000068, 902000016, 902000011, 902000084, 902000085, 902000087, 902000106, 902045016]
    return random.choice(avatars)
async def HELLXbuild_chat_message(uid: int, owner_uid: int, message: str, timestamp: int, key, iv) -> bytes:
    fields = {
        1: 1,
        2: {
            1: uid,
            2: owner_uid,
            4: message,
            5: timestamp,
            7: 6,
            9: {
                1: "HELLX",
                2: await get_randm_avatar(),
                3: 901000029,
                4: 330,
                5: 801043518,
                7: 2,
                10: 1,
                12: 0,
                13: {
                    1: 2,
                },
                13: "",
                14: {
                    1: uid,
                    2: 8,
                    3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006",
                }
            },
            10: "en",
            13: {3: 1},
            14: "",
        }
    }
    print(fields)
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '1215', key, iv)
def HELLXbuild_leave_team(uid: int, key, iv) -> bytes:
    fields = {
        1: 7,
        2: {1: uid}
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)
def HELLXbuild_chat_close(uid: int, key, iv) -> bytes:
    fields = {
        1: 4,
        2: {
            1: uid,
            3: "en",
        }
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '1215', key, iv)
def HELLXbuild_voice_redirect(uid: str, region_id: int, region_prefix: str = "EUROPE", ext_region: str = "de") -> bytes:
    device_id = "FFD58FB4F76F648C2A5E21EBCFA3AAE81B4C9B7D97"
    region_str = f"{region_prefix}_{region_id}"
    field1 = (device_id + region_str).encode()
    base = bytes.fromhex(_VOICE_BASE_HEX)
    inner = bytearray(base[3:3+142])
    inner[1] = 0x11
    ext_b = ext_region.encode()
    payload = bytearray()
    payload.append(0x0a)
    payload.append(len(field1))
    payload.extend(field1)
    payload.append(0x12)
    payload.append(0x8e); payload.append(0x01)
    payload.extend(inner)
    payload.append(0x18); payload.append(0x02)
    payload.append(0x22); payload.append(len(ext_b))
    payload.extend(ext_b)
    return _struct.pack('>I', len(payload)) + bytes(payload)

def HELLXbuild_emote(bot_uid: int, target_uid: int, emote_id: int, key, iv) -> bytes:
    fields = {
        1: 21,
        2: {
            1: int(target_uid),
            2: emote_id,
            5: {
                1: int(target_uid),
                3: int(emote_id),
            },
        },
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)

def HELLXbuild_create_squad(region: str, version: str, key, iv) -> bytes:
    fields = {
        1: 1,
        2: {
            2: bytes.fromhex("010304161d"),
            3: 15,
            4: 3,
            5: "en",
            8: [
                {1: "IDC1", 2: 80, 3: region},
                {1: "IDC2", 2: 53, 3: region},
                {1: "IDC3", 2: 124, 3: region},
                {1: "IDC4", 2: 233, 3: region},
            ],
            9: 1,
            10: bytes.fromhex("01030407090a0b12161920 1d27".replace(" ","")),
            11: 1,
            13: 1,
            14: {
                1: "08FFF3BE913CA75B02052F0222220000009600020094003C3A33107913D91078467625141101040ff77f2020ca3ca4f969cbc4e50000004f0e0e0801cacfa16d",
                2: 476,
                3: bytes.fromhex(
                    "7658515c16050804e550454504094c53570c0702525404025607060803"
                    "544f01055204575f5b025404131e0001485948464e1f001d011d16050a"
                    "4e1c447b5c5345707c514f6572401f5c5b40075541436b5c65640d1b03"
                    "4b1d055e771b670d4a7b024755466276195d5d404c4c4753630404000511"
                    "06054c59727272704056575b194178420d1d79735f6454686463055257"
                    "704e0a15084d5f4c6d0d774477025e6164735f5c0d775f4659505e4a"
                    "454e4c6d59440b1303464c5f5372 4d5d74554a024d6d767759 6e4a"
                    "7d5207677a59575487600d1208480d4c59464e01775f 584c4d754246"
                    "6d71655e4941514d525d595c5b435b0c1305 0d4852 7c5d7d1d6672"
                    "57025853770d5e627e7a5d564d 7c470e6763077109160744025f7c49"
                    "55024e0c7069741c656a53664657514802775f6048680008170c4e5c53"
                    "0876 4c41044d530d7e00097967006665000263 5c64717a78091b0007"
                    "4a7b417777067750 0a58657247410d5f665b624173574f6671474f59"
                    "4f0f14034c4752754c6c7954795903077e5b5643 5c04726579697e"
                    "054172 7e550a".replace(" ","")
                ),
                4: "zW\\R",
                6: 11,
                7: bytes.fromhex("14720467 6c64621613".replace(" ","")),
                8: version,
                9: 3,
                10: 2,
                11: "\x03bbSQ62iz591xAdV2KyoVlTtsUZkv08Zr7Qr3yXm7+zu4THgJA8epXNyEzy1ySZuypve2AhTz0XL1xQmE0f+gIBTN1dT5v3FFqy/GNyxyaVBm6o9+4/7rXepN29ERNRafz9Ke5spj1yt7bIV3/g/x5KKpfAQAiWKJmwgKSGHu2kOkH8koNaqLmO9m8+4LPzA9HaqzDbdLM1FZiGEIvVcZYBb5zW+lexeMkXPFPX62d1kOEBVy7/+DEKJUIIUoiyxGiPgZphr8JOpmYj65gOaIlnteZHAykqwuxeVNu8Y3UTGpjzalKkDaVY7YUBctOH8wGrrH+5WybIdXDGLrmjR5k3QzG6s3hkNGAOoeAGg1hWWQCsMMduk3dQvx1TI3nIpU77TV5WRz9Hgs5qgQr8deHPnAGdXYu3kehknt44WuRavs3PCsq+ylc2/n0IIGzeWfXfMiE5cUaQ/mqocMmUBYA9gBQGjPE+uTVcCM0h+a0OUqwQma5kCWUPoZ++ZFBGgMZYOxT8QWz2r7yvG+bghm2IjuHZRm0sh2XdkPjLrTfYRy3qdBGt8CRkmaBF55/bzmvNewX8obZtriQ0sZxnnhcDYjbx2M",
            },
            19: 324,
            21: bytes.fromhex("374f5219"),
            24: [
                {1: 3, 2: 391}, {1: 4, 2: 385}, {1: 5, 2: 192},
                {1: 29, 2: 204}, {1: 22, 2: 115}, {1: 14, 2: 175}, {1: 21},
            ],
            27: {7: 51},
        },
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)

def HELLXbuild_change_squad_size(grp_to: int, key, iv) -> bytes:
    fields = {
        1: 17,
        2: {
            1: 6728454010,
            2: 1,
            3: grp_to - 1,
            4: 15,
            5: "\x01\x03\x04\x16\x1d",
            8: 1,
        },
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)

def HELLXbuild_squad_info_request(bot_uid: int, key, iv) -> bytes:
    fields = {1: 15, 2: {1: int(bot_uid), 2: 1}}
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)

def HELLXbuild_ghost_msg(owner_id: int, bot_uid: int, secret_code: str, message: str, key, iv) -> bytes:
    import time as _t
    fields = {
        1: 61,
        2: {
            1: int(owner_id),
            2: {
                1: int(owner_id),
                2: int(bot_uid),
                3: message,
                5: 12,
                6: 15,
                7: 1,
                8: {2: 1, 3: 1},
                9: 3,
            },
            3: str(secret_code),
        },
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '0515', key, iv)

async def HELLXbuild_dm_message(bot_uid: int, target_uid: int, message: str, key, iv) -> bytes:
    import time as _t
    fields = {
        1: 1,
        2: {
            1: int(bot_uid),
            2: int(target_uid),
            3: 2,
            4: message,
            5: int(_t.time()),
            7: 6,
            9: {
                1: "HELLX",
                2: await get_randm_avatar(),
                4: 330,
                5: 910050002,
                13: {},
                14: {1: int(bot_uid), 3: {}},
                18: {1: int(bot_uid), 3: 1, 4: {}},
            },
            10: "en",
            13: {2: 1, 3: 1},
            14: {},
        },
    }
    proto_hex = HELLXcreate_proto(fields).hex()
    return HELLXgenerate_packet(proto_hex, '1215', key, iv)

async def HELLXequip_emote(jwt_token: str, login_url: str = None) -> bool:
    import aiohttp as _aiohttp
    import ssl as _ssl
    base = (login_url or "https://clientbp.ggpolarbear.com").rstrip("/")
    url = f"{base}/ChooseEmote"
    host = base.split("//", 1)[-1].split("/", 1)[0]
    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": f"Bearer {jwt_token}",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": host,
        "ReleaseVersion": "OB54",
        "User-Agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2022.3.47f1",
    }
    data = bytes.fromhex("673b1ad08072c36b91c0749256091802")
    ctx = _ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = _ssl.CERT_NONE
    try:
        async with _aiohttp.ClientSession() as s:
            async with s.post(url, headers=headers, data=data, ssl=ctx, timeout=8) as r:
                return r.status == 200
    except Exception:
        return False
