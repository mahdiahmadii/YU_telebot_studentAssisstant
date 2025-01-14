import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def search_and_get_results(search_string):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://www.yazd.ac.ir")
    time.sleep(3)  
    search_input = driver.find_element(By.ID, "ctl15_ctl00_ctl01_ctl00_m_769777930_ctl00__sbSearch_ctl00")
    search_input.send_keys(search_string)
    time.sleep(0.5)
    search_input.send_keys(Keys.RETURN)
    time.sleep(3)

    result_items = driver.find_elements(By.CLASS_NAME, "SEResultItem")
    results = []
    for item in result_items:
        result_text = item.text.strip()
        if result_text:
            results.append(result_text)

    # Close the browser
    driver.quit()

    return results

# Example of how to use the function

def saved_results(search_query):
    results = search_and_get_results(search_query)
    with open ('search_results/search_resault.txt' , 'w',encoding='utf-8') as file:
        for i in results:
            # print("#################")
            # print(i)
            file.write(i.replace('-','_').replace('|',' ') +'\n')

if __name__ == "__main__":
    saved_results(search_query)


    
    

        





