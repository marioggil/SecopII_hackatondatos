import py_compile
try:
    py_compile.compile('app/databaseUpgrade.py')
    print("Syntax OK")
except Exception as e:
    print(e)
