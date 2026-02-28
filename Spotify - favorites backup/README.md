# Spotify Saved Tracks Exporter (Java + RestAssured)

This project connects to the Spotify Web API, retrieves all saved tracks
(/me/tracks), parses them, and stores structured data in a local file.

------------------------------------------------------------------------

## 1. Create Spotify Developer App

Open: https://developer.spotify.com/dashboard

Create a new app.

Add Redirect URI: https://example.org/callback

Save the app.

------------------------------------------------------------------------

## 2. Get Client ID and Client Secret

From the Dashboard → Settings:

spotify.client.id spotify.client.secret

------------------------------------------------------------------------

## 3. Get Authorization Code

Open in browser:

https://accounts.spotify.com/authorize?client_id=56cacfdd08d34f2fa3162a866a5502b0&response_type=code&redirect_uri=https://example.org/callback&scope=user-library-read

After login, you will be redirected to:

https://example.org/callback?code=YOUR_AUTHORIZATION_CODE

Copy the `code` value.

------------------------------------------------------------------------

## 4. Convert client_id:client_secret to Base64

PowerShell:

Example that worked:

NTZjYWNmZGQwOGQzNGYyZmEzMTYyYTg2NmE1NTAyYjA6ZTg3M2IzMGUyYTA5NGMwYzlhN2QyMzRkZDI2ZmY1YTE=

------------------------------------------------------------------------

## 5. Exchange Authorization Code for Tokens

curl.exe -X POST https://accounts.spotify.com/api/token
`-H "Authorization: Basic NTZjYWNmZGQwOGQzNGYyZmEzMTYyYTg2NmE1NTAyYjA6ZTg3M2IzMGUyYTA5NGMwYzlhN2QyMzRkZDI2ZmY1YTE="`
-H "Content-Type: application/x-www-form-urlencoded"
`-d "grant_type=authorization_code"` -d "code=YOUR_AUTHORIZATION_CODE"
\` -d "redirect_uri=https://example.org/callback"

Response contains:

access_token refresh_token

Save the refresh_token.

------------------------------------------------------------------------

## 6. application.properties

spotify.client.id=YOUR_CLIENT_ID
spotify.client.secret=YOUR_CLIENT_SECRET
spotify.refresh.token=YOUR_REFRESH_TOKEN

------------------------------------------------------------------------

## 7. Refresh Token Flow

POST https://accounts.spotify.com/api/token grant_type=refresh_token
refresh_token=YOUR_REFRESH_TOKEN

Authorization: Basic BASE64(client_id:client_secret)

------------------------------------------------------------------------

## 8. Get Saved Tracks

GET https://api.spotify.com/v1/me/tracks?limit=20&offset=0

Supported params: limit offset market

Do NOT use `order` parameter.

Spotify already returns newest first.

------------------------------------------------------------------------

## 9. Output Format

spotify_tracks.txt

Example:

artist=Rihanna track=Desperado album=ANTI

artist=KRS-One track=Ova Here album=The Mix Tape

------------------------------------------------------------------------

## Common Errors

400 → invalid_client or invalid_grant 503 → temporary Spotify issue (add
retry) Offset not changing → remove unsupported query params

------------------------------------------------------------------------

Never commit client_secret or refresh_token.
