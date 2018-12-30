===========================
 Home Automation Utilities
===========================

This library facilitates home automation scripts for an OpenZWave system.
I use it with my local network, ``spicerack.parry.org``.
The scripts can easily be adapted for any home.
The library isn't production-ready, however, so only a Python programmer will find this useful.

Requirements
============

This library has been tested with Python 2.7 and Python 3.4.
It is implemented on top of `python-openzwave <https://github.com/OpenZWave/python-openzwave>`_.
An OpenZWave thrift server and STOMP server need to be running.
It is best if you already have a system with a functioning OpenZWave setup.

The following Python packages need to be present:

* astral
* enum
* six
* sortedcontainers
* stompy
* thrift
* tzlocal

For example, these commands get a system ready::

    sudo apt-get install python-enum34 python-pip python-six python-sortedcontainers python-stompy python-thrift rubygems-integration
    pip install astral tzlocal
    gem install stompserver
    git clone https://github.com/OpenZWave/python-openzwave.git
    pushd python-openzwave
    make
    sudo make install
    popd

Installation
============

The installation procedure is incomplete.
For now, I am running all the commands from ``/usr/local/src/homeauto``.

Usage
=====

A file called ``spicerack.py`` should be created to hold all the local network information.
The ``schedule_daily_scenes.py`` script should be changed so that the times and switch names match those in your local ``spicerack.py``.

The ``schedule_daily_scenes.py`` script should be scheduled to run once at the beginning of each day.
This can be done with the following command::

    ( crontab -l ; echo '0 0 * * * /usr/local/src/homeauto/schedule_daily_scenes.py' ) | crontab -

The network can be controlled using these ad-hoc commands:

* ``ozwd_get_value.py``
* ``ozwd_set_value.py``
* ``dim.py``
* ``pulse.py``
* ``ozwd_set_details.py``
* ``ozwd_get_all_values.py``
