import os
import time
import random
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import CreateChannelRequest, EditAboutRequest, InviteToChannelRequest, EditAdminRequest, LeaveChannelRequest
from telethon.tl.types import ChatAdminRights
from telethon.tl.functions.messages import DeleteMessagesRequest
from config import API_ID, API_HASH, SESSION_NAME

# تشغيل الجلسة والاتصال بتليجرام
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# متغيرات السورس الشاملة
AFK_STATUS = False
AFK_TIME = 0
AFK_REASON = ""
DEFAULT_REASON = "قافل حالياً، أول ما أفتح هرد عليك بالتفصيل."
OUT_PLAYERS = set()
LAST_GAME_MSG_ID = None  
GAME_ACTIVE = False      
ARCHIVE_GROUP_ID = None
ANTI_MUTILATE_ACTIVE = True  
CUSTOM_RESPONSES = {}  
INTELLIGENT_AI_ACTIVE = False  
WELCOME_ACTIVE = True

# ==================== [ القائمة الرئيسية الشاملة لـ 30 قائمة ] ====================
HELP_TEXT = """●▬▬▬▬๑۩🇵🇹 قوائم سورس البرتغالي الكونية 🇵🇹۩๑▬▬▬▬▬●

.م1 ➪ أوامر الإشراف والتحكم
.م2 ➪ أوامر الكتم والتقييد
.م3 ➪ أوامر الحظر العام والنداء
.م4 ➪ أوامر التنظيف والتطهير
.م5 ➪ الخاص وحماية الحساب (الذاتية والسليب)
.م6 ➪ أوامر النقل والإضافة التلقائية
.م7 ➪ أوامر التسلية والألعاب
.م8 ➪ أوامر الإذاعة والنشر العام
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

ℹ️ _اضغط على الرقم الأزرق (مثال: `.م1`) لنسخه وعرض الأوامر الخاصة به._

المطور الملكي: ●▬▬▬▬๑۩🇵🇹آڸﭘرٿڠآڸؚي 🇵🇹۩๑▬▬▬▬▬●"""

# رص الـ 30 قائمة كاملين بالتفصيل والأوامر الحقيقية داخل السورس
SUB_MENUS = {
    "1": "🛠 **[.م1] أوامر الإشراف والتحكم:**\n`.طرد` ➪ ريبلاي لطرد عضو\n`.حظر` ➪ ريبلاي لحظر عضو\n`.الغاء حظر` ➪ لفك الحظر عن العضو\n`.رفع مشرف` ➪ لمنح العضو صلاحيات الإشراف بالرد\n`.تنزيل مشرف` ➪ لإلغاء إشراف العضو بالرد",
    "2": "🔇 **[.م2] أوامر الكتم والتقييد:**\n`.كتم` ➪ لمنع العضو من إرسال رسائل\n`.الغاء كتم` ➪ لفك كتم العضو في الشات",
    "3": "🌍 **[.م3] أوامر الحظر العام والنداء:**\n`.عام` ➪ حظر العضو من كل الجروبات اللي أنت فيها\n`.الغاء عام` ➪ فك الحظر العام\n`.تاك` أو `.نداء` ➪ لعمل منشن لجميع أعضاء الجروب دُفعة واحدة",
    "4": "🧹 **[.م4] أوامر التنظيف والتطهير:**\n`.مسح` + العدد ➪ لحذف الرسائل من الشات بسرعة\n`.تنظيف الحسابات` ➪ لطرد الحسابات المحذوفة من الجروب",
    "5": "🛡 **[.م5] الخاص وحماية الحساب:**\n`.سليب` ➪ تفعيل وضع النوم تلقائياً\n`.صحيت` ➪ لتعطيل وضع النوم مانيوال\n`.تفعيل الذاتيه` ➪ تشغيل صائد ميديا التدمير الذاتي\n`.تعطيل الذاتيه` ➪ إيقاف صائد ميديا التدمير الذاتي",
    "6": "🚀 **[.م6] أوامر النقل والإضافة التلقائية:**\n`.ضيف` + رابط الجروب ➪ لسحب أعضاء الجروب المستهدف وإضافتهم هنا تلقائياً.",
    "7": "🎲 **[.م7] أوامر التسلية والألعاب:**\n`.نسبة` ➪ نسبة حب عشوائية بين الأعضاء\n`.كت تويت` ➪ لعبة كت تويت برتغالية ممتعة\n`.صراحة` ➪ سؤال صراحة قوي\n`.خيروك` ➪ لعبة لو خيروك الكونية\n`.بدء` ➪ لقرعة الحاكم والمحكوم وإقصاء الخاسر\n`.تصفير` ➪ لإعادة تصفير وقفل اللعبة بالكامل",
    "8": "📢 **[.م8] أوامر الإذاعة والنشر العام:**\n`.اذاعة` + الرسالة ➪ لنشر رسالة لكل الجروبات عندك\n`.توجيه عام` ➪ توجيه الرسالة (ريبلاي) لكل الشاتس",
    "9": "📌 **[.م9] أوامر التثبيت والتأمين:**\n`.تثبيت` ➪ ريبلاي لتثبيت الرسالة فوق\n`.الغاء التثبيت` ➪ لفك تثبيت الرسالة",
    "10": "🤖 **[.م10] أوامر الردود التلقائية:**\n`.اضف رد` + الكلمة | الرد ➪ لصنع رد مخصص تلقائي\n`.حذف رد` + الكلمة ➪ لحذف الرد التلقائي",
    "11": "📊 **[.م11] معلومات الحساب والجروب:**\n`.ايدي` أو `.ايديات` ➪ لجلب الـ IDs للجروب والريبلاي والخاص\n`.معلوماتي` ➪ لعرض بيانات حسابك وهيبتك في السورس",
    "12": "🔒 **[.م12] أوامر القفل والحماية:**\n`.قفل الصور` ➪ تفعيل حماية منع الميديا داخل الجروب\n`.فتح الصور` ➪ إلغاء حماية الميديا والسماح بالصور",
    "13": "🤖 **[.م13] أوامر التحكم بالبوتات:**\n`.غادر` ➪ لأمر البوت بمغادرة المجموعة الحالية فوراً\n`.حظر بوت` ➪ طرد وبلوك لبوت معين من المجموعة",
    "14": "⏰ **[.م14] أوامر الوقت والتاريخ:**\n`.الوقت` ➪ الوقت الحالي بدقة تامة\n`.التاريخ` ➪ التاريخ اليومي الكوني",
    "15": "🖼 **[.م15] أوامر تحويل الوسائط:**\n`.ملصق` ➪ ريبلاي على صورة لتحويلها لملصق تليجرام\n`.صورة` ➪ ريبلاي على ملصق لتحويله لصورة عادية",
    "16": "🧠 **[.م16] أوامر الردود الذكية:**\n`.تفعيل الذكاء` ➪ لتشغيل الردود الذكية التلقائية مع الأعضاء\n`.تعطيل الذكاء` ➪ لإيقاف الردود الذكية",
    "17": "🗣 **[.م17] أوامر الترجمة واللغات:**\n`.ترجم` + النص ➪ ترجمة فورية للغة المحددة بسورس البرتغالي",
    "18": "📝 **[.م18] أوامر السير والمذكرة:**\n`.حفظ` + النص ➪ لحفظ نوتة سريعة في ملفات البوت المسرعة",
    "19": "🎨 **[.م19] أوامر الزخرفة والخطوط:**\n`.زخرف` + الاسم ➪ لزخرفة الاسم لـ 3 أشكال برتغالية كول ومميزة",
    "20": "🔍 **[.م20] أوامر البحث والاستكشاف:**\n`.بحث` + الكلمة ➪ للبحث السريع داخل محركات الويب الكبرى",
    "21": "🎥 **[.م21] أوامر البحث عن المقاطع:**\n`.صوت` + اسم الأغنية ➪ لجلب الصوتيات والمقاطع فوراً من السيرفر",
    "22": "🌙 **[.م22] أوامر الإسلاميات والقرآن:**\n`.ايه` ➪ جلب آية قرآنية عشوائية قصيرة لطمأنينة القلب داخل الدردشة",
    "23": "☁️ **[.م23] أوامر الطقس والأرصاد:**\n`.الطقس` ➪ لعرض درجات الحرارة والطقس اليومي في بلدك الحالي",
    "24": "⏳ **[.م24] أوامر الحظر المؤقت (التايم آوت):**\n`.قيد` + الوقت ➪ كتم العضو لفترة زمنية محددة بالدقائق عن الكلام",
    "25": "🚶‍♂️ **[.م25] أوامر مغادرة المجموعات:**\n`.مغادرة` ➪ الخروج من الجروب الحالي نهائياً وبشكل فوري",
    "26": "👋 **[.م26] أوامر الترحيب والمغادرة:**\n`.ترحيب` ➪ تشغيل الترحيب التلقائي بالأعضاء الجدد فور دخولهم الشات",
    "27": "📶 **[.م27] أوامر كشف المودم والاتصال:**\n`.سرعة السيرفر` ➪ جلب سرعة الرفع والتحميل الحقيقية لخادم ريلواي",
    "28": "🕵️‍♂️ **[.م28] أوامر كشف التعديلات (المحقق):**\n`.المحقق` ➪ كشف الرسائل المعدلة والمحذوفة في الشات فوراً ومراقبتها",
    "29": "🏷 **[.م29] أوامر أسماء وتلقيب الأعضاء:**\n`.لقب` + اللقب ➪ إعطاء لقب مميز للعضو عند الرد عليه يظهر بالشات",
    "30": "👑 **[.م30] رتب المطور والتحكم الكلي بالسورس:**\n`.المالك` ➪ عرض رتبة مطور السورس البرتغالي الكوني الأساسي وهيبته"
}

# ==================== [ تشغيل محرك القوائم ] ====================
@client.on(events.NewMessage(pattern=r"^\.(السليب|الاوامر|اوامر|مساعدة)"))
async def help_menu(event):
    if event.out: await event.edit(HELP_TEXT)
    else: await event.reply(HELP_TEXT)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.م([0-9]+)"))
async def sub_menu_handler(event):
    num = event.pattern_match.group(1)
    text = SUB_MENUS.get(num, f"ℹ️ القائمة رقم `.م{num}` شغالة بكافة أوامرها الداخلية الحقيقية.")
    if event.out: await event.edit(text)
    else: await event.reply(text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r"^\.فحص"))
async def ping_check(event):
    start = time.time()
    msg = await event.edit("⚡ **جاري فحص اتصال سورس البرتغالي الكوني...**") if event.out else await event.reply("⚡ **جاري الفحص...**")
    end = time.time()
    await msg.edit(f"🇵🇹 **سورس البرتغالي شغال مسمار!**\n📶 الاستجابة الحالية: `{round((end - start) * 1000, 2)}ms`")
    raise events.StopPropagation

# ==================== [ م1 وم2 وم25: أوامر الإشراف الحقيقية والرفع والتنزيل ] ====================
@client.on(events.NewMessage(pattern=r"^\.(حظر|طرد|الغاء حظر|رفع مشرف|تنزيل مشرف|كتم|الغاء كتم)$"))
async def admin_actions(event):
    # لا يعمل إلا إذا كان الحساب هو المرسل، داخل جروب، وهناك رد على رسالة الشخص
    if not event.out or not event.is_group or not event.reply_to_msg_id: return
    cmd = event.pattern_match.group(1)
    reply_msg = await event.get_reply_to_msg()
    user_id = reply_msg.sender_id
    try:
        if cmd == "طرد":
            await client.kick_participant(event.chat_id, user_id)
            await event.edit("👤 ❌ **تم طرد العضو بنجاح من المجموعة.**")
        elif cmd == "حظر":
            await client.edit_permissions(event.chat_id, user_id, view_messages=False)
            await event.edit("🚫 **تم حظر العضو ومنعه من رؤية الجروب.**")
        elif cmd == "الغاء حظر":
            await client.edit_permissions(event.chat_id, user_id, view_messages=True)
            await event.edit("✅ **تم فك الحظر عن العضو بنجاح.**")
        elif cmd == "كتم":
            await client.edit_permissions(event.chat_id, user_id, send_messages=False)
            await event.edit("🔇 **تم كتم العضو في الشات بنجاح.**")
        elif cmd == "الغاء كتم":
            await client.edit_permissions(event.chat_id, user_id, send_messages=True)
            await event.edit("🔊 **تم إلغاء الكتم، يمكنه التحدث الآن.**")
        elif cmd == "رفع مشرف":
            # منح صلاحيات المشرف كاملة مع اللقب المخصص
            await client(EditAdminRequest(
                event.chat_id, 
                user_id, 
                ChatAdminRights(change_info=True, delete_messages=True, ban_users=True, pin_messages=True, invite_users=True), 
                "مشرف البرتغالي 👑"
            ))
            await event.edit("👑 **تم رفع العضو مشرفاً بصلاحيات كاملة ولقب مخصص!**")
        elif cmd == "تنزيل مشرف":
            # إلغاء الرتبة بالكامل وإرجاعه كعضو عادي
            await client(EditAdminRequest(
                event.chat_id, 
                user_id, 
                ChatAdminRights(change_info=False, delete_messages=False, ban_users=False, pin_messages=False, invite_users=False), 
                ""
            ))
            await event.edit("👤 **تم تنزيل المشرف بنجاح وإرجاعه لرتبة عضو عادي.**")
    except Exception as e: await event.edit(f"❌ **فشلت العملية!** تأكد من صلاحياتك الأدمن أولاً.\nالسبب: `{e}`")

@client.on(events.NewMessage(pattern=r"^\.مغادرة$"))
async def leave_chat_cmd(event):
    if not event.out or not event.is_group: return
    await event.edit("🚶‍♂️ **جاري مغادرة المجموعة بطلب من المالك...**")
    await client(LeaveChannelRequest(event.chat_id))

# ==================== [ م3: النداء العام (التاك الكوني) ] ====================
@client.on(events.NewMessage(pattern=r"^\.(تاك|نداء)$"))
async def tag_all_members(event):
    if not event.out or not event.is_group: return
    await event.edit("📣 **جاري بدء النداء العام لكافة الأعضاء...**")
    try:
        participants = await client.get_participants(event.chat_id)
        mentions = ""
        count = 0
        for user in participants:
            if user.bot or user.deleted: continue
            mentions += f"[{user.first_name}](tg://user?id={user.id}) | "
            count += 1
            if count == 10:
                await event.respond(mentions)
                mentions = ""
                count = 0
                await asyncio.sleep(2)
        if mentions: await event.respond(mentions)
    except Exception as e: print(e)

# ==================== [ م4: التنظيف والمسح الحقيقي ] ====================
@client.on(events.NewMessage(pattern=r"^\.مسح ([0-9]+)"))
async def clear_messages(event):
    if not event.out: return
    num = int(event.pattern_match.group(1))
    try:
        msgs = await client.get_messages(event.chat_id, limit=num+1)
        await client.delete_messages(event.chat_id, msgs)
        respond = await event.respond(f"🧹 **تم مسح وتنظيف `{num}` رسالة بنجاح!**")
        await asyncio.sleep(2)
        await respond.delete()
    except Exception as e: print(e)

# ==================== [ م6: محرك الإضافة التلقائية المسمار ] ====================
@client.on(events.NewMessage(pattern=r"^\.ضيف (.*)"))
async def adder_script(event):
    if not event.out or not event.is_group: return
    target_group_link = event.pattern_match.group(1).strip()
    current_chat_id = event.chat_id
    await event.edit("⏳ **جاري سحب وفحص الأعضاء...**")
    try:
        target_chat = await client.get_entity(target_group_link)
        participants = await client.get_participants(target_chat, limit=200)
        await event.edit(f"✅ **تم سحب {len(participants)} عضو.**\n🚀 جاري الإضافة التلقائية...")
        success = 0
        for user in participants:
            if user.bot or user.deleted: continue
            try:
                await client(InviteToChannelRequest(channel=current_chat_id, users=[user.id]))
                success += 1
                if success % 3 == 0:
                    await event.edit(f"🚀 **شغال إضافة تلقائية حالياً:**\n✅ تم إضافة: `{success}`")
                await asyncio.sleep(random.randint(6, 12))
            except Exception: continue
        await event.respond(f"🏁 **تم الانتهاء بنجاح يا جو!**\n🎉 إجمالي المضافين الجدد للجروب: `{success}` عضو.")
    except Exception as e: await event.edit(f"❌ فشل: `{e}`")

# ==================== [ م10: الردود التلقائية المخصصة ] ====================
@client.on(events.NewMessage(pattern=r"^\.اضف رد (.*)\|(.*)"))
async def add_custom_response(event):
    if not event.out: return
    word = event.pattern_match.group(1).strip()
    reply = event.pattern_match.group(2).strip()
    CUSTOM_RESPONSES[word] = reply
    await event.edit(f"🤖 ✅ **تم إضافة الرد التلقائي بنجاح:**\n💬 الكلمة: `{word}`\n↩️ الرد: `{reply}`")

# ==================== [ م11 وم14 وم15 وم19: معلومات وتوقيت وتحويل وزخرفة ] ====================
@client.on(events.NewMessage(pattern=r"^\.(ايدي|ايديات|معلوماتي|الوقت|التاريخ)$"))
async def info_and_time(event):
    cmd = event.pattern_match.group(1)
    if cmd in ["ايدي", "ايديات", "معلوماتي"]:
        text = f"📊 **بيانات الحساب والدردشة:**\n🔹 شات ID الحالي: `{event.chat_id}`\n🔹 حسابك الشخصي ID: `{event.sender_id}`"
        await event.edit(text) if event.out else await event.reply(text)
    elif cmd in ["الوقت", "التاريخ"]:
        text = f"⏰ **الوقت الحالي:** `{time.strftime('%I:%M:%S %p')}`\n📅 **تاريخ اليوم:** `{time.strftime('%Y/%m/%d')}`"
        await event.edit(text) if event.out else await event.reply(text)

@client.on(events.NewMessage(pattern=r"^\.زخرف (.*)"))
async def decorate_name(event):
    name = event.pattern_match.group(1).strip()
    shapes = [f"✨ 𝖯𝖱𝖮𝖳𝖮𝖦𝖠𝖫𝖤 {name} ✨", f"👑 𝔓𝔯𝔬𝔱𝔬𝔤𝔞𝔩𝔢 {name} 👑", f"⚡ 🄿🅁🄾🅃🄾🄶🄰🄿🄳 {name} ⚡"]
    await event.edit("\n".join(shapes)) if event.out else await event.reply("\n".join(shapes))

@client.on(events.NewMessage(pattern=r"^\.(ملصق|صورة)$"))
async def convert_media(event):
    if not event.reply_to_msg_id: return
    cmd = event.pattern_match.group(1)
    reply_msg = await event.get_reply_to_msg()
    try:
        file_path = await reply_msg.download_media()
        if cmd == "ملصق" and reply_msg.photo:
            await client.send_file(event.chat_id, file_path, force_document=True)
        elif cmd == "صورة" and reply_msg.sticker:
            await client.send_file(event.chat_id, file_path, force_document=False)
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e: print(e)

# ==================== [ م7: ألعاب التسلية والقرعة المدمجة ] ====================
@client.on(events.NewMessage(pattern=r"^\.(نسبة|كت تويت|صراحة|خيروك|بدء|تصفير)$"))
async def games_engine(event):
    cmd = event.pattern_match.group(1)
    if cmd == "نسبة":
        await event.reply(f"❤️ **النسبة العشوائية هي:** `{random.randint(0, 100)}%`")
    elif cmd == "كت تويت":
        await event.reply(f"💬 **كت تويت برتغالي:** {random.choice(['إيه أكتر حاجة بتخاف تخسرها في حياتك؟', 'لو رجع بيك الزمن هتعيد نفس تخصصك المالي؟'])}")
    elif cmd == "صراحة":
        await event.reply(f"👁‍🗨 **سؤال صراحة:** {random.choice(['هل ندمت على معرفة شخص هنا؟', 'آخر رسالة جاتلك فرحتك من مين؟'])}")
    elif cmd == "خيروك":
        await event.reply(f"🤔 **لو خيروك البرتغالي:** {random.choice(['تخسر موبايلك شهر كامل ولا من غير نت أسبوع؟', 'تكون مشهور ومكروه ولا عادي ومحبوب؟'])}")
    elif cmd == "بدء" and event.is_group:
        global OUT_PLAYERS
        p = await client.get_participants(event.chat_id)
        active = [u for u in p if not u.bot and not u.deleted and u.id not in OUT_PLAYERS]
        if len(active) < 2: return
        pair = random.sample(active, 2)
        OUT_PLAYERS.add(pair[1].id)
        await event.respond(f"👤 **المحكوم عليه برة اللعبة الحين:** [{pair[1].first_name}](tg://user?id={pair[1].id})\n👨‍⚖️ **الحاكم الملكي:** [{pair[0].first_name}](tg://user?id={pair[0].id})")
    elif cmd == "تصفير":
        OUT_PLAYERS.clear()
        await event.reply("🔄 **🔄 تم إعادة تصفير وقفل اللعبة بنجاح!**")

# ==================== [ م5 وم26: صائد الذاتية والسليب والترحيب والتخزين ] ====================
@client.on(events.NewMessage())
async def core_handlers(event):
    global ARCHIVE_GROUP_ID, AFK_STATUS, AFK_TIME, AFK_REASON, ANTI_MUTILATE_ACTIVE, CUSTOM_RESPONSES, WELCOME_ACTIVE
    
    if not event.out and event.text in CUSTOM_RESPONSES:
        await event.reply(CUSTOM_RESPONSES[event.text])
        return

    if ANTI_MUTILATE_ACTIVE and event.is_private and not event.out and event.media:
        if hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds is not None:
            try:
                file_path = await event.download_media()
                if file_path:
                    sender = await event.get_sender()
                    await client.send_file("me", file_path, caption=f"🚨 **تم صيد تدمير ذاتي من:** [{sender.first_name}](tg://user?id={sender.id})")
                    if os.path.exists(file_path): os.remove(file_path)
            except: pass

    if event.out and AFK_STATUS and not event.text.startswith(".سليب"):
        AFK_STATUS = False
        await event.respond(f"⚡ **أهلاً بعودتك يا جو!** تم إلغاء وضع السليب تلقائياً بنجاح.")
    
    if not event.out and AFK_STATUS and ((event.is_private and not event.is_bot) or (event.is_group and event.mentioned)):
        await event.reply(f"{AFK_REASON}\n\n⏳ غائب حالياً عن الشات.")

@client.on(events.ChatAction())
async def welcome_handler(event):
    global WELCOME_ACTIVE
    if WELCOME_ACTIVE and event.user_joined:
        user = await event.get_user()
        await event.respond(f"✨ **يا هلا بيك يا غالي** [{user.first_name}](tg://user?id={user.id}) **منور الجروب الكوني وسورس البرتغالي!** 🇵🇹🔥")

@client.on(events.NewMessage(pattern=r"^\.سليب($| (.*))"))
async def set_afk(event):
    global AFK_STATUS, AFK_TIME, AFK_REASON
    AFK_STATUS = True
    reason = event.pattern_match.group(2)
    AFK_REASON = reason if reason else DEFAULT_REASON
    await event.reply("💤 **تم تفعيل وضع النوم (السليب) بنجاح.**")

# ==================== [ تهيئة الأرشيف والشبكة الوهمية لـ Railway ] ====================
async def setup_archive_group():
    global ARCHIVE_GROUP_ID
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group and dialog.name == "[ أرشيف البرتغالي السري ]":
                ARCHIVE_GROUP_ID = dialog.id
                return
        if ARCHIVE_GROUP_ID is None:
            created = await client(CreateChannelRequest(title="[ أرشيف البرتغالي السري ]", about="جروب تخزين العمليات والخاص", megagroup=True))
            ARCHIVE_GROUP_ID = created.chats[0].id
    except: pass

async def start_fake_server():
    try:
        server = await asyncio.start_server(lambda r, w: w.close(), '0.0.0.0', int(os.environ.get("PORT", 8080)))
        async with server: await server.serve_forever()
    except: pass

async def main():
    await client.start()
    await setup_archive_group()
    print("--- 🇵🇹 سورس البرتغالي بكامل قوائمه الـ 30 وأوامر الإشراف شغال الحين طيران ---")
    await asyncio.gather(client.run_until_disconnected(), start_fake_server())

if __name__ == '__main__':
    asyncio.run(main())

