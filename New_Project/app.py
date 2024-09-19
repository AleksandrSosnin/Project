import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import mysql.connector
from datetime import datetime

# Функция для валидации и форматирования дат
def format_date(event=None, entry=None):
    text = entry.get().replace('.', '')
    if len(text) > 8:
        text = text[:8]
    new_text = ''
    for i in range(len(text)):
        if i in (2, 4):
            new_text += '.'
        new_text += text[i]
    entry.delete(0, tk.END)
    entry.insert(0, new_text)

# Функция для проверки формата дат
def validate_date_format(date_str):
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False

# Функция для отправки запроса к API Яндекс Метрики и получения данных
def export_data_to_db(api_ключ, номер_визита, дата_начала, дата_окончания, выбранные_поля):
    # URL для API Яндекс Метрики
    api_url = 'https://api-metrika.yandex.net/stat/v1/data'
    
    # Параметры запроса к API
    params = {
        'ids': номер_визита,
        'metrics': ','.join(выбранные_поля),
        'date1': datetime.strptime(дата_начала, "%d.%m.%Y").strftime("%Y-%m-%d"),
        'date2': datetime.strptime(дата_окончания, "%d.%m.%Y").strftime("%Y-%m-%d"),
        'oauth_token': api_ключ
    }

    # Отправка запроса
    response = requests.get(api_url, params=params)

    # Проверка успешности запроса
    if response.status_code == 200:
        data = response.json()
        save_to_mysql(data)  # Сохранение данных в базу данных MySQL
        messagebox.showinfo("Успех", "Данные успешно выгружены и сохранены в базу данных.")
    else:
        messagebox.showerror("Ошибка", f"Ошибка при запросе к API: {response.status_code}\n{response.text}")

# Функция для сохранения данных в MySQL
def save_to_mysql(data):
    # Настройки подключения к MySQL (замените на свои данные)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="yandex_metrika"
    )
    cursor = conn.cursor()

    # Пример вставки данных (адаптируйте под ваши поля)
    for row in data['data']:
        query = """
        INSERT INTO metrika_data (field1, field2, field3)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (row['dimensions'][0]['name'], row['metrics'][0], row['metrics'][1]))

    conn.commit()
    cursor.close()
    conn.close()

# Функция для запуска выгрузки данных
def start_data_export():
    номер_визита = номер_визита_entry.get()
    api_ключ = api_ключ_entry.get()
    дата_начала = дата_начала_entry.get()
    дата_окончания = дата_окончания_entry.get()

    # Валидация полей
    if not номер_визита.isdigit():
        messagebox.showerror("Ошибка", "Номер визита должен быть числом.")
        return
    if not api_ключ:
        messagebox.showerror("Ошибка", "API ключ не может быть пустым.")
        return
    if not validate_date_format(дата_начала):
        messagebox.showerror("Ошибка", "Дата начала должна быть в формате ДД.ММ.ГГГГ.")
        return
    if not validate_date_format(дата_окончания):
        messagebox.showerror("Ошибка", "Дата окончания должна быть в формате ДД.ММ.ГГГГ.")
        return

    выбранные_поля = [fields_list[i] for i, var in enumerate(checkbox_vars) if var.get()]

    if not выбранные_поля:
        messagebox.showerror("Ошибка", "Выберите хотя бы одно поле для выгрузки.")
        return

    export_data_to_db(api_ключ, номер_визита, дата_начала, дата_окончания, выбранные_поля)

# Поля для выбора
fields_list = [
    'ym:s:counterID', 
    'ym:s:watchIDs', 'ym:s:productBrand' 
    'ym:s:productName', 'ym:s:regionArea',
    'ym:s:<attribution>DirectClickOrder', 'ym:s:date', 'ym:s:dateTime', 'ym:s:dateTimeUTC', 'ym:s:isNewUser',
    'ym:s:startURL', 'ym:s:endURL', 'ym:s:pageViews', 'ym:s:visitDuration', 'ym:s:bounce', 'ym:s:ipAddress',
    'ym:s:regionCountry', 'ym:s:regionCity', 'ym:s:clientID', 'ym:s:networkType', 'ym:s:goalsID',
    'ym:s:goalsDateTime', 'ym:s:goalsPrice', 'ym:s:goalsOrder', 'ym:s:goalsCurrency', 'ym:s:lastTrafficSource',
    'ym:s:lastAdvEngine', 'ym:s:lastReferalSource', 'ym:s:lastSearchEngineRoot', 'ym:s:lastSearchEngine',
    'ym:s:lastSocialNetwork', 'ym:s:lastSocialNetworkProfile', 'ym:s:referer', 'ym:s:lastDirectClickOrder',
    'ym:s:lastDirectBannerGroup', 'ym:s:lastDirectClickBanner', 'ym:s:lastDirectClickOrderName',
    'ym:s:lastClickBannerGroupName', 'ym:s:lastDirectClickBannerName', 'ym:s:lastDirectPhraseOrCond',
    'ym:s:lastDirectPlatformType', 'ym:s:lastDirectPlatform', 'ym:s:lastDirectConditionType', 'ym:s:lastCurrencyID',
    'ym:s:from', 'ym:s:UTMCampaign', 'ym:s:UTMContent', 'ym:s:UTMMedium', 'ym:s:UTMSource', 'ym:s:UTMTerm',
    'ym:s:openstatAd', 'ym:s:openstatCampaign', 'ym:s:openstatService', 'ym:s:openstatSource', 'ym:s:hasGCLID',
    'ym:s:lastGCLID', 'ym:s:firstGCLID', 'ym:s:lastSignificantGCLID', 'ym:s:browserLanguage', 'ym:s:browserCountry',
    'ym:s:clientTimeZone', 'ym:s:deviceCategory', 'ym:s:mobilePhone', 'ym:s:mobilePhoneModel', 'ym:s:operatingSystem',
    'ym:s:browser', 'ym:s:browserMajorVersion', 'ym:s:browserMinorVersion', 'ym:s:browserEngine',
    'ym:s:browserEngineVersion1', 'ym:s:browserEngineVersion2', 'ym:s:browserEngineVersion3', 'ym:s:browserEngineVersion4',
    'ym:s:cookieEnabled', 'ym:s:javascriptEnabled', 'ym:s:flashMajor', 'ym:s:flashMinor', 'ym:s:screenFormat',
    'ym:s:screenColors', 'ym:s:screenOrientation', 'ym:s:screenWidth', 'ym:s:screenHeight', 'ym:s:physicalScreenWidth',
    'ym:s:physicalScreenHeight', 'ym:s:windowClientWidth', 'ym:s:windowClientHeight', 'ym:s:purchaseID',
    'ym:s:purchaseDateTime', 'ym:s:purchaseAffiliation', 'ym:s:purchaseRevenue', 'ym:s:purchaseTax',
    'ym:s:purchaseShipping', 'ym:s:purchaseCoupon', 'ym:s:purchaseCurrency', 'ym:s:purchaseProductQuantity',
    'ym:s:productsPurchaseID', 'ym:s:productsID', 'ym:s:productsName', 'ym:s:productsBrand', 'ym:s:productsCategory',
    'ym:s:productsCategory1', 'ym:s:productsCategory2', 'ym:s:productsCategory3', 'ym:s:productsCategory4',
    'ym:s:productsCategory5', 'ym:s:productsVariant', 'ym:s:productsPosition', 'ym:s:productsPrice', 'ym:s:productsCurrency',
    'ym:s:productsCoupon', 'ym:s:productsQuantity', 'ym:s:impressionsURL', 'ym:s:impressionsDateTime',
    'ym:s:impressionsProductID', 'ym:s:impressionsProductName', 'ym:s:impressionsProductBrand',
    'ym:s:impressionsProductCategory', 'ym:s:impressionsProductCategory1', 'ym:s:impressionsProductCategory2',
    'ym:s:impressionsProductCategory3', 'ym:s:impressionsProductCategory4', 'ym:s:impressionsProductCategory5',
    'ym:s:impressionsProductVariant', 'ym:s:impressionsProductPrice', 'ym:s:impressionsProductCurrency',
    'ym:s:impressionsProductCoupon', 'ym:s:offlineCallTalkDuration', 'ym:s:offlineCallHoldDuration', 'ym:s:offlineCallMissed',
    'ym:s:offlineCallTag', 'ym:s:offlineCallFirstTimeCaller', 'ym:s:offlineCallURL', 'ym:s:visitID'
]

# Создание основного окна
root = tk.Tk()
root.title("Приложение для выгрузки данных Яндекс Метрики")
root.geometry("600x700")

# Метки и поля ввода
tk.Label(root, text="Номер визита:").pack()
номер_визита_entry = tk.Entry(root)
номер_визита_entry.pack()

tk.Label(root, text="API ключ:").pack()
api_ключ_entry = tk.Entry(root)
api_ключ_entry.pack()

tk.Label(root, text="Дата начала (ДД.ММ.ГГГГ):").pack()
дата_начала_entry = tk.Entry(root)
дата_начала_entry.pack()
дата_начала_entry.bind('<KeyRelease>', lambda event: format_date(event, дата_начала_entry))

tk.Label(root, text="Дата окончания (ДД.ММ.ГГГГ):").pack()
дата_окончания_entry = tk.Entry(root)
дата_окончания_entry.pack()
дата_окончания_entry.bind('<KeyRelease>', lambda event: format_date(event, дата_окончания_entry))

# Секция выбора полей
fields_frame = tk.Frame(root)
fields_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(fields_frame)
scrollbar = ttk.Scrollbar(fields_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

checkbox_vars = []
for field in fields_list:
    var = tk.IntVar(value=1)  # Галочки установлены по умолчанию
    checkbox = tk.Checkbutton(scrollable_frame, text=field, variable=var)
    checkbox.pack(anchor="w")
    checkbox_vars.append(var)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Кнопка для запуска процесса
tk.Button(root, text="Запустить выгрузку данных", command=start_data_export).pack()

# Запуск главного цикла программы
root.mainloop()
