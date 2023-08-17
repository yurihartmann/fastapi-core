import os

result = os.popen("ls").read()
print("o resultado foi: ", str(result))