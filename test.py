from itertools import groupby

urls = ["asd", "qwe", "qwe", "vhdi", "njdu"]
print(urls)
urls = [i for i, _ in groupby(urls)]  # удаляем дубли

print(urls)