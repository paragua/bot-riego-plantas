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

@tasks.loop(minutes=10)  # Revisa cada 10 minutos
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
                        f"### NO OLVIDEN REGAR LAS PLANTAS! @everyone")
                    print(f"Recordatorio enviado - Inactividad: {hours_passed:.1f} horas")
            else:
                print(f"Canal activo - Último mensaje hace {hours_passed:.1f} horas")
            break
    except Exception as e:
        print(f"Error al verificar inactividad: {e}")


@tasks.loop(seconds=60)
async def keep_alive():
    pass  # Mantiene el contenedor vivo

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📊 Monitoreando canal ID: {CHANNEL_ID}')
    check_inactivity.start()
    keep_alive.start()  # ← AGREGAR ESTA LÍNEA


@bot.event
async def on_message(message):
    # Opcional: comando para verificar estado del bot
    if message.content == '!status' and message.channel.id == CHANNEL_ID:
        await message.channel.send("✅ Bot funcionando correctamente!")
    await bot.process_commands(message)


bot.run(TOKEN)
