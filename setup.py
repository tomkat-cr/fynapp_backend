import os
from setuptools import setup

requires = (
        "attrs==21.2.0", 
        "certifi==2018.11.29", 
        "cffi==1.15.0", 
        "click==8.0.3", 
        "cryptography==35.0.0", 
        "dnspython==1.16.0", 
        "Flask==2.0.2", 
        "Flask-Cors==3.0.10", 
        "gunicorn==20.1.0", 
        "iniconfig==1.1.1", 
        "itsdangerous==2.0.1", 
        "Jinja2==3.0.2", 
        "MarkupSafe==2.0.1", 
        "packaging==21.0", 
        "pluggy==1.0.0", 
        "py==1.10.0", 
        "pycairo==1.20.1", 
        "pycparser==2.20", 
        "PyJWT==2.3.0", 
        "pymongo==4.0.1", 
        "pyparsing==3.0.0", 
        "PyYAML==6.0", 
        "six==1.16.0", 
        "toml==0.10.2", 
        "Werkzeug==2.0.2", 
        "wheel==0.37.1"
        )

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "FynApp `Backend",
    # version = "0.1.1",
    version=read('version.txt'),
    author = "Carlos J. Ramirez MEDIABROS",
    author_email = "cramirez@mediabros.com",
    description = ("FynApp Backend"),
    license = "BSD",
    keywords = "health calorie deficit intermitent fasting fitness",
    url = "http://packages.python.org/fynapp_api",
    packages=['fynapp_api',],
    # namespace_packages = ['fynapp_api'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    # long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License"
    ],
)