# «Пошта» ішкі жүйесі (13-нұсқа)

Курстық жоба: MS SQL Server дерекқоры + Python (Tkinter) бағдарламасы. Кесте, баған, процедура атаулары, деректер және бағдарлама терезесі толығымен қазақша.

| Файл | Не бар |
|---|---|
| `schema.sql` | `Pochta` дерекқоры мен кестелер (PK, FK, CHECK) |
| `data.sql` | Тестілік деректер |
| `queries.sql` | 5 сұраныс, 3 есеп, 4 тапсырма: сақталған процедуралар (`Сұраныс_1`…, `Есеп_1`…, `Тапсырма_1`…) |
| `app.py` | Бағдарлама: кестелерді көру, қосу, өзгерту, жою; сұраныстар, есептер, CSV-ге сақтау |
| `Пошта_скриншоттар.pdf`, `скриншоттар/` | Бағдарламаның 5 скриншоты және олардың қысқаша түсіндірмесі |

Бағдарлама бірінші рет іске қосылғанда дерекқорды өзі жасайды: үш `.sql` файлды кезекпен орындайды.
Дерекқорды басынан қайта жасау үшін SSMS немесе VS Code-та үш файлды кезекпен орында
(`schema.sql` ескі `Pochta` дерекқорын жойып, жаңасын жасайды).

## Windows-та іске қосу

1. **SQL Server 2022 Express** орнат (microsoft.com → SQL Server Downloads → Express → *Basic*).
   Инстанс аты `SQLEXPRESS` болады.
2. **SSMS** орнат (міндетті емес, кестелер мен процедураларды көрсету үшін керек).
3. **Python** орнат (python.org, орнатқанда *Add python.exe to PATH* белгісін қой).
4. Командалық жолда (cmd):
   ```
   pip install pyodbc
   python app.py
   ```
Бағдарлама Windows кіруімен қосылады (`localhost\SQLEXPRESS`, `Trusted_Connection`).
Егер «ODBC-драйвер табылмады» деп шықса, **ODBC Driver 18 for SQL Server** орнат.
Егер сервер аты басқа болса: `set DB_SERVER=КОМПЬЮТЕР\ИНСТАНС`, содан кейін `python app.py`.

## Mac-та іске қосу

SQL Server Docker ішінде жұмыс істейді (Docker Desktop іске қосулы болуы керек):
```
docker run -d --name kurs-mssql --platform linux/amd64 -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD=Kurs_Proekt_2026 -p 1433:1433 --restart unless-stopped mcr.microsoft.com/mssql/server:2022-latest
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18
pip3 install pyodbc
python3 app.py
```
VS Code-та көру үшін: **SQL Server (mssql)** кеңейтімі, сервер `localhost,1433`, логин `sa`, пароль `Kurs_Proekt_2026`.

## Қорғауда не көрсету керек

- Сол жақтағы қойындылар: **Кестелер** (қосу, өзгерту, жою), **Сұраныстар** 1–5, **Есептер** 1–3, **Тапсырмалар** 1–4.
- Параметр сұрайтын әрекеттерде кодтарды тиісті кестеден қара (мысалы, `Елдер`, `Қызметкерлер`).
- Кейбір күндер бүгінгі күннен есептеледі, сондықтан «осы ай» туралы сұраулар әрқашан нәтиже береді.
