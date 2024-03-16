import psycopg2
import requests

BASE_URL = "https://randomuser.me/api/?nat=gb"
PARTIES = ["MANAGEMENT PARTY", "SAVIOR PARTY", "TECH REPUBLIC PARTY"]


def create_tables(conn, cur):
    cur.execute(
        """
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_id VARCHAR(255) PRIMARY KEY,
                candidate_name VARCHAR(255),
                party_affiliation VARCHAR(255),
                biography TEXT,
                campaign_platform TEXT,
                photo_url TEXT
            )
        """
    )

    cur.execute(
        """
            CREATE TABLE IF NOT EXISTS voters (
                voter_id VARCHAR(255) PRIMARY KEY,
                voter_name VARCHAR(255),
                date_of_birth DATE,
                gender VARCHAR(255),
                nationality VARCHAR(255),
                registration_number VARCHAR(255),
                address_street VARCHAR(255),
                address_city VARCHAR(255),
                address_state VARCHAR(255),
                address_country VARCHAR(255),
                address_postcode VARCHAR(255),
                email VARCHAR(255),
                phone_number VARCHAR(255),
                picture TEXT,
                registered_age INTEGER
            )
        """
    )

    cur.execute(
        """
            CREATE TABLE IF NOT EXISTS votes (
                voter_id VARCHAR(255),
                candidate_id VARCHAR(255),
                voting_time TIMESTAMP,
                vote INTEGER DEFAULT 1,
                primary key(voter_id, candidate_id)
            )
        """
    )

    print("Tables")
    conn.commit()


def generate_candidate_data(candidate_number, total_parties):
    response = requests.get(BASE_URL + '&gender=' + ("female" if candidate_number % 2 == 1 else "male"))

    if response.status_code == 200:
        user = response.json()["results"][0]

        return {
            'candidate_id': user['login']['uuid'],
            'candidate_name': f"{user['name']['first']}  {user['name']['last']}",
            'party_affiliation': PARTIES[candidate_number],
            'biography': 'A brief biography of the candidate',
            'campaign_platform': "Key campaign promises and or platform",
            'photo_url': user['picture']['large']
        }

    else:
        return "Error fetching data"


def generate_voter_data():
    response = requests.get(BASE_URL)

    if response.status_code == 200:
        user = response.json()['results'][0]

        return {
            'voter_id': user['login']['uuid'],
            'voter_name': user['name']['first'] + " " + user['name']['last'],
            'date_of_birth': user['dob']['date'],
            'gender': user['gender'],
            'nationality': user['nat'],
            'registration_number': user['id']['value'],
            'address_street': f"{user['location']['street']['number']} {user['location']['street']['name']}",
            'address_city': user['location']['city'],
            'address_state': user['location']['state'],
            'address_country': user['location']['country'],
            'address_postcode': user['location']['postcode'],
            'email': user['email'],
            'phone_number': user['phone'],
            'registered_age': user['dob']['age'],
            'picture': user['picture']['large']
        }


if __name__ == '__main__':
    try:
        conn = psycopg2.connect("host=localhost dbname=voting user=postgres password=postgres")
        cur = conn.cursor()

        print(conn)
        create_tables(conn, cur)

        cur.execute("""
            SELECT * FROM candidates
        """)

        candidates = cur.fetchall()
        print(candidates)

        if len(candidates) == 0:
            for i in range(3):
                candidate = generate_candidate_data(i, 3)
                cur.execute("""INSERT INTO candidates(candidate_id, candidate_name, party_affiliation, biography, 
                campaign_platform, photo_url) VALUES (%s, %s, %s, %s, %s, %s)
                """, (candidate['candidate_id'], candidate['candidate_name'], candidate['party_affiliation'],
                      candidate['biography'],
                      candidate['campaign_platform'], candidate['photo_url']))

                conn.commit()

        cur.execute("""
            SELECT * FROM voters
        """)

        voters = cur.fetchall()

        if len(voters) == 0:
            i = 0
            while i < 1000:
                voter = generate_voter_data()

                cur.execute("""INSERT INTO voters(voter_id, voter_name, date_of_birth, gender, nationality, 
                registration_number,address_street, address_city, address_state, address_country, 
                address_postcode,email,phone_number,picture,registered_age) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s)""",
                            (voter['voter_id'], voter['voter_name'], voter['date_of_birth'], voter['gender'],
                             voter['nationality'], voter['registration_number'], voter['address_street'],
                             voter['address_city'],
                             voter['address_state'], voter['address_country'], voter['address_postcode'],
                             voter['email'], voter['phone_number'], voter['picture'], voter['registered_age'])
                            )

                i += 1
                conn.commit()

    except Exception as e:
        print(e)
