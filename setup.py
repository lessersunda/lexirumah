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
        'clld>=3.1.0',
        'clldlucl',
        'clld-glottologfamily-plugin>=1.3.4',
        'pycldf',
        'pyconcepticon',
    ],
    tests_require=[
        'WebTest >= 1.3.1',  # py3 compat
        'mock',
    ],
    test_suite="lexibank",
    entry_points="""\
[paste.app_factory]
main = lexibank:main
""")
