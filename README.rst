=========
geolocate
=========

This program accepts any text and searchs inside every IP address. With
each of those IP addresses, geolocate queries `Maxmind GeoIP database <http://www.maxmind.com>`_
to look for the city and country where IP or URL is located.

Geolocate is designed to be used in console with pipes and redirections along
with applications like traceroute, etc.

Geolocate's output is the same text than input but each IP address is going to
have appended its country, city and long-lat coordinates (depending on verbosity
level).

See `wiki <https://github.com/dante-signal31/geolocate/wiki>`_ for more detailed info.

**Author:** Dante Signal31
**e-mail:** dante.signal31@gmail.com

News
----

* **2015-05-03:** Geolocate version 1.2.0 released. Now geolocate includes its
  own gzip decompressor, so its no longer needed as an external dependency.
* **2015-04-10:** Geolocate version 1.1.0 released. Now geolocate includes its
  own downloader, so its no longer needed as an external dependency.
* **2015-03-14:** Geolocate version 1.0.0 released.