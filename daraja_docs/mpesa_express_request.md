---
title: M-Pesa Express Payment Request
aliases:
  - STK Push
  - Lipa Na M-Pesa Online
  - LNMO
  - M-Pesa Express Simulate
  - Process Request
  - M-pesa Prompt
endpoint: /mpesa/stkpush/v1/processrequest
last_verified: 2026-11-15
---
# M-Pesa Express Payment Request (Prompt)

## M-Pesa Express Prompt Endpoint details
HTTP method, sandbox base URL, and path for initiating an M-Pesa Express payment prompt on a customer's phone.

- Method: `POST`
- Endpoint: `/mpesa/stkpush/v1/processrequest`
- Sandbox URL:`https://sandbox.safaricom.co.ke`
- Description: Allows a business to send a buy goods/pay bill payment prompt to a customer’s phone number.

## M-Pesa Express Prompt Sample Request  

```json
{
   "BusinessShortCode": "174379",
   "Password": "{{stk_password}}",
   "Timestamp": "{{stk_timestamp}}",
   "TransactionType": "CustomerPayBillOnline",
   "Amount": 1,
   "PartyA": 254708374149,
   "PartyB": 174379,
   "PhoneNumber": 254708374149,
   "CallBackURL": "https://mydomain.com/path",
   "AccountReference": "CompanyXLTD",
   "TransactionDesc": "Payment of X"
}
```

## M-Pesa Express Prompt Request definition

| Name | Description | Type | Required/ Optional | Note |
| :---- | :---- | :---- | :---- | :---- |
| BusinessShortCode | The paybill or buygoods account number used to receive mpesa payments. | Number | Required | Is between 5 and 7 digits. `Example:174349`  |
| Password | Base64-encoded string used to authenticate the transaction request | String | Required | Format:Base 64(BusinessShortCode+Passkey+Timestamp). This is a dynamic value that must be generated at runtime. See the dynamic generation section for sample automation scripts.: |
| Timestamp | Current time in YYYYMMDDHHmmss format in East Africa Time.  | String | Required |  Dynamic value. Must be generated at run time for each request.The timestamp and password are linked and must match. If the timestamp in the payload does not match the timestamp string baked into the password hash, authentification fails immediately with an invalid password error. |
| TransactionType | Payment method either Paybill or Buy Goods | String | Required | Accepted values:  `CustomerPayBillOnline` `CustomerBuyGoodsOnline` |
| Amount | Amount of money requested to the customer | Number | Required | `Minimum: 1` `Max: 999 999 999` |
| PartyA | Mobile phone number of the customer making payment in MSISDN format. | Number | Required | Phone number must be a  registered Safaricom number. `Format: 254XXXXXXXXX` Number of digits expected: 12 ⚠️ Docs discrepancy: Daraja documentation lists `2547xxxx` as default format. However, newer series phone numbers (e.g. 0110, 0111, 0112\) are also accepted. Input validation regex must accommodate both prefixes.  |
| PartyB | The business paybill or till  account number used to receive payments | Number | Required | Party B and the BusinessShortCode are identical. |
| PhoneNumber | The mobile number to receive the USSD prompt. | Number | Required | Can be the same as PartyA |
| CallBackUrl | The URL where the payment gateway will send the result. | String | Required | [https\://mydomain.com/mpesa-express-simulate/](https://mydomain.com/mpesa-express-simulate/). Always use standard port 443\. Safaricom's firewall frequently blocks outbound callbacks to custom ports. The URL must be publicly routable over the internet (use a tunnel like `ngrok` or `cloudflared` during local development). Safaricom’s WAF/validation layer rejects `CallBackURL` strings containing certain reserved words like `mpesa`, `safaricom`, `sql`, or `exec` in the path or domain  |
| AccountReference | Alphanumeric code which links the payment to a specific customer/invoice. Assigned by the business’ own system.  | String | Required | Displayed to the customer in the USSD prompt. Character length Minimum: `Max: 12 characters`. longer characters do not throw errors, they risk being truncated on the prompt message. ⚠️ **Docs Discrepancy:**  The gateway permits empty strings (`" "`), but passing blank strings breaks the customer STK prompt display and causes database lookup issues in webhooks. Always supply an actual order/account ID to be used as AccountReference. |
| TransactionDesc | Description of the purpose of payment | String | Optional  | `Character length Minimum: 2` `Maximum : 13`\.  longer characters do not throw errors, but they risk being truncated on the prompt message. ⚠️ **Docs Discrepancy:** While Daraja docs note that this field is optional, the API gateway strictly enforces a non-empty string. Omitting this field, passing `""`, or providing whitespace (`" "`) triggers an immediate `400 Bad Request`.  |

## M-Pesa Express Prompt Sample Response 
Daraja returns this JSON response when an M-Pesa Express payment prompt request is accepted for processing.

```json
{
   "MerchantRequestID": "3197-4224-a7b4-26167e300ff8201468",
   "CheckoutRequestID": "ws_CO_071120261312046708374149",
   "ResponseCode": "0",
   "ResponseDescription": "Success. Request accepted for processing",
   "CustomerMessage": "Success. Request accepted for processing"
}
```

## M-Pesa Express Prompt Response definition
Definitions for the JSON response returned by the `/mpesa/stkpush/v1/processrequest` endpoint.

| Name | Description | Type | Note |
| :---- | :---- | :---- | :---- |
| MerchantRequestID | Assigned by Safaricom for every M-Pesa Express (`/processrequest`) call. Used to trace the inbound API call through their gateway logs. | String | None |
| CheckoutRequestID | A unique tracking identifier generated by Safaricom for an **initiated checkout session** (STK Push prompt).  Serves as the  primary key to poll payment status via `/query` and to match incoming asynchronous callbacks to your database records. | String | ⚠️ Dynamic stateful value.There is no static mock `CheckoutRequestID` in the sandbox ledger.  To obtain a CheckOutRequestId, You must first call `/processrequest`. Extract the returned `CheckoutRequestID` from the response body and paste it. Use automation scripts to generate this dynamically. |
| ResponseCode | A code that indicates the gateway status of the API request.  | String |  `"0"` is for a successful API request. Indicates that it was dispatched to the customer.   Any non-zero value means the gateway encountered an internal or routing error. |
| ResponseDescription | A human-readable service status message returned by the API gateway. | String | Example: `Success. Request accepted for processing` |
| CustomerMessage | A pre-formatted acknowledgment message that the prompt was dispatched. | String | Example: `Success. Request accepted for processing` Intended for user-facing UI prompts. Typically mirrors `ResponseDescription` verbatim; do not rely on it as definitive user guidance on checkout screens. ⚠️ UI Trap: Despite the name and the word "Success", this does not confirm payment. Do not display this verbatim to end-users as a confirmation screen; prompt the user to check their phone and enter their PIN instead.`  |