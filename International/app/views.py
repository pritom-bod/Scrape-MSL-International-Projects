from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import os
import time


BASE_DIR = settings.BASE_DIR


def international_Project(request):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    chromedriver_path = os.path.join(BASE_DIR, 'chromedriver-win64', 'chromedriver.exe')
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        url = "https://maxwellstampltd.com/pds/"
        driver.get(url)
        time.sleep(5)

        select = Select(driver.find_element(By.NAME, "_sfm_country[]"))     
        country_options = [opt.text.strip() for opt in select.options if opt.get_attribute('value') and opt.text.strip().lower() != 'bangladesh']

        data = []

        for country_name in country_options:
            
            select = Select(driver.find_element(By.NAME, "_sfm_country[]"))
            select.select_by_visible_text(country_name)
            time.sleep(4)

            project_elements = driver.find_elements(By.CSS_SELECTOR, "h2 > a")

            for project in project_elements:
                title = project.text.strip()
                data.append({
                    "Project Name": title,
                    "Country": country_name
                })


        if not data:
            print("No international projects found!")

        #Save to Excel


        df = pd.DataFrame(data)

        output_dir = os.path.join(BASE_DIR, 'media', 'scrape')
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, 'international_projects.xlsx')
        df.to_excel(output_path, index=False)

        print("Excel file saved at:", output_path)

        return render(request, 'app/download_page.html')

    finally:
        driver.quit()

##make downloadable
def download_excel(request):
    file_path = os.path.join(BASE_DIR, 'media', 'scrape', 'international_projects.xlsx')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="international_projects.xlsx"'
            return response
    return HttpResponse("File not found")
