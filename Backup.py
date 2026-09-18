from pathlib import Path

def create_backup(backup_file:Path, save_file:str) -> None:
    if not backup_file.exists():
        backup_file.touch()
    with open(save_file, 'r',encoding='utf-8') as f:
        data = f.read()
    with open(backup_file, 'w',encoding='utf-8') as f:
        f.write(data)

def recover_backup(backup_file:Path, save_file:str) -> None:
    print('backuping')
    with open(backup_file, 'r',encoding='utf-8') as f:
        rec_data = f.read()
    with open(save_file,'w',encoding='utf-8') as f:
        f.write(rec_data)
