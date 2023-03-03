import discord
from discord.ext import commands
import os
import sqlite3
import random
import time

bot = commands.Bot(command_prefix=os.getenv('DISCORD_PREFIX'),intents=discord.Intents.all())
conn = sqlite3.connect('money.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS money
             (user_id TEXT PRIMARY KEY, balance INTEGER, last_daily INTEGER, cap INTEGER)''')

# The coinflip command
@bot.command()
async def flip(ctx, amount: int):
    user_id = str(ctx.author.id)
    c.execute('SELECT balance, cap FROM money WHERE user_id=?', (user_id,))
    result = c.fetchone()

    if result is None:
        balance = 0
        cap = 10000
    else:
        balance, cap = result

    if balance + amount > cap:
        await ctx.send("You have reached your money cap. Use `!upgrade_cap` command to increase your cap.")
        return

    outcome = random.choice(["heads", "tails"])
    if outcome == "heads":
        new_balance = balance + amount
        await ctx.send(f"Congratulations! You won {amount} coins! Your new balance is {new_balance} coins.")
    else:
        new_balance = balance - amount
        await ctx.send(f"Sorry, you lost {amount} coins. Your new balance is {new_balance} coins.")

    c.execute('REPLACE INTO money (user_id, balance, last_daily, cap) VALUES (?, ?, ?, ?)', (user_id, new_balance, int(time.time()), cap))
    conn.commit()

# Daily reward command
@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    c.execute('SELECT balance, last_daily, cap FROM money WHERE user_id=?', (user_id,))
    result = c.fetchone()

    if result is None:
        balance = 0
        last_daily = 0
        cap = 10000
    else:
        balance, last_daily, cap = result

    if time.time() - last_daily < 86400:
        await ctx.send("You can only claim your daily reward once every 24 hours.")
        return

    new_balance = balance + 10
    await ctx.send(f"You claimed your daily reward of 10 coins! Your new balance is {new_balance} coins.")

    c.execute('REPLACE INTO money (user_id, balance, last_daily, cap) VALUES (?, ?, ?, ?)', (user_id, new_balance, int(time.time()), cap))
    conn.commit()

@bot.command()
async def upgrade_cap(ctx):
    user_id = str(ctx.author.id)
    c.execute('SELECT cap, balance FROM money WHERE user_id=?', (user_id,))
    result = c.fetchone()

    if result is None:
        await ctx.send("You need to start playing the game to increase your cap.")
        return

    cap, balance = result

    if balance < cap * 0.8:
        await ctx.send("You need to have at least 80% of your current cap to upgrade your cap.")
        return

    new_cap = int(cap * 2.5)
    new_balance = balance - int(cap * 0.8)
    await ctx.send(f"You upgraded your money cap to {new_cap} coins by paying {int(cap * 0.8)} coins.")

    c.execute('REPLACE INTO money (user_id, balance, cap) VALUES (?, ?, ?)', (user_id, new_balance, new_cap))
    conn.commit()

bot.run(os.getenv('DISCORD_TOKEN'))