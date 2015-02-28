from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
with open(path.join(here, 'wiki/Home.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="geolocate",
      version="1.0.0",
      description="This script scans given text to find urls and IP addresses. "
                  "The output is the same text but every url and IP address "
                  "is going to have its geolocation appended.",
      long_description=long_description,
      author="Dante Signal31",
      author_email="dante.signal31@gmail.com",
      license="GPLv3",
      url="https://bitbucket.org/dante_signal31/geolocate",
      download_url="https://bitbucket.org/dante_signal31/geolocate/downloads",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: System Administrators',
                   'Intended Audience :: Telecommunications Industry',
                   'Intended Audience :: Other Audience',
                   'Topic :: System :: Networking',
                   'Topic :: Security',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4'],
      keywords="geolocation ip addresses",
      install_requires=["geoip2>=2.1.0", "maxminddb>=1.1.1", "requests>=2.5.0"],
      packages=find_packages(exclude=["tests*"]),
      entry_points={'console_scripts': ['geolocate=geolocate.geolocate:main', ],
                    },
      data_files=[("etc", ["geolocate/etc/geolocate.conf", ]),
                  ("local_database", ["", ])]
      )
