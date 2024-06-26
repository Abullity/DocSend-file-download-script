import asyncio

import aiohttp
import yarl


URL = ""        # https://docsend.com/view/...
EMAIL = ""      # a valid email if needed
PASSCODE = ""   # if needed


async def get_pdf(session: aiohttp.ClientSession):
    async with session.get(URL) as resp:
        # to set cookies for consequent requests
        pass

    # try getting download link
    async with session.get(f"{URL}/download") as resp:
        response_json = await resp.json()

        if "url" in response_json:
            async with session.get(yarl.URL(response_json["url"], encoded=True)) as resp:
                with open("test.pdf", "wb") as pdf_file:
                    pdf_file.write(await resp.content.read())
        else:
            # file is passcode or email protected
            data = {
                "_method": "patch",
                **({"link_auth_form[email]": EMAIL} if EMAIL else {}),
                **({"link_auth_form[passcode]": PASSCODE} if PASSCODE else {}),
                "link_auth_form[timezone_offset]": "",
                "button": ""
            }
            async with session.post(f"{URL}", data=data) as resp:
                if resp.status == 200:
                    # got permission to download file
                    return await get_pdf(session)
                else:
                    # failed getting permission to download
                    response_json = await resp.json()

                    # invalid passcode
                    if "link_auth_form[passcode]" in response_json["html"]:
                        return


async def main():
    async with aiohttp.ClientSession() as session:
        await get_pdf(session)


asyncio.run(main())
