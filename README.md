

## Python AgentX Client library

Currently the code is capable of the following:

* Open a session with AgentX master, e.g. net-snmpd snmpd, and register a new session.
* Send Ping request.
* Register the ".1.3.6.1.4.1.36985" MIB region.
* Respond to SNMP GET request for the value ".1.3.6.1.4.1.36985.100.1.0"

Example:

    $ snmpget -v2c -c public localhost .1.3.6.1.4.1.36985.100.1.0
    iso.3.6.1.4.1.36985.100.1.0 = Counter32: 1000


## SNMP Agent Configuration

You need to make sure the SNMP agent (snmpd) will act as AgentX master:

    master          agentx

Also make sure the SNMP agent accept requests for your MIB region:

    view   systemonly  included   .1.3.6.1.4.1.36985

To help debugging AgentX protocol run snmpd in foreground debug mode:

    sudo /usr/sbin/snmpd -f -Lsd  -Dagentx -Le -u snmp -g snmp -I -smux -p /var/run/snmpd.pid

