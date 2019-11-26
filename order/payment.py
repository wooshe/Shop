import datetime

import requests
import xmltodict
from django.contrib.sites.shortcuts import get_current_site
from requests.auth import HTTPBasicAuth


status_pay_body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sir="http://www.sirena-travel.ru">
   <soapenv:Header/>
   <soapenv:Body>
      <sir:get_status>
         <sir:order>
            <!--You may enter the following 2 items in any order-->
            <sir:shop_id>{shop_id}</sir:shop_id>
            <sir:number>{order_id}</sir:number>
         </sir:order>
      </sir:get_status>
   </soapenv:Body>
</soapenv:Envelope>
    """

register_pay_body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sir="http://www.sirena-travel.ru">
   <soapenv:Header/>
   <soapenv:Body>
      <sir:register>
         <!--You may enter the following 5 items in any order-->
         <sir:order>
            <!--You may enter the following 2 items in any order-->
            <sir:shop_id>{shop_id}</sir:shop_id>
            <sir:number>{order_id}</sir:number>
         </sir:order>

         <sir:cost>
            <!--You may enter the following 2 items in any order-->
            <sir:currency>{currency}</sir:currency>
            <sir:amount>{price}</sir:amount>
         </sir:cost>

         <sir:customer>
            <!--You may enter the following 4 items in any order-->
            <sir:email>{user_email}</sir:email>
            <sir:name>{user_name}</sir:name>
            <sir:phone>{user_phone}</sir:phone>
            <sir:id>{user_id}</sir:id>
         </sir:customer>

         <sir:description>
            <!--You may enter the following 6 items in any order-->
            <sir:timelimit>2025-01-23T10:42:00.000Z</sir:timelimit>
            <sir:shopref>75f76cf3-8e9e-452d-a912-e942992517d9</sir:shopref>
<sir:items>
               <!--Zero or more repetitions:-->
               <sir:OrderItem>
                         <sir:amount>
                     <!--You may enter the following 2 items in any order-->
                     <sir:currency>RUB</sir:currency>
                     <sir:amount>3000</sir:amount>
                  </sir:amount>
                  <sir:number>1</sir:number>
                  <sir:descr>dfh</sir:descr>
                  <sir:quantity>1</sir:quantity>
               </sir:OrderItem>
            </sir:items>

            <sir:descr>abgdescr</sir:descr>
         </sir:description>


         <sir:postdata>
            <!--Zero or more repetitions:-->
            <sir:PostEntry>
               <!--You may enter the following 2 items in any order-->
               <sir:name>ReturnURLOk</sir:name>
               <sir:value>{ReturnURL}</sir:value>
            </sir:PostEntry>
                        
            <sir:PostEntry>
               <!--You may enter the following 2 items in any order-->
               <sir:name>ReturnURLFault</sir:name>
               <sir:value>{ReturnURLError}</sir:value>
            </sir:PostEntry>
            
         </sir:postdata>
      </sir:register>
   </soapenv:Body>
</soapenv:Envelope>
    """


def make_request(type, body):
    body = body.encode('utf-8')
    session = requests.session()
    session.headers = {"Content-Type": "text/xml; charset=utf-8"}
    session.headers.update({"Content-Length": str(len(body))})
    responce = session.post(url=endpoint, auth=HTTPBasicAuth(user, password), data=body, verify=False)
    return get_value(type, responce)


def get_value(type, responce):
    content = xmltodict.parse((responce.content).decode('utf-8'))

    if responce.status_code == 200 and responce.ok:

        if type == "register_pay":
            ret = content['soap-env:Envelope']['soap-env:Body']['registerResponse']['retval']
            ret['ret_status'] = "success"
            return ret

        elif type == "status_pay":
            ret = content['soap-env:Envelope']['soap-env:Body']['get_statusResponse']['retval']
            ret['ret_status'] = "success"
            return ret

        elif type == "cancel_pay":
            ret = content['soap-env:Envelope']['soap-env:Body']['cancelResponse']['retval']
            ret['ret_status'] = "success"
            return ret

        elif type == "refund_pay":
            return {'ret_status': "success"}

        else:
            return {"ret_status": "undefined"}

    else:
        ret = content['soap-env:Envelope']['soap-env:Body']['soap-env:Fault']
        ret['ret_status'] = "error"
        return ret


def register_pay(request, order_id, price, user_id=None, user_name=None, user_email=None, user_phone=None):
    user_id = user_id
    user_name = user_name
    user_email = user_email
    user_phone = user_phone
    now = datetime.datetime.now() + datetime.timedelta(minutes=30)
    timelimit = now.isoformat()

    current_site = get_current_site(request)
    site_name = current_site.name

    ReturnURL = "http://"+site_name+"/profile/?order_id=" + str(order_id)
    ReturnURLError = "http://"+site_name+"/cart/?order_id=" + str(order_id)

    body = register_pay_body.format(order_id=order_id, price=price, timelimit=timelimit,
                                    user_id=user_id, user_name=user_name, user_email=user_email, user_phone=user_phone,
                                    ReturnURL=ReturnURL, ReturnURLError=ReturnURLError,
                                    shop_id=shop_id, shopref=shopref, currency=currency, )

    return make_request('register_pay', body)
    # responce = make_request('register_pay', body)
    # return redirect(responce['redirect_url']+"?session="+responce['session'])


def status_pay(order_id):
    body = status_pay_body.format(order_id=order_id, shop_id=shop_id)

    responce = make_request('status_pay', body)
    return responce
