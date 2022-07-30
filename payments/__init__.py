import json
import uuid
import requests
import hmac
import hashlib
from config import *

def momo_payment(amount):
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    partnerCode = PARTNER_CODE
    accessKey = ACCESS_KEY
    secretKey = MOMO_SECRET_KEY
    orderInfo = "foo"
    redirectUrl = "https://haha.com"
    ipnUrl = "https://webhook.site/be9ccc37-add5-4176-8296-43c19ae882da"
    amount = str(amount)
    orderId = str(uuid.uuid4())
    requestId = str(uuid.uuid4())
    extraData = ""
    requestType = "captureWallet"
    extraData = ""  # pass empty value or Encode base64 JsonString

    # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
    # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
    # &requestType=$requestType
    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType

    # puts raw signature
    # signature
    h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()
    data = {
        'partnerCode': partnerCode,
        'partnerName': "sunshoptest",
        'storeId': "sunshoptest",
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'redirectUrl': redirectUrl,
        'ipnUrl': ipnUrl,
        'lang': "vi",
        'extraData': extraData,
        'requestType': requestType,
        'signature': signature
    }
    data = json.dumps(data)

    clen = len(data)
    response = requests.post(endpoint, data=data, headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

    # f.close()
    if response.status_code != 200:
        return False, response.json()

    return True, response.json()['payUrl']
