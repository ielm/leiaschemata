from setuptools import setup, find_packages

setup(
    name="LEIASchemata",
    version="1.0.2",
    packages=find_packages(),

    install_requires=[
        "Flask==1.0.2",
        "Flask-Cors==3.0.7",
        "Flask-SocketIO==3.3.1",
        "pymongo==3.6.1",
        "boto3==1.7.6",
    ],

    author="Ivan Leon",
    author_email="leoni@rpi.edu",
    description="LEIA Schema Service and API",
    keywords="schema",
    project_urls={
        "Documentation": "https://app.nuclino.com/LEIA/Knowledge/",
        "Source Code": "https://bitbucket.org/ielm/leiaschemata/src/master/",
    }
)
