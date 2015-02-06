=========
geolocate
=========
This program accepts any text and searchs inside every IP address. With
each of them, geolocate queries `Maxmind GeoIP database <http://www.maxmind.com>`_
to look for the city and country where IP or URL is located.

Geolocate is designed to be used in console with pipes and redirections along
with applications like traceroute, etc. Geolocate's output is the same text
than input but IP is going to have appended its country and city.

It has two main running modes:

* Stream mode: used to parse piped output from other programs.

.. sourcecode:: bash

 $ traceroute -n www.google.com | ./geolocate.py -v 3 -s
 traceroute to www.google.com (216.58.210.164 [North America | United States | Mountain View | 37.419200000000004, -122.0574]), 30 hops max, 60 byte packets
 1  * * *
 2  * * *
 3  * * *
 4  * * *
 5  * * *
 6  5.53.1.82 [Europe | Spain | Unknown city | 40.0, -4.0]  12.277 ms  9.252 ms  8.790 ms
 7  209.85.252.150 [North America | United States | Mountain View | 37.419200000000004, -122.0574]  19.491 ms  16.614 ms  16.687 ms
 8  216.239.50.27 [Europe | United Kingdom | Unknown city | 51.5, -0.13]  16.614 ms  16.010 ms  16.025 ms
 9  216.58.210.164 [North America | United States | Mountain View | 37.419200000000004, -122.0574]  15.988 ms  14.372 ms  14.321 ms

* Text mode: used to parse a given string of text.

.. sourcecode:: bash

 $ ./geolocate.py "216.58.210.132" -v 3
 216.58.210.132 [North America | United States | Mountain View | 37.419200000000004, -122.0574]

For further information about how to use geolocate refer to next sections:

* `Installation <INSTALLATION>`_
* `Usage <USAGE>`_
* `Recommendations <RECOMMENDATIONS>`_

If you find geolocate useful and want to support its development,
you may wish give a `donation through Paypal <https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L43GKWTXB5QDA&lc=ES&item_number=geolocate&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHostedZ>`_

**Author:** Dante Signal31
**e-mail:** dante.signal31@gmail.com