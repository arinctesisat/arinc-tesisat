with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('desc TEXT', '"desc" TEXT')
code = code.replace('(name, desc, icon, img, video)', '(name, "desc", icon, img, video)')
code = code.replace('SET name=?, desc=?, icon=?', 'SET name=?, "desc"=?, icon=?')
code = code.replace('(img, title, desc)', '(img, title, "desc")')
code = code.replace('SET title=?, desc=?', 'SET title=?, "desc"=?')
code = code.replace('(vid_path, title, desc)', '(vid_path, title, "desc")')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed desc keyword')
