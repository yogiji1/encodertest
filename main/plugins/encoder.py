#  This file is part of the VIDEOconvertor distribution.
#  Copyright (c) 2021 vasusen-code ; All rights reserved. 
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  License can be found in < https://github.com/vasusen-code/VIDEOconvertor/blob/public/LICENSE> .

import asyncio, time, subprocess, re, os

from datetime import datetime as dt
from telethon import events
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.types import DocumentAttributeVideo
from ethon.telefunc import fast_download, fast_upload
from ethon.pyfunc import video_metadata

from .. import Drone, BOT_UN

from LOCAL.localisation import SUPPORT_LINK, JPG, JPG2, JPG3
from LOCAL.utils import ffmpeg_progress

async def encode(event, msg, scale=0):
    Drone = event.client
    edit = await Drone.send_message(event.chat_id, "Trying to process.", reply_to=msg.id)
    new_name = "out_" + dt.now().isoformat("_", "seconds")
    if hasattr(msg.media, "document"):
        file = msg.media.document
    else:
        file = msg.media
    mime = msg.file.mime_type
    if 'mp4' in mime:
        n = "media_" + dt.now().isoformat("_", "seconds") + ".mp4"
        out = new_name + ".mp4"
    elif msg.video:
        n = "media_" + dt.now().isoformat("_", "seconds") + ".mp4"
        out = new_name + ".mp4"
    elif 'x-matroska' in mime:
        n = "media_" + dt.now().isoformat("_", "seconds") + ".mkv" 
        out = new_name + ".mp4"            
    elif 'webm' in mime:
        n = "media_" + dt.now().isoformat("_", "seconds") + ".webm" 
        out = new_name + ".mp4"
    else:
        n = msg.file.name
        ext = (n.split("."))[1]
        out = new_name + ext
    DT = time.time()
    try:
        await fast_download(n, file, Drone, edit, DT, "**DOWNLOADING:**")
    except Exception as e:
        os.rmdir("encodemedia")
        print(e)
        return await edit.edit(f"An error occured while downloading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False) 
    name =  '__' + dt.now().isoformat("_", "seconds") + ".mp4"
    os.rename(n, name)
    await edit.edit("Extracting metadata...")
    vid = video_metadata(name)
    hgt = int(vid['height'])
    wdt = int(vid['width'])
    if scale == hgt:
        os.rmdir("encodemedia")
        return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 240:
        if 426 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 360:
        if 640 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 480:
        if 854 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 720:
        if 1280 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 1080:
        if 1920 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    FT = time.time()
    progress = f"progress-{FT}.txt"
    cmd = ''
    if scale == 240:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset faster -s 426x240 -crf 24 -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    elif scale == 360:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset faster -s 640x360 -crf 24 -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    elif scale == 480:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset faster -s 854x480 -crf 24 -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    elif scale == 720:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset faster -s 1280x720 -crf 24 -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    elif scale == 1080:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx265 -pix_fmt yuv420p10le -preset medium -s 1280x720 -crf 23 -metadata title='[Bhupinder Jogi Encode]' -metadata:s:v title='[Bhupinder Jogi Encode] - 720p - HEVC ' -metadata:s:a title='[Bhupinder Jogi] - Opus - 256 kbps' -metadata:s:s title='[Bhupinder Jogi]' -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    elif scale == 2160:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset medium -s 1280x720 -crf 23 -metadata title='[Bhupinder Jogi Encode]' -metadata:s:v title='[Bhupinder Jogi Encode] - 720p - HEVC ' -metadata:s:a title='[Bhupinder Jogi] - Opus - 256 kbps' -metadata:s:s title='[Bhupinder Jogi]' -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    try:
        await ffmpeg_progress(cmd, name, progress, FT, edit, '**ENCODING:**')
    except Exception as e:
        os.rmdir("encodemedia")
        print(e)
        return await edit.edit(f"An error occured while FFMPEG progress.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)   
    out2 = dt.now().isoformat("_", "seconds") + ".mp4" 
    if msg.file.name:
        out2 = msg.file.name
    else:
        out2 = dt.now().isoformat("_", "seconds") + ".mp4" 
    os.rename(out, out2)
    i_size = os.path.getsize(name)
    f_size = os.path.getsize(out2)
    text = f'**ENCODED by** : @{BOT_UN}\n\nbefore encoding : `{i_size}`\nafter ecoding : `{f_size}`'
    UT = time.time()
    if 'webm' in mime:
        try:
            uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
            await Drone.send_file(event.chat_id, uploader, caption=text, thumb=JPG, force_document=True)
        except Exception as e:
            os.rmdir("encodemedia")
            print(e)
            return await edit.edit(f"An error occured while uploading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)
    elif 'x-matroska' in mime:
        try:
            uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
            await Drone.send_file(event.chat_id, uploader, caption=text, thumb=JPG, force_document=True)
        except Exception as e:
            os.rmdir("encodemedia")
            print(e)
            return await edit.edit(f"An error occured while uploading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)
    else:
        metadata = video_metadata(out2)
        width = metadata["width"]
        height = metadata["height"]
        duration = metadata["duration"]
        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
        try:
            uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
            await Drone.send_file(event.chat_id, uploader, caption=text, thumb=JPG3, attributes=attributes, force_document=False)
        except Exception:
            try:
                uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
                await Drone.send_file(event.chat_id, uploader, caption=text, thumb=JPG, force_document=True)
            except Exception as e:
                os.rmdir("encodemedia")
                print(e)
                return await edit.edit(f"An error occured while uploading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)
    await edit.delete()
    os.remove(name)
    os.remove(out2)
    
