import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Running.")
    print(bot.application_commands)
    await bot.change_presence(activity=discord.Game("Bonk.io ᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼ Use /tutorial para um tutorial de como usar os comandos do bot de Bonk.io"), status=discord.Status.do_not_disturb)

bot.load_extension("cogs.base")
bot.load_extension("cogs.bonk")

bot.run(os.getenv('DISCORD_TOKEN'))

print(bot.all_commands)