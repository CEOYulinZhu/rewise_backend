"""
VIVO AI Gateway 鉴权工具

实现VIVO BlueLM API的正确签名算法
"""

import random
import string
import time
import hashlib
import hmac
import base64
import urllib.parse

__all__ = ['gen_sign_headers']


def gen_nonce(length=8):
    """生成随机字符串"""
    chars = string.ascii_lowercase + string.digits
    return ''.join([random.choice(chars) for _ in range(length)])


def gen_canonical_query_string(params):
    """生成规范化查询字符串"""
    if params:
        escape_uri = urllib.parse.quote
        raw = []
        for k in sorted(params.keys()):
            tmp_tuple = (escape_uri(k), escape_uri(str(params[k])))
            raw.append(tmp_tuple)
        s = "&".join("=".join(kv) for kv in raw)
        return s
    else:
        return ''


def gen_signature(app_secret, signing_string):
    """生成HMAC-SHA256签名"""
    bytes_secret = app_secret.encode('utf-8')
    hash_obj = hmac.new(bytes_secret, signing_string, hashlib.sha256)
    bytes_sig = base64.b64encode(hash_obj.digest())
    signature = str(bytes_sig, encoding='utf-8')
    return signature


def gen_sign_headers(app_id, app_key, method, uri, query):
    """生成VIVO API鉴权头部"""
    method = str(method).upper()
    uri = uri
    timestamp = str(int(time.time()))
    app_id = app_id
    app_key = app_key
    nonce = gen_nonce()
    canonical_query_string = gen_canonical_query_string(query)
    signed_headers_string = 'x-ai-gateway-app-id:{}\nx-ai-gateway-timestamp:{}\n' \
                            'x-ai-gateway-nonce:{}'.format(app_id, timestamp, nonce)
    signing_string = '{}\n{}\n{}\n{}\n{}\n{}'.format(method,
                                                     uri,
                                                     canonical_query_string,
                                                     app_id,
                                                     timestamp,
                                                     signed_headers_string)
    signing_string = signing_string.encode('utf-8')
    signature = gen_signature(app_key, signing_string)
    return {
        'X-AI-GATEWAY-APP-ID': app_id,
        'X-AI-GATEWAY-TIMESTAMP': timestamp,
        'X-AI-GATEWAY-NONCE': nonce,
        'X-AI-GATEWAY-SIGNED-HEADERS': "x-ai-gateway-app-id;x-ai-gateway-timestamp;x-ai-gateway-nonce",
        'X-AI-GATEWAY-SIGNATURE': signature
    } 