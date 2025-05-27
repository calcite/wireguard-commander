import yaml
from fastapi import HTTPException, status



def get_yaml(filename: str) -> dict:
    with open(filename, 'r+') as fd:
        return yaml.load(fd, Loader=yaml.FullLoader)