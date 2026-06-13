import datetime
import subprocess

date = datetime.datetime.now().strftime('%d-%m-%Y')
filename = f"playtime_{date}"
compiler_string = fr'pyinstaller --onefile --hide-console hide-early --icon=images.ico -n {filename} Main.py'

print("compiling", compiler_string)
subprocess.run(compiler_string, shell=True,text=True,encoding='utf-8')
print('done')
