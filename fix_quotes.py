with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('DEFAULT "#001d3d"', "DEFAULT '#001d3d'")
code = code.replace('DEFAULT "#ffc300"', "DEFAULT '#ffc300'")
code = code.replace('DEFAULT "Yıllık Tecrübe"', "DEFAULT 'Yıllık Tecrübe'")
code = code.replace('DEFAULT "21+"', "DEFAULT '21+'")
code = code.replace('DEFAULT "Profesyonel Ekip"', "DEFAULT 'Profesyonel Ekip'")
code = code.replace('DEFAULT "12+"', "DEFAULT '12+'")
code = code.replace('DEFAULT "Mutlu Müşteri"', "DEFAULT 'Mutlu Müşteri'")
code = code.replace('DEFAULT "5000+"', "DEFAULT '5000+'")
code = code.replace('DEFAULT "Şehir Dışı Hizmet"', "DEFAULT 'Şehir Dışı Hizmet'")
code = code.replace('DEFAULT "15+"', "DEFAULT '15+'")
code = code.replace('DEFAULT "Plumber"', "DEFAULT 'Plumber'")
code = code.replace('DEFAULT 0', 'DEFAULT 0') # unchanged

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed quotes in app.py')
