import discord
import mysql.connector
import os
import random
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_IDS = [
    1297181162099441664,  # chat-chung
    1297491136667189248,  # mods/bot
    1468490041042014447,   # checkin-tuyen-thu
    1468653551751270431  # nhibeo
]
ADMIN_ROLE_ID = 881081736006610974
CHECKIN_ROLE_ID = 1468448119153758301

# 3. Database Configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'dunghacknx123',
    'host': '127.0.0.1',
    'database': 'discord_bot_db',
    'port': 33061
}

# 4. Initialize Bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# --- FOOD LISTS FOR !NHISIEUBEO ---
SMALL_FOOD = [
    "1 bát cơm", "1 cốc trà sữa", "1 miếng gà rán", "1 cái bánh bao", 
    "1 gói bim bim", "1 cây xúc xích", "1 đĩa bánh cuốn", "1 hộp sữa chua",
    "1 cái kẹo mút", "1 cái bánh mì trứng"
]

MEDIUM_FOOD = [
    "10 bát cơm", "10 cốc trà sữa", "10 cái pizza", "5 đĩa mỳ ý", 
    "1 nồi lẩu thái", "1 set nướng BBQ", "10 cái hamburger", "1 mâm cỗ cưới",
    "5 con gà luộc", "20 cái bánh xèo"
]

BIG_FOOD = [
    "50 bát cơm", "100 cốc trà sữa", "10 gà rán nguyên con", 
    "cả cái tiệm buffet", "1 con bò Kobe nguyên tảng", "cả vựa hải sản",
    "100 cái bánh chưng", "1 tấn sầu riêng", "cả cái kho lương thực", "NGUYÊN 1 CON CẠP"
]

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    print('Bot is ready to accept messages.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check for TARGET_CHANNEL_IDS[1] if you want commands restricted to that channel
    # Or keep your logic specific to commands. 
    # Based on your previous code, commands seemed to work in ID[1].
    
    content = message.content.strip()
    content_lower = content.lower()
    cleaned_content = content.replace('\u2066', '').replace('\u2069', '').replace('\u202a', '').replace('\u202c', '')

    # ======================================================
    # COMMAND 1: !missing
    # ======================================================
    if content_lower == "!missing":
        if message.channel.id != TARGET_CHANNEL_IDS[1]: return # Restrict channel
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            sql = "SELECT full_name, ingame_name FROM game_profiles WHERE is_active = FALSE"
            cursor.execute(sql)
            rows = cursor.fetchall()

            if not rows:
                await message.channel.send("🎉 **Tất cả tuyển thủ đã checkin**")
            else:
                missing_names = [f"- {row[0]} ({row[1]})" for row in rows]
                count = len(missing_names)
                header = f"**Missing Players ({count}):**\n"
                current_message = header
                for name in missing_names:
                    if len(current_message) + len(name) + 1 >= 2000:
                        await message.channel.send(current_message)
                        current_message = name + "\n"
                    else:
                        current_message += name + "\n"
                if current_message:
                    await message.channel.send(current_message)

        except mysql.connector.Error as err:
            await message.channel.send(f"❌ Database error: {err}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
        return

    # ======================================================
    # COMMAND 2: !reset
    # ======================================================
    if content_lower == "!reset":
        if message.channel.id != TARGET_CHANNEL_IDS[1]: return # Restrict channel
        user_has_role = any(role.id == ADMIN_ROLE_ID for role in message.author.roles)
        if not user_has_role:
            return
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            sql = "UPDATE game_profiles SET is_active = FALSE"
            cursor.execute(sql)
            connection.commit()
            await message.channel.send(f"🔄 **RESET** Tất cả người chơi đã quay về trạng thái chưa checkin.")
        except mysql.connector.Error as err:
            await message.channel.send(f"❌ Database error: {err}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
        return
    
    # ======================================================
    # COMMAND 3: !nhibeo
    # Increases weight by 1kg (From Database)
    # ======================================================
    if content_lower == "!nhibeo":
        if message.channel.id != TARGET_CHANNEL_IDS[3]: return # Restrict channel
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # 1. Update weight + 1
            update_sql = "UPDATE nhibeo SET nhibeo_weight = nhibeo_weight + 1 WHERE id = 1"
            cursor.execute(update_sql)
            connection.commit()

            # 2. Get new weight
            select_sql = "SELECT nhibeo_weight FROM nhibeo WHERE id = 1"
            cursor.execute(select_sql)
            result = cursor.fetchone()
            
            if result:
                new_weight = result[0]
                await message.channel.send(f"Số cân nặng hiện tại của Nhi: **{new_weight}kg**")

        except mysql.connector.Error as err:
            await message.channel.send(f"❌ Database error: {err}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
        return

    # ======================================================
    # COMMAND 4: !nhisieubeo (NEW)
    # Adds random weight 0-100 with weighted probability
    # ======================================================
    if content_lower == "!nhisieubeo":
        if message.channel.id != TARGET_CHANNEL_IDS[3]: return # Restrict channel
        # 1. Logic to pick random number with rarity
        # We roll a dice from 0 to 100 to determine "Luck Tier"
        chance = random.randint(0, 100)

        # 60% chance for Small (0-32)
        # 35% chance for Medium (33-67)
        # 5% chance for Big (68-100) - Very rare!
        
        added_weight = 0
        food_item = ""

        if chance <= 60:
            # SMALL TIER
            added_weight = random.randint(1, 32)
            food_item = random.choice(SMALL_FOOD)
            template = "Linh Nhi đã ăn **{food}** và tăng **{n}** cân! Số cân hiện tại của Linh Nhi: **{total}kg**"
        elif chance <= 95:
            # MEDIUM TIER
            added_weight = random.randint(33, 67)
            food_item = random.choice(MEDIUM_FOOD)
            template = "Khá béo! Linh Nhi đã húp trọn **{food}** và tăng **{n}** cân! Số cân hiện tại của Linh Nhi: **{total}kg**"
        else:
            # BIG TIER (Jackpot)
            added_weight = random.randint(68, 100)
            food_item = random.choice(BIG_FOOD)
            if food_item == "NGUYÊN 1 CON CẠP":
                template = "🚨 **NỔ HŨ THẾ GIỚI**! Linh Nhi đã chén sạch **{food}** và tăng **{n}** cân! Số cân hiện tại của Linh Nhi: **{total}kg**"
            else:
                template = "🚨 **NỔ HŨ**! Linh Nhi đã chén sạch **{food}** và tăng **{n}** cân! Số cân hiện tại của Linh Nhi: **{total}kg**"

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Update DB
            update_sql = "UPDATE nhibeo SET nhibeo_weight = nhibeo_weight + %s WHERE id = 1"
            cursor.execute(update_sql, (added_weight,))
            connection.commit()

            # Get new total
            select_sql = "SELECT nhibeo_weight FROM nhibeo WHERE id = 1"
            cursor.execute(select_sql)
            result = cursor.fetchone()
            
            if result:
                total_weight = result[0]
                final_msg = template.format(food=food_item, n=added_weight, total=total_weight)
                await message.channel.send(final_msg)

        except mysql.connector.Error as err:
            await message.channel.send(f"❌ Database error: {err}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
        return

    # ======================================================
    # DEFAULT: CHECK USER IN
    # ======================================================
    if message.channel.id == TARGET_CHANNEL_IDS[2]:
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            check_sql = "SELECT full_name, is_active FROM game_profiles WHERE ingame_name = %s"
            cursor.execute(check_sql, (cleaned_content,))
            result = cursor.fetchone()

            if result:
                real_name = result[0]
                is_already_active = result[1]

                if is_already_active:
                     await message.add_reaction("🔁")
                else:
                    update_sql = "UPDATE game_profiles SET is_active = TRUE WHERE ingame_name = %s"
                    cursor.execute(update_sql, (cleaned_content,))
                    connection.commit()
                    
                    role = message.guild.get_role(CHECKIN_ROLE_ID)
                    if role:
                        try:
                            await message.author.add_roles(role)
                        except discord.Forbidden:
                            print("⚠️ Error: Bot cannot add role.")
                    
                    try:
                        await message.author.edit(nick=cleaned_content)
                    except Exception as e:
                        print(f"⚠️ Nickname error: {e}")

                    dm_content = (
                        "Chào mừng bạn đến với giải đấu NEC TFT CUP: CHRONICLES OF TACTIC!\n"
                        "Hãy vào group Zalo tuyển thủ để nhận những thông báo mới nhất: zalo.me"
                    )
                    try:
                        await message.author.send(dm_content)
                    except discord.Forbidden:
                        pass

                    await message.channel.send(f"✅ Checkin thành công: Chào mừng **{real_name}** ({cleaned_content}) đến với giải đấu NEC TFT CUP: CHRONICLES OF TACTIC!")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

client.run(TOKEN)