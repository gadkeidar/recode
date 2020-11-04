import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='recode',
    version='0.0.1',
    author='Gad Keidar',
    author_email='gadkeidar@gmail.com',
    description='Converts ICD-10 codes to CDC/NCHS Selected Causes of Death codes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gadkeidar/recode',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing :: General',
    ],
    python_requires='>=3.8',
)
