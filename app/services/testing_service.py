import asyncio
import aiohttp
import pprint


# async def main():
#     async with aiohttp.ClientSession() as session:
#         response = await session.get(
#             "https://api.apitube.io/v1/news/everything?language.code=en&per_page=10",
#             headers={
#                 "X-API-Key": "api_live_n7T51bHtniDb64WcP6WePTlU5UKzeEVR3U58ca9rYuhrvRpQZveTL"
#             }
#         )
#
#         data = await response.json()
#         pprint.pprint(data)
#
#
# asyncio.run(main())
import requests

response = requests.get(
    "https://api.apitube.io/v1/news/everything?language.code=en&per_page=10",
    headers={"X-API-Key": "api_live_n7T51bHtniDb64WcP6WePTlU5UKzeEVR3U58ca9rYuhrvRpQZveTL"},
)
print(response.json())