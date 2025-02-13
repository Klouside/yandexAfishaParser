from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Путь к Firefox и geckodriver
browser_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options = Options()
# Для отладки временно отключаем headless-режим, чтобы видеть окно браузера:
# options.add_argument("--headless")
options.add_argument("window-size=1920,1080")
options.binary_location = browser_path
options.set_preference("general.useragent.override",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0")
# Пробуем скрыть признак автоматизации (может помочь, если сайт фильтрует ботов)
options.set_preference("dom.webdriver.enabled", False)

service = Service(executable_path=r"C:\Users\Kana\Desktop\geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)


def get_links_from_page(url):
    driver.get(url)
    time.sleep(3)  # ждем первичную загрузку страницы

    # Если появляется окно согласия (cookies), попробуйте его закрыть
    try:
        consent = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button"))
        )
        if "cookie" in consent.text.lower():
            consent.click()
            print("Закрыто окно согласия (cookies).")
            time.sleep(2)
    except Exception:
        pass

    # Прокручиваем страницу несколько раз для загрузки ленивого контента
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Отладочный вывод: проверяем, есть ли в исходном коде нужный фрагмент
    page_source = driver.page_source
    if "eventCard.link" in page_source:
        print("Строка 'eventCard.link' найдена в исходном HTML.")
    else:
        print("Строка 'eventCard.link' не найдена в исходном HTML.")

    # Увеличиваем время ожидания до 60 секунд
    try:
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-test-id="eventCard.link"]')))
    except Exception as e:
        print("Элемент не найден через ожидание:", e)

    event_cards = driver.find_elements(By.CSS_SELECTOR, 'a[data-test-id="eventCard.link"]')
    print("Найдено элементов:", len(event_cards))
    links = []
    for card in event_cards:
        href = card.get_attribute("href")
        if href:
            links.append(href)
    return links


base_url = "https://afisha.yandex.ru/moscow/selections/nearest-events"
all_links = []
page = 1

while True:
    url = base_url if page == 1 else f"{base_url}?page={page}"
    print(f"\nОбрабатываем страницу {page}: {url}")
    links = get_links_from_page(url)
    if not links:
        print("На данной странице ссылки не найдены, завершаем сбор данных.")
        break
    all_links.extend(links)
    page += 1

driver.quit()

df = pd.DataFrame({'link': all_links})
# Сохраняем DataFrame в CSV (без индекса, кодировка UTF-8 с BOM для корректного отображения в Excel)
df.to_csv('afisha_links.csv', index=False, encoding='utf-8-sig')

print("Ссылки сохранены в файл afisha_links_msk.csv")
pd.set_option('display.max_colwidth', None)
print("\nНайденные ссылки:")
print(df)
