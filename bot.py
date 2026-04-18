import discord
from discord.ext import commands
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio
import os
import re
from collections import deque
from dotenv import load_dotenv

load_dotenv()

# ── Configurações ──────────────────────────────────────────────────────────────
DISCORD_TOKEN        = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT_ID    = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# ── Spotify client ─────────────────────────────────────────────────────────────
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
))

# ── Discord bot ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="Z_", intents=intents, help_command=None)

# ── Estado por servidor ────────────────────────────────────────────────────────
# { guild_id: deque([{ title, audio_url, requester }]) }
guild_queues:  dict[int, deque] = {}
# { guild_id: { title, audio_url, requester } | None }
guild_current: dict[int, dict | None] = {}

# ── yt-dlp ─────────────────────────────────────────────────────────────────────
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "source_address": "0.0.0.0",
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

# ── Helpers ────────────────────────────────────────────────────────────────────
def is_youtube(url: str) -> bool:
    return bool(re.match(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/", url))

def is_spotify(url: str) -> bool:
    return bool(re.match(r"(https?://)?open\.spotify\.com/track/", url))

def get_queue(guild_id: int) -> deque:
    if guild_id not in guild_queues:
        guild_queues[guild_id] = deque()
    return guild_queues[guild_id]

async def resolve_song(url: str) -> dict | None:
    """
    Resolve uma URL do YouTube ou Spotify e retorna um dict
    { title, audio_url } ou None se inválido.
    """
    loop = asyncio.get_event_loop()

    if is_spotify(url):
        track_id = url.split("track/")[-1].split("?")[0]
        track    = sp.track(track_id)
        artist   = track["artists"][0]["name"]
        name     = track["name"]
        query    = f"ytsearch:{name} {artist}"
        display  = f"{name} — {artist}"

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        data = data["entries"][0]

    elif is_youtube(url):
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if "entries" in data:
            data = data["entries"][0]
        display = data.get("title", "Desconhecido")

    else:
        return None  # link inválido

    return {"title": display, "audio_url": data["url"]}

async def play_next(ctx: commands.Context):
    """Toca a próxima música da fila, se houver."""
    guild_id = ctx.guild.id
    queue    = get_queue(guild_id)

    if not queue:
        guild_current[guild_id] = None
        await ctx.send("✅ Fila finalizada! Sem mais músicas.")
        return

    song = queue.popleft()
    guild_current[guild_id] = song

    source = discord.FFmpegPCMAudio(song["audio_url"], **FFMPEG_OPTIONS)

    def after(error):
        if error:
            print(f"[ERRO ao tocar] {error}")
        asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

    ctx.voice_client.play(source, after=after)
    await ctx.send(f"🎵 Tocando agora: **{song['title']}** (pedida por {song['requester']})")

# ── Comandos ───────────────────────────────────────────────────────────────────

@bot.command(name="Play")
async def play(ctx: commands.Context, url: str = None):
    """Z_Play <link> → toca / enfileira | Z_Play → retoma pausada"""

    # Sem link → retomar música pausada
    if url is None:
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Música retomada!")
        else:
            await ctx.send("❌ Nenhuma música pausada no momento.")
        return

    # Validar link
    if not is_youtube(url) and not is_spotify(url):
        await ctx.send(
            "❌ Link inválido! Apenas links do **YouTube** e do **Spotify** (faixa individual) são aceitos."
        )
        return

    # Checar canal de voz
    if not ctx.author.voice:
        await ctx.send("❌ Você precisa estar em um canal de voz para usar este comando!")
        return

    # Conectar ao canal se necessário
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    elif ctx.voice_client.channel != ctx.author.voice.channel:
        await ctx.voice_client.move_to(ctx.author.voice.channel)

    msg = await ctx.send("⏳ Carregando música...")

    try:
        song = await resolve_song(url)
    except Exception as e:
        await msg.edit(content=f"❌ Erro ao carregar a música: `{e}`")
        return

    if song is None:
        await msg.edit(content="❌ Link inválido! Apenas links do **YouTube** e do **Spotify** são aceitos.")
        return

    song["requester"] = ctx.author.display_name
    queue = get_queue(ctx.guild.id)

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        queue.append(song)
        await msg.edit(content=f"✅ **{song['title']}** adicionada à fila! Posição: **#{len(queue)}**")
    else:
        guild_current[ctx.guild.id] = song
        source = discord.FFmpegPCMAudio(song["audio_url"], **FFMPEG_OPTIONS)

        def after(error):
            if error:
                print(f"[ERRO] {error}")
            asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

        ctx.voice_client.play(source, after=after)
        await msg.edit(content=f"🎵 Tocando agora: **{song['title']}**")


@bot.command(name="Queue")
async def queue_cmd(ctx: commands.Context):
    """Z_Queue → exibe a fila de músicas"""
    guild_id = ctx.guild.id
    queue    = get_queue(guild_id)
    current  = guild_current.get(guild_id)

    if not current and not queue:
        await ctx.send("📭 A fila está vazia!")
        return

    lines = ["🎶 **Fila de músicas:**\n"]

    if current:
        lines.append(f"▶️ **Tocando agora:** {current['title']} — _{current['requester']}_\n")

    if queue:
        for i, s in enumerate(queue, 1):
            lines.append(f"`{i}.` {s['title']} — _{s['requester']}_")
    else:
        lines.append("_Sem músicas aguardando._")

    await ctx.send("\n".join(lines))


@bot.command(name="ClearQueue")
async def clear_queue(ctx: commands.Context):
    """Z_ClearQueue → limpa toda a fila"""
    get_queue(ctx.guild.id).clear()
    await ctx.send("🗑️ Fila limpa com sucesso!")


@bot.command(name="Stop")
async def stop(ctx: commands.Context):
    """Z_Stop → desconecta o bot e limpa a fila"""
    if not ctx.voice_client:
        await ctx.send("❌ O bot não está em nenhum canal de voz.")
        return

    get_queue(ctx.guild.id).clear()
    guild_current[ctx.guild.id] = None
    await ctx.voice_client.disconnect()
    await ctx.send("⏹️ Bot desconectado e fila limpa!")


@bot.command(name="Pause")
async def pause(ctx: commands.Context):
    """Z_Pause → pausa a música atual"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Música pausada!")
    else:
        await ctx.send("❌ Nenhuma música tocando no momento.")


@bot.command(name="Ping")
async def ping(ctx: commands.Context):
    """Z_Ping → Pong!"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latência: **{latency}ms**")


@bot.command(name="Help")
async def help_cmd(ctx: commands.Context):
    """Z_Help → lista todos os comandos"""
    help_text = (
        "🤖 **Comandos do Music Bot**\n\n"
        "`Z_Play <link>` — Toca uma música (YouTube ou Spotify). Se já houver uma tocando, entra na fila.\n"
        "`Z_Play` — Retoma a música que estava pausada.\n"
        "`Z_Pause` — Pausa a música atual.\n"
        "`Z_Queue` — Exibe todas as músicas na fila.\n"
        "`Z_ClearQueue` — Remove todas as músicas da fila.\n"
        "`Z_Stop` — Desconecta o bot e limpa a fila.\n"
        "`Z_Ping` — Verifica se o bot está online.\n"
        "`Z_Help` — Exibe esta mensagem.\n\n"
        "🔗 Links aceitos: **YouTube** e **Spotify** (somente faixas individuais)."
    )
    await ctx.send(help_text)


# ── Eventos ────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Comando não encontrado. Use `Z_Help` para ver os comandos disponíveis.")
    else:
        raise error

# ── Entry point ────────────────────────────────────────────────────────────────
bot.run(DISCORD_TOKEN)
