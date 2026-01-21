import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID_RAW = os.getenv('CHANNEL_ID')

print("TOKEN:", repr(TOKEN))
print("CHANNEL_ID_RAW:", repr(CHANNEL_ID_RAW))

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN no está definido en las variables de entorno")

if not CHANNEL_ID_RAW:
    raise RuntimeError("CHANNEL_ID no está definido en las variables de entorno")

CHANNEL_ID = int(CHANNEL_ID_RAW)
INACTIVITY_HOURS = 1  # o el valor que quieras


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@tasks.loop(minutes=2)  # Revisa cada 30 minutos
async def check_inactivity():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"No se encontró el canal {CHANNEL_ID}")
        return

    try:
        # Obtener el último mensaje
        async for message in channel.history(limit=1):
            last_message_time = message.created_at
            current_time = datetime.now(timezone.utc)
            time_diff = current_time - last_message_time

            hours_passed = time_diff.total_seconds() / 3600

            # Si pasó más tiempo del configurado
            if hours_passed >= INACTIVITY_HOURS:
                # Verificar que el último mensaje no sea del bot
                if not message.author.bot:
                    await channel.send(
                        f"⏰ **Recordatorio**: NO OLVIDEN REGAR LAS PLANTAS! @everyone")
                    print(f"Recordatorio enviado - Inactividad: {hours_passed:.1f} horas")
            else:
                print(f"Canal activo - Último mensaje hace {hours_passed:.1f} horas")
            break
    except Exception as e:
        print(f"Error al verificar inactividad: {e}")


@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📊 Monitoreando canal ID: {CHANNEL_ID}')
    check_inactivity.start()


@bot.event
async def on_message(message):
    # Opcional: comando para verificar estado del bot
    if message.content == '!status' and message.channel.id == CHANNEL_ID:
        await message.channel.send("✅ Bot funcionando correctamente!")
    await bot.process_commands(message)


bot.run(TOKEN)
