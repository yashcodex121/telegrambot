import os
import asyncio

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from yt_dlp import YoutubeDL

# =========================
# CONFIG
# =========================

API_ID = 123456
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

OWNER_USERNAME = "https://t.me/Brucerich12"

START_IMAGE = "https://files.catbox.moe/3jrvyp.jpg"

# =========================
# BOT CLIENT
# =========================

app = Client(
    "MusicEffectBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

user_files = {}

# =========================
# BUTTONS
# =========================

def main_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎛 Effect",
                callback_data="effects"
            )
        ],
        [
            InlineKeyboardButton(
                "❓ Help",
                callback_data="help"
            ),
            InlineKeyboardButton(
                "👑 Owner",
                url=OWNER_USERNAME
            )
        ]
    ])


def effects_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎧 Echo",
                callback_data="echo"
            ),
            InlineKeyboardButton(
                "🌙 Lofi",
                callback_data="lofi"
            )
        ],
        [
            InlineKeyboardButton(
                "🔊 Bass",
                callback_data="bass"
            ),
            InlineKeyboardButton(
                "🎵 Normal",
                callback_data="normal"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="back"
            )
        ]
    ])

# =========================
# DOWNLOAD SONG
# =========================

async def download_song(query):

    file_template = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": file_template,
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            query,
            download=True
        )

        file_path = ydl.prepare_filename(info)
        file_path = os.path.splitext(file_path)[0] + ".mp3"

    return file_path, info

# =========================
# APPLY EFFECT
# =========================

async def apply_effect(
    input_file,
    effect_name
):

    output_file = input_file.replace(
        ".mp3",
        f"_{effect_name}.mp3"
    )

    if effect_name == "echo":

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-filter:a",
            "aecho=0.8:0.9:1000:0.3",
            output_file
        ]

    elif effect_name == "lofi":

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-filter:a",
            "bass=g=3,treble=g=-2,asetrate=44100*0.9",
            output_file
        ]

    elif effect_name == "bass":

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-filter:a",
            "bass=g=10",
            output_file
        ]

    elif effect_name == "normal":

        return input_file

    else:

        return input_file

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    await process.communicate()

    return output_file

# =========================
# START COMMAND
# =========================

@app.on_message(filters.command("start"))
async def start(_, message):

    start_text = """
🎵 Welcome To Music Effect Bot

✨ Features:
• Download Songs
• Echo Effect
• Lofi Effect
• Bass Boost
• Normal Audio

📌 Commands:
/play song name
/skip
/stop

🎧 Enjoy High Quality Music
"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "❓ Help",
                callback_data="help"
            ),
            InlineKeyboardButton(
                "👑 Owner",
                url=OWNER_USERNAME
            )
        ]
    ])

    await message.reply_photo(
        photo=START_IMAGE,
        caption=start_text,
        reply_markup=buttons
    )

# =========================
# HELP MENU
# =========================

@app.on_callback_query(filters.regex("help"))
async def help_menu(_, query: CallbackQuery):

    text = """
🎵 Music Bot Help

📌 Commands:

/play song name
Download Any Song

/skip
Skip Current Song

/stop
Stop Current Song

🎛 Effects:
• Echo
• Lofi
• Bass Boost
• Normal Audio
"""

    await query.message.edit_caption(
        caption=text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅ Back",
                    callback_data="home"
                )
            ]
        ])
    )

# =========================
# BACK HOME
# =========================

@app.on_callback_query(filters.regex("home"))
async def home_page(_, query: CallbackQuery):

    start_text = """
🎵 Welcome To Music Effect Bot

✨ Features:
• Download Songs
• Echo Effect
• Lofi Effect
• Bass Boost
• Normal Audio

📌 Commands:
/play song name
/skip
/stop

🎧 Enjoy High Quality Music
"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "❓ Help",
                callback_data="help"
            ),
            InlineKeyboardButton(
                "👑 Owner",
                url=OWNER_USERNAME
            )
        ]
    ])

    await query.message.edit_caption(
        caption=start_text,
        reply_markup=buttons
    )

# =========================
# PLAY SONG
# =========================

@app.on_message(filters.command("play"))
async def play_song(_, message):

    if len(message.command) < 2:

        return await message.reply_text(
            "Usage:\n/play song name"
        )

    query = " ".join(message.command[1:])

    status = await message.reply_text(
        "🔍 Searching Song..."
    )

    try:

        song_path, info = await download_song(query)

        user_files[message.from_user.id] = song_path

        thumbnail = info.get("thumbnail")

        thumb_path = None

        if thumbnail:

            thumb_path = os.path.join(
                DOWNLOAD_DIR,
                "thumb.jpg"
            )

            os.system(
                f'wget "{thumbnail}" -O "{thumb_path}"'
            )

        await status.edit_text(
            "📤 Uploading Song..."
        )

        await message.reply_audio(
            audio=song_path,
            caption=f"🎵 {query}",
            thumb=thumb_path if thumb_path else None,
            title=info.get("title"),
            performer=info.get("uploader"),
            duration=info.get("duration"),
            reply_markup=main_buttons()
        )

        await status.delete()

    except Exception as e:

        await status.edit_text(
            f"❌ Error:\n{e}"
        )

# =========================
# EFFECT MENU
# =========================

@app.on_callback_query(filters.regex("effects"))
async def effects_menu(_, query: CallbackQuery):

    await query.message.edit_reply_markup(
        reply_markup=effects_buttons()
    )

# =========================
# BACK BUTTON
# =========================

@app.on_callback_query(filters.regex("back"))
async def back_button(_, query: CallbackQuery):

    await query.message.edit_reply_markup(
        reply_markup=main_buttons()
    )

# =========================
# APPLY EFFECT
# =========================

@app.on_callback_query(
    filters.regex(
        "echo|lofi|bass|normal"
    )
)
async def effect_apply(_, query: CallbackQuery):

    user_id = query.from_user.id

    if user_id not in user_files:

        return await query.answer(
            "Pehle Song Play Karo",
            show_alert=True
        )

    effect = query.data

    await query.answer(
        f"{effect.title()} Applying..."
    )

    original_file = user_files[user_id]

    processing = await query.message.reply_text(
        f"🎛 Applying {effect.title()} Effect..."
    )

    try:

        edited_file = await apply_effect(
            original_file,
            effect
        )

        await query.message.reply_audio(
            audio=edited_file,
            caption=f"🎧 Effect Applied: {effect.title()}",
            reply_markup=main_buttons()
        )

        await processing.delete()

    except Exception as e:

        await processing.edit_text(
            f"❌ Error:\n{e}"
        )

# =========================
# SKIP COMMAND
# =========================

@app.on_message(filters.command("skip"))
async def skip_song(_, message):

    await message.reply_text(
        "⏭ Song Changed Successfully"
    )

# =========================
# STOP COMMAND
# =========================

@app.on_message(filters.command("stop"))
async def stop_song(_, message):

    await message.reply_text(
        "⏹ Playback Stopped"
    )

# =========================
# RUN BOT
# =========================

print("Bot Started Successfully")

app.run()
