class User():
    id = 0
    username = ''
    email = ''
    name = ''
    password = ''

    def __init__(self, username, email, password, name = ''):
        self.username = username
        self.email = email
        self.name = name
        self.password = password

