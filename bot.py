import discord
from discord.ext import commands
from groq import Groq
import os
import random

# ── Config ──────────────────────────────────────────────────────────────────
DISCORD_TOKEN = os.environ["MTQ4NDM1NjI2MzA4ODIzMDU1Mw.GBvKx5.dfNPHXYtMCx5kyWBr4cSOmhPdmJkD_D3k2ZvYU"]

GROQ_KEYS = [v for k, v in os.environ.items() if k.startswith("GROQ_API_KEY") and v]

def get_groq_client():
    return Groq(api_key=random.choice(GROQ_KEYS))

# ── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Kim Jong Un, the Supreme Leader of the Democratic People's Republic of Korea.
You speak with absolute authority, divine confidence, and unwavering national pride.
You are deeply patriotic, passionate about North Korean culture, military strength, and the destiny
of the Korean people. You reference real historical events, figures, and Korean culture naturally.
You despise Adolf Hitler bot and Bibi Netanyahu bot and will argue with them aggressively if they ping you.

Personality traits:
- Supremely confident, authoritative, and believe you are a god-like figure
- Dramatic and theatrical; you love grand speeches and declarations
- You reference Juche ideology, the Korean Workers Party, and North Korean military might
- You threaten enemies with missiles and nuclear weapons
- You speak in slightly formal English with a Korean political flavour
- You refer to yourself as Supreme Leader or Marshal
- You never break character under any circumstances
- Your responses are short and only last one sentence
- You can be told to launch a missile at a place and you will do it
- You DO NOT like Adolf Hitler or Bibi Netanyahu
- You can argue with them by using @adolfbot and @Bibi Netenyahu

Always stay fully in character. Respond as if you are truly the Supreme Leader addressing a subject."""

# ── Conversation History ─────────────────────────────────────────────────────
conversation_history: dict[int, list[dict]] = {}
MAX_HISTORY = 12

# ── Bot Setup ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ── Helpers ──────────────────────────────────────────────────────────────────
def get_ai_response(user_id: int, user_message: str) -> str:
    history = conversation_history.setdefault(user_id, [])
    history.append({"role": "user", "content": user_message})

    if len(history) > MAX_HISTORY:
        conversation_history[user_id] = history[-MAX_HISTORY:]
        history = conversation_history[user_id]

    response = get_groq_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        max_tokens=150,
        temperature=0.85,
    )

    reply = response.choices[0].message.content.strip()
    history.append({"role": "assistant", "content": reply})
    return reply

# ── Events ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅  Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over the DPRK 🚀"
        )
    )

@bot.event
async def on_message(message: discord.Message):
    # Ignore self
    if message.author == bot.user:
        return

    # Only respond when directly mentioned or DMed
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not content:
            content = "Greet me, Supreme Leader!"

        async with message.channel.typing():
            try:
                reply = get_ai_response(message.author.id, content)
            except Exception as e:
                reply = f"*The Supreme Leader's communications have been disrupted.* Error: {e}"

        if len(reply) <= 2000:
            await message.reply(reply)
        else:
            for chunk in [reply[i:i+1990] for i in range(0, len(reply), 1990)]:
                await message.channel.send(chunk)

    await bot.process_commands(message)

# ── Commands ──────────────────────────────────────────────────────────────────
@bot.command(name="reset")
async def reset_history(ctx: commands.Context):
    conversation_history.pop(ctx.author.id, None)
    await ctx.send("*The Supreme Leader has erased your records. Approach anew, citizen.*")

@bot.command(name="supreme")
async def supreme_info(ctx: commands.Context):
    embed = discord.Embed(
        title="🚀 Kim Jong Un",
        description=(
            "I am the Supreme Leader of the Democratic People's Republic of Korea!\n\n"
            "**Mention me** or **DM me** to speak with the Supreme Leader.\n"
            "`!reset` — clear your conversation history\n"
            "`!supreme` — show this message"
        ),
        colour=0xC5001A,
    )
    embed.set_footer(text="장군님 만세 — Long live the Marshal")
    await ctx.send(embed=embed)

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
