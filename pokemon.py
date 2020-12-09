import re
import sqlite3
import urllib.request
from bs4 import BeautifulSoup


BASE_URL = "https://www.pokemon.com"
conn = sqlite3.connect("pokemon.sqlite")
cur = conn.cursor()

cur.executescript(
    """
CREATE TABLE IF NOT EXISTS Pokemon(
    Number      INTEGER PRIMARY KEY,
    Name        TEXT UNIQUE,
    Type        TEXT,
    Category_id INTEGER,
    Gender_id   INTEGER,
    Height      TEXT,
    Weight      FLOAT,
    Description TEXT
);

CREATE TABLE IF NOT EXISTS Category (
    id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    category TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Gender (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    gender TEXT UNIQUE
)
"""
)

cur.execute("SELECT Number, Name FROM Pokemon ORDER BY Number DESC LIMIT 1")
row = cur.fetchone()
if row is None:
    url = f"{BASE_URL}/us/pokedex/bulbasaur"
    start = 0
else:
    start = row[0]
    start_name = row[1].lower()
    url = f"{BASE_URL}/us/pokedex/{start_name}"

count = 1
while True:
    if count < start:
        count = start
        continue
    try:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
    except KeyboardInterrupt:
        print("Interrupted by user.")
        break
    except:
        print("Error occured!!!")
        break

    # Getting all details of the Pokemon
    div = soup.find("div", {"class": "pokedex-pokemon-pagination-title"})
    num_str = re.findall("#([0-9]+)", div.text)[0]
    number = int(num_str)
    name = re.findall(r"(.+)\s+", div.text.strip())[0]
    if count != number:
        print(f"{count-1} Pokemon added to database")
        break
    print("Loading:", name)
    all_details = soup.find("div", {"class": "info match-height-tablet"})
    type_details = all_details.contents[5]
    types = ""
    for a_tag in type_details.find_all("a"):
        if "type" in a_tag.get("href"):
            types = types + ", " + a_tag.text
    category_details = all_details.contents[1].contents[3]
    details = all_details.contents[1].contents[1]
    height = details.find_all("span")[1].text
    if len(height.split("'")[0]) < 2:
        height = "0" + height
    weight = float(details.find_all("span")[3].text[:-3])
    gender_details = details.find_all("i")
    if len(gender_details) == 2:
        gender = "Male, Female"
    elif len(gender_details) == 1:
        class_attr = gender_details[0].get("class")[1]
        gender = re.findall(r"_(\S+)_", class_attr)
        gender = gender[0].title()
    else:
        gender = "Unknown"
    category = category_details.find_all("span")[1].text
    p_tag = soup.find("p", {"class": "version-x"})
    description = p_tag.text.strip()

    cur.execute("INSERT OR IGNORE INTO Gender (gender) VALUES (?)", (gender,))
    cur.execute("SELECT id FROM Gender WHERE gender = ? ", (gender,))
    gender_id = cur.fetchone()[0]

    cur.execute(
        "INSERT OR IGNORE INTO Category (category) VALUES (?)", (category,)
    )
    cur.execute("SELECT id FROM Category WHERE category = ? ", (category,))
    category_id = cur.fetchone()[0]

    cur.execute(
        "INSERT OR IGNORE INTO Pokemon VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            number,
            name,
            types[2:],
            category_id,
            gender_id,
            height,
            weight,
            description,
        ),
    )

    # Getting URL for next Pokemon
    a_tag = soup.find("a", {"class": "next"})
    url = BASE_URL + a_tag.get("href")
    if count % 20 == 0:
        conn.commit()
    count += 1

conn.commit()
conn.close()
