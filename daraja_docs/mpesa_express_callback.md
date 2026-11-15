---
title: M-Pesa Express Callback
aliases:
  - STK Push Callback
  - M-Pesa Express Webhook
endpoint: POST <CallBackURL>
last_verified: 2026-11-15
---
# M-Pesa Express Callback 

Description: An asynchronous webhook payload that Safaricom sends via HTTP POST to your CallBackURL once an M-Pesa Express Payment Request (STK Push) succeeds, fails, or is cancelled by the customer. 

## Mpesa Express Callback URL Requirements

* **Public HTTPS URL:** Your `CallBackURL` must use `https` and be publicly reachable over the internet (for local testing, expose your port using an HTTPS tunnel such as `ngrok`).  
* **Avoid Restricted Keywords:** Do not include terms like `mpesa` or `safaricom` in your callback URL path, as Safaricom's gateway may block or drop requests to URLs containing those strings.

### M-Pesa Express Callback Response

When your server receives the `POST` payload, immediately return an HTTP `200 OK` response with the following JSON body:

```json
{
  "ResultCode": 0,
  "ResultDesc": "Accepted"
}
```

## Handling Failed or Missed M-Pesa Express Callbacks

If your server is unavailable or fails to respond, the Safaricom API Gateway logs a `503` error and discards the callback payload without retrying.

## M-Pesa Express Callback Fallback Mechanism

If your application does not receive a callback within your expected timeout window, call the M-Pesa Express Query endpoint (`/mpesa/stkpushquery/v1/query`) to confirm the transaction status. This reconciliation check ensures your database records match the final transaction state.

To implement this fallback:

1. Monitor pending transactions that do not receive a callback within a set window (for example, 60–90 seconds after initiation).  
2. Trigger a `POST` request to `/mpesa/stkpushquery/v1/query` using the stored `CheckoutRequestID` to finalize the transaction state.  
3. Check whether the `CheckoutRequestID` has already been finalized in your database before updating records, in case a delayed or duplicate callback arrives later.

## M-pesa Express Unsuccessful payment callback payload

```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "f1e2-4b95-a71d-b30d3cdbb7a7942864",
      "CheckoutRequestID": "ws_CO_21072024125243250722943992",
      "ResultCode": 1032,
      "ResultDesc": "Request cancelled by user"
    }
  }
}
```

### M-pesa Express Successful Payment Callback Payload

```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "29115-34620561-1",
      "CheckoutRequestID": "ws_CO_191220191020363925",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {
            "Name": "Amount",
            "Value": 1.0
          },
          {
            "Name": "MpesaReceiptNumber",
            "Value": "NLJ7RT61SV"
          },
          {
            "Name": "TransactionDate",
            "Value": 20191219102115
          },
          {
            "Name": "PhoneNumber",
            "Value": 254708374149
          }
        ]
      }
    }
  }
}
```

## M-Pesa Express Callback Response Definitions

Every M-Pesa Express callback wraps transaction status fields inside `Body.stkCallback`:

| Field | Type | Description |
| :---- | :---- | :---- |
| MerchantRequestID | String | Gateway request trace ID matching the initial /processrequest response. |
| CheckoutRequestID | String | identifier for the processed checkout transaction request. Same as in the initial request response. |
| ResultCode | Number | Transaction outcome code. 0 indicates success; any non-zero integer indicates failure or cancellation. |
| ResultDesc | String | Human-readable status message describing the outcome. |
| CallbackMetadata | Object | Included only in successful payment callbacks.  Contains the \`Item\` array of payment receipt details. Omitted completely from unsuccessful callbacks |
 

## M-Pesa Express `CallbackMetadata.Item` Array Fields

`CallbackMetadata` is only included in successful M-Pesa Express callbacks (ResultCode: 0). It is completely omitted from failed or cancelled callbacks. 

When present, `CallbackMetadata` contains an `.Item` array which returns transaction values as an array of {"Name": "...", "Value": ...} objects rather than a standard key-value dictionary:

| Name  | Value Type | Value Description |
| :---- | :---- | :---- |
| Amount | Number | Total amount paid by the customer. |
| MpesaReceiptNumber | String | Unique M-Pesa transaction confirmation code (e.g., NLJ7RT61SV). |
| TransactionDate | Number | Payment completion timestamp formatted as YYYYMMDDHHMMSS. |
| PhoneNumber | Number | Customer phone number used for payment in MSISDN format 254XXXXXXXXX. 12 digits expected. |
| Balance |  | Updated account balance of the receiving business shortcode (PartyB) after the payment is credited. |

## M-pesa Express Callback Result codes

| ResultCode | Meaning | What to Do |
| :---- | :---- | :---- |
| **0** | Success | Confirm with an STK Query, then mark order paid and fulfill |
| **1** | Insufficient balance | Show user-friendly message, suggest top-up |
| **17** | Internal failure | Retry once, then show generic error |
| **26** | System busy | Backoff and retry after 30 seconds |
| **1001** | Unable to lock subscriber, transaction in progress | User has another M-Pesa transaction. Wait, retry |
| **1019** | Transaction expired | User waited too long. Allow retry |
| **1025** | An error occurred while sending push request | Network or Safaricom-side issue. Retry |
| **1032** | Request cancelled by user | User pressed Cancel. Show retry button |
| **1037** | DS timeout user cannot be reached | User didn't respond before the prompt timed out (roughly 1–3 minutes). Phone off or no signal |
| **2001** | Wrong PIN | User entered wrong PIN. They can retry |

## Verifying M-Pesa Express Callback Origin

Because M-Pesa Express callbacks lack cryptographic signature headers, restrict inbound traffic on your callback endpoint to Safaricom's 12 published gateway IP addresses. Allowlist all 12 addresses on your firewall or reverse proxy so legitimate callbacks are not dropped:

```
196.201.214.200
196.201.214.206
196.201.213.114
196.201.214.207
196.201.214.208
196.201.213.44
196.201.212.127
196.201.212.138
196.201.212.129
196.201.212.136
196.201.212.74
196.201.212.69
```

## Local Testing for M-Pesa Express Callbacks

Safaricom delivers callbacks over the public internet, which cannot reach `localhost` (`127.0.0.1`) directly behind your local network and firewall.

During sandbox development, expose your local `POST` endpoint using an HTTPS tunneling tool (such as `ngrok` or `localtunnel`) to create a public `https://` URL that forwards requests to your local port:

* Pass the generated `https://` URL (not `http://`) as your `CallBackURL`.  
* Keep the URL path generic (for example, `/callback`), avoiding terms such as `mpesa` or `safaricom` that Safaricom's gateway may block.