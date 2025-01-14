import telebot
import os
import logging
from telebot import types
from gtts import gTTS
import requests
from kalinan import main_def
from AI_chatbot import answering_question
from yazd_ac import search_and_get_results , saved_results
import json

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)





API_TOKEN = os.environ.get("API_TOKEN")
TARGET_CHANNEL_ID = '@py_workshop_jozve'
bot = telebot.TeleBot(API_TOKEN)




#------------------------------------------------------------------------------------------------------
#-------------------------------          Directories           ---------------------------------------
#------------------------------------------------------------------------------------------------------
DOWNLOAD_DIR = "downloads/"
VOICE_DIR = "voices/"
BOOKS_DIR = "books/"



#------------------------------------------------------------------------------------------------------
#-------------------------------          global_flags          ---------------------------------------
#------------------------------------------------------------------------------------------------------
waiting_for_text = False
waiting_for_url = False
waiting_for_query = False





start_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
button1 = types.KeyboardButton("تبدیل متن به صوت")#
button2 = types.KeyboardButton("دانلود برنامه و فایل")#
button3 = types.KeyboardButton("ارسال و دریافت جزوه")#
button4 = types.KeyboardButton("جستجوی یک رویداد در دانشگاه یزد")#
button5 = types.KeyboardButton("چت‌بات هوشمند")#
button6 = types.KeyboardButton("ایجاد اسپم")
button7 = types.KeyboardButton("رزرو غذای کالینان")#
button8 = types.KeyboardButton("رزرو غذای سبد غذایی از کالینان")#

start_keyboard.add(button1, button2,button3,button4,button5,button6,button7,button8)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام این یک بات تلگرام با قابلیت های محدود به عنوان پروژه درس کارگاه پایتون است", reply_markup=start_keyboard)




#------------------------------------------------------------------------------------------------------
#-------------------------------        spam_generating         ---------------------------------------
#------------------------------------------------------------------------------------------------------
@bot.message_handler(func=lambda message: message.text == 'ایجاد اسپم')
def spam_generating(message):
    file_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button2 = types.KeyboardButton("بازگشت به منوی اصلی")
    file_keyboard.add(button2)
    bot.send_message(message.chat.id,"این قابلیت در حال حاضر در دسترس نمی باشد",reply_markup=file_keyboard)
    




#------------------------------------------------------------------------------------------------------
#-------------------------------        text_to_speech          ---------------------------------------
#------------------------------------------------------------------------------------------------------
@bot.message_handler(func=lambda message: message.text == 'تبدیل متن به صوت')
def text_to_speech(message):
    
    text_to_speech_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton("ارسال متن")
    button2 = types.KeyboardButton("بازگشت به منوی اصلی")

    text_to_speech_keyboard.add(button1, button2)
    bot.reply_to(message, ":لطفا گزینه مورد نظر را انتخاب کنید", reply_markup=text_to_speech_keyboard)



@bot.message_handler(func=lambda message: message.text == "ارسال متن")
def text_to_speech1(message):
    global waiting_for_text
    waiting_for_text = True
    bot.reply_to(message, ":لطفا متن خود را ارسال کنید")



@bot.message_handler(func=lambda message: waiting_for_text and message.text != 'بازگشت به منوی اصلی')
def text_to_speech(message):
    global waiting_for_text
    text= message.text
    file_name = "output.mp3"
    file_path = VOICE_DIR+file_name
    output = gTTS(text=text, lang="en",tld='com.au')
    output.save(file_path)
    bot.send_voice(chat_id=message.chat.id,reply_to_message_id=message.id,voice=open(file_path,"rb"))
    os.remove(file_path)



@bot.message_handler(func=lambda message: message.text == 'بازگشت به منوی اصلی')
def return_to_main_menu(message):
    global waiting_for_text
    global waiting_for_url
    waiting_for_text = False  
    waiting_for_url = False
    send_welcome(message)

#------------------------------------------------------------------------------------------------------
#-------------------------------     File & APP downloader      ---------------------------------------
#------------------------------------------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == 'دانلود برنامه و فایل')
def text_to_speech(message):
    global waiting_for_url
    waiting_for_url = True
    file_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button2 = types.KeyboardButton("بازگشت به منوی اصلی")
    file_keyboard.add(button2)
    bot.reply_to(message, ":لطفاآدرس فایل مورد نظر را ارسال کنید", reply_markup=file_keyboard)



def download_file(url):
    local_filename = url.split('/')[-1]
    file_path = DOWNLOAD_DIR + local_filename
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return file_path



@bot.message_handler(func=lambda message: waiting_for_url and message.text != 'بازگشت به منوی اصلی')
def download_file_url(message):
    logger.info(message.text)
    url = message.text
    try:
        file_path = download_file(url)
        print(file_path)
        with open(file_path,"rb") as doc:
            bot.send_document(timeout=60,chat_id=message.chat.id,document=doc,caption="file downloaded successfully!")
        os.remove(file_path)
    except Exception as e:
        bot.reply_to(message, text="problem downloading the requested file")
        print(e)



#------------------------------------------------------------------------------------------------------
#-------------------------------           REFRENCES            ---------------------------------------
#------------------------------------------------------------------------------------------------------


user_sessions = {}
REFERENCES_FILE = 'refrences/refrences.txt'


os.makedirs(os.path.dirname(REFERENCES_FILE), exist_ok=True)
if not os.path.exists(REFERENCES_FILE):
    with open(REFERENCES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False)


@bot.message_handler(func=lambda message: message.text == "ارسال و دریافت جزوه")
def handle_send_file_request(message):
    file_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button2 = types.KeyboardButton("بازگشت به منوی اصلی")
    file_keyboard.add(button2)
    bot.reply_to(
        message, "محتوای مورد نظر خود را ارسال کنید",reply_markup=file_keyboard
    )
    user_sessions[message.chat.id] = {"state": "awaiting_file"}


@bot.message_handler(content_types=["document"])
def handle_file_upload(message):
    user_id = message.chat.id

    
    if user_sessions.get(user_id, {}).get("state") == "awaiting_file":
    
        file_id = message.document.file_id
        mime_type = message.document.mime_type
        user_sessions[user_id]["file_id"] = file_id
        user_sessions[user_id]["mime_type"] = mime_type
        user_sessions[user_id]["state"] = "awaiting_caption"

        bot.reply_to(
            message, "کپشن مورد نظرتون برای این فایل را ارسال کنید"
        )
    else:
        bot.reply_to(
            message, "ابتدا از دستور 'ارسال جزوه' استفاده کنید."
        )


@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id].get("state") == "awaiting_caption")
def handle_caption(message):
    user_id = message.chat.id
    caption = message.text
    file_id = user_sessions[user_id]["file_id"]
    mime_type = user_sessions[user_id]["mime_type"]

    sent_message = bot.send_document(
        TARGET_CHANNEL_ID, file_id, caption=caption
    )
    document_url = f"https://t.me/{TARGET_CHANNEL_ID}/{sent_message.message_id}"
    reference_entry = {
        "message_id": sent_message.message_id,
        "caption": caption,
        "document_url": document_url.replace('@',''),
        "mime_type": mime_type
    }

    with open(REFERENCES_FILE, 'r+', encoding='utf-8') as f:
        references = json.load(f)
        references.append(reference_entry)
        f.seek(0)
        json.dump(references, f, ensure_ascii=False, indent=4)

    del user_sessions[user_id]

    bot.reply_to(
        message, "فایل و کپشن با موفقیت ذخیره شدند."
    )


@bot.inline_handler(lambda query: query.query != "")
def handle_inline_query(inline_query):
    query_text = inline_query.query.lower()
    results = []

    with open(REFERENCES_FILE, 'r', encoding='utf-8') as f:
        references = json.load(f)

    for ref in references:
        if query_text in ref['caption'].lower():
            results.append(
                types.InlineQueryResultDocument(
                    id=str(ref['message_id']),
                    title=ref['caption'],
                    document_url=ref['document_url'],
                    mime_type=ref['mime_type'],
                    caption=ref['document_url']
                )
            )

    bot.answer_inline_query(inline_query.id, results, cache_time=1)


#------------------------------------------------------------------------------------------------------
#-------------------------------       shoping assisstant       ---------------------------------------
#------------------------------------------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == 'جستجوی یک کالا در سایت های فروشگاهی')
def start_shopping(message):
    global waiting_for_query
    waiting_for_query = True
    bot.send_message(
        message.chat.id, "لطفا کلید واژه مورد نظر خود برای سرچ در دیوار را وارد نمایید")
    



def fetch_divar_ads(text_query):
    url = "https://api.divar.ir/v8/web-search/yazd"
    params = {
        "q":text_query
    }
    response = requests.get(url=url,params=params)
    return response.json()


 
@bot.message_handler(func=lambda message:waiting_for_query and message.text != 'بازگشت به منوی اصلی')
def fetch_ads(message):
    text = message.text
    data = fetch_divar_ads(text)
    for item in data["web_widgets"]["post_list"][1:11]:
        title = item["data"]["title"]
        top_description_text = item["data"]["top_description_text"]
        middle_description_text = item["data"]["middle_description_text"]
        bottom_description_text = item["data"]["bottom_description_text"]
        photo = item["data"]["image_url"][0]["src"]
        token = item["data"]["token"]
        description = f"{title}\n{top_description_text}\n{middle_description_text}\n{bottom_description_text}\nhttps://divar.ir/v/{token}"
        bot.send_photo(chat_id=message.chat.id,caption=description,photo=photo)



@bot.message_handler(func=lambda message: message.text == 'بازگشت به منوی اصلی')
def return_to_main_menu(message):
    global waiting_for_query
    waiting_for_query = False
    send_welcome(message)


#------------------------------------------------------------------------------------------------------
#-------------------------------            AI_CHATBOT          ---------------------------------------
#------------------------------------------------------------------------------------------------------


@bot.message_handler(func=lambda message: message.text == 'چت‌بات هوشمند')
def chatbot(message):
    file_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button2 = types.KeyboardButton("بازگشت به منوی اصلی")
    file_keyboard.add(button2)
    bot.reply_to(message, "سوال خود را بپرسید",reply_markup=file_keyboard)
    
    @bot.message_handler(func=lambda message1: True and message.text != 'بازگشت به منوی اصلی')
    def next_message_handler(message1):
        bot.reply_to(message,answering_question(message1))
    @bot.message_handler(func=lambda message: message.text == 'بازگشت به منوی اصلی')
    def return_to_main_menu(message):
        send_welcome(message)   
    
        


#------------------------------------------------------------------------------------------------------
#-------------------------------     Yazduni info crawler       ---------------------------------------
#------------------------------------------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == 'جستجوی یک رویداد در دانشگاه یزد')
def search_info(message):
    file_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button2 = types.KeyboardButton("بازگشت به منوی اصلی")
    file_keyboard.add(button2)
    bot.reply_to(message,"در مورد چه چیزی میخواهید جست و جو کنید",reply_markup=file_keyboard)

    @bot.message_handler(func=lambda message1: True and message1.text != 'بازگشت به منوی اصلی')
    def search_in_resources(message1):
        saved_results(message1.text)
        with open ('search_results/search_resault.txt','r',encoding='utf-8')as file:
            line = 0
            message_collection=[]
            for i in file:
                message_collection.append(i.strip())
                line += 1
                if(line %3 ==0):
                    line = 0
                    title = message_collection[0]
                    description = message_collection[1]
                    link = message_collection[2]
                    message_markdown = f"""
                    *{escape_markdown(title, version=2)}*
                    _{escape_markdown(description, version=2)}_

                    [link]({escape_markdown(link, version=2)})
                    """
                    bot.send_message(message.chat.id,message_markdown,parse_mode='MarkdownV2')
                    message_collection.clear()
    @bot.message_handler(func=lambda message1:True and message.text == 'بازگشت به منوی اصلی')
    def return_to_main_menu(message1):
        send_welcome(message1)



def escape_markdown(text, version=2):
    """
    Escapes special characters in the text for MarkdownV2 formatting.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
                

                
                    

#------------------------------------------------------------------------------------------------------
#-------------------------------      kalinan_reservation       ---------------------------------------
#------------------------------------------------------------------------------------------------------
@bot.message_handler(func=lambda message: message.text == 'رزرو کالینان')
def kalinan_reservation(message):
    main_def()
    with open('launch_reserve.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    with open('dinner_reserve.png','rb') as photo:
        bot.send_photo(message.chat.id, photo)




#------------------------------------------------------------------------------------------------------
#-------------------------------      kalinan_meal_ped          ---------------------------------------
#------------------------------------------------------------------------------------------------------
@bot.message_handler(func=lambda message: message.text == 'رزرو غذای سبد غذایی از کالینان')
def kalinan_reservation_meal_ped(message):
    resault = kalinan_reservation_meal_ped()
    bot.send_message(resault)
    






    


bot.infinity_polling()
