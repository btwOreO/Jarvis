# Jarvis - Userbot

"""
✘ Commands Available -

• `{i}poto <username>/reply`
  `{i}poto <reply/upload-limit>/all`

  Ex: `{i}poto 10` - uploads starting 10 pfps of user.
    Upload the photo of Chat/User if Available.
"""

import os

from . import eod, eor, get_string, mediainfo, jarvis_cmd


@jarvis_cmd(pattern="poto( (.*)|$)")
async def gpoto(e):
    jar = e.pattern_match.group(1).strip()

    if e.is_reply:
        gs = await e.get_reply_message()
        user_id = gs.sender_id
    elif jar:
        split = jar.split()
        user_id = split[0]
        if len(jar) > 1:
            jar = jar[-1]
        else:
            jar = None
    else:
        user_id = e.chat_id

    a = await e.eor(get_string("com_1"))
    limit = None

    just_dl = jar in ["-dl", "--dl"]
    if just_dl:
        jar = None

    if jar and jar != "all":
        try:
            limit = int(jar)
        except ValueError:
            pass

    if not limit or e.client._bot:
        okla = await e.client.download_profile_photo(user_id)
    else:
        okla = []
        if limit == "all":
            limit = None
        async for photo in e.client.iter_profile_photos(user_id, limit=limit):
            photo_path = await e.client.download_media(photo)
            if photo.video_sizes:
                await e.respond(file=photo_path)
                os.remove(photo_path)
            else:
                okla.append(photo_path)
    if not okla:
        return await eor(a, "`Pfp Not Found...`")
    if not just_dl:
        await a.delete()
        await e.reply(file=okla)
        if not isinstance(okla, list):
            okla = [okla]
        for file in okla:
            os.remove(file)
        return
    if isinstance(okla, list):
        okla = "\n".join(okla)
    await a.edit(f"Downloaded pfp to [ `{okla}` ].")
