import os
import time
import random
import asyncio
import glob
from pathlib import Path
from telethon import TelegramClient, events
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
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

# متغيرات حماية الذاتية
ANTI_MUTILATE_ACTIVE = True  

# ==================== [ القائمة الرئيسية باسم .الاوامر ] ====================
HELP_TEXT = """●▬▬▬▬๑۩🇵🇹 قوائم سورس البرتغالي الكونية 🇵🇹۩๑▬▬▬▬▬●

.م1 ➪ أوامر الإشراف والتحكم
.م2 ➪ أوامر الكتم والتقييد
.م3 ➪ أوامر الكتم والحظر العام
.م4 ➪ أوامر التنظيف والتطهير
.م5 ➪ الخاص وحماية الحساب (الذاتية والسليب)
.م6 ➪ أوامر النقل والإضافة التلقائية
.م7 ➪ أوامر التسلية والألعاب
.م10 ➪ أوامر الردود التلقائية
.م11 ➪ معلومات الحساب والجروب

ℹ️ _اضغط على الأمر الأزرق فوق لنسخه مباشرة بدون أي أقواس._

المطور الملكي: ●▬▬▬▬๑۩🇵🇹آڸﭘرٿڠآڸؚي 🇵🇹۩๑▬▬▬▬▬●"""

SUB_MENUS = {
    "1": "🛠 **أوامر الإشراف والتحكم:**\n`.طرد` ➪ ريبلاي لطرد عضو\n`.حظر` ➪ ريبلاي لحظر عضو\n`.الغاء حظر` ➪ لفك الحظر عن العضو",
    "2": "🔇 **أوامر الكتم والتقييد:**\n`.كتم` ➪ لمنع العضو من إرسال رسائل\n`.الغاء كتم` ➪ لفك كتم العضو في الشات",
    "3": "🌍 **أوامر الحظر العام:**\n`.عام` ➪ حظر العضو من كل الجروبات اللي أنت فيها\n`.الغاء عام` ➪ فك الحظر العام",
    "4": "🧹 **أوامر التنظيف والتطهير:**\n`.مسح` + العدد ➪ لحذف الرسائل من الشات بسرعة",
    "5": "🛡 **الخاص وحماية الحساب:**\n`.سليب` ➪ تفعيل وضع النوم تلقائياً\n`.سليب` + السبب ➪ تفعيل وضع النوم مع سبب مخصص\n`.صحيت` ➪ لتعطيل وضع النوم مانيوال\n`.تفعيل الذاتيه` ➪ لتشغيل صائد ميديا التدمير الذاتي (إلى المحفوظات)\n`.تعطيل الذاتيه` ➪ لإيقاف صائد ميديا التدمير الذاتي",
    "6": "🚀 **أوامر النقل والإضافة التلقائية:**\n`.ضيف` + رابط الجروب ➪ لسحب أعضاء الجروب التاني وإضافتهم هنا تلقائياً.\n💡 مثال: `.ضيف https://t.me/target_group`",
    "7": "🎲 **أوامر التسلية والألعاب:**\n`.نسبة` ➪ لمعرفة نسبة حبك أو تفاعلك مع شخص\n`.كت تويت` ➪ لعبه كت تويت ممتعة\n`.صراحة` ➪ سؤال صراحة قوي\n`.خيروك` ➪ لعبة لو خيروك الكونية\n`.بدء` ➪ لاختيار (الحاكم والمحكوم) وإقصاء الخاسر\n`.تصفير` ➪ لإنهاء وقفل اللعبة تماماً وإعادة تصفير كل شيء\n`.شارك` ➪ بعمل إعادة توجيه لرسالة القرعة فقط أثناء اللعب",
    "10": "🤖 **أوامر الردود التلقائية:**\n`.اضف رد` + الكلمة | الرد ➪ لصنع رد مخصص تلقائي",
    "11": "📊 **معلومات الحساب والجروب:**\n`.ايدي` أو `.ايديات` ➪ لجلب معلومات الشات والريبلاي والـ ID\n`.معلوماتي` ➪ لعرض بيانات حسابك وهيبتك في السورس",
}

@client.on(events.NewMessage(pattern=r"^\.(السليب|الاوامر|اوامر|مساعدة)"))
async def help_menu(event):
    if event.out: await event.edit(HELP_TEXT)
    else: await event.reply(HELP_TEXT)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.م([0-9]+)"))
async def sub_menu_handler(event):
    num = event.pattern_match.group(1)
    text = SUB_MENUS.get(num, f"ℹ️ القائمة الفرعية رقم `.م{num}` قيد التطوير وجاهزة للاستخدام في التحديث البرتغالي.")
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.فحص"))
async def ping_check(event):
    start = time.time()
    ping_text = "⚡ **جاري فحص اتصال سورس البرتغالي الكوني...**"
    msg = await event.edit(ping_text) if event.out else await event.reply(ping_text)
    end = time.time()
    ping_ms = round((end - start) * 1000, 2)
    result = f"🇵🇹 **سورس البرتغالي يعمل بنجاح ساحق!**\n📶 سرعة الاستجابة الحالية: `{ping_ms}ms`"
    await msg.edit(result)
    raise events.StopPropagation

# ==================== [ محرك النقل والإضافة التلقائية المسمار ] ====================
@client.on(events.NewMessage(pattern=r"^\.ضيف (.*)"))
async def adder_script(event):
    if not event.out: return  # لضمان إنك أنت بس اللي تتحكم بالأمر
    if not event.is_group:
        await event.edit("❌ الأمر ده شغال جوة الجروب اللي عايز تضيف فيه الناس بس!")
        return

    target_group_link = event.pattern_match.group(1).strip()
    current_chat_id = event.chat_id
    
    await event.edit("⏳ **جاري فحص الجروب المستهدف وسحب الأعضاء...**")
    
    try:
        # الحصول على كيان الجروب المستهدف
        target_chat = await client.get_entity(target_group_link)
        # سحب الأعضاء (المتفاعلين مؤخراً عشان الحسابات الميتة متقفلش الإضافة)
        participants = await client.get_participants(target_chat, limit=200)
        
        await event.edit(f"✅ **تم سحب {len(participants)} عضو بنجاح.**\n🚀 جاري بدء الإضافة التلقائية مع تفعيل نظام الحماية...")
        
        success_count = 0
        fail_count = 0
        
        for user in participants:
            if user.bot or user.deleted:
                continue
            try:
                # محاولة إضافة العضو للجروب الحالي
                await client(InviteToChannelRequest(channel=current_chat_id, users=[user.id]))
                success_count += 1
                # تحديث الرسالة كل 3 إضافات عشان النسبة تظهر قدامك
                if success_count % 3 == 0:
                    await event.edit(f"🚀 **شغال إضافة تلقائية الحين:**\n✅ تم إضافة: `{success_count}`\n❌ فشل/خصوصية: `{fail_count}`")
                
                # وقت عشوائي بين الإضافات لحماية حسابك من حظر التليجرام الفجائي
                await asyncio.sleep(random.randint(5, 10))
                
            except Exception:
                fail_count += 1
                continue
                
        await event.respond(f"🏁 **تم انتهاء عملية النقل بنجاح يا جو!**\n🎉 تم إضافة: `{success_count}` عضو جديد.\n🔒 حسابات خصوصيتها مغلقة/مرفوضة: `{fail_count}`")
        
    except Exception as e:
        await event.edit(f"❌ **فشل النقل!** تأكد من الرابط أو إن حسابك أدمن في الجروب الحالي.\nالسبب: `{e}`")
    raise events.StopPropagation

# ==================== [ محرك التحكم في صائد الذاتية ] ====================
@client.on(events.NewMessage(pattern=r"^\.تفعيل الذاتي[هة]$"))
async def enable_anti_ttl(event):
    global ANTI_MUTILATE_ACTIVE
    ANTI_MUTILATE_ACTIVE = True
    text = "📸 ✅ **تم تفعيل صائد الميديا ذاتية التدمير بنجاح!** أي صورة أو فيديو بمؤقت هيتحفظ في الرسائل المحفوظة فوراً."
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.تعطيل الذاتي[هة]$"))
async def disable_anti_ttl(event):
    global ANTI_MUTILATE_ACTIVE
    ANTI_MUTILATE_ACTIVE = False
    text = "📸 ❌ **تم تعطيل صائد الميديا ذاتية التدمير.**"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

# ==================== [ محرك صائد الميديا وتخزين السليب تلقائياً ] ====================
@client.on(events.NewMessage())
async def core_anti_destruct_and_afk(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON, ANTI_MUTILATE_ACTIVE
    
    if ANTI_MUTILATE_ACTIVE and event.is_private and not event.out and event.media:
        is_ttl = hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds is not None
        if is_ttl:
            try:
                file_path = await event.download_media()
                if file_path:
                    sender = await event.get_sender()
                    sender_name = sender.first_name if sender else "مجهول"
                    caption = f"🚨 **تم صيد ميديا ذاتية التدمير!**\n👤 من: [{sender_name}](tg://user?id={sender.id})\n⏰ مؤقت التدمير: `{event.media.ttl_seconds} ثانية`"
                    await client.send_file("me", file_path, caption=caption)
                    if os.path.exists(file_path): os.remove(file_path)
            except Exception as e:
                print(f"❌ فشل صيد الميديا: {e}")

    if event.out and AFK_STATUS and not event.text.startswith(".سليب"):
        AFK_STATUS = False
        duration = round(time.time() - AFK_TIME)
        hours, rem = divmod(duration, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f"{hours} ساعة و {minutes} دقيقة" if hours else f"{minutes} دقيقة و {seconds} ثانية"
        await event.respond(f"⚡ **أهلاً بعودتك يا جو!** تم تعطيل وضع السليب تلقائياً.\n⏳ غيبتك كانت مدتها: `{time_str}`")
        raise events.StopPropagation
    
    if not event.out and AFK_STATUS:
        if event.is_private and not event.is_bot:
            duration = round(time.time() - AFK_TIME)
            hours, rem = divmod(duration, 3600)
            minutes, seconds = divmod(rem, 60)
            time_str = f"{hours} س و {minutes} د" if hours else f"{minutes} د و {seconds} ث"
            await event.reply(f"{AFK_REASON}\n\n⏳ غائب منذ: {time_str}")
            raise events.StopPropagation
        elif event.is_group and event.mentioned:
            duration = round(time.time() - AFK_TIME)
            hours, rem = divmod(duration, 3600)
            minutes, seconds = divmod(rem, 60)
            time_str = f"{hours} س و {minutes} د" if hours else f"{minutes} د و {seconds} ث"
            await event.reply(f"{AFK_REASON}\n\n⏳ غائب منذ: {time_str}")
            raise events.StopPropagation

# ==================== [ أوامر وضع السليب ] ====================
@client.on(events.NewMessage(pattern=r"^\.سليب($| (.*))"))
async def set_afk(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON
    if not AFK_STATUS:
        AFK_STATUS = True
        AFK_TIME = time.time()
        reason = event.pattern_match.group(2)
        AFK_REASON = reason if reason else DEFAULT_REASON
        text = f"💤 **تم تفعيل وضع النوم (السليب) بنجاح.**\n📝 ردك الحالي على الخاص: `{AFK_REASON}`"
        if event.out: await event.edit(text)
        else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.(صحيت|الغاء السليب|الغاء سليب)$"))
async def disable_afk_command(event):
    global AFK_STATUS
    if AFK_STATUS:
        AFK_STATUS = False
        text = "⚡ **تم إلغاء وضع السليب، منور الدنيا وجاهز للرد!**"
        if event.out: await event.edit(text)
        else: await event.reply(text)
    raise events.StopPropagation

# ==================== [ محرك ألعاب التسلية المطور ] ====================
@client.on(events.NewMessage(pattern=r"^\.نسبة"))
async def love_percentage(event):
    num = random.randint(0, 100)
    text = f"❤️ **النسبة العشوائية للطلب هي:** `{num}%`"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.كت تويت"))
async def cut_tweet(event):
    questions = ["إيه أكتر حاجة بتخاف تخسرها في حياتك؟", "لو رجع بيك الزمن، هتختار نفس تخصصك الحالي ولا هتغيره؟", "تفضل العزلة والهدوء، ولا قعدة الصحاب واللمة؟"]
    text = f"💬 **كت تويت برتغالي:** {random.choice(questions)}"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.صراحة"))
async def saraha_cmd(event):
    questions = ["هل ندمت على معرفة شخص هنا؟", "آخر رسالة جاتلك فرحتك من مين؟", "إيه صفتك السيئة اللي حابب تغيرها؟"]
    text = f"👁‍🗨 **سؤال صراحة:** {random.choice(questions)}"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.خيروك"))
async def khayrouk_cmd(event):
    options = ["تخسر موبايلك لمدة شهر ولا تقعد من غير نت أسبوع؟", "تكون مشهور ومكروه ولا عادي ومحبوب؟"]
    text = f"🤔 **لو خيروك:** {random.choice(options)}"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

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
        text = "⚠️ المتبقين في اللعبة أقل من شخصين! اكتب `.تصفير` لبدء دورة جديدة ونضيفة."
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
    
    reply_msg = f"👤 **المحكوم عليه برة اللعبة:** {victim_mention}\n👨‍⚖️ **الـحـاكـم الملكي:** {judge_mention}"
    
    if event.out: await event.delete()
    sent_msg = await event.respond(reply_msg)
    LAST_GAME_MSG_ID = sent_msg.id  
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.تصفير"))
async def reset_game(event):
    global OUT_PLAYERS, LAST_GAME_MSG_ID, GAME_ACTIVE
    OUT_PLAYERS.clear()
    LAST_GAME_MSG_ID = None
    GAME_ACTIVE = False  
    text = "🔄 **تم قفل وتصفير اللعبة بنجاح! جاهزين لدورة جديدة.**"
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.شارك"))
async def forward_handler(event):
    global LAST_GAME_MSG_ID, GAME_ACTIVE
    if not GAME_ACTIVE or LAST_GAME_MSG_ID is None:
        text = "❌ اللعبه منتهية أو مقفولة حالياً!"
        if event.out: await event.edit(text)
        else: await event.reply(text)
        raise events.StopPropagation
    if not event.reply_to_msg_id or event.reply_to_msg_id != LAST_GAME_MSG_ID:
        text = "⚠️ غلط! لازم تعمل ريبلاي على رسالة القرعة الأخيرة بالظبط."
        if event.out: await event.edit(text)
        else: await event.reply(text)
        raise events.StopPropagation
    if event.out: await event.delete()
    await client.forward_messages(event.chat_id, event.reply_to_msg_id)
    raise events.StopPropagation

def load_plugins():
    possible_folders = ["plugins", "modules", "commands"]
    for folder in possible_folders:
        if os.path.exists(folder):
            for f in glob.glob(f"{folder}/*.py"):
                name = Path(f).stem
                if not name.startswith("__"):
                    try: __import__(f"{folder}.{name}")
                    except Exception: pass

async def main():
    await client.start()
    load_plugins()
    print("--- 🇵🇹 سورس البرتغالي شغال بكامل الأوامر الكونية + سحب الأعضاء ---")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

