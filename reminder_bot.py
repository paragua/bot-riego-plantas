import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
INACTIVITY_HOURS = 1.25  # 1hs 15

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@tasks.loop(minutes=10)
async def check_inactivity():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"No se encontró el canal {CHANNEL_ID}")
        return

    try:
        # Buscar el último mensaje de un HUMANO (ignorar todos los bots)
        last_human_message = None
        async for message in channel.history(limit=10):  # ← Revisar últimos 10 mensajes
            if not message.author.bot:  # ← Encontrar primer mensaje humano
                last_human_message = message
                break

        if not last_human_message:
            print("No hay mensajes de humanos en el historial")
            return

        current_time = datetime.now(timezone.utc)
        time_diff = current_time - last_human_message.created_at
        hours_passed = time_diff.total_seconds() / 3600

        if hours_passed >= INACTIVITY_HOURS:
            await channel.send("### NO OLVIDEN REGAR LAS PLANTAS! @everyone")
            print(f"Recordatorio enviado - Inactividad: {hours_passed:.1f} horas")
        else:
            print(f"Canal activo - Último mensaje humano hace {hours_passed:.1f} horas")

    except Exception as e:
        print(f"Error al verificar inactividad: {e}")


#@tasks.loop(seconds=60)
#async def keep_alive():
#    pass  # Mantiene el contenedor vivo

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📊 Monitoreando canal ID: {CHANNEL_ID}')
    check_inactivity.start()
    #keep_alive.start()  # ← AGREGAR ESTA LÍNEA


@bot.event
async def on_message(message):
    # Opcional: comando para verificar estado del bot
    if message.content == '!status' and message.channel.id == CHANNEL_ID:
        await message.channel.send("✅ Bot funcionando correctamente!")
    await bot.process_commands(message)


bot.run(TOKEN)
