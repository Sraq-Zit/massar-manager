

from massar.user import User


if __name__ == '__main__':
    user = User('username', 'password').login().set_language('fr').scrap_students()

    for section in user.by_sections.values():
        print(section)