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
driver_path = r"C:\Users\Klouside\Desktop\geckodriver.exe"

options = Options()
options.binary_location = browser_path
options.add_argument("window-size=1920,1080")

service = Service(executable_path=driver_path)
driver = webdriver.Firefox(service=service, options=options)

def get_event_details(url):
    driver.get(url)
    time.sleep(3)

    try:
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        ).text
    except:
        title = "Не найдено"

    try:
        date = driver.find_element(By.CSS_SELECTOR, 'span.session-date__day').text
        time_ = driver.find_element(By.CSS_SELECTOR, 'span.session-date__time').text
        date_time = f"{date} {time_}"
    except:
        date_time = "Не найдено"

    try:
        location = driver.find_element(By.CSS_SELECTOR, '[class="event-concert-description__place-name"]').text
    except:
        location = "Не найдено"

    try:
        description = driver.find_element(By.CSS_SELECTOR, '[data-test-id="eventInfo.description"]').text
    except:
        description = "Не найдено"

    try:
        rating = driver.find_element(By.CSS_SELECTOR, 'span.Value-ie9gjh-2').text
    except:
        rating = "Не найдено"

    try:
        theater = driver.find_element(By.CSS_SELECTOR, 'dd.event-attributes__category-value').text
    except:
        theater = "Не найдено"

    try:
        actors = [actor.text for actor in
                  driver.find_elements(By.CSS_SELECTOR, 'dd.event-attributes__category-value a')]
        actors = ", ".join(actors) if actors else "Не найдено"
    except:
        actors = "Не найдено"

    try:
        director = driver.find_element(By.XPATH, "//dt[contains(text(), 'Режиссёр')]/following-sibling::dd").text
    except:
        director = "Не найдено"

    try:
        duration = driver.find_element(By.XPATH, "//dt[contains(text(), 'Время')]/following-sibling::dd").text
    except:
        duration = "Не найдено"

    return {
        "Название": title,
        "Дата и время": date_time,
        "Место": location,
        "Описание": description,
        "Рейтинг": rating,
        "Театр": theater,
        "Актеры": actors,
        "Режиссер": director,
        "Продолжительность": duration
    }

# Чтение ссылок из файла
links_df = pd.read_csv('afisha_links.csv')
event_links = links_df['link'].tolist()  # Исправил 'links' -> 'link'


events_data = []
for link in event_links:
    event_details = get_event_details(link)
    events_data.append(event_details)

driver.quit()

df = pd.DataFrame(events_data)
pd.set_option('display.max_colwidth', None)
df.to_csv('afisha_events.csv', index=False)
print("\nДетали мероприятий:")
print(df)
