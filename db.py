import sqlite3

connect = sqlite3.connect('mytest.db')
cursor = connect.cursor()



# Create book table
cursor.execute('''
select DISTINCT name from user_books;

               
''')


connect.commit()
results = cursor.fetchall()

for row in results:
    print(row)

connect.close()
