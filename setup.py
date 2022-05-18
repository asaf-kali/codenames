from setuptools import setup

WEB_DEPS = ["selenium~=4.1"]
ALL_DEPS = WEB_DEPS

setup(
    name="codenames",
    version="1.0.3",
    description="Codenames board game logic implementation in python.",
    author="Asaf Kali",
    author_email="akali93@gmail.com",
    url="https://github.com/asaf-kali/codenames",
    install_requires=[
        # Core
        "pydantic~=1.9",
        # CLI
        "beautifultable~=1.0",
    ],
    extras_require={
        "all": ALL_DEPS,
        "web": WEB_DEPS,
    },
    include_package_data=True,
)
