# Bot de Discord:
# - Comandos para unirse/salir de canales de voz y gestionar estado de orador en Escenarios.
# - Sondea archivos de ZDex (capture_flag.json y last_detection.json) para anunciar nuevas capturas.
import discord
from discord.ext import commands
import os
import json
from pathlib import Path
import asyncio
from zdex import config as zdex_config

LAST_DET_PATH = zdex_config.DATA_DIR / "last_detection.json"
FLAG_PATH = zdex_config.DATA_DIR / "capture_flag.json"

def _read_flag():
    try:
        with FLAG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"active": False}

def _deactivate_flag():
    try:
        with FLAG_PATH.open("w", encoding="utf-8") as f:
            json.dump({"active": False, "updated_at": None}, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def _read_last_detection():
    try:
        with LAST_DET_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# --- 1. Configuración de Intents ---
# Habilita lectura de contenido de mensajes y estados de voz (requerido para comandos)
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# --- 2. Instancia ÚNICA del Bot ---
bot = commands.Bot(command_prefix='!', intents=intents)
POLL_TASKS: dict[int, asyncio.Task] = {}

@bot.event
async def on_ready():
    # Evento de inicio del bot
    print(f'Hemos iniciado sesión como {bot.user}')

@bot.command(name='hola')
async def greet(ctx):
    """Responde con un saludo. Uso: !hola"""
    await ctx.send(f'¡Hola! Mi nombre es {bot.user.name}.')

@bot.command(name='unirse', aliases=['join', 'entrar'])
async def join(ctx):
    """
    Une el bot al canal de voz del invocador y:
    - Mutea/ensordece al invocador.
    - Intenta ponerlo como orador si es un Escenario.
    - Sondea nuevas capturas de ZDex por tiempo limitado y arranca sondeo persistente.
    """
    member = ctx.author

    if member.voice and member.voice.channel:
        channel = member.voice.channel

        # Conecta o mueve el bot al canal de voz
        if ctx.voice_client and ctx.voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)
        elif not ctx.voice_client:
            await channel.connect()

        # Nuevo: mutear y ensordecer al invocador
        try:
            await member.edit(mute=True, deafen=True, reason="Solicitado vía !unirse")
            await ctx.send(f"🔇 {member.display_name} ha sido muteado y ensordecido en **{channel.name}**.")
        except discord.Forbidden:
            await ctx.send("⚠️ Me uní, pero no tengo permisos para mutear/ensordecer al invocador.")
        except Exception as e:
            await ctx.send(f"⚠️ Error al mutear/ensordecer: {e}")

        # Si es un Escenario (Stage), intenta pasar al usuario a orador (unsuppress)
        if isinstance(channel, discord.StageChannel):
            try:
                await member.edit(suppress=False, reason="Permitir hablar/usar cámara en Escenario")
                await ctx.send(
                    f"Me he unido a **{channel.name}** y te he pasado a orador. "
                    "Ahora puedes encender tu cámara con el botón 'Iniciar video' en Discord."
                )
            except discord.Forbidden:
                await ctx.send(
                    "⚠️ Me uní, pero no tengo permisos para ponerte como orador en este Escenario."
                )
            except Exception as e:
                await ctx.send(f"Me uní, pero ocurrió un error al pasarte a orador: {e}")
        else:
            # En canales de voz normales, los bots no pueden encender cámaras por API
            await ctx.send(
                f"Me he unido a **{channel.name}**. No puedo encender cámaras automáticamente; "
                "enciéndela con el botón 'Iniciar video' en Discord."
            )

        #retornar captura  
        # Reemplaza el bucle infinito por un sondeo asíncrono con pausa
        max_wait_seconds = 120  # tiempo máximo para esperar una nueva captura
        poll_interval = 1.0     # segundos entre cada sondeo
        waited = 0
        while waited < max_wait_seconds:
            # salir si el bot se desconecta del canal de voz
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                break

            flag = _read_flag()
            if flag.get("active"):
                data = _read_last_detection()
                if data:
                    specie = data.get("common_name") or data.get("scientific_name") or "Especie desconocida"
                    await ctx.send(f"Nueva captura registrada: {specie}")
                else:
                    await ctx.send("No pude leer last_detection.json.")
                _deactivate_flag()
                break  # salir después de procesar la captura
            # dormir para no bloquear el loop de eventos
            await asyncio.sleep(poll_interval)
            waited += poll_interval
        if waited >= max_wait_seconds:
            await ctx.send("No se recibió ninguna captura nueva en el tiempo esperado.")

        # Inicia una tarea de sondeo persistente si no existe ya
        gid = ctx.guild.id if ctx.guild else None
        if gid is not None and gid not in POLL_TASKS:
            async def _poll_captures():
                try:
                    poll_interval = 1.0
                    while True:
                        # salir si el bot se desconecta del canal de voz
                        if not ctx.voice_client or not ctx.voice_client.is_connected():
                            break
                        flag = _read_flag()
                        if flag.get("active"):
                            data = _read_last_detection()
                            if data:
                                specie = data.get("common_name") or data.get("scientific_name") or "Especie desconocida"
                                await ctx.send(f"Nueva captura registrada: {specie}")
                            else:
                                await ctx.send("No pude leer last_detection.json.")
                            _deactivate_flag()
                        await asyncio.sleep(poll_interval)
                except asyncio.CancelledError:
                    # tarea cancelada al salir
                    pass
                except Exception as e:
                    # evitar que la tarea muera silenciosamente
                    await ctx.send(f"⚠️ Error en sondeo de capturas: {e}")
            POLL_TASKS[gid] = asyncio.create_task(_poll_captures())
    else:
        await ctx.send("¡Debes estar en un canal de voz para que pueda unirme!")

# --- Comando para SALIR del canal de voz ---
@bot.command(name='salir', aliases=['leave', 'desconectar'])
async def leave(ctx):
    """
    Hace que el bot salga del canal de voz y cancela tareas de sondeo.
    Uso: !salir
    """
    # 1. Verifica si el bot está conectado a un canal de voz
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Me he desconectado del canal de voz. ¡Adiós!")
    else:
        await ctx.send("No estoy conectado a ningún canal de voz.")

    # Cancela la tarea de sondeo para este servidor
    gid = ctx.guild.id if ctx.guild else None
    task = POLL_TASKS.pop(gid, None) if gid is not None else None
    if task:
        task.cancel()

@bot.command(name='permitirvideo', aliases=['startvid'])
@commands.has_permissions(mute_members=True)
async def unsuppress_video(ctx, member: discord.Member, *, reason=None):
    """
    Pasa a orador a un usuario en un Escenario (Stage).
    Uso: !permitirvideo @usuario [razón]
    """
    if member.voice and member.voice.channel:
        ch = member.voice.channel
        if isinstance(ch, discord.StageChannel):
            try:
                await member.edit(suppress=False, reason=reason)
                await ctx.send(
                    f"✅ {member.display_name} ahora es orador en **{ch.name}**. "
                    "Puede encender su cámara desde el cliente."
                )
            except discord.Forbidden:
                await ctx.send("⚠️ No tengo permisos para modificar el estado de orador en este Escenario.")
            except Exception as e:
                await ctx.send(f"⚠️ Ocurrió un error al modificar el estado de orador: {e}")
        else:
            await ctx.send(
                f"**{member.display_name}** está en un canal de voz normal. "
                "Los bots no pueden encender cámaras por API; pídele que pulse 'Iniciar video'."
            )
    else:
        await ctx.send(f"**{member.display_name}** no está en un canal de voz.")

@bot.command(name='quitarvideo', aliases=['stopvid'])
@commands.has_permissions(mute_members=True)
async def suppress_video(ctx, member: discord.Member, *, reason=None):
    """
    Pasa a oyente (suppress=True) a un usuario en un Escenario.
    Uso: !quitarvideo @usuario [razón]
    """
    if member.voice and member.voice.channel:
        ch = member.voice.channel
        if isinstance(ch, discord.StageChannel):
            try:
                await member.edit(suppress=True, reason=reason)
                await ctx.send(f"📹 {member.display_name} ahora es oyente en **{ch.name}**.")
            except discord.Forbidden:
                await ctx.send("⚠️ No tengo permisos para pasarlo a oyente en este Escenario.")
            except Exception as e:
                await ctx.send(f"⚠️ Ocurrió un error al modificar el estado de oyente: {e}")
        else:
            await ctx.send("Este canal no es un Escenario. No puedo forzar apagar la cámara en canales de voz normales.")
    else:
        await ctx.send(f"**{member.display_name}** no está en un canal de voz.")

# --- 6. Inicia el bot ---
# Requiere variable de entorno ZUNIBOT_TOKEN con el token del bot
bot.run(os.getenv('ZUNIBOT_TOKEN'))