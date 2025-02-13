from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Настройка параметров Firefox
options = Options()
browser_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.binary_location = browser_path
options.set_preference("general.useragent.override",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0")
# Пробуем скрыть признак автоматизации (может помочь, если сайт фильтрует ботов)
options.set_preference("dom.webdriver.enabled", False)

service = Service(executable_path=r"C:\Users\Klouside\Desktop\geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)

def get_event_details(url):
    driver.get(url)
    time.sleep(4)
    try:
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        ).text
    except:
        title = "Не найдено"
    try:
        location = driver.find_element(By.CSS_SELECTOR, '[class="event-concert-description__place-name"]').text
    except:
        location = "Не найдено"

    try:
        description = driver.find_element(By.CSS_SELECTOR, '[data-test-id="eventInfo.description"]').text
    except:
        description = "Не найдено"

    # Считывание тегов только из блока event-concert-heading__info
    try:
        tags_elements = driver.find_elements(By.CSS_SELECTOR, "div.event-concert-heading__info ul.event-concert-heading__tags li.tags__item")
        tags = [tag.text for tag in tags_elements]
    except:
        tags = []

    return {
        "Название": title,
        "Место": location,
        "Описание": description,
        "Теги": tags
    }



# Чтение ссылок из файла
links_df = pd.read_csv('afisha_links_msk.csv')
event_links = links_df['link'].tolist()  # Исправил 'links' -> 'link'

events_data = []

for link in event_links[500:1000]:
    event_details = get_event_details(link)
    events_data.append(event_details)

driver.quit()

df = pd.DataFrame(events_data)
pd.set_option('display.max_colwidth', None)
df.to_csv('afisha_events_msk2.csv', index=False)
print("\nДетали мероприятий:")
print(df)
