import os
import time
import random
import asyncio
import sqlite3
from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME

# تشغيل الجلسة والاتصال بتليجرام
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# متغيرات وضع السليب (AFK)
AFK_STATUS = False
AFK_TIME = 0
AFK_REASON = ""
DEFAULT_REASON = "قافل حالياً، أول ما أفتح هرد عليك بالتفصيل."

# متغيرات اللعبة وحمايتها
OUT_PLAYERS = set()
LAST_GAME_MSG_ID = None  
GAME_ACTIVE = False      

# ==================== [ القائمة الرئيسية ] ====================
HELP_TEXT = """●▬▬▬▬๑۩🇵🇹 قوائم سورس البرتغالي الكونية 🇵🇹۩๑▬▬▬▬▬●

.م1 ➪ أوامر الإشراف والتحكم
.م2 ➪ أوامر الكتم والتقييد
.م3 ➪ أوامر الكتم والحظر العام
.م4 ➪ أوامر التنظيف والتطهير
.م5 ➪ الخاص وحماية الحساب
.م6 ➪ أوامر الكول والتشغيل
.م7 ➪ أوامر التسلية والألعاب
.م8 ➪ أوامر الإذاعة والنشر
.م9 ➪ أوامر التثبيت والتأمين
.م10 ➪ أوامر الردود التلقائية
.م11 ➪ معلومات الحساب والجروب
.م12 ➪ أوامر القفل والحماية
.م13 ➪ أوامر التحكم بالبوتات
.م14 ➪ أوامر الوقت والتاريخ
.م15 ➪ أوامر تحويل الوسائط
.م16 ➪ أوامر الردود الذكية
.م17 ➪ أوامر الترجمة واللغات
.م18 ➪ أوامر السير والمذكرة
.م19 ➪ أوامر الزخرفة والخطوط
.م20 ➪ أوامر البحث والاستكشاف
.م21 ➪ أوامر البحث عن المقاطع
.م22 ➪ أوامر الإسلاميات والقرآن
.م23 ➪ أوامر الطقس والأرصاد
.م24 ➪ أوامر الحظر المؤقت (التايم آوت)
.م25 ➪ أوامر مغادرة المجموعات
.م26 ➪ أوامر الترحيب والمغادرة
.م27 ➪ أوامر كشف المودم والاتصال
.م28 ➪ أوامر كشف التعديلات (المحقق)
.م29 ➪ أوامر أسماء وتلقيب الأعضاء
.م30 ➪ رتب المطور والتحكم الكلي بالسورس

ℹ️ _اضغط على الأمر الأزرق فوق لنسخه مباشرة بدون أي أقواس._

المطور الملكي: ●▬▬▬▬๑۩🇵🇹آڸﭘرٿڠآڸؚي 🇵🇹۩๑▬▬▬▬▬●"""

SUB_MENUS = {
    "1": "🛠 **أوامر الإشراف والتحكم:**\n`.طرد` ريبلاي لطرد عضو\n`.حظر` ريبلاي لحظر عضو\n`.الغاء حظر` لفك الحظر",
    "2": "🔇 **أوامر الكتم والتقييد:**\n`.كتم` لمنع العضو من إرسال رسائل\n`.الغاء كتم` لفك كتم العضو",
    "5": "🛡 **الخاص وحماية الحساب:**\n`.سليب` تفعيل وضع النوم تلقائياً\n`.سليب + السبب` تفعيل وضع النوم مع سبب مخصص\n`.سماح` ريبلاي للسماح لشخص بالخاص",
    "7": "🎲 **أوامر التسلية والألعاب:**\n`.نسبة` لمعرفة نسبة حبك لشخص\n`.كت تويت` لعبه كت تويت ممتعة\n`.صراحة` سؤال صراحة قوي\n`.خيروك` لعبة لو خيروك\n`.بدء` لاختيار (الحاكم والمحكوم) وإقصاء الخاسر\n`.تصفير` لإنهاء وقفل اللعبة تماماً وإعادة تصفير كل شيء\n`.شارك` بعمل إعادة توجيه لرسالة القرعة فقط أثناء اللعب",
    "11": "📊 **معلومات الحساب والجروب:**\n`.ايدي` أو `.ايديات` لجلب معلومات الشات والريبلاي\n`.معلوماتي` لعرض بيانات حسابك"
}

@client.on(events.NewMessage(pattern=r"^\.(الاوامر|اوامر|مساعدة)"))
async def help_menu(event):
    if event.out:
        await event.edit(HELP_TEXT)
    else:
        await event.reply(HELP_TEXT)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.م([0-9]+)"))
async def sub_menu_handler(event):
    num = event.pattern_match.group(1)
    text = SUB_MENUS.get(num, f"ℹ️ القائمة الفرعية رقم `.م{num}` قيد التطوير والتحديث البرتغالي.")
    if event.out:
        await event.edit(text)
    else:
        await event.reply(text)
    raise events.StopPropagation

# ==================== [ محرك أمر فحص البوت ] ====================
@client.on(events.NewMessage(pattern=r"^\.فحص"))
async def ping_check(event):
    start = time.time()
    ping_text = "⚡ **جاري فحص اتصال سورس البرتغالي...**"
    msg = await event.edit(ping_text) if event.out else await event.reply(ping_text)
    end = time.time()
    ping_ms = round((end - start) * 1000, 2)
    result = f"🇵🇹 **سورس البرتغالي يعمل بنجاح (داخلي وخارجي)!**\n📶 الاستجابة: `{ping_ms}ms`"
    await msg.edit(result)
    raise events.StopPropagation

# ==================== [ محرك وضع السليب (AFK) والرد التلقائي ] ====================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سليب(?: (.*))?"))
async def set_afk(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON
    if not AFK_STATUS:
        AFK_STATUS = True
        AFK_TIME = time.time()
        reason = event.pattern_match.group(1)
        AFK_REASON = reason if reason else DEFAULT_REASON
        await event.edit(f"💤 **تم تفعيل وضع السليب بنجاح.**\n📝 الرد الحالي: `{AFK_REASON}`")
    raise events.StopPropagation

@client.on(events.NewMessage())
async def afk_handler(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON
    if event.out and AFK_STATUS and not event.text.startswith(".سليب"):
        AFK_STATUS = False
        duration = round(time.time() - AFK_TIME)
        hours, rem = divmod(duration, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f"{hours} ساعة و {minutes} دقيقة" if hours else f"{minutes} دقيقة و {seconds} ثانية"
        await event.respond(f"⚡ **أهلاً بعودتك يا جو!** تم تعطيل وضع السليب تلقائياً.\n⏳ كنت غائب لمدة: `{time_str}`")
        raise events.StopPropagation
    
    if not event.out and AFK_STATUS:
        duration = round(time.time() - AFK_TIME)
        hours, rem = divmod(duration, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f"{hours} س و {minutes} د" if hours else f"{minutes} د و {seconds} ث"
        full_reply = f"{AFK_REASON}\n\n⏳ غائب منذ: {time_str}"
        
        if event.is_private and not event.is_bot and not event.is_channel:
            await event.reply(full_reply)
            raise events.StopPropagation
        elif event.is_group:
            if event.mentioned or (event.reply_to_msg_id and (await event.get_reply_to_msg()).sender_id == (await event.client.get_me()).id):
                await event.reply(full_reply)
                raise events.StopPropagation

# ==================== [ محرك ألعاب التسلية ] ====================
@client.on(events.NewMessage(pattern=r"^\.نسبة"))
async def love_percentage(event):
    num = random.randint(0, 100)
    text = f"❤️ **النسبة العشوائية للطلب هي:** `{num}%`"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.كت تويت"))
async def cut_tweet(event):
    questions = ["إيه أكتر حاجة بتخاف تخسرها؟", "لو رجع بيك الزمن، هتختار نفس تخصصك الدراسي؟", "تفضل العزلة ولا قعدة الصحاب واللمة؟"]
    text = f"💬 **كت تويت:** {random.choice(questions)}"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

# ==================== [ نظام لعبة الحاكم والمحكوم النظيف والمحمي ] ====================
@client.on(events.NewMessage(pattern=r"^\.بدء"))
async def start_choosing(event):
    global OUT_PLAYERS, LAST_GAME_MSG_ID, GAME_ACTIVE
    if not event.is_group:
        if event.out: await event.edit("❌ هذا الأمر يعمل داخل المجموعات فقط!")
        else: await event.reply("❌ هذا الأمر يعمل داخل المجموعات فقط!")
        raise events.StopPropagation
    
    participants = await client.get_participants(event.chat_id)
    active_users = [u for u in participants if not u.bot and not u.deleted and u.id not in OUT_PLAYERS]
    
    if len(active_users) < 2:
        text = "⚠️ المتبقين في اللعبة أقل من شخصين! اكتب `.تصفير` لفتح دورة جديدة."
        if event.out: await event.edit(text)
        else: await event.reply(text)
        raise events.StopPropagation
    
    chosen_pair = random.sample(active_users, 2)
    judge = chosen_pair[0]
    victim = chosen_pair[1]
    
    OUT_PLAYERS.add(victim.id)
    GAME_ACTIVE = True  
    
    judge_mention = f"[{judge.first_name}](tg://user?id={judge.id})"
    victim_mention = f"[{victim.first_name}](tg://user?id={victim.id})"
    
    reply_msg = f"👤 **المحكوم عليه:** {victim_mention}\n"
    reply_msg += f"👨‍⚖️ **الـحـاكـم:** {judge_mention}"
    
    if event.out:
        await event.delete()
        
    sent_msg = await event.respond(reply_msg)
    LAST_GAME_MSG_ID = sent_msg.id  
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.تصفير"))
async def reset_game(event):
    global OUT_PLAYERS, LAST_GAME_MSG_ID, GAME_ACTIVE
    OUT_PLAYERS.clear()
    LAST_GAME_MSG_ID = None
    GAME_ACTIVE = False  
    text = "🔄 **تم قفل وتصفير اللعبة بنجاح!**"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

# ==================== [ محرك أمر شارك المحمي ] ====================
@client.on(events.NewMessage(pattern=r"^\.شارك"))
async def forward_handler(event):
    global LAST_GAME_MSG_ID, GAME_ACTIVE
    
    if not GAME_ACTIVE or LAST_GAME_MSG_ID is None:
        text = "❌ اللعبه قفلت خلاص!"
        if event.out: await event.edit(text)
        else: await event.reply(text)
        raise events.StopPropagation
        
    if not event.reply_to_msg_id:
        text = "⚠️ لازم ريبلاي على رسالة القرعة!"
        if event.out: await event.edit(text)
        else: await event.reply(text)
        raise events.StopPropagation
    
    if event.reply_to_msg_id != LAST_GAME_MSG_ID:
        text = "❌ غلط! لازم ريبلاي على رسالة القرعة الأخيرة بس."
        if event.out: await event.edit(text)
        else: await event.reply(text)
        raise events.StopPropagation
    
    if event.out:
        await event.delete()
        
    await client.forward_messages(event.chat_id, event.reply_to_msg_id)
    raise events.StopPropagation

# ==================== [ المحرك السحري لتشغيل السورس بشكل دائم ] ====================
async def main():
    # بدء تشغيل الحساب بأمان كامل دون انقطاع الاتصال
    await client.start()
    print("--- 🇵🇹 سورس البرتغالي شغال الآن طيران داخلي وخارجي بأمان تام ---")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # تشغيل الـ Async loop الرئيسي لحماية البوت من الموت والتوقف
    asyncio.run(main())

