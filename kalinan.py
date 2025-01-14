from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract
import io
from io import BytesIO
import time
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter, ImageEnhance
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import Table
import tkinter as tk
from tkinter import filedialog
from bidi.algorithm import get_display
from arabic_reshaper import reshape
import logging
import os


#--------------------------------------------------------
STUDENT_NUMBER = os.environ.get("STUDENT_NUMBER")
PASSWORD_KALINAN = os.environ.get("PASSWORD_KALINAN")
print(STUDENT_NUMBER,PASSWORD_KALINAN)
#---------------------------------------------------------
def read_csv(file_path):
    return pd.read_csv(file_path)



def prepend_headers_to_csv(file_path):
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["self", "food", "number"])
    headers_df = pd.DataFrame(columns=["self", "food", "number"])
    combined_df = pd.concat([headers_df, df], ignore_index=True)
    combined_df.to_csv(file_path, index=False)




def plot_table(df):
    persian_days = ["شنبه", "یکشنبه", "دوشنبه", "سه شنبه", "چهارشنبه"]
    df_to_plot = df.iloc[:5].reset_index(drop=True)
    df_to_plot['day'] = persian_days
    fig, ax = plt.subplots()
    ax.axis('tight')
    ax.axis('off')
    table = Table(ax, bbox=[0, 0, 1, 1])
    headers = ['self', 'food', 'number','day']
    for i, column in enumerate(headers):
        table.add_cell(0, i, 0.2, 0.1, text=column, loc='center', facecolor='lightgrey')
    for i in range(len(df_to_plot)):
        for j in range(len(df_to_plot.columns)):
            color = 'lightblue' if i % 2 == 0 else 'lightgreen'
            table.add_cell(i + 1, j, 0.2, 0.1, text=str(df_to_plot.iloc[i, j]), loc='center', facecolor=color)
    ax.add_table(table)
    plt.show()


def save_table_as_image(fig, filename):
    fig.savefig(filename, bbox_inches='tight',)




def show_resault(input_path):
    # root = tk.Tk()
    # root.withdraw()  
    # file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    file_path = input_path
    if file_path:
        df = read_csv(file_path)
        # plot_table(df)
        # save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        save_path = file_path.replace('.csv','.png')
        if save_path:
            fig, ax = plt.subplots()
            ax.axis('tight')
            ax.axis('off')
            table = Table(ax, bbox=[0, 0, 1, 1])
            
            for i, column in enumerate(df.columns):
                table.add_cell(0, i, 0.2, 0.1, text=column, loc='center', facecolor='lightgrey')
            
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    color = 'lightblue' if (i + j) % 2 == 0 else 'lightgreen'
                    table.add_cell(i + 1, j, 0.2, 0.1, text=str(df.iloc[i, j]), loc='center', facecolor=color)
            for (i, j), cell in table.get_celld().items():
                cell.set_text_props(fontsize=24)  # Set the desired font size
            ax.add_table(table)
            save_table_as_image(fig, save_path)
            print(f"Table saved as image at: {save_path}")

#----------------------------------------------------------------------------------
def save_the_reserved_meal(table, meal):
    
    csv_file_name = meal+'_reserve.csv'
    with open (csv_file_name,'w',encoding='utf-8') as report:
        i = 1
        report.write("seld,food,number\n")
        for t in table:
            if('selected' in t.get_attribute('outerHTML')):
                line = t.text
                if(line != ''):
                    # if(i2 <=5 ):
                    line = line+' ,'
                    line = line.strip()
                    if(i%3 == 0):
                        line = line.replace(',','\n')
                    print(line)
                    report.write(line)
                        # i2 += 1
                    i+=1
                    print("______________")

#--------------------------------------------------------------------------------

def start1():
    browser = webdriver.Chrome()
    implicit_time = 5
    browser.get('https://jeton.yazd.ac.ir/')
    browser.implicitly_wait(5)
    captcha_text = ""
    retry_login = True
    first_try_login = True
    while(retry_login):
        for _ in range (0,5):
            browser.implicitly_wait(implicit_time)        
            captcha_element = browser.find_element('id' ,'Img1')
            captcha_image = captcha_element.screenshot_as_png

            image = Image.open(io.BytesIO(captcha_image))
            img = image.convert('L')
            image = img.filter(ImageFilter.MedianFilter())
            image.save('captcha_image.png', 'PNG')
            
            pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
            
            image = Image.open(BytesIO(captcha_image))
            captcha_text = pytesseract.image_to_string(image, config='--psm 6')
            print("CAPTCHA Text:", captcha_text)
            captcha_text = captcha_text.strip()
            
            if(not (str.isnumeric(captcha_text) and len(captcha_text)==4) ):
                print(f"{str.isnumeric(captcha_text)} and {len(captcha_text)}")
                browser.refresh()
                continue
            break
        captch_box = browser.find_element('id','txtCaptcha')
        captch_box.send_keys(captcha_text)

        if(first_try_login):
            box1 = browser.find_element('id','txtUsernamePlain')
            box2 = browser.find_element('id','txtPasswordPlain')
            box1.send_keys(STUDENT_NUMBER)
            box2.send_keys(PASSWORD_KALINAN)
            first_try_login = False

        browser.implicitly_wait(implicit_time)
        encript_btn = browser.find_element('id','btnEncript')
        encript_btn.click()
        browser.implicitly_wait(implicit_time)
        try:
            test = browser.find_element('id','btnEncript')
        except:
            retry_login = False

    buy_button = browser.find_element('id','ui-id-3')
    buy_button.click()
    browser.implicitly_wait(implicit_time)

    #weekly reserve button
    buy_weekly_food = browser.find_element(By.XPATH,'/html/body/form/div[5]/div[1]/div[2]/div[2]/a[1]/div')
    buy_weekly_food.click()
    browser.implicitly_wait(implicit_time)

    #next_week
    btn_nextweek = browser.find_element('id','cphMain_imgbtnNextWeek')
    btn_nextweek.click()
    # browser.implicitly_wait(implicit_time)
    time.sleep(3)

    #reseve_launch
    btn_all_launch = browser.find_element('id','cphMain_grdReservationLunch_chkbxAll')
    btn_all_launch.click()
    # browser.implicitly_wait(implicit_time)
    time.sleep(2)

    btn_save_launch = browser.find_element('id','cphMain_btnSaveLunch')
    btn_save_launch.click()
    # browser.implicitly_wait(implicit_time)
    time.sleep(2)
    table = browser.find_elements(By.TAG_NAME,'option')
    save_the_reserved_meal(table,'launch')
    #save_launch_log
    
    browser.implicitly_wait(implicit_time)

    #reserve_dinner
    btn_dinners = browser.find_element('id','cphMain_lblDinner')
    btn_dinners.click()

    # browser._wait(implicit_time)
    time.sleep(2)
    btn_all_dinner = browser.find_element('id','cphMain_grdReservationDinner_chkbxAll')
    btn_all_dinner.click()
    # browser.implicitly_wait(implicit_time)
    time.sleep(2)
    btn_save_dinner = browser.find_element('id','cphMain_btnSaveDinner')
    btn_save_dinner.click()
    # browser.implicitly_wait(implicit_time)
    time.sleep(5)

    #save_dinner_log
    table = browser.find_elements(By.TAG_NAME,'option')
    save_the_reserved_meal(table,'dinner')

    #end
    browser.quit()

#---------------------------------------------------------------------------------- 
def main_def():
    logger = logging.getLogger('selenium')
    logger.setLevel(logging.DEBUG)
    start1()
    show_resault('launch_reserve.csv')
    show_resault('dinner_reserve.csv')

def meal_ped ():
    message = ''
    browser = webdriver.Chrome()
    implicit_time = 5
    browser.get('https://jeton.yazd.ac.ir/')
    browser.implicitly_wait(5)
    captcha_text = ""
    retry_login = True
    first_try_login = True
    while(retry_login):
        for _ in range (0,5):
            browser.implicitly_wait(implicit_time)        
            captcha_element = browser.find_element('id' ,'Img1')
            captcha_image = captcha_element.screenshot_as_png

            image = Image.open(io.BytesIO(captcha_image))
            img = image.convert('L')
            image = img.filter(ImageFilter.MedianFilter())
            image.save('captcha_image.png', 'PNG')
            
            pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
            
            image = Image.open(BytesIO(captcha_image))
            captcha_text = pytesseract.image_to_string(image, config='--psm 6')
            print("CAPTCHA Text:", captcha_text)
            captcha_text = captcha_text.strip()
            
            if(not (str.isnumeric(captcha_text) and len(captcha_text)==4) ):
                print(f"{str.isnumeric(captcha_text)} and {len(captcha_text)}")
                browser.refresh()
                continue
            break
        captch_box = browser.find_element('id','txtCaptcha')
        captch_box.send_keys(captcha_text)

        if(first_try_login):
            box1 = browser.find_element('id','txtUsernamePlain')
            box2 = browser.find_element('id','txtPasswordPlain')
            box1.send_keys(STUDENT_NUMBER)
            box2.send_keys(PASSWORD_KALINAN)
            first_try_login = False

        browser.implicitly_wait(implicit_time)
        encript_btn = browser.find_element('id','btnEncript')
        encript_btn.click()
        browser.implicitly_wait(implicit_time)
        try:
            test = browser.find_element('id','btnEncript')
        except:
            retry_login = False

    buy_button = browser.find_element('id','ui-id-5')
    buy_button.click()
    browser.implicitly_wait(implicit_time)

    buy_meal_ped = browser.find_element(By.XPATH , '//*[@id="ui-id-6"]/a[1]/div')
    buy_meal_ped.click()
    browser.implicitly_wait(implicit_time)

    food_available_to_buy = False

    while(not food_available_to_buy):
        try:
            label = driver.find_element(By.ID, "cphMain_lblCreditValue")

            # CHECKING THE CREDIT
            text_content = label.text 
            numeric_part = text_content.split(":")[1].strip().split(" ")[0].replace(",", "")  
            credit_value = int(numeric_part)
            if(credit_value > 180000):
                checkbox = browser.find_element('id', "cphMain_grdReservationBreakfast_chkReserve_0")
                if checkbox.is_enabled():
                    checkbox.click()
                    food_available_to_buy = True
                
                checkbox = browser.find_element('id', "cphMain_grdReservationBreakfast_chkReserve_1")
                if checkbox.is_enabled():
                    checkbox.click()
                    food_available_to_buy = True

                checkbox = browser.find_element('id', "cphMain_grdReservationBreakfast_chkReserve_2")
                if checkbox.is_enabled():
                    checkbox.click()
                    food_available_to_buy = True
            else:
                message = 'the credit is not enough'
                break
        except Exception as e:
            print(f"An error occurred: {e}")


        save_the_changes = browser.find_element(By.XPATH,'//*[@id="cphMain_btnSave"]')
        save_the_changes.click()

        if(food_available_to_buy ):
            message = 'غذای سبد غذایی با موفقیت رزرو شد'

        
    return message























if __name__ == "__main__":
    main_def()