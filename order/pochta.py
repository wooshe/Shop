import json
import uuid
from decimal import Decimal

import requests
import xmltodict



request_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json;charset=UTF-8",
    "Authorization": "AccessToken " + token,
    "X-User-Authorization": "Basic " + key
}


def pr_tracking(barcode):
    body_request = """
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:oper="http://russianpost.org/operationhistory" xmlns:data="http://russianpost.org/operationhistory/data" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soap:Header/>
   <soap:Body>
      <oper:getOperationHistory>
         <!--Optional:-->
         <data:OperationHistoryRequest>
            <data:Barcode>{barcode}</data:Barcode>
            <data:MessageType>0</data:MessageType>
            <!--Optional:-->
            <data:Language>RUS</data:Language>
         </data:OperationHistoryRequest>
         <!--Optional:-->
         <data:AuthorizationHeader soapenv:mustUnderstand="?">
            <data:login>TEjtsqnpsVAJWN</data:login>
            <data:password>5FT7NUVEsFCl</data:password>
         </data:AuthorizationHeader>
      </oper:getOperationHistory>
   </soap:Body>
</soap:Envelope>
"""
    ret = {}

    try:
        format_body = body_request.format(barcode=barcode)

        format_body = format_body.encode('utf-8')
        session = requests.session()
        session.headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
        session.headers.update({"Content-Length": str(len(format_body))})
        responce = session.post(url="https://tracking.russianpost.ru/rtm34", data=format_body, verify=False)

        content = xmltodict.parse((responce.content).decode('utf-8'))

        if responce.status_code == 200 and responce.ok:

            ret['status'] = \
            content['S:Envelope']['S:Body']['ns7:getOperationHistoryResponse']['ns3:OperationHistoryData'][
                'ns3:historyRecord']['ns3:OperationParameters']['ns3:OperType']['ns3:Name']
            ret['ret_status'] = "success"
            return ret

        else:
            ret['ret_status'] = "error"
            return ret

    except:
        ret['ret_status'] = "error"
        return ret


def pr_get_doc(batch_name):
    path = "/1.0/forms/" + str(batch_name) + "/zip-all?print-type=PAPER&print-form-type=ONE_SIDED"

    url = protocol + host + path
    response = requests.get(url, headers=request_headers)

    ret = {}

    if response.status_code == 200:

        try:
            filename = 'media/delivery/pochta_rossii_order_' + batch_name + '.zip'
            with open(filename, 'wb') as handle:
                for block in response.iter_content(1024):
                    handle.write(block)

            ret['ret_status'] = "success"
            ret['url'] = filename
            return ret
        except:
            ret['ret_status'] = "error"
            return ret

    else:
        ret['ret_status'] = "error"
        return ret


def pr_send_doc(ids):
    path = "/1.0/batch/" + ids + "/checkin"

    url = protocol + host + path

    response = requests.post(url, headers=request_headers)
    ret = {}

    if response.status_code == 200:

        try:
            body = json.loads(response.content.decode('utf-8'))
            if body['f103-sent'] == True:
                ret['ret_status'] = "success"
            else:
                ret['ret_status'] = "error"
            return ret
        except:
            ret['ret_status'] = "error"
            return ret

    else:
        ret['ret_status'] = "error"
        return ret


def pr_get_shipment(id):
    path = "/1.0/shipment/search?query=" + str(id)

    url = protocol + host + path
    response = requests.get(url, headers=request_headers)

    ret = {}

    if response.status_code == 200:

        try:
            body = json.loads(response.content.decode('utf-8'))[0]
            ret['ret_status'] = "success"
            ret['barcode'] = body['barcode']
            ret['batch-name'] = body['batch-name']
            ret['id'] = body['id']
            return ret
        except:
            ret['ret_status'] = "error"
            return ret

    else:
        ret['ret_status'] = "error"
        return ret


def pr_shipment(ids):
    path = "/1.0/user/shipment"

    addresses = [
        ids
    ]

    url = protocol + host + path

    response = requests.post(url, headers=request_headers, data=json.dumps(addresses))
    ret = {}

    if response.status_code == 200:

        try:
            body = json.loads(response.content.decode('utf-8'))
            ret['result-ids'] = body['result-ids'][0]
            ret['batch-name'] = body['batches'][0]['batch-name']
            ret['body'] = body
            ret['ret_status'] = "success"
            return ret
        except:
            ret['ret_status'] = "error"
            return ret

    else:
        ret['ret_status'] = "error"
        return ret


def pr_get_order(id):
    path = "/1.0/backlog/search?query=" + str(id)

    url = protocol + host + path
    response = requests.get(url, headers=request_headers)

    ret = {}

    if response.status_code == 200:

        try:
            body = json.loads(response.content.decode('utf-8'))[0]

            ret['barcode'] = body['barcode']
            ret['id'] = body['id']

            ret['ret_status'] = "success"
            ret['max-days'] = body['delivery-time']['max-days']
            ret['min-days'] = body['delivery-time']['min-days']
            ret['total'] = body['total-rate-wo-vat'] / 100
            ret['nds'] = body['total-vat'] / 100

            ret['total_nds'] = (ret['total'] + ret['nds'])
            return ret
        except:
            ret['ret_status'] = "error"
            return ret

    else:
        ret['ret_status'] = "error"
        return ret


def pr_order(order):
    path = "/1.0/user/backlog"

    addresses = [{

        "postoffice-code": "440000",
        "fragile": "false",
        "dimension": {
            "length": 40,
            "width": 40,
            "height": 10
        },
        "tel-address": order.phone,
        "surname": order.surname,
        "given-name": order.name,
        "middle-name": order.fathername,
        "mail-direct": 643,
        "address-type-to": "DEFAULT",
        "index-to": order.index,
        "region-to": order.region,
        "area-to": order.area,
        "place-to": order.city,
        "street-to": order.street,
        "house-to": order.house,
        "room-to": order.room,
        "mass": 1000,
        "mail-category": "ORDINARY",
        "mail-type": "POSTAL_PARCEL",
        "order-num": str(order.id),
        "transport-type": "SURFACE"
    }]

    url = protocol + host + path

    response = requests.put(url, headers=request_headers, data=json.dumps(addresses))
    ret = {}

    if response.status_code == 200:

        try:
            body = json.loads(response.content.decode('utf-8'))
            ret['result-ids'] = body['result-ids'][0]
            ret['ret_status'] = "success"
            return ret
        except:
            ret['ret_status'] = "error"
            return ret

    else:
        ret['ret_status'] = "error"
        return ret


def pr_pre_calc(index_to):
    path = "/1.0/tariff"

    addresses = {
        "completeness-checking": "false",
        "courier": "false",
        "declared-value": 0,
        "dimension": {
            "height": 10,
            "length": 40,
            "width": 40
        },
        "entries-type": "SALE_OF_GOODS",
        "fragile": "false",
        "index-from": "440000",
        "index-to": index_to,
        "mail-category": "ORDINARY",
        "mail-direct": 643,
        "mail-type": "POSTAL_PARCEL",
        "mass": 1000,
        "payment-method": "CASHLESS",
        "transport-type": "SURFACE",
        "with-order-of-notice": "false",
        "with-simple-notice": "true"
    }

    url = protocol + host + path

    response = requests.post(url, headers=request_headers, data=json.dumps(addresses))
    ret = {}

    if response.status_code == 200:

        try:
            body = json.loads(response.content.decode('utf-8'))

            ret['ret_status'] = "success"
            ret['max-days'] = body['delivery-time']['max-days']
            try:
                ret['min-days'] = body['delivery-time']['min-days']
            except:
                ret['min-days'] = 0
            ret['total'] = round(Decimal(body['total-rate'] / 100), 2)
            ret['nds'] = round(Decimal(body['total-vat'] / 100), 2)

            ret['total_nds'] = (ret['total'] + ret['nds'])
            return ret
        except:
            ret['ret_status'] = "error"
            return ret

    else:
        ret['ret_status'] = "error"
        return ret


def pr_address_normalize(country, region, area, city, street, house, room, index):
    path = "/1.0/clean/address"

    address = country + ", " + region + ", "

    if area != None:
        address = address + area + ", "

    address = address + city + ", " + street + ", " + house + ", "

    if room != None:
        address = address + room + ", "

    address = address + index

    addresses = [
        {
            "id": str(uuid.uuid4()),
            "original-address": address
        }
    ]

    url = protocol + host + path

    response = requests.post(url, headers=request_headers, data=json.dumps(addresses))
    ret = {}

    if response.status_code == 200:

        body = json.loads(response.content.decode('utf-8'))[0]

        if (body['quality-code'] == "GOOD" or body['quality-code'] == "POSTAL_BOX" or body[
            'quality-code'] == "ON_DEMAND" or body['quality-code'] == "UNDEF_05") and (
                body['validation-code'] == "VALIDATED" or body['validation-code'] == "OVERRIDDEN" or body[
            'validation-code'] == "CONFIRMED_MANUALLY"):
            ret['ret_status'] = "success"
            ret['body'] = body
            return ret

        else:
            return {"ret_status": "undefined"}

    else:
        ret['ret_status'] = "error"
        return ret
