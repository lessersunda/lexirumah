from setuptools import setup, find_packages


setup(
    name='lexirumah',
    version='0.2',
    description='lexibank clone for the LexiRumah webapp',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clld',
        'clldlucl',
        'clld-glottologfamily-plugin',
        'csvw',
        'pycldf',
        'sqlalchemy',
        'waitress',
        'pyconcepticon',
    ],
    extras_require={
        'dev': [
            'flake8',
            'tox'
        ],
        'test': [
            'mock',
            'psycopg2',
            'pytest>=3.1',
            'pytest-clld',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    test_suite="lexirumah",
    entry_points="""\
[paste.app_factory]
main = lexirumah:main
""")
