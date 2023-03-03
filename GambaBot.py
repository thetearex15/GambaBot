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
             (user_id TEXT PRIMARY KEY, balance INTEGER, last_daily INTEGER)''')

# The coinflip command
@bot.command()
async def flip(ctx, amount: int):
    user_id = str(ctx.author.id)
    c.execute('SELECT balance FROM money WHERE user_id=?', (user_id,))
    result = c.fetchone()
    if result is None:
        balance = 0
    else:
        balance = result[0]

    if balance < amount:
        await ctx.send("You don't have enough money to flip that amount.")
        return

    outcome = random.choice(["heads", "tails"])
    if outcome == "heads":
        new_balance = balance + amount
        await ctx.send(f"Congratulations! You won {amount} coins! Your new balance is {new_balance} coins.")
    else:
        new_balance = balance - amount
        await ctx.send(f"Sorry, you lost {amount} coins. Your new balance is {new_balance} coins.")

    c.execute('REPLACE INTO money (user_id, balance, last_daily) VALUES (?, ?, ?)', (user_id, new_balance, int(time.time())))
    conn.commit()

@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    c.execute('SELECT balance, last_daily FROM money WHERE user_id=?', (user_id,))
    result = c.fetchone()

    if result is None:
        balance = 0
        last_daily = 0
    else:
        balance, last_daily = result

    if time.time() - last_daily < 86400:
        await ctx.send("You can only claim your daily reward once every 24 hours.")
        return

    new_balance = balance + 100
    await ctx.send(f"You claimed your daily reward of 10 coins! Your new balance is {new_balance} coins.")

    c.execute('REPLACE INTO money (user_id, balance, last_daily) VALUES (?, ?, ?)', (user_id, new_balance, int(time.time())))
    conn.commit()

bot.run(os.getenv('DISCORD_TOKEN'))