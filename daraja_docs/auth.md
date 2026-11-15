---
title: Authorisation
aliases:
- Authorization
- Generate auth token
- Client Credentials
- Bearer token
- OAuth
endpoint: /oauth/v1/generate?grant_type=client_credentials
last_verified: 2026-11-15
---
# Authorisation

## Authorisation Endpoint Details
- Method: `GET`
- Endpoint: `/oauth/v1/generate?grant_type=client_credentials`
- Sandbox Base URL: `https://sandbox.safaricom.co.ke`
- Description: Generates a temporary access token which provides authentication to access all other Mpesa endpoints. The temporary access token expires in 3599 seconds (~1 hour). 

## Authorisation Request Body 

No body for a GET request

## Authorisation Request Headers

| Name | Description | Required/Optional | Format |
| :---- | :---- | :---- | :---- |
| Authorization | Base64-encoded string of your Consumer Key and Consumer Secret separated by a colon | **Required** | Basic \<Base64(ConsumerKey:ConsumerSecret)\> |

## Authorisation Query Parameter

| Name | Description | Type | Required/Optional | Value | Note |
| :---- | :---- | :---- | :---- | :---- | :---- |
| grant_type | The OAuth 2.0 flow type used to exchange client credentials for a token | String  | **Required** | client_credentials | **This is a constant value that must always be set to `client_credentials`.**   |

## Authorisation Sample Request



```bash
 curl -X GET "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" \
  -H "Authorization: Basic SW52YWxpZTpBdXRoVG9rZW5Gb3JEYXJhamE="
```
## Authorisation Sample Response

```json
{  
  "access_token": "cNvGf19rFhF48Xb0mAAQJ723h...",  
  "expires_in": "3599"  
}
```
## Authorisation Response Definition 

| Name | Description | Type | Notes |
| :---- | :---- | :---- | :---- |
| access_token | temporary access\_token that must be used as a bearer token value to authorise requests to all other mpesa endpoints | String  | **Example: c9SQxWWhmdVRlyh0zh8gZDTkubVF**. Pass this value as the Bearer \<access token\> in the authorisation header for all other mpesa endpoints. |
| expires_in | The lifespan of the access token in seconds from the moment of generation.  | string | Default: 3599   |