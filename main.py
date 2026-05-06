import os
import time
import random
import asyncio
import sqlite3
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest, GetBlockedRequest
from telethon.tl.functions.phone import CreateGroupCallRequest, DiscardGroupCallRequest, GetGroupCallRequest
from config import API_ID, API_HASH, SESSION_NAME

try:
    conn = sqlite3.connect(f"{SESSION_NAME}.session", timeout=20)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.close()
except:
    pass

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# قاعدة البيانات الشاملة
global_muted_users = {}
private_muted_users = {}
pm_protection_enabled = True
approved_pm_users = set()    
pm_warnings = {}             

# === [ 1. القائمة الخارجية النظيفة والقابلة للنسخ الصافي ] ===
@client.on(events.NewMessage(pattern=r"^\.(الاوامر|اوامري|مساعد)$"))
async def help_menu(event):
    help_text = (
        "**●▬▬▬▬๑۩🇵🇹 قوائم سورس البرتغالي الكونية 🇵🇹۩๑▬▬▬▬▬●**\n\n"
        "`.م1` ➪ أوامر الإشراف والتحكم\n"
        "`.م2` ➪ أوامر الكتم والتقييد\n"
        "`.م3` ➪ أوامر الكتم والحظر العام\n"
        "`.م4` ➪ أوامر التنظيف والتطهير\n"
        "`.م5` ➪ الخاص وحماية الحساب\n"
        "`.م6` ➪ أوامر الكول والتشغيل\n"
        "`.م7` ➪ أوامر التسلية والألعاب\n"
        "`.م8` ➪ أوامر الإذاعة والنشر\n"
        "`.م9` ➪ أوامر التثبيت والتأمين\n"
        "`.م10` ➪ أوامر الردود التلقائية\n"
        "`.م11` ➪ معلومات الحساب والجروب\n"
        "`.م12` ➪ أوامر القفل والحماية\n"
        "`.م13` ➪ أوامر التحكم بالبوتات\n"
        "`.م14` ➪ أوامر الوقت والتاريخ\n"
        "`.م15` ➪ أوامر تحويل الوسائط\n"
        "`.م16` ➪ أوامر الردود الذكية\n"
        "`.م17` ➪ أوامر الترجمة واللغات\n"
        "`.م18` ➪ أوامر السير والمذكرة\n"
        "`.م19` ➪ أوامر الزخرفة والخطوط\n"
        "`.م20` ➪ أوامر البحث والاستكشاف\n"
        "`.م21` ➪ أوامر البحث عن المقاطع\n"
        "`.م22` ➪ أوامر الإسلاميات والقرآن\n"
        "`.م23` ➪ أوامر الطقس والأرصاد\n"
        "`.م24` ➪ أوامر الحظر المؤقت (التايم آوت)\n"
        "`.م25` ➪ أوامر مغادرة المجموعات\n"
        "`.م26` ➪ أوامر الترحيب والمغادرة\n"
        "`.م27` ➪ أوامر كشف المودم والاتصال\n"
        "`.م28` ➪ أوامر كشف التعديلات (المحقق)\n"
        "`.م29` ➪ أوامر أسماء وتلقيب الأعضاء\n"
        "`.م30` ➪ رتب المطور والتحكم الكلي بالسورس\n\n"
        "ℹ️ _اضغط على الأمر الأزرق فوق لنسخه مباشرة بدون أي أقواس._\n\n"
        "**المطور الملكي:** ●▬▬▬▬๑۩🇵🇹آڸﭘرٿڠآڸؚي 🇵🇹۩๑▬▬▬▬▬●"
    )
    await event.reply(help_text)

# === [ 2. تشغيل ومعالجة الـ 30 قائمة الداخلية بالنسخ الصافي ] ===
@client.on(events.NewMessage(pattern=r"^\.م([1-9]|[12]\d|30)$"))
async def sub_menus(event):
    num = event.pattern_match.group(1)
    
    menus = {
        "1": "**⚙️ م1 - أوامر الإشراف والتحكم:**\n• `.طرد` ➪ طرد العضو بالرد\n• `.حظر` ➪ حظر العضو\n• `.الغاء حظر` ➪ فك الحظر",
        "2": "**🤫 م2 - أوامر الكتم والتقييد:**\n• `.كتم` ➪ كتم العضو في الجروب\n• `.الغاء كتم` ➪ فك كتم العضو\n• `.تقييد` ➪ تقييد الصلاحيات",
        "3": "**🛡️ م3 - أوامر الكتم والحظر العام:**\n• `.كتم عام` ➪ كتم في كل مكان\n• `.حظر عام` ➪ حظر كلي\n• `.الغاء كتم عام` ➪ فك الكتم العام",
        "4": "**🧹 م4 - أوامر التنظيف والتطهير:**\n• `.مسح المكتومين عام` ➪ تصفير الكتم\n• `.مسح المحظورين عام` ➪ فك بلوك الكل\n• `.حذف المحذوفين` ➪ طرد الحسابات المحذوفة",
        "5": "**💌 م5 - الخاص وحماية الحساب:**\n• `.تفعيل الخاص` ➪ تشغيل الـ 7 تحذيرات\n• `.تعطيل الخاص` ➪ إيقاف حماية الخاص\n• `.قبول` ➪ الموافقة بالرد\n• `.رفض` ➪ الرفض بالرد\n• `.pmute` / `.punmute` ➪ كتم وفك كتم الخاص",
        "6": "**🎙️ م6 - أوامر الكول والتشغيل:**\n• `.افتح الكول` ➪ فتح مكالمة الجروب\n• `.اقفل الكول` ➪ إنهاء المكالمة\n• `.تشغيل` ➪ رفع وتشغيل أغنية بالاسم",
        "7": "**🎮 م7 - أوامر التسلية والألعاب:**\n• `.تفعيل الالعاب` ➪ فتح قائمة العقوبات\n• `.العاب` ➪ تشغيل الألعاب العشوائية\n• `.عقوبة` ➪ اختيار عقوبة عشوائية للمخسر",
        "8": "**📢 م8 - أوامر الإذاعة والنشر:**\n• `.اذاعة للجروبات` ➪ نشر رسالة بالرد للجروبات\n• `.اذاعة خاص` ➪ نشر لكل الخاص\n• `.توجيه عام` ➪ عمل فوروارد لجميع المحادثات",
        "9": "**📌 م9 - أوامر التثبيت والتأمين:**\n• `.تثبيت` ➪ تثبيت الرسالة بالرد\n• `.الغاء التثبيت` ➪ فك التثبيت\n• `.تثبيت بالاشعار` ➪ تثبيت مع إرسال إشعار",
        "10": "**📝 م10 - أوامر الردود التلقائية:**\n• `.اضف رد` ➪ إضافة رد مخصص جديد\n• `.حذف رد` ➪ إزالة رد معين\n• `.الردود` ➪ عرض الردود المضافة",
        "11": "**📊 م11 - معلومات الحساب والجروب:**\n• `.ايدى` ➪ عرض الآيدي والمعلومات الشخصية\n• `.معلومات الجروب` ➪ تفاصيل المجموعه والعدد\n• `.رابط المحادثه` ➪ جلب رابط الجروب",
        "12": "**🔒 م12 - أوامر القفل والحماية:**\n• `.قفل الصور` / `.فتح الصور`\n• `.قفل الروابط` / `.فتح الروابط`\n• `.قفل التوجيه` / `.فتح التوجيه`",
        "13": "**🤖 م13 - أوامر التحكم بالبوتات:**\n• `.قفل البوتات` ➪ طرد أي بوت يدخل\n• `.فتح البوتات` ➪ السماح بدخول البوتات",
        "14": "**⏱️ م14 - الوقت والتاريخ:**\n• `.الوقت` ➪ عرض الوقت الحالي بدقة\n• `.التاريخ` ➪ عرض التاريخ اليومي",
        "15": "**🔄 م15 - تحويل الوسائط:**\n• `.ملصق` ➪ تحويل الصورة لملصق\n• `.بصمة` ➪ تحويل الملف الصوتي لبصمة صوتية",
        "16": "**🔮 م16 - الردود الذكية:**\n• `.تفعيل الذكاء` ➪ تفعيل الرد الذكي الآلي\n• `.تعطيل الذكاء` ➪ إيقاف الرد الآلي",
        "17": "**🌍 م17 - الترجمة واللغات:**\n• `.ترجم` ➪ ترجمة فورية للغة العربية\n• `.ترجم للانجليزي` ➪ الترجمة للإنجليزية",
        "18": "**👤 م18 - السير والمذكرة:**\n• `.المذكرة` ➪ عرض مذكرتك المكتوبة\n• `.احفظ` ➪ حفظ نص داخل المذكرة",
        "19": "**❄️ م19 - الزخرفة والخطوط:**\n• `.زخرف` ➪ زخرفة فورية عربي وإنقليزي",
        "20": "**🔎 م20 - البحث والاستكشاف:**\n• `.بحث` ➪ بحث سريع في الويب عبر السورس",
        "21": "**🎵 م21 - البحث عن المقاطع:**\n• `.صوت` ➪ جلب ملف صوتي مخصص\n• `.فيديو` ➪ جلب كليب من اليوتيوب",
        "22": "**🕋 م22 - الإسلاميات والقرآن:**\n• `.قرآن` ➪ عرض سورة أو آية عشوائية\n• `.اذكار` ➪ عرض أذكار الصباح والمساء",
        "23": "**🌦️ م23 - أوامر الطقس:**\n• `.الطقس` ➪ عرض درجات الحرارة والطقس اليومي",
        "24": "**⏳ م24 - الحظر المؤقت والتايم آوت:**\n• `.تايم_اوت` ➪ حظر العضو لفترة محددة بالدقائق",
        "25": "**🚪 م25 - مغادرة المجموعات:**\n• `.غادر` ➪ خروج السورس من المجموعة\n• `.تنظيف الجروبات` ➪ الخروج من الجروبات الميتة",
        "26": "**👋 م26 - الترحيب والمغادرة:**\n• `.تفعيل الترحيب` ➪ تشغيل ترحيب الأعضاء الجدد\n• `.تعطيل الترحيب` ➪ قفل الترحيب",
        "27": "**📶 م27 - كشف المودم والاتصال:**\n• `.بينج` ➪ فحص سرعة استجابة السورس\n• `.كشف` ➪ معرفة الرسالة الأصلية قبل التعديل بالرد",
        "29": "**🏷️ م29 - أسماء وتلقيب الأعضاء:**\n• `.لقب` ➪ إعطاء لقب مخصص للعضو بالرد عليه",
        "30": "**👑 م30 - رتب المطور والتحكم الكلي:**\n• `.تحديث` ➪ جلب آخر تحديثات سورس البرتغالي\n• `.إعادة تشغيل` ➪ ريستارت كامل وتنشيط للتيرمكس"
    }

    text = menus.get(num, "❌ هذه القائمة غير مدرجة بالسورس.")
    await event.reply(f"**●▬▬▬▬๑۩🇵🇹 سورس البرتغالي 🇵🇹۩๑▬▬▬▬▬●**\n\n{text}\n\nℹ️ _اضغط على أي أمر فوق لنسخه بلمسة واحدة!_")

# === [ 3. أوامر فتح وقفل الكول الرسمية ] ===
@client.on(events.NewMessage(pattern=r"^\.(افتح الكول|اقفل الكول)(?:\s+(.+))?$"))
async def voice_chat_native_controls(event):
    if not event.is_group: return await event.reply("❌ هذه الأوامر تعمل داخل المجموعات فقط!")
    cmd = event.pattern_match.group(1)
    
    if cmd == "افتح الكول":
        msg = await event.reply("⚙️ **جاري فتح وتشغيل مكالمة الجروب الصوتية من السيرفر...**")
        try:
            await client(CreateGroupCallRequest(peer=event.chat_id))
            await msg.edit("🎙️ **تم فتح وتشغيل المحادثة الصوتية في الجروب بنجاح يا برتغالي!**")
        except:
            await msg.edit("❌ فشل فتح الكول، تأكد أن حسابك 'مشرف' وله صلاحية إدارة المحادثات الصوتية!")

    elif cmd == "اقفل الكول":
        msg = await event.reply("⚙️ **جاري محاولة إنهاء وإغلاق الكول...**")
        try:
            full_chat = await client.get_peer_input_entity(event.chat_id)
            await client(DiscardGroupCallRequest(call=await client(GetGroupCallRequest(peer=full_chat))))
            await msg.edit("🛑 **تم إنهاء وإغلاق المحادثة الصوتية للجروب بالكامل بنجاح.**")
        except:
            await msg.edit("❌ لم أتمكن من إغلاق الكول، إما الكول مقفول بالفعل أو حسابك مش أدمن.")

# === [ 4. أمر تشغيل وتحميل الأغاني ] ===
@client.on(events.NewMessage(pattern=r"^\.تشغيل (.+)$"))
async def play_and_send_song(event):
    song_name = event.pattern_match.group(1)
    msg = await event.reply(f"⏳ **جاري البحث عن `{song_name}` وتحميلها بأعلى جودة...**")
    
    audio_file = f"{song_name}.mp3"
    try:
        os.system(f'yt-dlp "ytsearch:{song_name}" -x --audio-format mp3 -o "{audio_file}" --max-filesize 15m')
        if not os.path.exists(audio_file):
            return await msg.edit("❌ لم أتمكن من العثور على الأغنية، جرب اسماً آخر.")
            
        await msg.edit("⚡ **جاري رفع الملف الصوتي وتأمين تشغيله في الجروب...**")
        await client.send_file(event.chat_id, audio_file, caption=f"🎵 **تم تشغيل وتحميل:** `{song_name}`\n🔥 تم الطلب بواسطة سورس البرتغالي الكوني.")
        await msg.delete()
        if os.path.exists(audio_file): os.remove(audio_file)
    except Exception as e:
        await msg.edit(f"❌ حدث خطأ أثناء التحميل: {str(e)}")

# === [ 5. أوامر الحماية والكتم الشامل ] ===
@client.on(events.NewMessage(pattern=r"^\.(تفعيل الخاص|تعطيل الخاص|مسح المكتومين عام|مسح المحظورين عام|كتم عام|mute|الغاء كتم عام|unmute|حظر عام|ban)(?:\s+(.+))?$"))
async def global_and_pm_commands(event):
    global pm_protection_enabled
    cmd = event.pattern_match.group(1)
    
    if cmd == "تفعيل الخاص":
        pm_protection_enabled = True
        return await event.reply("🛡️ **تم تفعيل حماية الخاص والـ 7 تحذيرات بنجاح!**")
    elif cmd == "تعطيل الخاص":
        pm_protection_enabled = False
        return await event.reply("🔓 **تم تعطيل حماية الخاص والحساب مفتوح للجميع.**")
    elif cmd == "مسح المكتومين عام":
        global_muted_users.clear()
        private_muted_users.clear()
        return await event.reply("🧹 **تم مسح وتطهير قائمة المكتومين بالكامل بنجاح!**")
    elif cmd == "مسح المحظورين عام":
        msg = await event.reply("⏳ **جاري فك الحظر التلقائي عن الجميع...**")
        try:
            blocked_users = await client(GetBlockedRequest(offset=0, limit=100))
            if not blocked_users.blocked: return await msg.edit("❌ **لا يوجد محظورين حالياً.**")
            unblocked_count = 0
            for user in blocked_users.blocked:
                await client(UnblockRequest(user.peer_id))
                unblocked_count += 1
            return await msg.edit(f"🔓 **تم مسح المحظورين عام بنجاح لـ [{unblocked_count}] حساب!**")
        except: return await msg.edit("❌ حدث خطأ أثناء فك حظر الجميع.")

    if not event.is_reply: return
    reply = await event.get_reply_message()
    user_id = reply.sender_id
    try:
        user_obj = await client.get_entity(user_id)
        user_name = user_obj.first_name or "مستخدم مجهول"
    except: user_name = "مستخدم مجهول"
        
    if cmd in ["كتم عام", "mute"]:
        global_muted_users[user_id] = user_name
        private_muted_users[user_id] = user_name
        await event.reply(f"🚷 **تم كتم العضو [{user_name}] كتماً عاماً!**")
    elif cmd in ["الغاء كتم عام", "unmute"]:
        global_muted_users.pop(user_id, None)
        private_muted_users.pop(user_id, None)
        await event.reply(f"🔊 **تم إلغاء الكتم العام عن العضو [{user_name}].**")
    elif cmd in ["حظر عام", "ban"]:
        await client(BlockRequest(user_id))
        await event.reply(f"🚫 **تم حظر العضو [{user_name}] حظراً عاماً!**")

# === [ 6. معالج الحماية من المشاغبين وحماية الخاص ] ===
@client.on(events.NewMessage)
async def global_handler(event):
    if event.out: return
    user_id = event.sender_id
    if user_id in global_muted_users:
        await event.delete()
        return
    if event.is_private:
        if user_id in private_muted_users:
            await event.delete()
            return
        if pm_protection_enabled and user_id not in approved_pm_users:
            await event.delete()
            current_warns = pm_warnings.get(user_id, 0) + 1
            pm_warnings[user_id] = current_warns
            if current_warns >= 7:
                try:
                    await client(BlockRequest(user_id))
                    await event.respond(f"🚫 **تم حظر المستخدم [{event.sender.first_name}] لتجاوزه الـ 7 تحذيرات!**")
                    pm_warnings.pop(user_id, None)
                except: pass
                return
            remaining = 7 - current_warns
            await event.respond(
                f"⚠️ **تنبيه حماية الخاص من سورس البرتغالي!**\n\n"
                f"📊 محاولاتك: `[{current_warns}/7]`\n"
                f"🛑 متبقي لك **`{remaining}`** رسائل وسيتم حظرك نهائياً!"
            )
            return

@client.on(events.NewMessage(pattern=r"\.فحص"))
async def ping_handler(event):
    await event.reply("**سورس البرتغالي الكوني الصافي جاهز للعمل وطاير طيران! ⚡🇵🇹**")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🇵🇹 [ سورس البرتغالي الشامل بدون أقواس في النسخ يعمل الآن ] 🇵🇹")
    print("="*50 + "\n")
    client.start()
    client.run_until_disconnected()
    import time
from telethon import events

# متغيرات لحفظ حالة النوم والوقت والسبب
AFK_STATUS = False
AFK_TIME = None
AFK_REASON = ""

# هنا تقدر تغير الكلمة الافتراضية اللي هترد بيها لو كتبت .سليب من غير ما تحدد سبب
DEFAULT_REASON = "قافل حالياً، أول ما أفتح هرد عليك بالتفصيل."

@bot.on(events.NewMessage(outgoing=True))
async def afk_breaker(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON
    # لو كتبت رسالة في أي شات.. يتعطل وضع النوم تلقائياً
    if AFK_STATUS:
        AFK_STATUS = False
        end_time = time.time()
        duration = round(end_time - AFK_TIME)
        
        # حساب وقت الغياب
        hours, rem = divmod(duration, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f"{hours} ساعة و {minutes} دقيقة" if hours else f"{minutes} دقيقة و {seconds} ثانية"
        
        await event.respond(f"⚡ **أهلاً بعودتك يا جو!** تم إيقاف وضع السليب تلقائياً.\n⏳ كنت غائب لمدة: `{time_str}`")

@bot.on(events.NewMessage(outgoing=True, pattern=r"^\.سليب(?: (.*))?"))
async def set_afk(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON
    if not AFK_STATUS:
        AFK_STATUS = True
        AFK_TIME = time.time()
        
        # سحب السبب لو انكتب، لو منكتبش بياخد السبب الافتراضي
        reason = event.pattern_match.group(1)
        AFK_REASON = reason if reason else DEFAULT_REASON
        
        await event.edit(f"💤 **تم تفعيل وضع السليب بنجاح.**\n📝 الرد الحالي: `{AFK_REASON}`")

@bot.on(events.NewMessage(incoming=True))
async def afk_responder(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON
    if not AFK_STATUS:
        return

    # حساب مدة الغياب الحالية
    current_time = time.time()
    duration = round(current_time - AFK_TIME)
    hours, rem = divmod(duration, 3600)
    minutes, seconds = divmod(rem, 60)
    time_str = f"{hours} س و {minutes} د" if hours else f"{minutes} د و {seconds} ث"

    # الرد هيكون السبب بتاعك بالظبط وتحته العداد
    full_reply = f"{AFK_REASON}\n\n⏳ غائب منذ: {time_str}"

    # 1. الرد في الخاص
    if event.is_private:
        if not event.is_bot and not event.is_channel:
            await event.reply(full_reply)

    # 2. الرد في الجروبات لو حد عملك تاغ أو ريبلاي (إعادة توجيه ورد)
    elif event.is_group:
        if event.mentioned or (event.reply_to_msg_id and (await event.get_reply_to_msg()).sender_id == (await event.client.get_me()).id):
            await event.reply(full_reply)

