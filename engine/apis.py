import calendar
import csv
import logging
import random
from datetime import date, timedelta
import editdistance
import xmltodict
import pandas as pd
import math
import requests
import json
import uuid
import datetime
import socket

from pprint import pprint
from bs4 import BeautifulSoup

from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
from django.utils.safestring import SafeData, SafeText, mark_safe
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import *
from .constants import *
from .parsers import *


def call_api(input_query):
    try:
        s = socket.socket()
        port = int(SysConfig.objects.all()[0].api_port)  # Admin
        ip = SysConfig.objects.all()[0].api_ip  # Admin
        s.connect((ip, port))
        s.sendall(input_query)
        output_string = ""
        while True:
            data = s.recv(1024)
            if not data:
                break
            output_string += data
        s.close()
        return output_string
    except Exception as e:
        return "-5"				# Error code
        print("Exception: ", str(e))


def get_user_id(mobile_number):
    if not Config.objects.all()[0].prod:
        return "HARSH"

    input_query = """<XML>
				   <MessageType>1200</MessageType>
				   <ProcCode>E00011</ProcCode>
				   <LocalTxnDtTime>20060215034205</LocalTxnDtTime>
				   <Identifier>MA</Identifier>
				   <MobileNo>""" + mobile_number + """</MobileNo>
				   <UserID></UserID>
				   <DeliveryChannelCtrlID>TLB</DeliveryChannelCtrlID>
				   </XML>"""
    response = call_api(input_query)
    user_id = parse_user_id(response)
    return user_id


def get_grid_response(mobile_number, account_number, val1, val2, val3, index1, index2, index3, index4, index5, index6):
    if not Config.objects.all()[0].prod:
        return "000"

    input_query = '<XML>\
				<ProcCode>plugin5001</ProcCode>\
				<MessageType>1200</MessageType>\
				<DeliveryChannelCtrlId>RIB</DeliveryChannelCtrlId>\
				<LocalDateTimeStamp>20150315130211</LocalDateTimeStamp>\
				<STAN>202304</STAN>\
				<inputtype>A</inputtype>\
				<input>' + account_number + '</input>\
			<validation>\
				<value offset="' + index1 + '">' + val1[0] + '</value>\
				<value offset="' + index2 + '">' + val1[1] + '</value>\
				<value offset="' + index3 + '">' + val2[0] + '</value>\
				<value offset="' + index4 + '">' + val2[1] + '</value>\
				<value offset="' + index5 + '">' + val3[0] + '</value>\
				<value offset="' + index6 + '">' + val3[1] + '</value>\
			</validation>\
			 <REMARK></REMARK>\
			</XML>'

    response = call_api(input_query)
    actcode = parse_otp_send(response)
    return actcode


def get_list_of_payees(mobile_number, type_of_connection):
    user_id = get_user_id(mobile_number)
    #user_id = "RIB11XTEST"
    input_query = """<XML>
	<HEADER>UBPS</HEADER>
	<MessageType>1200</MessageType>
	<ProcCode>960800</ProcCode>
	<TxnAmt>0</TxnAmt>
	<STAN>20141216006</STAN>
	<LocalTxnDtTime>00180207075531</LocalTxnDtTime>
	<CaptureDt>20180207</CaptureDt>
	<FuncCode>200</FuncCode>
	<AcqInstIdenCode>504642</AcqInstIdenCode>
	<Identification1>""" + user_id + """</Identification1>
	<Currency>INR</Currency>
	<ConsumerNo />
	<AcctIdentificationOne>                                      </AcctIdentificationOne>
	<DeliveryChannelCtrlID>IMB</DeliveryChannelCtrlID>
	<AddDataPvt125>
		<UbpsReqTyp>08</UbpsReqTyp>
		<PayeeID />
		<InstancePymntDate />
		<ScheduleId></ScheduleId>
		<NoOfPayements>12</NoOfPayements>
		<PaymentType>P</PaymentType>
	</AddDataPvt125>
</XML>"""
    print("Request payee id is: ", input_query)
    response = call_api(input_query)
    print(response)
    payee_ids_1 = parse_payee_ids_amount(response, "P")

    input_query = """<XML>
	<HEADER>UBPS</HEADER>
	<MessageType>1200</MessageType>
	<ProcCode>960800</ProcCode>
	<TxnAmt>0</TxnAmt>
	<STAN>20141216006</STAN>
	<LocalTxnDtTime>00180207075531</LocalTxnDtTime>
	<CaptureDt>20180207</CaptureDt>
	<FuncCode>200</FuncCode>
	<AcqInstIdenCode>504642</AcqInstIdenCode>
	<Identification1>""" + user_id + """</Identification1>
	<Currency>INR</Currency>
	<ConsumerNo />
	<AcctIdentificationOne>                                      </AcctIdentificationOne>
	<DeliveryChannelCtrlID>IMB</DeliveryChannelCtrlID>
	<AddDataPvt125>
		<UbpsReqTyp>08</UbpsReqTyp>
		<PayeeID />
		<InstancePymntDate />
		<ScheduleId></ScheduleId>
		<NoOfPayements>12</NoOfPayements>
		<PaymentType>N</PaymentType>
	</AddDataPvt125>
</XML>"""
    response = call_api(input_query)
    print(response)
    payee_ids_2 = parse_payee_ids_amount(response, "N")
    payee_ids = payee_ids_1 + payee_ids_2
    print(payee_ids)
    return payee_ids


def write_file(data):
    f = open("logger.txt", "a+")
    f.write(data + "\n")
    f.close()


def get_list_of_connections(mobile_number):
    user_id = get_user_id(mobile_number)
    write_file(user_id)
    #user_id = "RIB11XTEST"
    input_query = """<XML>
	<HEADER>UBPS</HEADER>
	<MessageType>1200</MessageType>
	<ProcCode>960800</ProcCode>
	<TxnAmt>0</TxnAmt>
	<STAN>20180618006</STAN>
	<LocalTxnDtTime>00180207075531</LocalTxnDtTime>
	<CaptureDt>20180207</CaptureDt>
	<FuncCode>200</FuncCode>
	<AcqInstIdenCode>504642</AcqInstIdenCode>
	<Identification1>""" + user_id + """</Identification1>
	<Currency>INR</Currency>
	<ConsumerNo />
	<AcctIdentificationOne>                                      </AcctIdentificationOne>
	<DeliveryChannelCtrlID>IMB</DeliveryChannelCtrlID>
	<AddDataPvt125>
		<UbpsReqTyp>08</UbpsReqTyp>
		<PayeeID />
		<InstancePymntDate />
		<ScheduleId></ScheduleId>
		<NoOfPayements>4</NoOfPayements>
		<PaymentType> </PaymentType>
	</AddDataPvt125>
</XML>"""
    input_query = input_query.replace("\n\t", "")
    input_query = input_query.replace("\t", "")
    print("Request payee id is: ", input_query)
    write_file(input_query)
    response = call_api(input_query)
    write_file(response)
    print(response)
    payee_ids = parse_payee_ids(response)
    print("Payee ids are: ", payee_ids)
    write_file(str(payee_ids))
    list_different_connections = []
    for i in range(len(payee_ids)):
        payee_ids[i] = payee_ids[i].lstrip('0')
    set_payee = set(payee_ids)
    write_file(str(set_payee))
    print(set_payee)
    for payee_id in set_payee:
        if payee_id != "":
            try:
                print(payee_id)
                a = BillApiCustom.objects.filter(payee_id=payee_id)[0]
                print(a)
                list_different_connections.append(a.payee_type)
                print(a)
            except:
                pass
    print(list_different_connections)
    return list_different_connections


def get_account_numbers_original(mobile_number):
    if not Config.objects.all()[0].prod:
        return ["12800003412", "12800004512"]
    
    user_id = get_user_id(mobile_number)    
    input_query = """<XML>
					 <MessageType>1104</MessageType>
					 <ProcCode>916000</ProcCode>
					 <STAN>020202020202</STAN>
					 <LocalTxnDtTime>20090903105241</LocalTxnDtTime>
					 <FuncCode>200</FuncCode>
					 <PvtDataField48>
					 <UserID>""" + user_id + """</UserID>
					 </PvtDataField48>
					 <TxnDestnCode>3</TxnDestnCode>
					 <TxnOrigCode>8</TxnOrigCode>
					 <DeliveryChannelCtrlID>ACS</DeliveryChannelCtrlID>
					 </XML>"""
    response = call_api(input_query)    
    account_numbers = parse_account_numbers(response)        
    return account_numbers


def get_account_numbers(mobile_number):
    if not Config.objects.all()[0].prod:
        return ["ending in 3@4@1@2", "ending in 4@5@1@2"]

    user_id = get_user_id(mobile_number)
    input_query = """<XML>
					 <MessageType>1104</MessageType>
					 <ProcCode>916000</ProcCode>
					 <STAN>020202020202</STAN>
					 <LocalTxnDtTime>20090903105241</LocalTxnDtTime>
					 <FuncCode>200</FuncCode>
					 <PvtDataField48>
					 <UserID>""" + user_id + """</UserID>
					 </PvtDataField48>
					 <TxnDestnCode>3</TxnDestnCode>
					 <TxnOrigCode>8</TxnOrigCode>
					 <DeliveryChannelCtrlID>ACS</DeliveryChannelCtrlID>
					 </XML>"""
    response = call_api(input_query)
    account_numbers = parse_account_numbers(response)
    for i in range(len(account_numbers)):
        acc_temp = account_numbers[i][-4:]
        acc_temp = "@".join(acc_temp)
        account_numbers[i] = "ending in " + acc_temp
    print("Account numbers are : ", account_numbers)
    return account_numbers


def pay_bill(mobile_number, amount, account_number, consumer_code, payee_id):
    user_id = get_user_id(mobile_number)
    account_number = "ICI" + "        " + \
        str(account_number)[0:4] + "    " + str(account_number)
    input_query = """<XML><HEADER MSGFORMATID="157" PASSTHROUGH="N" ROUTEHOSTTYPE="UBPS" ROUTETO="UBPS" SCRIPTNAME="com.mphasis.businessScripts.bin.ChangeAttribute"></HEADER><MessageType DEFAULT="1200" DT="numeric" LSP="0" MNL="4" MXL="4" PL="4" PRE="mandatory">1200</MessageType><ProcCode DEFAULT="961100" DT="numeric" IND="3" LSP="0" MNL="6" MXL="6" PL="6" PRE="mandatory">961100</ProcCode><TxnAmt DT="numeric" IND="4" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">""" + amount + """</TxnAmt><STAN DT="alphabetnumericspaces" IND="11" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">000151182800</STAN><LocalTxnDtTime DT="numeric" IND="12" LSP="0" MNL="14" MXL="14" PL="14" PRE="mandatory">20160808151651</LocalTxnDtTime><CaptureDt DT="date" IND="17" LSP="0" MNL="8" MXL="8" PL="8" PRE="optional">20160808</CaptureDt><FuncCode DT="numeric" IND="24" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">200</FuncCode><AcqInstIdenCode DT="numeric" IND="32" LSP="2" MNL="1" MXL="11" PL="" PRE="mandatory">504642</AcqInstIdenCode><Identification1 MXL="28" MNL="1" DT="alphabetnumeric" PL="" LSP="2" IND="34" PRE="mandatory">""" + user_id + """</Identification1><RRNNumber DT="numeric" IND="37" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">120809133559</RRNNumber><CardAccTerminalID DT="alphabetnumericspaces" IND="41" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">UBPS</CardAccTerminalID><CardAccIdentification DT="alphabetnumericspaces" IND="42" LSP="0" MNL="15" MXL="15" PL="15" PRE="optional">504642</CardAccIdentification><CardAccNameLocation DT="alphabetnumericspaces" IND="43" LSP="2" MNL="1" MXL="99" PL="" PRE="optional">UBPS</CardAccNameLocation><Currency DT="alphabetnumeric" IND="49" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">INR</Currency><PrivateField DT="alphabetnumericspecialspaces" IND="60" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField><PrivateField2 DT="alphabetnumericspecialspaces" IND="61" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField2><ConsumerNumber DT="alphabetnumericspecialspaces" IND="63" LSP="3" MNL="01" MXL="999" PL="" PRE="optional">""" + consumer_code + """</ConsumerNumber><AcctIdentificationOne DT="alphabetnumericspecialspaces" IND="102" LSP="2" MNL="01" MXL="38" PL="" PRE="mandatory">""" + account_number + """</AcctIdentificationOne><DeliveryChannelCtrlID DT="alphabet" IND="123" LSP="3" MNL="1" MXL="3" PL="" PRE="mandatory">IMB</DeliveryChannelCtrlID><AddDataPvt125 DT="alphabetnumericspecialspaces" IND="125" LSP="3" MNL="1" MXL="999" PL="" PRE="optional" RLI="0"><UbpsReqTyp DT="alphabetnumeric" IND="125" LSP="0" MNL="2" MXL="2" PL="" PRE="optional">11</UbpsReqTyp><ScheduleBegngDate DT="alphabetnumericspaces" IND="125" LSP="0" MNL="8" MXL="8" PL="" PRE="optional">00000000</ScheduleBegngDate><PayementFrequency DT="numeric" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">0</PayementFrequency><TotNoOfPymnts DT="numeric" IND="125" LSP="0" MNL="5" MXL="5" PL="" PRE="optional">00001</TotNoOfPymnts><PayeeID DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="12" MXL="12" PL="" PRE="optional">""" + payee_id + """</PayeeID><PaymntRemrks DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional">Hi</PaymntRemrks><BillRefInfo DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional"></BillRefInfo><ValidationFlag DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">A</ValidationFlag><PersonalPayee DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional"></PersonalPayee><PayeeNick DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="40" MXL="40" PL="" PRE="optional"></PayeeNick><ConsumerCode DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="64" MXL="64" PL="" PRE="optional">""" + consumer_code + """</ConsumerCode></AddDataPvt125></XML>
	"""
    print("Input: ", input_query)
    response = call_api(input_query)
    print(response)


def pay_credit_card_bill(mobile_number, credit_card_number, account_number):
    if not Config.objects.all()[0].prod:
        return "000"

    user_id = get_user_id(mobile_number)
    txn_due, txn_amount = get_credit_card_details(
        credit_card_number, mobile_number)
    account_number = "ICI" + "        " + \
        account_number[0:4] + "    " + account_number
    
    last_4_digit = ""
    for d in credit_card_number:
        print(d)
        if d.isdigit():
            last_4_digit += d
    credit_card_numbers = get_credit_card_numbers_original(mobile_number)
    for cc in credit_card_numbers:
        if cc[-4:] == last_4_digit:
            credit_card_number = cc
    input_query = """
	<XML>
	<HEADER MSGFORMATID="157" PASSTHROUGH="N" ROUTEHOSTTYPE="UBPS" ROUTETO="UBPS" SCRIPTNAME="com.mphasis.businessScripts.bin.ChangeAttribute"></HEADER>
	<MessageType DEFAULT="1200" DT="numeric" LSP="0" MNL="4" MXL="4" PL="4" PRE="mandatory">1200</MessageType>
	<ProcCode DEFAULT="961100" DT="numeric" IND="3" LSP="0" MNL="6" MXL="6" PL="6" PRE="mandatory">961100</ProcCode>
	<TxnAmt DT="numeric" IND="4" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">""" + txn_amount + """</TxnAmt>
	<STAN DT="alphabetnumericspaces" IND="11" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">002064724924</STAN>
	<LocalTxnDtTime DT="numeric" IND="12" LSP="0" MNL="14" MXL="14" PL="14" PRE="mandatory">20180207202344</LocalTxnDtTime>
	<CaptureDt DT="date" IND="17" LSP="0" MNL="8" MXL="8" PL="8" PRE="optional">20180207</CaptureDt>
	<FuncCode DT="numeric" IND="24" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">200</FuncCode>
	<AcqInstIdenCode DT="numeric" IND="32" LSP="2" MNL="1" MXL="11" PL="" PRE="mandatory">504642</AcqInstIdenCode>
	<Identification1 MXL="28" MNL="1" DT="alphabetnumeric" PL="" LSP="2" IND="34" PRE="mandatory">""" + user_id + """</Identification1>
	<RRNNumber DT="numeric" IND="37" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">120809133559</RRNNumber>
	<CardAccTerminalID DT="alphabetnumericspaces" IND="41" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">UBPS</CardAccTerminalID>
	<CardAccIdentification DT="alphabetnumericspaces" IND="42" LSP="0" MNL="15" MXL="15" PL="15" PRE="optional">504642</CardAccIdentification>
	<CardAccNameLocation DT="alphabetnumericspaces" IND="43" LSP="2" MNL="1" MXL="99" PL="" PRE="optional">UBPS</CardAccNameLocation>
	<Currency DT="alphabetnumeric" IND="49" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">INR</Currency>
	<PrivateField DT="alphabetnumericspecialspaces" IND="60" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField>
	<PrivateField2 DT="alphabetnumericspecialspaces" IND="61" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField2>
	<ConsumerNumber DT="alphabetnumericspecialspaces" IND="63" LSP="3" MNL="01" MXL="999" PL="" PRE="optional">""" + credit_card_number + """</ConsumerNumber>
	<AcctIdentificationOne DT="alphabetnumericspecialspaces" IND="102" LSP="2" MNL="01" MXL="38" PL="" PRE="mandatory">""" + account_number + """</AcctIdentificationOne>
	<DeliveryChannelCtrlID DT="alphabet" IND="123" LSP="3" MNL="1" MXL="3" PL="" PRE="mandatory">IMB</DeliveryChannelCtrlID>
	<AddDataPvt125 DT="alphabetnumericspecialspaces" IND="125" LSP="3" MNL="1" MXL="999" PL="" PRE="optional" RLI="0">
		<UbpsReqTyp DT="alphabetnumeric" IND="125" LSP="0" MNL="2" MXL="2" PL="" PRE="optional">11</UbpsReqTyp>
		<ScheduleBegngDate DT="alphabetnumericspaces" IND="125" LSP="0" MNL="8" MXL="8" PL="" PRE="optional">00000000</ScheduleBegngDate>
		<PayementFrequency DT="numeric" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">0</PayementFrequency>
		<TotNoOfPymnts DT="numeric" IND="125" LSP="0" MNL="5" MXL="5" PL="" PRE="optional">01</TotNoOfPymnts>
		<PayeeID DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="12" MXL="12" PL="" PRE="optional">000000001232</PayeeID>
		<PaymntRemrks DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional"></PaymntRemrks>
		<BillRefInfo DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional"></BillRefInfo>
		<ValidationFlag DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">A</ValidationFlag>
		<PersonalPayee DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional"></PersonalPayee>
		<PayeeNick DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="40" MXL="40" PL="" PRE="optional"></PayeeNick>
		<ConsumerCode DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="64" MXL="64" PL="" PRE="optional">""" + credit_card_number + """</ConsumerCode>
	</AddDataPvt125>
</XML>
	"""
    input_query = input_query.replace("\n", "")
    response = call_api(input_query)
    acct_code = parse_pay_creditcard_bill(response)
    return acct_code

def generate_ticket(credit_card_number):
	input_query = """<XML><MessageType>1200</MessageType><ProcCode>777001</ProcCode><SOAPMessage><soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'xmlns:xsd='http://www.w3.org/2001/XMLSchema'><soap:Body><AcquireTicket xmlns='http://CTL.COM.Services.Prime.Issuer.WebServices/PrimeIssuerServices'><xmlRequest><Header><MessageID>1111</MessageID><CorrelationID></CorrelationID><SystemID></SystemID><RequestorID></RequestorID><Ticket>"""+credit_card_number+"""</Ticket>    (CREDIT CARD number need to pass)<CallerRef></CallerRef><Origin></Origin><Culture></Culture></Header><Ticket><hostIP></hostIP><applicationName></applicationName></Ticket></xmlRequest></AcquireTicket></soap:Body></soap:Envelope></SOAPMessage></XML>"""
	response = call_api(input_query)
	ticket_number = parse_ticket_number(response)
	return ticket_number

def get_credit_card_details(credit_card_number, mobile_number):
    if not Config.objects.all()[0].prod:
        return ("04/04/2016", "121212")

    last_4_digit = ""
    for d in credit_card_number:
        if d.isdigit():
            last_4_digit += d
    credit_card_numbers = get_credit_card_numbers_original(mobile_number)
    for cc in credit_card_numbers:
        if cc[-4:] == last_4_digit:
            credit_card_number = cc

    ticket_number = generate_ticket(credit_card_number)

    #input_query = """<XML><MessageType MXL='4' MNL='4' PL='4' DT='numeric' LSP='0' PRE='mandatory' DEFAULT='1200'>1200</MessageType><CustID MXL='19' MNL='19' DT='numeric' PL='19' LSP='0' IND='2' PRE='mandatory'>""" + credit_card_number + """</CustID><ProcCode MXL='6' MNL='6' PL='6' DT='numeric' LSP='0' IND='3' PRE='mandatory' DEFAULT='610000'>610000</ProcCode><TxnAmt MXL='16' MNL='16' DT='numeric' PL='16' LSP='0' IND='4' PRE='mandatory'>1</TxnAmt><STAN MXL='6' MNL='6' DT='numeric' PL='6' LSP='0' IND='11' PRE='mandatory'>123456</STAN><LocalTxnDtTime MXL='12' MNL='12' DT='numeric' PL='12' LSP='0' IND='12' PRE='mandatory'>20180129152948</LocalTxnDtTime><CaptureDt MXL='8' MNL='8' DT='numeric' PL='' LSP='0' IND='17' PRE='mandatory'>19991015</CaptureDt><FuncCode MXL='3' MNL='3' DT='numeric' PL='' LSP='0' IND='24' PRE='mandatory' OVERRIDE='200'>200</FuncCode><AcqInstIdenCode MXL='11' MNL='1' DT='numeric' PL='' LSP='2' IND='32' PRE='mandatory' OVERRIDE='010'>001</AcqInstIdenCode><Currency MXL='3' MNL='3' DT='alphabet' PL='' LSP='0' IND='49' PRE='mandatory' DEFAULT='INR'>INR</Currency><FaxNo MXL='999' MNL='1' DT='alphabetnumericspecialspaces' PL='' LSP='3' IND='59' PRE='optional' /><FourDigitYear MXL='999' MNL='1' DT='alphabetnumericspecial' PL='' LSP='3' IND='62' PRE='mandatory'>1999</FourDigitYear><ConsumerNo MXL='28' MNL='1' DT='alphabetnumericspaces' PL='' LSP='2' IND='63' PRE='optional'>1</ConsumerNo><AcctIdentificationOne MXL='38' MNL='1' DT='alphabetnumericspaces' PL='' LSP='2' IND='102' PRE='mandatory'>""" + \
    #    credit_card_number + """</AcctIdentificationOne><DeliveryChannelCtrlID MXL='3' MNL='3' DT='alphabet' PL='' LSP='0' IND='123' PRE='mandatory' OVERRIDE='INT'>CCI</DeliveryChannelCtrlID><AddDataPvt125 MXL='999' MNL='1' DT='alphabetnumericspecialspaces' PL='' LSP='3' IND='125' RLI='0' PRE='optional'><RecordFrom MXL='999' MNL='1' DT='numeric' PRE='optional' PL='' LSP='1' IND='125'>1</RecordFrom><NoofRecordRequested MXL='99' MNL='1' DT='numeric' PRE='optional' PL='' LSP='1' IND='125'>16</NoofRecordRequested></AddDataPvt125></XML>"""
    input_query = """<XML><MessageType>1200</MessageType><ProcCode>777010</ProcCode><SOAPMessage><soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'xmlns:xsd='http://www.w3.org/2001/XMLSchema'><soap:Body><StatementInquiry xmlns='http://CTL.COM.Services.Prime.Issuer.WebServices/PrimeIssuerServices'><xmlRequest><Header><MessageID>1234</MessageID><CorrelationID></CorrelationID><SystemID></SystemID><RequestorID></RequestorID><Ticket>"""+ticket_number+"""</Ticket><CallerRef></CallerRef><Origin></Origin><Culture></Culture></Header><Paging><Size>0</Size><Key></Key></Paging><Period>Last</Period><DateFrom></DateFrom><DateTo></DateTo><Content>Account</Content><Reference>C</Reference><Number>"""+credit_card_number+"""</Number><HierarchicalTrxns>false</HierarchicalTrxns><CustomerNumber></CustomerNumber><LevelDepth>0</LevelDepth><TransactionMemos>None</TransactionMemos></xmlRequest></StatementInquiry></soap:Body></soap:Envelope></SOAPMessage></XML>"""
    response = call_api(input_query)
    due_date, due_amount = parse_cc_date_amount(response)
    return (due_date, due_amount)


def get_credit_card_numbers_original(mobile_number):
    if not Config.objects.all()[0].prod:
        return ["1231231231", "1234123412341"]

    user_id = get_user_id(mobile_number)
    input_query = """<XML>
					 <MessageType>1104</MessageType>
					 <ProcCode>916000</ProcCode>
					 <STAN>020202020202</STAN>
					 <LocalTxnDtTime>20090903105241</LocalTxnDtTime>
					 <FuncCode>200</FuncCode>
					 <PvtDataField48>
					 <UserID>""" + user_id + """</UserID>
					 </PvtDataField48>
					 <TxnDestnCode>3</TxnDestnCode>
					 <TxnOrigCode>8</TxnOrigCode>
					 <DeliveryChannelCtrlID>ACS</DeliveryChannelCtrlID>
					 </XML>"""
    response = call_api(input_query)
    creditcard_numbers = parse_credit_card_numbers(response)
    return creditcard_numbers


def get_credit_card_numbers(mobile_number):
    if not Config.objects.all()[0].prod:
        return ["ending in 1@2@3@1", "ending in 2@3@4@1"]

    user_id = get_user_id(mobile_number)
    input_query = """<XML>
					 <MessageType>1104</MessageType>
					 <ProcCode>916000</ProcCode>
					 <STAN>020202020202</STAN>
					 <LocalTxnDtTime>20090903105241</LocalTxnDtTime>
					 <FuncCode>200</FuncCode>
					 <PvtDataField48>
					 <UserID>""" + user_id + """</UserID>
					 </PvtDataField48>
					 <TxnDestnCode>3</TxnDestnCode>
					 <TxnOrigCode>8</TxnOrigCode>
					 <DeliveryChannelCtrlID>ACS</DeliveryChannelCtrlID>
					 </XML>"""
    response = call_api(input_query)
    creditcard_numbers = parse_credit_card_numbers(response)
    for i in range(len(creditcard_numbers)):
        credit_card_temp = creditcard_numbers[i][-4:]
        credit_card_temp = "@".join(credit_card_temp)
        creditcard_numbers[i] = "ending in " + credit_card_temp
    return creditcard_numbers

def get_balance(account_number, mobile_number):
    if not Config.objects.all()[0].prod:
        return ("120", "100", "220")

    last_4_digit = ""
    for d in account_number:
        print(d)
        if d.isdigit():
            last_4_digit += d
    account_numbers = get_account_numbers_original(mobile_number)
    for acc in account_numbers:
        if acc[-4:] == last_4_digit:
            account_number = acc
    acc_num = "ICI" + "        " + \
        account_number[0:4] + "    " + account_number
    input_query = """<XML><MessageType DEFAULT="1200" DT="numeric" LSP="0" MNL="4" MXL="4" PL="4" PRE="mandatory">1200</MessageType><CustID DT="numeric" IND="2" LSP="2" MNL="1" MXL="19" PL="19" PRE="optional">""" + account_number + \
        """</CustID><ProcCode DEFAULT="380000" DT="numeric" IND="3" LSP="0" MNL="6" MXL="6" PL="6" PRE="mandatory">380000</ProcCode><AuthNum DT="alphabetnumericspaces" IND="11" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">0</AuthNum><LocalTxnDtTime DT="numeric" IND="12" LSP="0" MNL="14" MXL="14" PL="14" PRE="mandatory">20180510031525</LocalTxnDtTime><CaptureDt DT="date" IND="17" LSP="0" MNL="8" MXL="8" PL="8" PRE="mandatory">20180510</CaptureDt><FuncCode DT="numeric" IND="24" LSP="0" MNL="3" MXL="3" PL="3" PRE="mandatory">200</FuncCode><AcqInstIdenCode DT="numeric" IND="32" LSP="2" MNL="1" MXL="11" PL="6" PRE="mandatory">504642</AcqInstIdenCode><INR DT="alphabet" IND="49" LSP="0" MNL="3" MXL="3" PL="3" PRE="mandatory">INR</INR><AccNum DT="alphabetnumericspaces" IND="102" LSP="2" MNL="1" MXL="38" PL="" PRE="mandatory">""" + \
        acc_num + """</AccNum><DeliveryChannelCtrlID DT="alphabetnumericspecial" IND="123" LSP="3" MNL="1" MXL="999" PL="3" PRE="mandatory">TLB</DeliveryChannelCtrlID></XML>"""
    response = call_api(input_query)
    available_balance, fd_balance, effective_balance = parse_account_balance(response)
    return (available_balance, fd_balance, effective_balance)

def recharge_mobile_topup(mobile_number, amount, account_numbers):
    if not Config.objects.all()[0].prod:
        return "000"

    user_id = get_user_id(mobile_number)
    account_number = "ICI" + "        " + \
        str(account_numbers)[0:4] + "    " + str(account_numbers)
    input_query = """<XML><HEADER MSGFORMATID="157" PASSTHROUGH="N" ROUTEHOSTTYPE="UBPS" ROUTETO="UBPS" SCRIPTNAME="com.mphasis.businessScripts.bin.ChangeAttribute"></HEADER><MessageType DEFAULT="1200" DT="numeric" LSP="0" MNL="4" MXL="4" PL="4" PRE="mandatory">1200</MessageType><ProcCode DEFAULT="961100" DT="numeric" IND="3" LSP="0" MNL="6" MXL="6" PL="6" PRE="mandatory">961100</ProcCode><TxnAmt DT="numeric" IND="4" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">""" + amount + """</TxnAmt><STAN DT="alphabetnumericspaces" IND="11" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">000151182800</STAN><LocalTxnDtTime DT="numeric" IND="12" LSP="0" MNL="14" MXL="14" PL="14" PRE="mandatory">20160808151651</LocalTxnDtTime><CaptureDt DT="date" IND="17" LSP="0" MNL="8" MXL="8" PL="8" PRE="optional">20160808</CaptureDt><FuncCode DT="numeric" IND="24" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">200</FuncCode><AcqInstIdenCode DT="numeric" IND="32" LSP="2" MNL="1" MXL="11" PL="" PRE="mandatory">504642</AcqInstIdenCode><Identification1 MXL="28" MNL="1" DT="alphabetnumeric" PL="" LSP="2" IND="34" PRE="mandatory">"""+user_id+"""</Identification1><RRNNumber DT="numeric" IND="37" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">120809133559</RRNNumber><CardAccTerminalID DT="alphabetnumericspaces" IND="41" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">UBPS</CardAccTerminalID><CardAccIdentification DT="alphabetnumericspaces" IND="42" LSP="0" MNL="15" MXL="15" PL="15" PRE="optional">504642</CardAccIdentification><CardAccNameLocation DT="alphabetnumericspaces" IND="43" LSP="2" MNL="1" MXL="99" PL="" PRE="optional">UBPS</CardAccNameLocation><Currency DT="alphabetnumeric" IND="49" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">INR</Currency><PrivateField DT="alphabetnumericspecialspaces" IND="60" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField><PrivateField2 DT="alphabetnumericspecialspaces" IND="61" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField2><ConsumerNumber DT="alphabetnumericspecialspaces" IND="63" LSP="3" MNL="01" MXL="999" PL="" PRE="optional">""" + \
        mobile_number + """</ConsumerNumber><AcctIdentificationOne DT="alphabetnumericspecialspaces" IND="102" LSP="2" MNL="01" MXL="38" PL="" PRE="mandatory">""" + account_number + """</AcctIdentificationOne><DeliveryChannelCtrlID DT="alphabet" IND="123" LSP="3" MNL="1" MXL="3" PL="" PRE="mandatory">IMB</DeliveryChannelCtrlID><AddDataPvt125 DT="alphabetnumericspecialspaces" IND="125" LSP="3" MNL="1" MXL="999" PL="" PRE="optional" RLI="0"><UbpsReqTyp DT="alphabetnumeric" IND="125" LSP="0" MNL="2" MXL="2" PL="" PRE="optional">11</UbpsReqTyp><ScheduleBegngDate DT="alphabetnumericspaces" IND="125" LSP="0" MNL="8" MXL="8" PL="" PRE="optional">00000000</ScheduleBegngDate><PayementFrequency DT="numeric" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">0</PayementFrequency><TotNoOfPymnts DT="numeric" IND="125" LSP="0" MNL="5" MXL="5" PL="" PRE="optional">00001</TotNoOfPymnts><PayeeID DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="12" MXL="12" PL="" PRE="optional">000000000230</PayeeID><PaymntRemrks DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional">Hi</PaymntRemrks><BillRefInfo DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional">TOPUP-VODMU20-</BillRefInfo><ValidationFlag DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">A</ValidationFlag><PersonalPayee DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional"></PersonalPayee><PayeeNick DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="40" MXL="40" PL="" PRE="optional"></PayeeNick><ConsumerCode DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="64" MXL="64" PL="" PRE="optional">""" + mobile_number + """</ConsumerCode></AddDataPvt125></XML>"""
    response = call_api(input_query)
    acc_code = parse_recharge_mobile(response)
    return acc_code


def recharge_mobile(mobile_number, amount, account_numbers):
    if not Config.objects.all()[0].prod:
        return "000"

    user_id = get_user_id(mobile_number)
    account_number = "ICI" + "        " + \
        str(account_numbers)[0:4] + "    " + str(account_numbers)
    input_query = """<XML><HEADER MSGFORMATID="157" PASSTHROUGH="N" ROUTEHOSTTYPE="UBPS" ROUTETO="UBPS" SCRIPTNAME="com.mphasis.businessScripts.bin.ChangeAttribute"></HEADER><MessageType DEFAULT="1200" DT="numeric" LSP="0" MNL="4" MXL="4" PL="4" PRE="mandatory">1200</MessageType><ProcCode DEFAULT="961100" DT="numeric" IND="3" LSP="0" MNL="6" MXL="6" PL="6" PRE="mandatory">961100</ProcCode><TxnAmt DT="numeric" IND="4" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">""" + amount + """</TxnAmt><STAN DT="alphabetnumericspaces" IND="11" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">000151182800</STAN><LocalTxnDtTime DT="numeric" IND="12" LSP="0" MNL="14" MXL="14" PL="14" PRE="mandatory">20160808151651</LocalTxnDtTime><CaptureDt DT="date" IND="17" LSP="0" MNL="8" MXL="8" PL="8" PRE="optional">20160808</CaptureDt><FuncCode DT="numeric" IND="24" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">200</FuncCode><AcqInstIdenCode DT="numeric" IND="32" LSP="2" MNL="1" MXL="11" PL="" PRE="mandatory">504642</AcqInstIdenCode><Identification1 MXL="28" MNL="1" DT="alphabetnumeric" PL="" LSP="2" IND="34" PRE="mandatory">"""+user_id+"""</Identification1><RRNNumber DT="numeric" IND="37" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">120809133559</RRNNumber><CardAccTerminalID DT="alphabetnumericspaces" IND="41" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">UBPS</CardAccTerminalID><CardAccIdentification DT="alphabetnumericspaces" IND="42" LSP="0" MNL="15" MXL="15" PL="15" PRE="optional">504642</CardAccIdentification><CardAccNameLocation DT="alphabetnumericspaces" IND="43" LSP="2" MNL="1" MXL="99" PL="" PRE="optional">UBPS</CardAccNameLocation><Currency DT="alphabetnumeric" IND="49" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">INR</Currency><PrivateField DT="alphabetnumericspecialspaces" IND="60" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField><PrivateField2 DT="alphabetnumericspecialspaces" IND="61" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField2><ConsumerNumber DT="alphabetnumericspecialspaces" IND="63" LSP="3" MNL="01" MXL="999" PL="" PRE="optional">""" + \
        mobile_number + """</ConsumerNumber><AcctIdentificationOne DT="alphabetnumericspecialspaces" IND="102" LSP="2" MNL="01" MXL="38" PL="" PRE="mandatory">""" + account_number + """</AcctIdentificationOne><DeliveryChannelCtrlID DT="alphabet" IND="123" LSP="3" MNL="1" MXL="3" PL="" PRE="mandatory">IMB</DeliveryChannelCtrlID><AddDataPvt125 DT="alphabetnumericspecialspaces" IND="125" LSP="3" MNL="1" MXL="999" PL="" PRE="optional" RLI="0"><UbpsReqTyp DT="alphabetnumeric" IND="125" LSP="0" MNL="2" MXL="2" PL="" PRE="optional">11</UbpsReqTyp><ScheduleBegngDate DT="alphabetnumericspaces" IND="125" LSP="0" MNL="8" MXL="8" PL="" PRE="optional">00000000</ScheduleBegngDate><PayementFrequency DT="numeric" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">0</PayementFrequency><TotNoOfPymnts DT="numeric" IND="125" LSP="0" MNL="5" MXL="5" PL="" PRE="optional">00001</TotNoOfPymnts><PayeeID DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="12" MXL="12" PL="" PRE="optional">000000000230</PayeeID><PaymntRemrks DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional">Hi</PaymntRemrks><BillRefInfo DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional">TOPUP-VODMU20-</BillRefInfo><ValidationFlag DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">A</ValidationFlag><PersonalPayee DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional"></PersonalPayee><PayeeNick DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="40" MXL="40" PL="" PRE="optional"></PayeeNick><ConsumerCode DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="64" MXL="64" PL="" PRE="optional">""" + mobile_number + """</ConsumerCode></AddDataPvt125></XML>"""
    response = call_api(input_query)
    acc_code = parse_recharge_mobile(response)
    return acc_code


def get_bill_connections(mobile_number, type_of_connection):
    user_id = get_user_id(mobile_number)
    bill_connections = ["Mahanagar Connection", "Vivanagar Connection"]
    return bill_connections


def get_payees(mobile_number):
    #user_id = get_user_id(mobile_number)
    user_id = "RIB11XTEST"
    input_query = """<XML>
	<HEADER>UBPS</HEADER>
	<MessageType>1200</MessageType>
	<ProcCode>960800</ProcCode>
	<TxnAmt>0</TxnAmt>
	<STAN>20141216006</STAN>
	<LocalTxnDtTime>00180207075531</LocalTxnDtTime>
	<CaptureDt>20180207</CaptureDt>
	<FuncCode>200</FuncCode>
	<AcqInstIdenCode>504642</AcqInstIdenCode>
	<Identification1>RIB11XTEST</Identification1>
	<Currency>INR</Currency>
	<ConsumerNo />
	<AcctIdentificationOne>                                      </AcctIdentificationOne>
	<DeliveryChannelCtrlID>IMB</DeliveryChannelCtrlID>
	<AddDataPvt125>
		<UbpsReqTyp>08</UbpsReqTyp>
		<PayeeID />
		<InstancePymntDate />
		<ScheduleId></ScheduleId>
		<NoOfPayements>12</NoOfPayements>
		<PaymentType> </PaymentType>
	</AddDataPvt125>
</XML>"""
    response = call_api(input_query)
    print("Response is: ", response)

def get_topup_list(mobile_number):
	r = requests.get("https://invas01.euronetworldwide.com/RechargePlansAPI_prod/RechargePlans.aspx?merchantcode=ICI&servicecode=MR&consumerno=&spcode=ART&sspcode=ARTBH")
	print(r.text)
	r = xmltodict.parse(r.text)
	r = json.loads(json.dumps(r))
	types = r['rechargeplan']['circle']['rechargetype']
	return types.keys()

def get_different_topup_plans(mobile_number, plan):
	r = requests.get("https://invas01.euronetworldwide.com/RechargePlansAPI_prod/RechargePlans.aspx?merchantcode=ICI&servicecode=MR&consumerno=&spcode=ART&sspcode=ARTBH")
	print(r.text)
	r = xmltodict.parse(r.text)
	r = json.loads(json.dumps(r))
	types = r['rechargeplan']['circle']['rechargetype'][plan]

	global_list = []
	for value in types:
		temp_tuple = (value['remarks'], value['denomination'], value['validity'], "", "")
		global_list.append(temp_tuple)
	return global_list

def get_account_number_value(mobile_number):

    input_query = """
    <XML> <MessageType>1200</MessageType> <ProcCode>E00011</ProcCode> <LocalTxnDtTime>20060215034205</LocalTxnDtTime> <Identifier>MA</Identifier> <MobileNo>""" + mobile_number + """</MobileNo> <UserID></UserID> <DeliveryChannelCtrlID>TLB</DeliveryChannelCtrlID> </XML>
    """
    response = call_api(input_query)
    account_number_value = parse_account_number_value(response)
    return account_number_value


def get_personal_payees(mobile_number):
    user_id = get_user_id(mobile_number)
    account_number_value = get_account_number_value(mobile_number)

    input_query = """
	<XML> <HEADER MSGFORMATID="" PASSTHROUGH="" ROUTETO="" ROUTEHOSTTYPE=""SCRIPTNAME=""></HEADER> <MessageType MXL="4" MNL="4" PL="" DT="numeric" LSP="0" PRE="mandatory" DEFAULT="1200">1200</MessageType> <ProcCode MXL="6" MNL="6" PL="" DT="numeric" LSP="0" IND="3" PRE="mandatory" DEFAULT="960023">960023</ProcCode> <STAN MXL="12" MNL="12" PL="" DT="alphabetnumericspaces" LSP="0" IND="11" PRE="mandatory">001901073335</STAN> <LocalTxnDtTime MXL="14" MNL="14" PL="" DT="numeric" LSP="0" IND="12" PRE="mandatory">20180207183451</LocalTxnDtTime> <CaptureDt MXL="8" MNL="8" DT="date" PL="" LSP="0" IND="17" PRE="optional">20180207</CaptureDt> <FuncCode MXL="3" MNL="3" PL="" DT="numeric" LSP="0" IND="24" PRE="mandatory">200</FuncCode> <AcqInstIdenCode MXL="11" MNL="1" DT="numeric" PL="" LSP="2" IND="32" PRE="mandatory">504642</AcqInstIdenCode> <Identification1 MXL="28" MNL="1" DT="alphabetnumeric" PL="" LSP="2" IND="34" PRE="mandatory">""" + user_id + """</Identification1> <Identification2 MXL="16" MNL="16" DT="alphabet" PL="" LSP="0" IND="41" PRE="mandatory">BWY</Identification2> <CardAcceptorNameLocation MXL="99" MNL="1" DT="alphabet" PL="0" LSP="2" IND="43" PRE="mandatory">BANKAWAY</CardAcceptorNameLocation> <Currency MXL="3" MNL="3" DT="alphabetnumeric" PL="" LSP="0" IND="49" PRE="mandatory">INR</Currency> <AcctIdentificationOne MXL="38" MNL="01" DT="alphabetnumericspecialspaces" PL="" LSP="2" IND="102" PRE="mandatory">""" + account_number_value + """</AcctIdentificationOne> <DeliveryChannelCtrlID MXL="3" MNL="1" PL="" DT="alphabet" LSP="3" IND="123" PRE="mandatory">IMB</DeliveryChannelCtrlID> <TransportData MXL="8" MNL="8" PL="8" DT="alphabet" LSP="3" IND="59" PRE="optional">RCRETIME</TransportData> <AddDataPvt125 MXL="999" MNL="1" DT="alphabetnumericspecialspaces" PL="" LSP="3" IND="125" RLI="0" PRE="optional"> <UbpsReqTyp MXL="2" MNL="2" DT="numeric" PL="" LSP="0" IND="125" PRE="optional">23</UbpsReqTyp> <PayeeType MXL="1" MNL="1" DT="numeric" PL="" LSP="0" IND="125" PRE="optional">B</PayeeType> <PayeeListID MXL="12" MNL="12" DT="alphabetnumericspecialspaces" PL="" LSP="0" IND="125" PRE="optional"></PayeeListID> <NoOfPayees MXL="2" MNL="2" DT="numeric" PL="" LSP="0" IND="125" PRE="optional">21</NoOfPayees> <PaymentType MXL="1" MNL="1" DT="alphabetnumericspecialspaces" PL="" LSP="0" IND="125"PRE="optional"> </PaymentType> <StatusFlag MXL="1" MNL="1" DT="alphabetnumericspecialspaces" PL="" LSP="0" IND="125" PRE="optional">N</StatusFlag> </AddDataPvt125> </XML>
    """
    response = call_api(input_query)
    (more_flag, list_of_payee_list_id, list_of_consumer_code,
     list_of_nick_name) = parse_payee_payment_billers(response)

    final_list_of_payee_id = list_of_payee_list_id
    final_list_of_consumer_code = list_of_consumer_code
    final_list_of_nick_name = list_of_nick_name

    while more_flag == 'Y':
        last_payee_list_id = final_list_of_payee_id[-1:]
        input_query = """
        <XML> <HEADER MSGFORMATID="" PASSTHROUGH="" ROUTETO="" ROUTEHOSTTYPE=""SCRIPTNAME=""></HEADER> <MessageType MXL="4" MNL="4" PL="" DT="numeric" LSP="0" PRE="mandatory" DEFAULT="1200">1200</MessageType> <ProcCode MXL="6" MNL="6" PL="" DT="numeric" LSP="0" IND="3" PRE="mandatory" DEFAULT="960023">960023</ProcCode> <STAN MXL="12" MNL="12" PL="" DT="alphabetnumericspaces" LSP="0" IND="11" PRE="mandatory">001901073335</STAN> <LocalTxnDtTime MXL="14" MNL="14" PL="" DT="numeric" LSP="0" IND="12" PRE="mandatory">20180207183451</LocalTxnDtTime> <CaptureDt MXL="8" MNL="8" DT="date" PL="" LSP="0" IND="17" PRE="optional">20180207</CaptureDt> <FuncCode MXL="3" MNL="3" PL="" DT="numeric" LSP="0" IND="24" PRE="mandatory">200</FuncCode> <AcqInstIdenCode MXL="11" MNL="1" DT="numeric" PL="" LSP="2" IND="32" PRE="mandatory">504642</AcqInstIdenCode> <Identification1 MXL="28" MNL="1" DT="alphabetnumeric" PL="" LSP="2" IND="34" PRE="mandatory">""" + user_id + """</Identification1> <Identification2 MXL="16" MNL="16" DT="alphabet" PL="" LSP="0" IND="41" PRE="mandatory">BWY</Identification2> <CardAcceptorNameLocation MXL="99" MNL="1" DT="alphabet" PL="0" LSP="2" IND="43" PRE="mandatory">BANKAWAY</CardAcceptorNameLocation> <Currency MXL="3" MNL="3" DT="alphabetnumeric" PL="" LSP="0" IND="49" PRE="mandatory">INR</Currency> <AcctIdentificationOne MXL="38" MNL="01" DT="alphabetnumericspecialspaces" PL="" LSP="2" IND="102" PRE="mandatory">""" + account_number_value + """</AcctIdentificationOne> <DeliveryChannelCtrlID MXL="3" MNL="1" PL="" DT="alphabet" LSP="3" IND="123" PRE="mandatory">IMB</DeliveryChannelCtrlID> <TransportData MXL="8" MNL="8" PL="8" DT="alphabet" LSP="3" IND="59" PRE="optional">RCRETIME</TransportData> <AddDataPvt125 MXL="999" MNL="1" DT="alphabetnumericspecialspaces" PL="" LSP="3" IND="125" RLI="0" PRE="optional"> <UbpsReqTyp MXL="2" MNL="2" DT="numeric" PL="" LSP="0" IND="125" PRE="optional">23</UbpsReqTyp> <PayeeType MXL="1" MNL="1" DT="numeric" PL="" LSP="0" IND="125" PRE="optional">B</PayeeType> <PayeeListID MXL="12" MNL="12" DT="alphabetnumericspecialspaces" PL="" LSP="0" IND="125" PRE="optional">""" + last_payee_list_id + """</PayeeListID> <NoOfPayees MXL="2" MNL="2" DT="numeric" PL="" LSP="0" IND="125" PRE="optional">21</NoOfPayees> <PaymentType MXL="1" MNL="1" DT="alphabetnumericspecialspaces" PL="" LSP="0" IND="125"PRE="optional"> </PaymentType> <StatusFlag MXL="1" MNL="1" DT="alphabetnumericspecialspaces" PL="" LSP="0" IND="125" PRE="optional">N</StatusFlag> </AddDataPvt125> </XML>
        """
        response = call_api(input_query)

        (more_flag,
         list_of_payee_list_id,
         list_of_consumer_code,
         list_of_nick_name) = parse_payee_payment_billers(response)

        final_list_of_payee_id += list_of_payee_list_id
        final_list_of_consumer_code += list_of_consumer_code
        final_list_of_nick_name += list_of_nick_name

    return (final_list_of_payee_id, final_list_of_consumer_code, list_of_nick_name)


def get_presentment_payees(mobile_number):

    user_id = get_user_id(mobile_number)

    input_query = """
    <XML> <HEADER>UBPS</HEADER><MessageType>1200</MessageType> <ProcCode>960800</ProcCode> <TxnAmt>0</TxnAmt> <STAN>20141216006</STAN> <LocalTxnDtTime>180703053035</LocalTxnDtTime> <CaptureDt>20180703</CaptureDt> <FuncCode>200</FuncCode> <AcqInstIdenCode>504642</AcqInstIdenCode> <Identification1>""" + user_id + """</Identification1> <Currency>INR</Currency> <ConsumerNo /> <AcctIdentificationOne /> <DeliveryChannelCtrlID>IMB</DeliveryChannelCtrlID> <AddDataPvt125> <UbpsReqTyp>08</UbpsReqTyp> <PayeeID /> <InstancePymntDate /> <ScheduleId> </ScheduleId> <NoOfPayements>12</NoOfPayements> <PaymentType>P</PaymentType> </AddDataPvt125> </XML>
    """
    response = call_api(input_query)
    (schedule_id_list,
     instance_amt_list,
     payee_id_list,
     payee_name_list) = parse_presentment_payees(response)

    return (schedule_id_list,
            instance_amt_list,
            payee_id_list,
            payee_name_list)


def pay_bill_payment_biller(mobile_number, nick_name, transaction_amt):

    user_id = get_user_id(mobile_number)
    (list_of_payee_id,
     list_of_consumer_code,
     list_of_nick_name) = get_personal_payees(mobile_number)

    list_of_nick_name = [item.lower() for item in list_of_nick_name]
    index = list_of_nick_name.index(nick_name)
    consumer_code = list_of_consumer_code[index]
    payee_id = list_of_payee_id[index]

    input_query = """
    <XML> <HEADER MSGFORMATID="157" PASSTHROUGH="N" ROUTEHOSTTYPE="UBPS" ROUTETO="UBPS" SCRIPTNAME="com.mphasis.businessScripts.bin.ChangeAttribute"></HEADER> <MessageType DEFAULT="1200" DT="numeric" LSP="0" MNL="4" MXL="4" PL="4" PRE="mandatory">1200</MessageType> <ProcCode DEFAULT="961100" DT="numeric" IND="3" LSP="0" MNL="6" MXL="6" PL="6" PRE="mandatory">961100</ProcCode> <TxnAmt DT="numeric" IND="4" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">""" + transaction_amt + """</TxnAmt> <STAN DT="alphabetnumericspaces" IND="11" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">002064724924</STAN> <LocalTxnDtTime DT="numeric" IND="12" LSP="0" MNL="14" MXL="14" PL="14" PRE="mandatory">20180207202344</LocalTxnDtTime> <CaptureDt DT="date" IND="17" LSP="0" MNL="8" MXL="8" PL="8" PRE="optional">20180207</CaptureDt> <FuncCode DT="numeric" IND="24" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">200</FuncCode> <AcqInstIdenCode DT="numeric" IND="32" LSP="2" MNL="1" MXL="11" PL="" PRE="mandatory">504642</AcqInstIdenCode> <Identification1 MXL="28" MNL="1" DT="alphabetnumeric" PL="" LSP="2" IND="34" PRE="mandatory">""" + user_id + """</Identification1> <RRNNumber DT="numeric" IND="37" LSP="0" MNL="12" MXL="12" PL="12" PRE="mandatory">120809133559</RRNNumber><CardAccTerminalID DT="alphabetnumericspaces" IND="41" LSP="0" MNL="16" MXL="16" PL="16" PRE="optional">UBPS</CardAccTerminalID> <CardAccIdentification DT="alphabetnumericspaces" IND="42" LSP="0" MNL="15" MXL="15" PL="15" PRE="optional">504642</CardAccIdentification> <CardAccNameLocation DT="alphabetnumericspaces" IND="43" LSP="2" MNL="1" MXL="99" PL="" PRE="optional">UBPS</CardAccNameLocation> <Currency DT="alphabetnumeric" IND="49" LSP="0" MNL="3" MXL="3" PL="" PRE="mandatory">INR</Currency> <PrivateField DT="alphabetnumericspecialspaces" IND="60" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField> <PrivateField2 DT="alphabetnumericspecialspaces" IND="61" LSP="3" MNL="01" MXL="999" PL="" PRE="optional"></PrivateField2> <ConsumerNumber DT="alphabetnumericspecialspaces" IND="63" LSP="3" MNL="01" MXL="999" PL="" PRE="optional">""" + consumer_code + """</ConsumerNumber> <AcctIdentificationOne DT="alphabetnumericspecialspaces" IND="102" LSP="2" MNL="01" MXL="38" PL="" PRE="mandatory">ICI 0151 0151015*****</AcctIdentificationOne> <DeliveryChannelCtrlID DT="alphabet" IND="123" LSP="3" MNL="1" MXL="3" PL="" PRE="mandatory">IMB</DeliveryChannelCtrlID> <AddDataPvt125 DT="alphabetnumericspecialspaces" IND="125" LSP="3" MNL="1" MXL="999" PL="" PRE="optional" RLI="0"> <UbpsReqTyp DT="alphabetnumeric" IND="125" LSP="0" MNL="2" MXL="2" PL="" PRE="optional">11</UbpsReqTyp> <ScheduleBegngDate DT="alphabetnumericspaces" IND="125" LSP="0" MNL="8" MXL="8" PL="" PRE="optional">00000000</ScheduleBegngDate> <PayementFrequency DT="numeric" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">0</PayementFrequency> <TotNoOfPymnts DT="numeric" IND="125" LSP="0" MNL="5" MXL="5" PL="" PRE="optional">01</TotNoOfPymnts> <PayeeID DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="12" MXL="12" PL="" PRE="optional">""" + payee_id + """</PayeeID> <PaymntRemrks DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional"></PaymntRemrks> <BillRefInfo DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="254" MXL="254" PL="" PRE="optional">QBPREFID-fbba4335-387d-405b-b02d-4971e2a337b8</BillRefInfo> <ValidationFlag DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional">A</ValidationFlag> <PersonalPayee DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="1" MXL="1" PL="" PRE="optional"></PersonalPayee> <PayeeNick DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="40" MXL="40" PL="" PRE="optional"></PayeeNick><ConsumerCode DT="alphabetnumericspecialspaces" IND="125" LSP="0" MNL="64" MXL="64" PL="" PRE="optional">""" + consumer_code + """</ConsumerCode> </AddDataPvt125> </XML> 
    """

    response = call_api(input_query)

    act_code = parse_payment_biller_success(response)
    return act_code


def pay_bill_presentment_biller(mobile_number, payee_name):

    user_id = get_user_id(mobile_number)
    (schedule_id_list,
     instance_amt_list,
     payee_id_list,
     payee_name_list) = get_presentment_payees(mobile_number)

    payee_name_list = [item.lower() for item in payee_name_list]
    index = payee_name_list.index(payee_name)
    transaction_amt = instance_amt_list[index]
    schedule_id = schedule_id_list[index]

    input_query = """
    <XML><HEADER>UBPS</HEADER> <MessageType>1200</MessageType> <ProcCode>961500</ProcCode> <TxnAmt>"""+transaction_amt+"""</TxnAmt> <STAN>001350483575</STAN> <LocalTxnDtTime>20180703172852</LocalTxnDtTime> <CaptureDt>20180703</CaptureDt> <FuncCode>200</FuncCode> <AcqInstIdenCode>504642</AcqInstIdenCode> <Identification1>534812011</Identification1> <Currency>INR</Currency> <ConsumerNo /> <AcctIdentificationOne>ICI 0411 041101519236</AcctIdentificationOne> <DeliveryChannelCtrlID>IMB</DeliveryChannelCtrlID> <AddDataPvt125> <UbpsReqTyp>15</UbpsReqTyp> <TimeStamp>00001</TimeStamp> <ScheduleId>"""+schedule_id+"""</ScheduleId> <PenaltyAmount>.00</PenaltyAmount> <PaymntRemrks>Testing p</PaymntRemrks> <ScheduleDate>00000000</ScheduleDate> </AddDataPvt125> </XML>
    """

    response = call_api(input_query)
    act_code = parse_presentment_biller_sucess(response)
    return act_code



def get_last_transactions(credit_card_number, mobile_number):
    if not Config.objects.all()[0].prod:
        return [("AAAA","12"),("BBBB","23")]

    last_4_digit = ""
    for d in credit_card_number:
        print(d)
        if d.isdigit():
            last_4_digit += d    
    credit_card_numbers = get_credit_card_numbers_original(mobile_number)
    for cc in credit_card_numbers:
        if cc[-4:] == last_4_digit:
            credit_card_number = cc

    ticket_number = generate_ticket(credit_card_number)

    #input_query = """<XML><MessageType MXL='4' MNL='4' PL='4' DT='numeric' LSP='0' PRE='mandatory' DEFAULT='1200'>1200</MessageType><CustID MXL='19' MNL='19' DT='numeric' PL='19' LSP='0' IND='2' PRE='mandatory'>""" + credit_card_number + """</CustID><ProcCode MXL='6' MNL='6' PL='6' DT='numeric' LSP='0' IND='3' PRE='mandatory' DEFAULT='610000'>610000</ProcCode><TxnAmt MXL='16' MNL='16' DT='numeric' PL='16' LSP='0' IND='4' PRE='mandatory'>1</TxnAmt><STAN MXL='6' MNL='6' DT='numeric' PL='6' LSP='0' IND='11' PRE='mandatory'>123456</STAN><LocalTxnDtTime MXL='12' MNL='12' DT='numeric' PL='12' LSP='0' IND='12' PRE='mandatory'>20180129152948</LocalTxnDtTime><CaptureDt MXL='8' MNL='8' DT='numeric' PL='' LSP='0' IND='17' PRE='mandatory'>19991015</CaptureDt><FuncCode MXL='3' MNL='3' DT='numeric' PL='' LSP='0' IND='24' PRE='mandatory' OVERRIDE='200'>200</FuncCode><AcqInstIdenCode MXL='11' MNL='1' DT='numeric' PL='' LSP='2' IND='32' PRE='mandatory' OVERRIDE='010'>001</AcqInstIdenCode><Currency MXL='3' MNL='3' DT='alphabet' PL='' LSP='0' IND='49' PRE='mandatory' DEFAULT='INR'>INR</Currency><FaxNo MXL='999' MNL='1' DT='alphabetnumericspecialspaces' PL='' LSP='3' IND='59' PRE='optional' /><FourDigitYear MXL='999' MNL='1' DT='alphabetnumericspecial' PL='' LSP='3' IND='62' PRE='mandatory'>1999</FourDigitYear><ConsumerNo MXL='28' MNL='1' DT='alphabetnumericspaces' PL='' LSP='2' IND='63' PRE='optional'>1</ConsumerNo><AcctIdentificationOne MXL='38' MNL='1' DT='alphabetnumericspaces' PL='' LSP='2' IND='102' PRE='mandatory'>""" + \
    #    credit_card_number + """</AcctIdentificationOne><DeliveryChannelCtrlID MXL='3' MNL='3' DT='alphabet' PL='' LSP='0' IND='123' PRE='mandatory' OVERRIDE='INT'>CCI</DeliveryChannelCtrlID><AddDataPvt125 MXL='999' MNL='1' DT='alphabetnumericspecialspaces' PL='' LSP='3' IND='125' RLI='0' PRE='optional'><RecordFrom MXL='999' MNL='1' DT='numeric' PRE='optional' PL='' LSP='1' IND='125'>1</RecordFrom><NoofRecordRequested MXL='99' MNL='1' DT='numeric' PRE='optional' PL='' LSP='1' IND='125'>16</NoofRecordRequested></AddDataPvt125></XML>"""
    input_query = """<XML><MessageType>1200</MessageType><ProcCode>777010</ProcCode><SOAPMessage><soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'xmlns:xsd='http://www.w3.org/2001/XMLSchema'><soap:Body><StatementInquiry xmlns='http://CTL.COM.Services.Prime.Issuer.WebServices/PrimeIssuerServices'><xmlRequest><Header><MessageID>1234</MessageID><CorrelationID></CorrelationID><SystemID></SystemID><RequestorID></RequestorID><Ticket>"""+ticket_number+"""</Ticket><CallerRef></CallerRef><Origin></Origin><Culture></Culture></Header><Paging><Size>0</Size><Key></Key></Paging><Period>Current</Period><DateFrom></DateFrom><DateTo></DateTo><Content>Account</Content><Reference>C</Reference><Number>"""+credit_card_number+"""</Number><HierarchicalTrxns>false</HierarchicalTrxns><CustomerNumber></CustomerNumber><LevelDepth>0</LevelDepth><TransactionMemos>None</TransactionMemos></xmlRequest></StatementInquiry></soap:Body></soap:Envelope></SOAPMessage></XML>"""    
    response = call_api(input_query)    
    last_transactions = parse_last_transactions(response)

    current_transaction = []
    if len(last_transactions) <= 5:
        input_query = """<XML><MessageType>1200</MessageType><ProcCode>777010</ProcCode><SOAPMessage><soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'xmlns:xsd='http://www.w3.org/2001/XMLSchema'><soap:Body><StatementInquiry xmlns='http://CTL.COM.Services.Prime.Issuer.WebServices/PrimeIssuerServices'><xmlRequest><Header><MessageID>1234</MessageID><CorrelationID></CorrelationID><SystemID></SystemID><RequestorID></RequestorID><Ticket>"""+ticket_number+"""</Ticket><CallerRef></CallerRef><Origin></Origin><Culture></Culture></Header><Paging><Size>0</Size><Key></Key></Paging><Period>Last</Period><DateFrom></DateFrom><DateTo></DateTo><Content>Account</Content><Reference>C</Reference><Number>"""+credit_card_number+"""</Number><HierarchicalTrxns>false</HierarchicalTrxns><CustomerNumber></CustomerNumber><LevelDepth>0</LevelDepth><TransactionMemos>None</TransactionMemos></xmlRequest></StatementInquiry></soap:Body></soap:Envelope></SOAPMessage></XML>"""    
        response = call_api(input_query)    
        current_transaction = parse_last_transactions(response)


    return last_transactions + current_transaction
