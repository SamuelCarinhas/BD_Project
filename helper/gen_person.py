import bcrypt

persons = [
'Ebony Herrera',
'Debra Buchanan',
'Bertha Rodriquez',
'Carolyn Porter',
'Peter Roberts',
'Aaron Henry',
'Darrin Allison',
'May Patterson',
'Celia Medina',
'Luis Zimmerman',
'Pablo Bowman',
'Faith Willis',
'Kayla Gonzalez',
'Benny Silva',
'Derek Fisher',
'Corey Glover',
'Dora Fowler',
'Joseph Cooper',
'Cheryl Ward',
'Grace Wells',
'Alice Davis',
'Raul Santos',
'Charlene Alvarado',
'Abel Baker',
'Ira Aguilar',
'Jesse May',
'Hector Swanson',
'Ashley Simon',
'Natasha Campbell',
'Veronica Lindsey',
'Sherman Klein',
'Homer Lloyd',
'Roger Clark',
'Francisco Massey',
'Eloise Adams',
'Monica Collins',
'Gina Barnes',
'Allen Moore',
'Sonja Bailey',
'Kate Ross',
'Terry Mathis',
'Nora Blake',
'Virgil Peterson',
'Louis Craig',
'Delores Carlson',
'Bennie Turner',
'Jimmy Tucker',
'Justin Jackson',
'Emanuel Malone',
'Emilio Waters',
'Lillian Saunders',
'Noah Rios',
'Eileen Brewer',
'Velma Murray',
'Loren King',
'Mathew Rose',
'Brent Paul',
'Shawn Ball',
'Lisa Powell',
'Amber Montgomery',
'Irene Caldwell',
'Peggy Snyder',
'Blake Arnold',
'Debbie Richards',
'Wilbur Lamb',
'Lloyd Tyler',
'Marvin Figueroa',
'Sheila Cobb',
'Rufus Vaughn',
'Jackie Moody',
'Salvador Lane',
'Eduardo Bowers',
'Leonard Johnston',
'Casey Gibbs',
'Alison Vargas',
'Susan Mclaughlin',
'Lawrence Oliver',
'Willie Lewis',
'Gerald Moran',
'Emma Hammond',
'Leo Barker',
'Tommy Howell',
'Irvin Mccormick',
'Timothy Hunt',
'Alicia Murphy',
'Loretta Mcdonald',
'Marcos Christensen',
'Jeannette Park',
'Anna Henderson',
'Alyssa Watkins',
'Hilda Bishop',
'Geoffrey Townsend',
'Arlene Guzman',
'Darnell Ruiz',
'Hubert Thornton',
'Ernest Foster',
'Stacey Barnett',
'Craig Cohen',
'Delia Holland',
'Lester Graves',
]

import random
import string

letters = string.ascii_lowercase

def generate_hash(password):
    # https://pypi.org/project/bcrypt/
    return bcrypt.hashpw(password, bcrypt.gensalt(8))


def check_password(password, password_hash):
    # https://pypi.org/project/bcrypt/
    return bcrypt.checkpw(password, password_hash)

for person in persons:
    username = person.lower().replace(' ', '_')
    email = '%s@gmail.com' % (username)
    password = ''.join(random.choice(letters) for i in range(10))
    print("insert into users(username, email, password) values ('%s', '%s', '%s'); --- password = %s" %(username, email, generate_hash(password), password))
