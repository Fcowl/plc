import datetime
import subprocess
import os
from pathlib import Path
import time

date = datetime.datetime.now()
dist_path = Path(__file__).parent / 'dist'
files = os.listdir(dist_path)




def main():
    filename = f"playtime_{date.strftime('%d-%m-%Y')}"
    print(filename)

    while f"{filename}.exe" in files:
        filename_sp = list(filename)
        if filename_sp[-1] == ')' and filename_sp[-2].isdigit():
            filename_sp[-2] = str(int(filename_sp[-2])+1)
        else:
            filename_sp += ['(', '1', ')']
        filename = ''.join(filename_sp)

    print(filename)
    compiler_string = fr'pyinstaller --onefile --hide-console hide-early --icon=images.ico -n {filename} Main.py'
    t1 = time.time()
    print(f"compiling started {date.strftime('%H:%M:%S')} ", compiler_string)

    try:
        subprocess.run(compiler_string, shell=True,text=True,encoding='utf-8')
    except Exception as e:
        print('Error occured trying to compile')
        print(type(e).__name__ ,e )

    else:
        print(f'{filename}.exe compiled successfully')
        print(f'elapsed time: {round(time.time() - t1,3)}s')

    try:
        os.remove(f'{filename}.spec')
    except Exception as e:
        print('Error occurred trying to remove file')
        print(type(e).__name__ ,e )
    else:
        print('spec removed successfully')


if __name__ == '__main__':
    main()