---
title: Daraja API Error Codes
aliases:
  - Result Codes
  - HTTP Status Codes
  - STK Push Errors
  - Troubleshooting
last_verified: 2026-11-15
---
# **API Error Codes Reference**

M-Pesa Express returns errors across two distinct execution stages: synchronous **API Gateway HTTP errors** (returned immediately when an HTTP request fails validation, authentication, or routing before reaching the subscriber) and asynchronous **Transaction ResultCode values** (returned inside `stkCallback` payloads or `/mpesa/stkpushquery/v1/query` responses after M-Pesa processes the prompt).

## **Global API Gateway HTTP Errors**

### **HTTP 400 Errors (Bad Request and Token Validation)**

Safaricom's API gateway returns these synchronous HTTP 400 errors immediately when the JSON request body fails parameter validation or when the OAuth bearer token is rejected at the request validation layer.

| HTTP Status | Daraja errorCode | errorMessage | Root Cause | Remediation |
| :---- | :---- | :---- | :---- | :---- |
| **400** | 400.002.02 | Bad Request \- Invalid \<Field\> | A specific payload field failed validation (for example, IdentifierType, TransactionType, Amount, Timestamp, or Remarks). | Inspect the field named in errorMessage and verify its data type, allowed enum value, integer formatting, and character limit. |
| **400** | 400.002.05 | Invalid Request Payload | Malformed JSON syntax, missing required top-level keys, or missing Content-Type: application/json header. | Validate the JSON body syntax, confirm all required keys exist, and set Content-Type: application/json. |
| **400** | 400.003.01 | Invalid Access Token | Expired, revoked, or malformed OAuth token rejected at the request validation layer. | Request a fresh bearer token from /oauth/v1/generate?grant\_type=client\_credentials and retry. |

### **HTTP 404 and 405 Errors (Routing, Token, and Method Errors)**

Safaricom's API gateway returns these synchronous HTTP 404 and 405 errors when the endpoint path, HTTP verb, Authorization header format, or bearer token fails gateway routing checks.

| HTTP Status | Daraja errorCode | errorMessage | Root Cause | Remediation |
| :---- | :---- | :---- | :---- | :---- |
| **404** | 404.001.01 | Resource not found | Incorrect API endpoint URL path or environment base URL mismatch. | Verify the exact endpoint path (/mpesa/stkpush/v1/processrequest or /mpesa/stkpushquery/v1/query) and environment host. |
| **404** | 404.001.03 | Invalid Access Token | Expired or invalid OAuth token rejected by the API gateway routing layer (tokens expire after 3600 seconds). | Request a fresh bearer token from /oauth/v1/generate?grant\_type=client\_credentials and retry. |
| **404** | 404.001.04 | Invalid Authentication Header | Missing Authorization header or missing Bearer prefix before the access token. | Set the Authorization header to Bearer \<access\_token\> with a single space after Bearer and retry. |
| **405** | 405.001 | Method Not Allowed | Request was sent using GET or another unsupported HTTP verb instead of POST. | Send the request using the HTTP POST method. |

### **HTTP 429 and 500 Errors (Rate Limits and Server Errors)**

Safaricom's API gateway returns these synchronous HTTP 429 and 500 errors when request rates exceed spike-arrest limits, when credentials or subscriber locks fail, or when `/mpesa/stkpushquery/v1/query` is polled while a prompt is still awaiting handset input.

| HTTP Status | Daraja errorCode | errorMessage | Root Cause | Remediation |
| :---- | :---- | :---- | :---- | :---- |
| **429** | 429 (Apigee) | Spike Arrest Violation / Too Many Requests | Request rate exceeded Safaricom's transactions-per-second (TPS) spike-arrest threshold. | Pause outbound requests and retry using exponential backoff with jitter. |
| **500** | 500.001.1001 | \[MerchantValidate\] \- Wrong credentials / Merchant does not exist | Password Base64 encoding mismatch (BusinessShortCode \+ Passkey \+ Timestamp), or BusinessShortCode does not belong to the active environment. | Generate Timestamp (YYYYMMDDHHmmss) once, reuse it in Password and the JSON body, and verify sandbox vs. production credentials. |
| **500** | 500.001.1001 | Unable to lock subscriber, a transaction is already in process for the current subscriber | The subscriber's handset currently has an active USSD or STK Push session in progress. | Wait at least 60 seconds for the active handset session to clear before initiating a new STK Push. |
| **500** | 500.001.1001 | (empty string "") | Returned by /mpesa/stkpushquery/v1/query when polled immediately after initiation while the STK prompt is still awaiting user input on the handset. | Do not mark the transaction failed; treat as non-terminal and continue polling /mpesa/stkpushquery/v1/query on your backoff schedule. |
| **500** | 500.003.02 | Error Occurred: Spike Arrest Violation | Legacy gateway representation of a transactions-per-second (TPS) rate-limit violation. | Pause outbound requests and retry using exponential backoff with jitter. |
| **500** | 500.003.03 | Quota Violation | Application exceeded its allocated API request quota for the time window. | Throttle outbound traffic and contact Safaricom Daraja support if higher production quota limits are required. |
| **500** | 500.003.1001 | Internal Server Error | Transient upstream Safaricom gateway or core processing failure. | Do not assume payment failure; reconcile transaction status via /mpesa/stkpushquery/v1/query before retrying. |

## Asynchronous M-Pesa Express Callback Result Codes

### M-Pesa Express ResultCodes 0 to 99 

Safaricom returns these low-range numeric ResultCode values inside Body.stkCallback and /mpesa/stkpushquery/v1/query responses for completed payments, insufficient balances, or core M-Pesa system states.

| ResultCode | Meaning | Root Cause | Remediation |
| :---- | :---- | :---- | :---- |
| **0** | Success | Subscriber entered the valid M-Pesa PIN and M-Pesa settled the payment. | Confirm the transaction with an STK Query (/mpesa/stkpushquery/v1/query), then mark the order paid and fulfill it. |
| **1** | Insufficient balance | Subscriber's M-Pesa wallet balance is lower than the requested transaction amount. | Display a user-friendly message explaining the insufficient balance and suggest topping up their M-Pesa account before retrying. |
| **17** | Internal failure | Transient internal M-Pesa system failure occurred while processing the request. | Retry the request once; if it fails again, show a generic error message to the user. |
| **26** | System busy | M-Pesa core system is experiencing temporary high load. | Apply backoff and retry the request after 30 seconds. |

### M-Pesa Express Callback ResultCodes 1000 to 2999 

Safaricom returns these four-digit numeric ResultCode values inside Body.stkCallback and /mpesa/stkpushquery/v1/query responses when a subscriber cancels, enters a wrong PIN, times out, or has another transaction in progress.

| ResultCode | Meaning | Root Cause | Remediation |
| :---- | :---- | :---- | :---- |
| **1001** | Unable to lock subscriber, transaction in progress | Subscriber currently has another active M-Pesa transaction session in progress. | Wait for the active subscriber transaction to finish, then retry the STK Push. |
| **1019** | Transaction expired | Subscriber waited too long to respond before the STK Push prompt expired. | Mark the attempt expired and allow the user to retry the payment. |
| **1025** | An error occurred while sending push request | Network or Safaricom-side issue prevented the STK Push request from being sent. | Retry the STK Push request. |
| **1032** | Request cancelled by user | Subscriber pressed Cancel or dismissed the STK Push prompt on their handset. | Mark the attempt cancelled and display a retry button to the user. |
| **1037** | DS timeout user cannot be reached | Subscriber did not respond before the prompt timed out (roughly 1–3 minutes) because the phone was off or had no signal. | Inform the user their handset could not be reached (phone off or out of network coverage) and allow them to retry once connected. |
| **2001** | Wrong PIN | Subscriber entered an incorrect M-Pesa PIN on the STK Push prompt. | Inform the user that an incorrect PIN was entered and allow them to retry. |

