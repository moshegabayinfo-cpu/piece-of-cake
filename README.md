# עדכון: .env ולוגים של SQL

1. התקינו מחדש את requirements.txt באמצעות Python של .venv.
2. פתחו את .env שנמצא ליד app.py ומלאו את הסיסמה, למשל:

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=poc
PGUSER=postgres
PGPASSWORD='your_actual_password'
```

הסיסמה בקובץ המקורי ריקה בכוונה; מלאו אותה פעם אחת ושמרו.
אפשר להשתמש גם בגרשיים כפולים. אין להוסיף רווחים או תווים לסיסמה עצמה.
הקובץ הוא טקסט מקומי לא מוצפן ונמצא ב-.gitignore. אל תשלחו את .env לאחר מילויו.
בקובץ להפצה יש לשתף רק .env.example ללא סיסמה.
משתני סביבה מפורשים מקבלים עדיפות: אם PGPASSWORD ישן מוגדר במסוף, הסירו אותו:

```powershell
Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
```

לאחר שינוי .env הפעילו מחדש את השרת.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py --check-db
.\.venv\Scripts\python.exe app.py
```

אין צורך להזין סיסמה במסוף. במסד חדש מריצים --init-db קודם.
בפתרון הברכה, מסד קיים דורש את migrations/001_add_greeting.sql כפי שמוסבר בהמשך.

## מה רואים בלוגים

- SQL QUERY: השאילתה עם מצייני המקום, ללא הדפסת רשימת הפרמטרים.
- SQL OK: סטטוס, מספר שורות וזמן ביצוע במילישניות.
- SQL RESULT: הנתונים ש-fetchone או fetchall החזירו ליישום, כולל תוצאה ריקה.
- SQL ERROR: קוד השגיאה והסבר PostgreSQL. השגיאה עדיין מטופלת ביישום.

db_logging.py מגדיר LoggingCursor, ו-connect() משתמש בו דרך cursor_factory.
תוצאות אינן נקראות פעמיים. SQL OK מציין הצלחת פקודה, לא אישור commit של עסקה שלמה.
INSERT עם RETURNING id ידפיס גם את מזהה ההזמנה. UPDATE ללא RETURNING ידפיס מספר שורות שהושפעו.
הלוגים מודפסים למסוף. הם כוללים את נתוני ההזמנות ולכן יש לשתף רק פלט רלוונטי.
סיסמת החיבור מושחרת בלוגי SQL ואינה מודפסת בפרטי החיבור.


---

# Piece of Cake (POC)

עדכון אבחון: הקוד מציג כעת את סיבת שגיאת PostgreSQL במסוף בלי להציג סיסמה,
ומוודא שגם הטבלאות קיימות לפני שהאתר עולה. `--check-db` בודק חיבור וגם טבלאות.
להחלפת גרסה קיימת מספיק להחליף app.py; לא מוחקים מסד או הזמנות.

פרויקט לימודי בסיסי: קטלוג עוגות, הזמנה, ניהול הזמנות ומשלוחים.
Python 3.10 ומעלה, Flask ו-PostgreSQL. שם מסד הנתונים: `poc`.

## 1. יצירת מסד הנתונים

הפעילו PostgreSQL ופתחו pgAdmin. מתוך Query Tool של מסד `postgres`
הריצו את הפקודה הבאה פעם אחת, כפקודה נפרדת:

```sql
CREATE DATABASE poc;
```

אפשר גם: לחיצה ימנית על Databases > Create > Database > השם poc.
אם poc כבר קיים אין צורך ליצור אותו שוב. השתמשו במסד ייעודי לפרויקט,
ללא טבלאות אחרות בשם products או orders.

## 2. התקנת ספריות

חלצו את כל תיקיית הפרויקט. פתחו PowerShell בתיקייה שבה נמצא app.py:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

אין צורך להפעיל Activate, ולכן אין צורך לשנות את Execution Policy של Windows.

## 3. יצירת טבלאות ומוצרי דוגמה

```powershell
.\.venv\Scripts\python.exe app.py --init-db
```

כשתופיע `PostgreSQL password:` הזינו את סיסמת postgres שבחרתן בהתקנה.
בזמן ההקלדה לא יופיעו תווים - זו התנהגות רגילה. הסיסמה אינה נשמרת בקבצים.
הפקודה יוצרת את הטבלאות ואת שלוש עוגות הדוגמה ומסיימת. היא אינה מפעילה את האתר.
אפשר להריץ אותה שוב: הנתונים הקיימים אינם נמחקים ומוצרי הדוגמה אינם מוכפלים.
זו אינה מערכת מיגרציות: שינוי עתידי במבנה טבלה דורש ALTER TABLE.

ברירת המחדל היא localhost:5432, משתמש postgres ומסד poc.
אם התקנתן בפורט אחר או עם משתמש אחר, הגדירו לפני ההרצה, למשל:

```powershell
$env:PGPORT = "5433"
$env:PGUSER = "my_user"
```

אפשר גם להגדיר PGHOST ו-PGDATABASE. אין לכתוב סיסמה בתוך קוד או לשלוח אותה במייל.
הקוד תומך גם ב-PGPASSWORD אם כבר מוגדר בסביבה; אחרת יבקש סיסמה בכל הפעלה.

## 4. בדיקת החיבור והפעלת האתר

```powershell
.\.venv\Scripts\python.exe app.py --check-db
.\.venv\Scripts\python.exe app.py
```

הזינו סיסמה בכל פקודה אם תתבקשו. ההודעה `Connected to poc` מאשרת חיבור אמיתי.

- קטלוג: http://127.0.0.1:8000
- ניהול הזמנות ומשלוחים: http://127.0.0.1:8000/admin
- עצירה: Ctrl+C במסוף.
- אם פורט 8000 תפוס: `app.py --port 8001` באמצעות אותו Python של הסביבה.

## איך הקוד מחולק

| קובץ | תפקיד |
| --- | --- |
| app.py | החיבור למסד, כתובות האתר, אימות ושמירת הנתונים |
| schema.sql | הגדרת products ו-orders ומוצרי דוגמה |
| templates/ | עמודי HTML; Jinja ממלא אותם בנתונים ומבצע escaping |
| static/style.css | עיצוב האתר ואיורי העוגות ב-CSS |
| tests/test_app.py | בדיקות אינטגרציה מול PostgreSQL אמיתי |

## זרימת הנתונים

1. GET / קורא מוצרים באמצעות SELECT ומציג קטלוג.
2. GET /order/1 מציג טופס למוצר שנבחר.
3. POST לאותו נתיב בודק שם, טלפון, כמות, מועד ואופן קבלה.
4. המחיר נקרא מהמסד ונשמר עם ההזמנה באמצעות INSERT ופרמטרים (%s).
5. החיבור מבצע commit, ואז הדפדפן מופנה לעמוד אישור עם מספר הזמנה.
6. GET /admin מבצע JOIN בין המוצרים וההזמנות ומחשב מחיר כפול כמות.
7. POST ממסך הניהול מעדכן את הסטטוס באמצעות UPDATE.

בהזמנת משלוח חובה כתובת. באיסוף עצמי הכתובת אינה נשמרת.
כל הזמנה כוללת סוג עוגה אחד וכמות של 1 עד 20. אפשר להזמין למחר והלאה.
המחירים בשקלים. אין תוספת משלוח בדוגמה ואין חיוב מקוון.
הטלפון נבדק כשדה טקסט לא ריק עם מגבלת אורך, ללא אימות מספר טלפון אמיתי.

זרימת סטטוסים:

- איסוף: חדשה -> בהכנה -> מוכנה -> נאספה.
- משלוח: חדשה -> בהכנה -> מוכנה -> יצאה למשלוח -> נמסרה.
- לפני סיום אפשר לבטל. ביטול וסיום הם מצבים סופיים בדוגמה.

## בדיקה ידנית לתלמידות

1. צרו הזמנת איסוף של 2 עוגות שוקולד. הסכום צריך להיות 280 ש״ח.
2. ודאו שההזמנה מופיעה בניהול ובטבלת orders ב-pgAdmin.
3. העבירו אותה בהכנה, מוכנה, נאספה.
4. צרו משלוח עם כתובת והעבירו אותו עד נמסרה.
5. נסו לשלוח משלוח ללא כתובת ותאריך שכבר עבר. השמירה צריכה להיחסם.
6. הפעילו מחדש את האתר ובדקו שההזמנות נשמרו.

שאילתה להצגת ההזמנות ב-pgAdmin של poc:

```sql
SELECT o.id, o.customer_name, p.name, o.quantity,
       o.unit_price * o.quantity AS total,
       o.fulfillment, o.address, o.due_date, o.status
FROM orders o
JOIN products p ON p.id = o.product_id
ORDER BY o.id DESC;
```

## בדיקות אוטומטיות

נדרש חיבור PostgreSQL פעיל עם הרשאה ליצור schema. הבדיקות יוצרות schema זמני
בשם אקראי ומוחקות רק אותו בסיום; הן אינן משנות את נתוני public.
הגדירו PGHOST, PGPORT, PGUSER ו-PGDATABASE לפי המסד הייעודי לבדיקה.
אם אין PGPASSWORD, הרצת הבדיקות תבקש את הסיסמה באופן מוסתר.

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest tests -v
```

## תקלות נפוצות

- connection refused: שירות PostgreSQL אינו פועל, או ש-host/port שגויים.
- password authentication failed: בדקו את הסיסמה ושם המשתמש.
- database poc does not exist: צרו poc לפי שלב 1.
- relation products does not exist: הריצו app.py --init-db.
- ModuleNotFoundError: השתמשו ב-Python מתוך .venv והתקינו requirements.txt.

## היקף הדוגמה

האתר מיועד להרצה מקומית בלבד: אין התחברות למנהל, סל מרובה מוצרים,
בדיקת קיבולת ייצור, סליקה, הודעות ללקוח או מעקב שליחים במפה.
ניהול משלוחים בדוגמה כולל כתובת, מועד וסטטוס ידני.
יש אימות טפסים, אסימון CSRF, escaping ושאילתות פרמטריות.
לפני פרסום נדרשים בין השאר משתמשי מנהל, הרשאות ושרת הפקה.

מקורות: [Flask](https://flask.palletsprojects.com/en/stable/quickstart/),
[Psycopg](https://www.psycopg.org/psycopg3/docs/basic/params.html).
#   H i   e v e r y o n e !  
 