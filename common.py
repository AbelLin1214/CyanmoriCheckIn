'''
Author: Abel
Date: 2023-05-22 15:21:52
LastEditTime: 2023-05-22 16:43:17
'''
import yaml
from pathlib import Path
from pydantic import BaseModel

class Account(BaseModel):
    '''账号'''
    name: str
    email: str
    password: str

    def __str__(self):
        return f'Account({self.name}, {self.email})'

class Config(BaseModel):
    '''配置'''
    headless: bool
    debug_level: str
    run_time: str
    accounts: list[Account]
    remote_port: int = None

    @classmethod
    def load(cls, path: str):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f'配置文件不存在: {path}, 请参照demo新建配置文件')
        data: dict = yaml.safe_load(p.read_text('utf-8'))
        data['accounts'] = [Account(**account) for account in data['accounts']]
        return cls(**data)
