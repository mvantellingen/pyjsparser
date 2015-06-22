try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    
version = '0.1'

setup(
    name="pyjsparser",
    version=version,
    description="Python Javascript lexer/parser",
    long_description="""""",
    keywords='javascript ecmascript lexer parser ply',
    license='BSD License',
    author='Michael van Tellingen',
    author_email='michaelvantellingen@gmail.com',
    url='',
    packages=['pyjsparser'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    setup_requires=[
        'nose'
    ],
    install_requires=[
        "ply>=3.2"  
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
    ]
)
