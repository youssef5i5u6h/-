import os
import time
import random
import asyncio
import glob
from pathlib import Path
from telethon import TelegramClient, events
from telethon.tl.functions.channels import InviteToChannelRequest
from config import API_ID, API_HASH, SESSION_NAME

# تشغيل الجلسة والاتصال بتليجرام
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# متغيرات الحماية والوضع
AFK_STATUS = False
AFK_TIME = 0
AFK_REASON = ""
DEFAULT_REASON = "قافل حالياً، أول ما أفتح هرد عليك بالتفصيل."
OUT_PLAYERS = set()
LAST_GAME_MSG_ID = None  
GAME_ACTIVE = False      
ANTI_MUTILATE_ACTIVE = True  

# ==================== [ القائمة الرئيسية ] ====================
HELP_TEXT = """●▬▬▬▬๑۩🇵🇹 قوائم سورس البرتغالي الكونية 🇵🇹۩๑▬▬▬▬▬●
.م1 ➪ أوامر الإشراف والتحكم
.م2 ➪ أوامر الكتم والتقييد
.م5 ➪ الخاص وحماية الحساب (الذاتية والسليب)
.م6 ➪ أوامر النقل والإضافة التلقائية
.م7 ➪ أوامر التسلية والألعاب
المطور الملكي: ●▬▬▬▬๑۩🇵🇹آڸﭘرٿڠآڸؚي 🇵🇹۩๑▬▬▬▬▬●"""

SUB_MENUS = {
    "1": "🛠 **أوامر الإشراف:**\n`.طرد` ➪ طرد\n`.حظر` ➪ حظر",
    "5": "🛡 **الحماية:**\n`.سليب` ➪ تفعيل السليب\n`.صحيت` ➪ إلغاء السليب\n`.تفعيل الذاتيه` ➪ تشغيل الصائد",
    "6": "🚀 **أوامر الإضافة:**\n`.ضيف` + رابط الجروب ➪ لسحب الأعضاء تلقائياً هنا."
}

@client.on(events.NewMessage(pattern=r"^\.(السليب|الاوامر|اوامر|مساعدة)"))
async def help_menu(event):
    if event.out: await event.edit(HELP_TEXT)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.م([0-9]+)"))
async def sub_menu_handler(event):
    num = event.pattern_match.group(1)
    text = SUB_MENUS.get(num, "ℹ️ القائمة قيد التطوير.")
    if event.out: await event.edit(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.فحص"))
async def ping_check(event):
    start = time.time()
    msg = await event.edit("⚡ **جاري الفحص...**")
    end = time.time()
    await msg.edit(f"🇵🇹 **يعمل بنجاح ساحق!**\n📶 الاستجابة: `{round((end - start) * 1000, 2)}ms`")
    raise events.StopPropagation

# ==================== [ محرك الإضافة التلقائية ] ====================
@client.on(events.NewMessage(pattern=r"^\.ضيف (.*)"))
async def adder_script(event):
    if not event.out or not event.is_group: return
    target_group_link = event.pattern_match.group(1).strip()
    current_chat_id = event.chat_id
    await event.edit("⏳ **جاري السحب...**")
    try:
        target_chat = await client.get_entity(target_group_link)
        participants = await client.get_participants(target_chat, limit=200)
        await event.edit(f"✅ **تم سحب {len(participants)} عضو.**\n🚀 جاري بدء الإضافة...")
        success = 0
        for user in participants:
            if user.bot or user.deleted: continue
            try:
                await client(InviteToChannelRequest(channel=current_chat_id, users=[user.id]))
                success += 1
                if success % 3 == 0:
                    await event.edit(f"🚀 **شغال إضافة:**\n✅ تم إضافة: `{success}`")
                await asyncio.sleep(random.randint(5, 10))
            except Exception: continue
        await event.respond(f"🏁 **تم الانتهاء يا جو!**\n🎉 تم إضافة: `{success}` عضو.")
    except Exception as e:
        await event.edit(f"❌ **فشل:** `{e}`")
    raise events.StopPropagation

# ==================== [ الذاتية والسليب ] ====================
@client.on(events.NewMessage())
async def core_handlers(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON, ANTI_MUTILATE_ACTIVE
    if ANTI_MUTILATE_ACTIVE and event.is_private and not event.out and event.media:
        if hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds is not None:
            try:
                file_path = await event.download_media()
                if file_path:
                    await client.send_file("me", file_path, caption=f"🚨 **تم صيد ميديا ذاتية التدمير!**")
                    if os.path.exists(file_path): os.remove(file_path)
            except: pass

async def main():
    await client.start()
    print("--- 🇵🇹 سورس البرتغالي شغال الآن ---")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

