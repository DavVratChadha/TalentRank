from setuptools import setup, find_packages

setup(
    name='talentrank',
    version='0.0.1',
    author='Dav Vrat Chadha',
    author_email='davvratchadha1@gmail.com',
    description='An advanced information retrieval and recommendation system for ranking job candidates.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/DavVratChadha/TalentRank',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'chromadb>=0.5.20',
        'pandas>=1.5.3',
        'numpy>=1.26.0',
        'sentence-transformers>=2.2.2'
    ],
    entry_points={
        'console_scripts': [
            'talentrank=talentrank.main:main',
            'TalentRank=talentrank.main:main',
        ],
    },
    include_package_data=True,
)