from setuptools import setup

BASE_DEPS = [
    # Core
    "pydantic==1.9.0",
    # CLI
    "beautifultable~=1.0",
]
WEB_DEPS = ["selenium~=4.1"]
ALL_DEPS = BASE_DEPS + WEB_DEPS

setup(
    name="codenames",
    version="1.2.4",
    description="Codenames board game logic implementation in python.",
    author="Asaf Kali",
    author_email="akali93@gmail.com",
    url="https://github.com/asaf-kali/codenames",
    install_requires=BASE_DEPS,
    extras_require={
        "all": ALL_DEPS,
        "web": WEB_DEPS,
    },
    include_package_data=True,
)
