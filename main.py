from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import requests
import time
import threading
import logging

# Web elements
PROCEED_TO_CHECKOUT_ELEMENT = '//*[@id="maincontent"]/div[3]/div/div[2]/div[1]/ul/li[1]/button/span'
SHOPPING_CART_ELEMENT = '//*[@id="maincontent"]/div[1]/div[2]/div/div/div/a'
SEARCH_ELEMENT = '//*[@id="search"]'
LUMA_ICON = '/html/body/div[2]/header/div[2]/a/img'

driver_option = webdriver.ChromeOptions()
driver_option.add_argument("--incognito")
chromedriver_path = 'F:\\Download\\chromedriver-win64\\chromedriver.exe'
debug = True


def create_webdriver():
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=driver_option)


def create_account(new_browser):
    logging.info("--------------------- Creating Account ----------------------")
    new_browser.find_element(By.XPATH, '/html/body/div[2]/header/div[1]/div/ul/li[3]/a').click()
    elements_list = ['//*[@id="firstname"]', '//*[@id="lastname"]', '//*[@id="email_address"]', '//*[@id="password"]', '//*[@id="password-confirmation"]',
                     '//*[@id="form-validate"]/div/div[1]/button/span']

    data_to_fill = [user_data['name']['first'],
                    user_data['name']['last'],
                    user_data['email'],
                    user_data['login']['uuid'],
                    user_data['login']['uuid'],
                    None
                    ]

    for element, data in zip(elements_list, data_to_fill):
        try:
            element_to_find = new_browser.find_element(By.XPATH, element)
            if data:
                element_to_find.send_keys(data)
                logging.info(data)
            else:
                element_to_find.click()

        except Exception as e:
            logging.error(e)
            print("Error in {}".format(e))

    logging.info("--------------------- Account Created ---------------------")


def finalizes_checkout(new_browser):
    logging.info("--------------------- Finalize Checkout ---------------------")
    elements_list = [
        "//input[@class='input-text' and @name='street[0]']",
        "//input[@class='input-text' and @name='city']",
        "//input[@class='input-text' and @name='postcode']",
        "//input[@class='input-text' and @name='telephone']",
        "//input[@class='radio' and @name='ko_unique_1']"
    ]

    data_to_fill = [
        f"{user_data['location']['street']['number']} {user_data['location']['street']['name']}",
        user_data['location']['city'],
        user_data['location']['postcode'],
        user_data['cell'],
    ]

    for element, data in zip(elements_list, data_to_fill):
        try:
            element_to_find = WebDriverWait(new_browser, 15).until(
                EC.element_to_be_clickable((By.XPATH, element)))
            if data:
                element_to_find.send_keys(data)
                logging.info(data)

        except Exception as e:
            logging.error(e)
            print('Error in {}'.format(e))

    elements = ["country_id", "region_id"]
    count = 0
    for element in elements:
        try:
            element_to_find = new_browser.find_element(By.NAME, element)
            select = Select(element_to_find)
            if count == 0:
                select.select_by_visible_text(user_data['location']['country'])
                logging.info(user_data['location']['country'])
            if count == 1:
                select.select_by_visible_text(user_data['location']['state'])
                logging.info(user_data['location']['state'])

            count += 1
            time.sleep(2)

        except Exception as e:
            logging.error(e)
            print(e)

    time.sleep(5)

    # Go to place Order Page
    try:
        new_browser.find_element(By.XPATH, '//*[@id="shipping-method-buttons-container"]/div/button').click()
        time.sleep(5)
        new_browser.find_element(By.XPATH, '//*[@id="checkout-payment-method-load"]/div/div/div[2]/div[2]/div[4]/div/button').click()
        logging.info("Place Order Page Loaded")

    except Exception as e:
        logging.error(e)
        print("Error {} !".format(e))

    time.sleep(5)
    finished_purchase = WebDriverWait(new_browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="base"]')))
    # finished_purchase = new_browser.find_element(By.XPATH, '//*[@class="base"]')
    if finished_purchase.text == "Thank you for your purchase!":
        logging.info("--------------------- Order purchase is completed ---------------------")
        print("Order purchase is completed")
    else:
        logging.error("Could not completed your order !")
        print("Could not completed your order !")


def access_url(url):
    new_browser = create_webdriver()
    new_browser.get(url)
    if debug:
        if new_browser.find_element(By.XPATH, LUMA_ICON).is_displayed():
            logging.info("Completed page load")
            print("Completed page load")
        else:
            logging.error("Could not load page")
            print("Could not load page")
            return

    create_account(new_browser)

    shirt_search = new_browser.find_element(By.XPATH, SEARCH_ELEMENT)
    shirt_key = "shirt"
    shirt_search.send_keys(shirt_key)

    monitor_thread = threading.Thread(target=monitor_request)
    monitor_thread.start()

    monitor_thread.join()
    try:
        shirt_search = WebDriverWait(new_browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, SEARCH_ELEMENT))
        )
        shirt_search.send_keys(Keys.ENTER)
    except Exception as e:
        print(f'Error trying to click in: {e}')

    elements_list = ['//*[@id="maincontent"]/div[3]/div[1]/div[2]/div[2]/ol/li[5]/div/a/span/span/img', '//*[@id="option-label-size-143-item-166"]', '//*[@id="option-label-color-93-item-50"]',
                     '//*[@id="product-addtocart-button"]/span']

    for element in elements_list:
        WebDriverWait(new_browser, 15).until(EC.element_to_be_clickable((By.XPATH, element))).click()

    # add review here
    add_review(new_browser)

    secondary_elements_to_add = ['//*[@id="maincontent"]/div[2]/div/div[5]/div[2]/div/ol/li[2]/div/a/span/span/img', '//*[@id="option-label-size-143-item-166"]',
                                 '//*[@id="option-label-color-93-item-49"]',
                                 '//*[@id="product-addtocart-button"]/span']

    for element in secondary_elements_to_add:
        WebDriverWait(new_browser, 15).until(EC.element_to_be_clickable((By.XPATH, element))).click()

    confirm_add_to_cart = WebDriverWait(new_browser, 25).until(
        EC.element_to_be_clickable((By.XPATH, SHOPPING_CART_ELEMENT))
    )

    confirm_add_to_cart.click()

    new_browser.find_element(By.XPATH, PROCEED_TO_CHECKOUT_ELEMENT).click()

    finalizes_checkout(new_browser)

    new_browser.quit()


def add_review(new_browser):
    new_browser.find_element(By.XPATH, '//*[@id="tab-label-reviews-title"]').click()
    add_review_ = [
        '//*[@id="Rating_4_label"]', '//*[@id="nickname_field"]', '//*[@id="summary_field"]', '//*[@id="review_field"]',
        '//*[@id="review-form"]/div/div/button']
    data_to_fill_review = [
        "Add_Start",
        'UserTest',
        'Good Review Test',
        'Good !',
        None
    ]
    for element, data in zip(add_review_, data_to_fill_review):
        element_to_fill = WebDriverWait(new_browser, 15).until(EC.element_to_be_clickable((By.XPATH, element)))
        if data == "Add_Start":
            new_browser.execute_script("arguments[0].click();", element_to_fill)
            time.sleep(3)
            continue
        elif data:
            element_to_fill.send_keys(data)
        else:
            element_to_fill.click()
        time.sleep(2)


def user_random_data():
    get_user_data = requests.get('https://randomuser.me/api/')
    if get_user_data.status_code == 200:
        return get_user_data.json()


def monitor_request():
    while True:
        response = requests.get(request_url)
        if response.status_code == 200:
            print('Requisition Completed')
            break
        else:
            print('waiting...')
            time.sleep(1)


if __name__ == '__main__':
    url = 'https://magento.softwaretestingboard.com/'
    request_url = 'https://magento.softwaretestingboard.com/catalogsearch/result/?q=shirt'
    get_user_data = user_random_data()
    user_data = get_user_data['results'][0]

    # Create Log
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    log_file = 'test_report.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    logging.getLogger('').addHandler(file_handler)

    access_url(url)
