#!/usr/bin/python3

import os
from glob import glob
from pathlib import Path
from mimetypes import MimeTypes
from data_model import ChatStore, Message
from utility import APPLE_TIME, Device


def contacts(db, data):
    c = db.cursor()
    # Get status only lol
    c.execute("""SELECT count() FROM ZWAADDRESSBOOKCONTACT WHERE ZABOUTTEXT IS NOT NULL""")
    total_row_number = c.fetchone()[0]
    print(f"Pre-processing contacts...({total_row_number})")
    c.execute("""SELECT ZWHATSAPPID, ZABOUTTEXT FROM ZWAADDRESSBOOKCONTACT WHERE ZABOUTTEXT IS NOT NULL""")
    content = c.fetchone()
    while content is not None:
        if not content["ZWHATSAPPID"].endswith("@s.whatsapp.net"):
            _id = content["ZWHATSAPPID"] + "@s.whatsapp.net"
        data[_id] = ChatStore(Device.IOS)
        data[_id].status = content["ZABOUTTEXT"]
        content = c.fetchone()


def messages(db, data, media_folder):
    c = db.cursor()
    # Get contacts
    c.execute("""SELECT count() FROM ZWACHATSESSION""")
    total_row_number = c.fetchone()[0]
    print(f"Processing contacts...({total_row_number})")

    c.execute(
        """SELECT ZCONTACTJID,
                ZPARTNERNAME,
                ZPUSHNAME
           FROM ZWACHATSESSION
                LEFT JOIN ZWAPROFILEPUSHNAME
                    ON ZWACHATSESSION.ZCONTACTJID = ZWAPROFILEPUSHNAME.ZJID;"""
    )
    content = c.fetchone()
    while content is not None:
        is_phone = content["ZPARTNERNAME"].replace("+", "").replace(" ", "").isdigit()
        if content["ZPUSHNAME"] is None or (content["ZPUSHNAME"] and not is_phone):
            contact_name = content["ZPARTNERNAME"]
        else:
            contact_name = content["ZPUSHNAME"]
        contact_id = content["ZCONTACTJID"]
        if contact_id not in data:
            data[contact_id] = ChatStore(Device.IOS, contact_name, media_folder)
        else:
            data[contact_id].name = contact_name
            data[contact_id].my_avatar = os.path.join(media_folder, "Media/Profile/Photo.jpg")
        path = f'{media_folder}/Media/Profile/{contact_id.split("@")[0]}'
        avatars = glob(f"{path}*")
        if 0 < len(avatars) <= 1:
            data[contact_id].their_avatar = avatars[0]
        else:
            for avatar in avatars:
                if avatar.endswith(".thumb") and data[content["ZCONTACTJID"]].their_avatar_thumb is None:
                    data[contact_id].their_avatar_thumb = avatar
                elif avatar.endswith(".jpg") and data[content["ZCONTACTJID"]].their_avatar is None:
                    data[contact_id].their_avatar = avatar
        content = c.fetchone()

    # Get message history
    c.execute("""SELECT count() FROM ZWAMESSAGE""")
    total_row_number = c.fetchone()[0]
    print(f"Processing messages...(0/{total_row_number})", end="\r")

    c.execute("""SELECT COALESCE(ZFROMJID, ZTOJID) as _id,
                        ZWAMESSAGE.Z_PK,
                        ZISFROMME,
                        ZMESSAGEDATE,
                        ZTEXT,
                        ZMESSAGETYPE,
                        ZWAGROUPMEMBER.ZMEMBERJID,
						ZMETADATA,
                        ZSTANZAID
                 FROM ZWAMESSAGE
                    LEFT JOIN ZWAGROUPMEMBER
                        ON ZWAMESSAGE.ZGROUPMEMBER = ZWAGROUPMEMBER.Z_PK
					LEFT JOIN ZWAMEDIAITEM
						ON ZWAMESSAGE.Z_PK = ZWAMEDIAITEM.ZMESSAGE;""")
    i = 0
    content = c.fetchone()
    while content is not None:
        _id = content["_id"]
        Z_PK = content["Z_PK"]
        if _id not in data:
            data[_id] = ChatStore(Device.IOS)
            path = f'{media_folder}/Media/Profile/{_id.split("@")[0]}'
            avatars = glob(f"{path}*")
            if 0 < len(avatars) <= 1:
                data[_id].their_avatar = avatars[0]
            else:
                for avatar in avatars:
                    if avatar.endswith(".thumb"):
                        data[_id].their_avatar_thumb = avatar
                    elif avatar.endswith(".jpg"):
                        data[_id].their_avatar = avatar
        ts = APPLE_TIME + content["ZMESSAGEDATE"]
        message = Message(
            from_me=content["ZISFROMME"],
            timestamp=ts,
            time=ts, # TODO: Could be bug
            key_id=content["ZSTANZAID"][:17],
        )
        invalid = False
        if "-" in _id and content["ZISFROMME"] == 0:
            name = None
            if content["ZMEMBERJID"] is not None:
                if content["ZMEMBERJID"] in data:
                    name = data[content["ZMEMBERJID"]].name
                if "@" in content["ZMEMBERJID"]:
                    fallback = content["ZMEMBERJID"].split('@')[0]
                else:
                    fallback = None
            else:
                fallback = None
            message.sender = name or fallback
        else:
            message.sender = None
        if content["ZMESSAGETYPE"] == 6:
            # Metadata
            if "-" in _id:
                # Group
                if content["ZTEXT"] is not None:
                    # Chnaged name
                    try:
                        int(content["ZTEXT"])
                    except ValueError:
                        msg = f"The group name changed to {content['ZTEXT']}"
                        message.data = msg
                        message.meta = True
                    else:
                        invalid = True
                else:
                    message.data = None
            else:
                message.data = None
        else:
            # real message
            if content["ZMETADATA"] is not None and content["ZMETADATA"].startswith(b"\x2a\x14"):
                quoted = content["ZMETADATA"][2:19]
                message.reply = quoted.decode()
                message.quoted_data = None # TODO
            if content["ZMESSAGETYPE"] == 15: # Sticker
                message.sticker = True

            if content["ZISFROMME"] == 1:
                if content["ZMESSAGETYPE"] == 14:
                    msg = "Message deleted"
                    message.meta = True
                else:
                    msg = content["ZTEXT"]
                    if msg is not None:
                        if "\r\n" in msg:
                            msg = msg.replace("\r\n", "<br>")
                        if "\n" in msg:
                            msg = msg.replace("\n", "<br>")
            else:
                if content["ZMESSAGETYPE"] == 14:
                    msg = "Message deleted"
                    message.meta = True
                else:
                    msg = content["ZTEXT"]
                    if msg is not None:
                        if "\r\n" in msg:
                            msg = msg.replace("\r\n", "<br>")
                        if "\n" in msg:
                            msg = msg.replace("\n", "<br>")
            message.data = msg
        if not invalid:
            data[_id].add_message(Z_PK, message)
        i += 1
        if i % 1000 == 0:
            print(f"Processing messages...({i}/{total_row_number})", end="\r")
        content = c.fetchone()
    print(
        f"Processing messages...({total_row_number}/{total_row_number})", end="\r")


def media(db, data, media_folder):
    c = db.cursor()
    # Get media
    c.execute("""SELECT count() FROM ZWAMEDIAITEM""")
    total_row_number = c.fetchone()[0]
    print(f"\nProcessing media...(0/{total_row_number})", end="\r")
    i = 0
    c.execute("""SELECT COALESCE(ZWAMESSAGE.ZFROMJID, ZWAMESSAGE.ZTOJID) as _id,
                        ZMESSAGE,
                        ZMEDIALOCALPATH,
                        ZMEDIAURL,
                        ZVCARDSTRING,
                        ZMEDIAKEY,
                        ZTITLE
                 FROM ZWAMEDIAITEM
                    INNER JOIN ZWAMESSAGE
                        ON ZWAMEDIAITEM.ZMESSAGE = ZWAMESSAGE.Z_PK
                 WHERE ZMEDIALOCALPATH IS NOT NULL
                 ORDER BY _id ASC""")
    content = c.fetchone()
    mime = MimeTypes()
    while content is not None:
        file_path = f"{media_folder}/Message/{content['ZMEDIALOCALPATH']}"
        _id = content["_id"]
        ZMESSAGE = content["ZMESSAGE"]
        message = data[_id].messages[ZMESSAGE]
        message.media = True
        if os.path.isfile(file_path):
            message.data = file_path
            if content["ZVCARDSTRING"] is None:
                guess = mime.guess_type(file_path)[0]
                if guess is not None:
                    message.mime = guess
                else:
                    message.mime = "application/octet-stream"
            else:
                message.mime = content["ZVCARDSTRING"]
        else:
            if False: # Block execution
                try:
                    r = requests.get(content["ZMEDIAURL"])
                    if r.status_code != 200:
                        raise RuntimeError()
                except:
                    message.data = "The media is missing"
                    message.mime = "media"
                    message.meta = True
                else:
                    ...
            message.data = "The media is missing"
            message.mime = "media"
            message.meta = True
        if content["ZTITLE"] is not None:
            message.caption = content["ZTITLE"]
        i += 1
        if i % 100 == 0:
            print(f"Processing media...({i}/{total_row_number})", end="\r")
        content = c.fetchone()
    print(
        f"Processing media...({total_row_number}/{total_row_number})", end="\r")


def vcard(db, data):
    c = db.cursor()
    c.execute("""SELECT DISTINCT ZWAVCARDMENTION.ZMEDIAITEM,
                        ZWAMEDIAITEM.ZMESSAGE,
                        COALESCE(ZWAMESSAGE.ZFROMJID,
                        ZWAMESSAGE.ZTOJID) as _id,
                        ZVCARDNAME,
                        ZVCARDSTRING
                 FROM ZWAVCARDMENTION
                    INNER JOIN ZWAMEDIAITEM
                        ON ZWAVCARDMENTION.ZMEDIAITEM = ZWAMEDIAITEM.Z_PK
                    INNER JOIN ZWAMESSAGE
                        ON ZWAMEDIAITEM.ZMESSAGE = ZWAMESSAGE.Z_PK""")
    contents = c.fetchall()
    total_row_number = len(contents)
    print(f"\nProcessing vCards...(0/{total_row_number})", end="\r")
    base = "AppDomainGroup-group.net.whatsapp.WhatsApp.shared/Message/vCards"
    if not os.path.isdir(base):
        Path(base).mkdir(parents=True, exist_ok=True)
    for index, content in enumerate(contents):
        file_name = "".join(x for x in content["ZVCARDNAME"] if x.isalnum())
        file_name = file_name.encode('utf-8')[:230].decode('utf-8', 'ignore')
        file_path = os.path.join(base, f"{file_name}.vcf")
        if not os.path.isfile(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content["ZVCARDSTRING"])
        message = data[content["_id"]].messages[content["ZMESSAGE"]]
        message.data = content["ZVCARDNAME"] + \
            "The vCard file cannot be displayed here, " \
            f"however it should be located at {file_path}"
        message.mime = "text/x-vcard"
        message.media = True
        message.meta = True
        print(f"Processing vCards...({index + 1}/{total_row_number})", end="\r")
