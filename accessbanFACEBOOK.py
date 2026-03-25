#!/usrs/env python3
# -*- coding: utf-8 -*-
"""
============================================================
FREE FIRE COMPLETE BOT - ULTIMATE ALL-IN-ONE v13.0
============================================================
GUEST LOGIN → TOKEN → MAJORLOGIN → ONLINE
Complete flow with proper OAuth
"""

import asyncio
import aiohttp
import ssl
import json
import random
import sys
import struct
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ============================================================
# CONFIGURATION - EDIT HERE
# ============================================================

# Option 1: Use Guest Credentials (Recommended)
GUEST_UID = "nah"  # <-- EDIT THIS
GUEST_PASSWORD = "lol"  # <-- EDIT THIS

# Option 2: Use Access Token Directly (Needs OpenID too)
ACCESS_TOKEN = "7c8e9321150badd32ddd83b56f98f6246a5615ce2621174cabbd687295c1dbec"  # <-- Leave empty to use Guest Login
OPEN_ID = "9f8644d39b9694b5a2b311e57216a0e8"       # <-- Required if using ACCESS_TOKEN

# ============================================================
# CONSTANTS
# ============================================================

OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLIENT_ID = "100067"

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# ============================================================
# PROTOBUF SYSTEM
# ============================================================

class ProtoWriter:
    @staticmethod
    def varint(value):
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)

    @staticmethod
    def tag(field_num, wire_type):
        return ProtoWriter.varint((field_num << 3) | wire_type)

    @staticmethod
    def write_varint(field_num, value):
        return ProtoWriter.tag(field_num, 0) + ProtoWriter.varint(value)

    @staticmethod
    def write_string(field_num, value):
        if isinstance(value, str):
            value = value.encode('utf-8')
        return ProtoWriter.tag(field_num, 2) + ProtoWriter.varint(len(value)) + value

    @staticmethod
    def write_message(field_num, data):
        if isinstance(data, dict):
            data = ProtoWriter.create_message(data)
        return ProtoWriter.tag(field_num, 2) + ProtoWriter.varint(len(data)) + data

    @staticmethod
    def create_message(fields):
        result = bytearray()
        for field_num, value in sorted(fields.items()):
            if isinstance(value, dict):
                result.extend(ProtoWriter.write_message(field_num, value))
            elif isinstance(value, int):
                result.extend(ProtoWriter.write_varint(field_num, value))
            elif isinstance(value, str):
                result.extend(ProtoWriter.write_string(field_num, value))
            elif isinstance(value, bytes):
                result.extend(ProtoWriter.write_string(field_num, value))
        return bytes(result)


class ProtoReader:
    @staticmethod
    def read_varint(data, offset=0):
        result = 0
        shift = 0
        while True:
            byte = data[offset]
            result |= (byte & 0x7F) << shift
            offset += 1
            if not (byte & 0x80):
                break
            shift += 7
        return result, offset

    @staticmethod
    def parse_message(data):
        result = {}
        offset = 0
        while offset < len(data):
            try:
                tag, offset = ProtoReader.read_varint(data, offset)
                field_num = tag >> 3
                wire_type = tag & 0x7

                if wire_type == 0:
                    value, offset = ProtoReader.read_varint(data, offset)
                    result[field_num] = value
                elif wire_type == 2:
                    length, offset = ProtoReader.read_varint(data, offset)
                    if length > len(data) - offset:
                        break
                    value = data[offset:offset+length]
                    offset += length
                    try:
                        result[field_num] = value.decode('utf-8')
                    except:
                        result[field_num] = value
                else:
                    break
            except:
                break
        return result


# ============================================================
# CRYPTOGRAPHY
# ============================================================

class Crypto:
    @staticmethod
    def encrypt(data, key=None, iv=None):
        k = key if key else AES_KEY
        i = iv if iv else AES_IV
        cipher = AES.new(k, AES.MODE_CBC, i)
        return cipher.encrypt(pad(data, AES.block_size))

    @staticmethod
    def decrypt(data, key, iv):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(data), AES.block_size)


# ============================================================
# PROTOCOL BUILDERS
# ============================================================

class Protocol:
    @staticmethod
    def build_major_login(open_id, access_token):
        random_ip = f"223.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        random_device = f"Google|{random.randint(10000000, 99999999)}"

        fields = {
            3: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            4: "free fire",
            5: 1,
            7: "1.120.2",
            8: "RIZER OSSSSSS FUCKKKKK56)",
            9: "Handheld",
            10: "Verizon",
            11: "WIFI",
            12: 1920,
            13: 1080,
            14: "280",
            15: "ARM64 HOLY SHITTT| 4",
            16: 4096,
            17: "Adreno (TM) 640",
            18: "OpenGL ES 3.2 v1.46",
            19: random_device,
            20: random_ip,
            21: "en",
            22: open_id,
            23: "8",
            24: "Handheld",
            25: {6: 55, 8: 81},
            29: access_token,
            30: 1,
            41: "Verizon",
            42: "WIFI",
            57: "JOHNY JOHNY YES PAAPA",
            60: 36235,
            61: 31335,
            62: 2519,
            63: 703,
            64: 25010,
            65: 26628,
            66: 32992,
            67: 36235,
            73: 3,
            74: "/data/arm64",
            76: 1,
            77: "5b892aaabd688e571f688053118a162b|/data/app/hmmmmmmmsksksksk-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk",
            78: 3,
            79: 2,
            81: "64",
            83: "2019118695",
            86: "OpenGLES2",
            87: 16383,
            88: 4,
            89: b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg==",
            90: random.randint(10000, 15000),
            91: "android",
            92: "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY=",
            95: 110009,
            97: 1,
            98: 0,
            99: "3",
            100: "3"
        }

        return ProtoWriter.create_message(fields)

    @staticmethod
    def parse_major_login_response(data):
        parsed = ProtoReader.parse_message(data)
        return {
            "account_uid": parsed.get(1, 0),
            "region": parsed.get(2, ""),
            "token": parsed.get(8, ""),
            "url": parsed.get(10, ""),
            "timestamp": parsed.get(21, 0),
            "key": parsed.get(22, b""),
            "iv": parsed.get(23, b"")
        }

    @staticmethod
    def parse_login_data(data):
        parsed = ProtoReader.parse_message(data)
        return {
            "account_uid": parsed.get(1, 0),
            "region": parsed.get(3, ""),
            "account_name": parsed.get(4, ""),
            "online_ip_port": parsed.get(14, ""),
            "clan_id": parsed.get(20, 0),
            "account_ip_port": parsed.get(32, ""),
            "clan_compiled_data": parsed.get(55, b"")
        }

    @staticmethod
    def create_auth_packet(uid, token, timestamp, key, iv):
        uid_int = int(uid)
        uid_hex = format(uid_int, 'x')
        if len(uid_hex) % 2 == 1:
            uid_hex = '0' + uid_hex

        ts_int = int(timestamp)
        ts_hex = format(ts_int, 'x')
        if len(ts_hex) % 2 == 1:
            ts_hex = '0' + ts_hex

        cipher = AES.new(key, AES.MODE_CBC, iv)
        token_padded = pad(token.encode('utf-8'), AES.block_size)
        token_encrypted = cipher.encrypt(token_padded)
        token_enc_hex = token_encrypted.hex()

        token_len_bytes = len(token_encrypted)
        token_len_hex = format(token_len_bytes, 'x')
        if len(token_len_hex) % 2 == 1:
            token_len_hex = '0' + token_len_hex

        uid_len = len(uid_hex)
        if uid_len == 8:
            uid_header = '00000000'
        elif uid_len == 9:
            uid_header = '0000000'
        elif uid_len == 10:
            uid_header = '000000'
        elif uid_len == 7:
            uid_header = '000000000'
        else:
            target_start = 16
            uid_header_len = target_start - 4 - uid_len
            if uid_header_len < 0:
                uid_header_len = 0
            uid_header = '0' * uid_header_len

        if len(token_len_hex) % 2 == 0:
            separator = "0000"
        else:
            separator = "00000"

        packet = f"0115{uid_header}{uid_hex}{ts_hex}{separator}{token_len_hex}{token_enc_hex}"
        return bytes.fromhex(packet)


# ============================================================
# NETWORK CLIENT
# ============================================================

class FreeFireClient:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(ssl=ssl_ctx)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    @staticmethod
    def generate_ua():
        versions = ['5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3', '5.3.0B1']
        models = ['SM-A515F', 'Redmi 9A', 'POCO M3', 'RMX2185', 'ASUS_Z01QD']
        android = ['10', '11', '12', '13']
        return f"GarenaMSDK/{random.choice(versions)}({random.choice(models)};Android {random.choice(android)};en-US;USA;)"

    async def oauth_login(self, uid, password):
        """OAuth Login to get open_id and access_token"""
        print("[Step 1/4] OAuth Login...")

        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": self.generate_ua(),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close"
        }

        data = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": CLIENT_SECRET,
            "client_id": CLIENT_ID
        }

        try:
            async with self.session.post(OAUTH_URL, headers=headers, data=data) as resp:
                print(f"   OAuth Response: {resp.status}")

                if resp.status == 200:
                    result = await resp.json()
                    print(f"   OAuth Result: {json.dumps(result, indent=2)[:300]}")

                    oid = result.get("open_id")
                    at = result.get("access_token")

                    if oid and at:
                        print(f"✅ OAuth Success!")
                        print(f"   Open ID: {oid}")
                        print(f"   Access Token: {at[:30]}...")
                        return oid, at
                    else:
                        print(f"❌ Missing open_id or access_token in response")
                elif resp.status == 429:
                    print("❌ Rate limited. Wait 60 seconds...")
                else:
                    text = await resp.text()
                    print(f"❌ OAuth HTTP {resp.status}: {text[:200]}")
        except Exception as e:
            print(f"❌ OAuth Error: {e}")

        return None, None

    async def major_login(self, encrypted_payload):
        print("[Step 2/4] MajorLogin...")

        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB52"
        }

        try:
            async with self.session.post(MAJOR_LOGIN_URL, data=encrypted_payload, headers=headers) as resp:
                print(f"   MajorLogin Response: {resp.status}")

                if resp.status == 200:
                    data = await resp.read()
                    print(f"✅ MajorLogin Success ({len(data)} bytes)")
                    return data
                else:
                    text = await resp.text()
                    print(f"❌ MajorLogin HTTP {resp.status}: {text[:200]}")
        except Exception as e:
            print(f"❌ MajorLogin Error: {e}")

        return None

    async def get_login_data(self, url, token, encrypted_payload):
        print("[Step 3/4] GetLoginData...")

        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB52",
            "Authorization": f"Bearer {token}"
        }

        try:
            async with self.session.post(f"{url}/GetLoginData", data=encrypted_payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    print(f"✅ GetLoginData Success ({len(data)} bytes)")
                    return data
                else:
                    print(f"❌ GetLoginData HTTP {resp.status}")
        except Exception as e:
            print(f"❌ GetLoginData Error: {e}")

        return None

    async def tcp_connect(self, ip, port, auth_packet, name):
        print(f"[Step 4/4] TCP {name}: {ip}:{port}")

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, int(port)),
                timeout=10
            )

            writer.write(auth_packet)
            await writer.drain()

            data = await asyncio.wait_for(reader.read(4096), timeout=10)

            if data:
                print(f"✅ {name} Connected ({len(data)} bytes)")
                return True, writer
            else:
                writer.close()
                await writer.wait_closed()
                return False, None

        except Exception as e:
            print(f"❌ {name} Error: {e}")
            return False, None


# ============================================================
# MAIN BOT
# ============================================================

class CompleteBot:
    def __init__(self, uid=None, password=None, access_token=None, open_id=None):
        self.uid = uid
        self.password = password
        self.access_token = access_token
        self.open_id = open_id
        self.client = None
        self.online_writer = None
        self.chat_writer = None

    def print_banner(self):
        print("=" * 70)
        print("FREE FIRE COMPLETE BOT - ULTIMATE ALL-IN-ONE v13.0")
        print("=" * 70)

        if self.access_token and self.open_id:
            print("🔑 Mode: Direct Token Login")
            print(f"   Open ID: {self.open_id}")
            print(f"   Token: {self.access_token[:30]}...")
        else:
            print("👤 Mode: Guest Login")
            print(f"   UID: {self.uid}")
            print(f"   Password: {'*' * len(self.password) if self.password else 'None'}")
        print("=" * 70)

    async def get_credentials(self):
        """Get open_id and access_token"""
        if self.access_token and self.open_id:
            print("\n[Step 0/4] Using provided credentials...")
            return self.open_id, self.access_token

        if not self.uid or not self.password:
            print("\n❌ Error: No credentials provided!")
            print("   Either provide Guest UID/Password OR Access Token + Open ID")
            return None, None

        # OAuth Login
        open_id, access_token = await self.client.oauth_login(self.uid, self.password)
        return open_id, access_token

    async def run(self):
        self.print_banner()

        async with FreeFireClient() as client:
            self.client = client

            # Step 0: Get Credentials
            open_id, access_token = await self.get_credentials()
            if not open_id or not access_token:
                return False

            # Step 1: Build MajorLogin
            print("\n[Step 1/4] Building MajorLogin...")
            major_payload = Protocol.build_major_login(open_id, access_token)
            encrypted_payload = Crypto.encrypt(major_payload)
            print(f"✅ Payload encrypted ({len(encrypted_payload)} bytes)")

            # Step 2: MajorLogin
            major_response = await client.major_login(encrypted_payload)
            if not major_response:
                return False

            # Step 3: Parse MajorLogin
            major_data = Protocol.parse_major_login_response(major_response)
            if not major_data or not major_data.get("account_uid"):
                print("❌ Failed to parse MajorLogin response")
                return False

            print(f"✅ Account UID: {major_data['account_uid']}")
            print(f"✅ Region: {major_data['region']}")

            # Step 4: GetLoginData
            login_response = await client.get_login_data(
                major_data["url"],
                major_data["token"],
                encrypted_payload
            )
            if not login_response:
                return False

            # Step 5: Parse LoginData
            login_info = Protocol.parse_login_data(login_response)
            if not login_info:
                print("❌ Failed to parse LoginData")
                return False

            print(f"✅ Name: {login_info['account_name']}")
            print(f"✅ Online: {login_info['online_ip_port']}")
            print(f"✅ Chat: {login_info['account_ip_port']}")

            # Step 6: Create Auth Packet
            auth_packet = Protocol.create_auth_packet(
                major_data["account_uid"],
                major_data["token"],
                major_data["timestamp"],
                major_data["key"],
                major_data["iv"]
            )

            # Step 7: Parse IPs
            online_ip, online_port = login_info["online_ip_port"].split(":")
            chat_ip, chat_port = login_info["account_ip_port"].split(":")

            # Step 8: TCP Connect
            online_ok, self.online_writer = await client.tcp_connect(
                online_ip, online_port, auth_packet, "Online"
            )
            chat_ok, self.chat_writer = await client.tcp_connect(
                chat_ip, chat_port, auth_packet, "Chat"
            )

            # Final Status
            print("\n" + "=" * 70)
            if online_ok and chat_ok:
                print("✅✅✅ BOT IS FULLY ONLINE! ✅✅✅")
                print(f"✅ Account: {login_info['account_name']}")
                print(f"✅ UID: {major_data['account_uid']}")
                print(f"✅ Region: {login_info['region']}")
                print("\n🤖 Bot is running! Press Ctrl+C to stop")

                try:
                    while True:
                        await asyncio.sleep(30)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping...")
                return True
            else:
                print("⚠️  PARTIAL CONNECTION")
                print(f"   Online: {'✅' if online_ok else '❌'}")
                print(f"   Chat: {'✅' if chat_ok else '❌'}")
                return online_ok or chat_ok

    async def cleanup(self):
        if self.online_writer:
            self.online_writer.close()
            await self.online_writer.wait_closed()
        if self.chat_writer:
            self.chat_writer.close()
            await self.chat_writer.wait_closed()


# ============================================================
# AUTO-RETRY
# ============================================================

async def run_with_retry(max_retries=3, **kwargs):
    for attempt in range(1, max_retries + 1):
        print(f"\n{'='*70}")
        print(f"ATTEMPT {attempt}/{max_retries}")
        print(f"{'='*70}")

        bot = CompleteBot(**kwargs)
        try:
            result = await bot.run()
            if result:
                return True
        except Exception as e:
            print(f"\n💥 Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await bot.cleanup()

        if attempt < max_retries:
            wait_time = 5 * attempt
            print(f"\n⏳ Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)

    print(f"\n❌ All {max_retries} attempts failed")
    return False


# ============================================================
# ENTRY POINT
# ============================================================

async def main():
    # Check command line arguments
    import sys

    uid = GUEST_UID
    password = GUEST_PASSWORD
    access_token = ACCESS_TOKEN if ACCESS_TOKEN else None
    open_id = OPEN_ID if OPEN_ID else None

    if len(sys.argv) >= 3:
        # Usage: python script.py <uid> <password>
        uid = sys.argv[1]
        password = sys.argv[2]
        access_token = None
        open_id = None
        print("🔑 Using credentials from command line")
    elif len(sys.argv) >= 2:
        # Usage: python script.py <access_token>
        access_token = sys.argv[1]
        open_id = access_token[:32] if len(access_token) >= 32 else access_token
        uid = None
        password = None
        print("🔑 Using token from command line")

    # Determine which mode to use
    if access_token and open_id:
        success = await run_with_retry(
            max_retries=3,
            access_token=access_token,
            open_id=open_id
        )
    else:
        success = await run_with_retry(
            max_retries=3,
            uid=uid,
            password=password
        )

    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Critical Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)