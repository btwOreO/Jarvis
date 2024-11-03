# Jarvis - Userbot

"""
✘ Commands Available -

• `{i}border <reply to photo/sticker>`
    To create border around that media..
    Ex - `{i}border 12,22,23`
       - `{i}border 12,22,23 ; width (in number)`

• `{i}color <reply to any Black nd White media>`
    To make it Colorfull.

• `{i}blue <reply to any media>`
    just cool.

• `{i}csample <color name /color code>`
   example : `{i}csample red`
             `{i}csample #ffffff`

• `{i}pixelator <reply image>`
    Create a Pixelated Image..

• `{i}ascii <reply image>`
    Convert replied image into html.
"""

import os

from . import LOGS, con

try:
    import cv2
except ImportError:
    LOGS.error(f"{__file__}: OpenCv not Installed.")

try:
    from PIL import Image
except ImportError:
    Image = None
    LOGS.info(f"{__file__}: PIL  not Installed.")
from telegraph import upload_file as upf
from telethon.errors.rpcerrorlist import (
    ChatSendMediaForbiddenError,
    MessageDeleteForbiddenError,
)

from . import (
    Redis,
    async_searcher,
    download_file,
    get_string,
    requests,
    udB,
    jarvis_cmd,
)

try:
    from htmlwebshot import WebShot
except ImportError:
    WebShot = None
try:
    from img2html.converter import Img2HTMLConverter
except ImportError:
    Img2HTMLConverter = None


@jarvis_cmd(pattern="color$")
async def _(event):
    reply = await event.get_reply_message()
    if not (reply and reply.media):
        return await event.eor("`Reply To a Black and White Image`")
    xx = await event.eor("`Coloring image 🎨🖌️...`")
    image = await reply.download_media()
    img = cv2.VideoCapture(image)
    ret, frame = img.read()
    cv2.imwrite("jar.jpg", frame)
    if udB.get_key("DEEP_API"):
        key = Redis("DEEP_API")
    else:
        key = "quickstart-QUdJIGlzIGNvbWluZy4uLi4K"
    r = requests.post(
        "https://api.deepai.org/api/colorizer",
        files={"image": open("jar.jpg", "rb")},
        headers={"api-key": key},
    )
    os.remove("jar.jpg")
    os.remove(image)
    if "status" in r.json():
        return await event.edit(
            r.json()["status"] + "\nGet api nd set `{i}setdb DEEP_API key`"
        )
    r_json = r.json()["output_url"]
    await event.client.send_file(event.chat_id, r_json, reply_to=reply)
    await xx.delete()


@jarvis_cmd(pattern="csample (.*)")
async def sampl(jar):
    if color := jar.pattern_match.group(1).strip():
        img = Image.new("RGB", (200, 100), f"{color}")
        img.save("csample.png")
        try:
            try:
                await jar.delete()
                await jar.respond(f"Colour Sample for `{color}` !", file="csample.png")
            except MessageDeleteForbiddenError:
                await jar.reply(f"Colour Sample for `{color}` !", file="csample.png")
        except ChatSendMediaForbiddenError:
            await jar.eor("Umm! Sending Media is disabled here!")

    else:
        await jar.eor("Wrong Color Name/Hex Code specified!")


@jarvis_cmd(
    pattern="blue$",
)
async def jrvs(event):
    ureply = await event.get_reply_message()
    xx = await event.eor("`...`")
    if not (ureply and (ureply.media)):
        await xx.edit(get_string("cvt_3"))
        return
    jarr = await ureply.download_media()
    if jarr.endswith(".tgs"):
        await xx.edit(get_string("sts_9"))
    file = await con.convert(jarr, convert_to="png", outname="jar")
    got = upf(file)
    lnk = f"https://graph.org{got[0]}"
    r = await async_searcher(
        f"https://nekobot.xyz/api/imagegen?type=blurpify&image={lnk}", re_json=True
    )
    ms = r.get("message")
    if not r["success"]:
        return await xx.edit(ms)
    await download_file(ms, "jar.png")
    img = Image.open("jar.png").convert("RGB")
    img.save("jar.webp", "webp")
    await event.client.send_file(
        event.chat_id,
        "jar.webp",
        force_document=False,
        reply_to=event.reply_to_msg_id,
    )
    await xx.delete()
    os.remove("jar.png")
    os.remove("jar.webp")
    os.remove(jarr)


@jarvis_cmd(pattern="border( (.*)|$)")
async def ok(event):
    hm = await event.get_reply_message()
    if not (hm and (hm.photo or hm.sticker)):
        return await event.eor("`Reply to Sticker or Photo..`")
    col = event.pattern_match.group(1).strip()
    wh = 20
    if not col:
        col = [255, 255, 255]
    else:
        try:
            if ";" in col:
                col_ = col.split(";", maxsplit=1)
                wh = int(col_[1])
                col = col_[0]
            col = [int(col) for col in col.split(",")[:2]]
        except ValueError:
            return await event.eor("`Not a Valid Input...`")
    okla = await hm.download_media()
    img1 = cv2.imread(okla)
    constant = cv2.copyMakeBorder(img1, wh, wh, wh, wh, cv2.BORDER_CONSTANT, value=col)
    cv2.imwrite("output.png", constant)
    await event.client.send_file(event.chat.id, "output.png")
    os.remove("output.png")
    os.remove(okla)
    await event.delete()


@jarvis_cmd(pattern="pixelator( (.*)|$)")
async def pixelator(event):
    reply_message = await event.get_reply_message()
    if not (reply_message and (reply_message.photo or reply_message.sticker)):
        return await event.eor("`Reply to a photo`")
    hw = 50
    try:
        hw = int(event.pattern_match.group(1).strip())
    except (ValueError, TypeError):
        pass
    msg = await event.eor(get_string("com_1"))
    image = await reply_message.download_media()
    input_ = cv2.imread(image)
    height, width = input_.shape[:2]
    w, h = (hw, hw)
    temp = cv2.resize(input_, (w, h), interpolation=cv2.INTER_LINEAR)
    output = cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)
    cv2.imwrite("output.jpg", output)
    await msg.respond("• Pixelated by Jarvis", file="output.jpg")
    await msg.delete()
    os.remove("output.jpg")
    os.remove(image)


@jarvis_cmd(
    pattern="ascii( (.*)|$)",
)
async def _(e):
    if not Img2HTMLConverter:
        return await e.eor("'img2html-converter' not installed!")
    if not e.reply_to_msg_id:
        return await e.eor(get_string("ascii_1"))
    m = await e.eor(get_string("ascii_2"))
    img = await (await e.get_reply_message()).download_media()
    char = e.pattern_match.group(1).strip() or "■"
    converter = Img2HTMLConverter(char=char)
    html = converter.convert(img)
    shot = WebShot(quality=85)
    pic = await shot.create_pic_async(html=html)
    await m.delete()
    await e.reply(file=pic)
    os.remove(pic)
    os.remove(img)
