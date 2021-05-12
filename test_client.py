import urllib.request

contents = urllib.request.urlopen("http://localhost:8080/register").read()

print(contents)