from setuptools import setup, find_packages

setup(
    name='random_teams',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2-binary',
        'pydantic-settings'
    ],
)