# -- How to set 2 apps in Openshift
from bs4 import BeautifulSoup
import requests
import psycopg2
from flask import Flask

application = Flask(__name__)

def init_table():
    url = r"https://en.wikipedia.org/wiki/List_of_stations_of_the_Paris_M%C3%A9tro"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find('table')
    data = []
    nbr_stations = 0

    connection = connect_postgres()
    cursor = connection.cursor()

    for tr in table.findAll('tr'):
        index = 0
        station = ""
        lignes = []
        for td in tr.findAll('td')[::3]:
            for a in td.findAll('a'):
                if index == 0:
                    index += 1
                    station = a.text
                    nbr_stations += 1
                    #print(station)
                else:
                    lignes.append(a.text)
                    #print(lignes)
                    index += 1
                    data.append([station, lignes])

    print(data)

    for x in data:
        for t in x[1]:
            if len(x[1]) > 1:
                for i in t:
                    try:
                        cursor.execute("""INSERT INTO metro_data (name,ligne)
                        VALUES (%s,%s::integer)""", (x[0], i))
                    except (Exception, psycopg2.DatabaseError) as error:
                        val = error
                    connection.commit()
            else:
                try:
                    cursor.execute("""INSERT INTO metro_data (name,ligne)
                    VALUES (%s,%s::integer)""", (x[0], x[1]))
                except (Exception, psycopg2.DatabaseError) as error:
                    val = error
                connection.commit()

    return nbr_stations

def connect_postgres():
    try:
        connect_str = "dbname='metro' user='metro' host='localhost' " + \
        "password='metro'"
        print("Connecting to database\n	->%s" % (connect_str))
        # use our connection values to establish a connection
        conn = psycopg2.connect(connect_str)
        print("Connected!\n")
    except Exception as e:
        print("Uh oh, can't connect. Invalid dbname, user or password?")
    return conn



@application.route("/")
def hello():
    nb_stations = init_table()
    return 'Nombre de stations : {}'.format(nb_stations)

if __name__ == "__main__":
    application.run()
