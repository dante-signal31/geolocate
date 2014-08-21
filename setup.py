from distutils.core import setup

setup(name="geolocate",
      version="0.1.0",
      description="This scripts scan given text to find urls and IP addresses. "
                  "The output is the same text but every url and IP address "
                  "is going to have its geolocation appended.",
      long_description=open("README.rst").read(),
      author="Dante Signal31",
      author_email="dante.signal31@gmail.com",
      license="LICENSE.txt",
      url="https://bitbucket.org/dante_signal31/geolocate",
      download_url="https://bitbucket.org/dante_signal31/geolocate/downloads",
      install_requires=["geoip2", "maxminddb"],
      packages=["geolocate", "tests"],
      # package_data={"pyqtmake": ["pyqtmakehelp.qhc",
      #                            "*.qm",
      #                            "pyqtmake_help/*.html"]},
      scripts=["run_tests.py", "geolocate/geolocate"],
      data_files=[(".", ["README.rst",]),]
      )
