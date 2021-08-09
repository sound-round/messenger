from messenger.client import network

# contents = urllib.request.urlopen("http://127.0.0.1:8080/register").read()

# print(contents)


# типы клиента
# 1) Command line client -
# 2) Desktop ui client - tkinter,
# 3) web client - some python web libraries%s


import tkinter as tk
from messenger.client import mainmenu

# TODO каждый экран в отдельный файл
# TODO работа с базой данных в отдельные файлы
# TODO move client to sqlite


def main():
    root = tk.Tk()
    root.title("messenger")
    root.geometry('320x568')

    mainmenu.display_mainmenu(root)

    root.mainloop()


if __name__ == '__main__':
    main()
