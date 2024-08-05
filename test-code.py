@app.route('/view_user_books')
@login_required
def view_user_books():
    connect = sqlite3.connect('mytest.db')
    cursor = connect.execute('SELECT * FROM user_books;')
    usern = cursor.fetchall()
    cursor = connect.execute('SELECT id FROM user;')
    userid = cursor.fetchall()
    print("printing......")
    print(usern)
    print("user id: ", userid)
    cc=userid[0]
    print("printingcc", cc)
    cursor = connect.execute('SELECT book_id FROM user_books where name = ?', (cc))
    useridcc = cursor.fetchall()
    print("printing useridccc: ", useridcc)
    for i in useridcc:
        
      cursor = connect.execute('SELECT title FROM books where id = ?', (i))
      useridcc = cursor.fetchall()
      print(i)

    connect.close()
    if usern:
        return usern[0][2]  # Access the first tuple and the third element which is the username
    else:
        return "No books found for this user."
    #return render_template('home.html', books=books, user_name=current_user.name, is_admin=current_user.is_admin)

