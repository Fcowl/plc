from pathlib import Path

class EmptyBackupErr(Exception):
    pass

def create_backup(backup_file:Path, save_file:str) -> None:
    if not backup_file.exists():
        backup_file.touch()
    with open(save_file, 'r',encoding='utf-8') as f:
        data = f.read()
    with open(backup_file, 'w',encoding='utf-8') as f:
        f.write(data)

def recover_backup(backup_file:Path, save_file:str) -> None:
    if backup_file.stat().st_size == 0:
        raise EmptyBackupErr('')
    # todo ошибку
    with open(backup_file, 'r',encoding='utf-8') as f:
        rec_data = f.read()
    with open(save_file,'w',encoding='utf-8') as f:
        f.write(rec_data)


# тут тоже поменялось