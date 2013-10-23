## Python AgentX Implementation

''pyagentx'' is pure Python implementation of AgentX protocol (RFC 2741), it will allow you to extend SNMP agent (snmpd) by writing AgentX subagents, without modifying your original SNMP agent.

Some SNMP agents can be extended using many mechanisms, e.g. net-snmp can be extended using:

* running external commands (exec, extend, pass)
* loading new code dynamically (embedded perl, dlmod)
* communicating with other agents (proxy, SMUX, AgentX)

Check "EXTENDING AGENT FUNCTIONALITY" in snmpd.conf man page for more details.

[RFC 2741: Agent Extensibility (AgentX) Protocol Version 1]
(http://www.ietf.org/rfc/rfc2741.txt)

### Status

Currently the code is capable of the following:

* Open a session with AgentX master, e.g. net-snmpd snmpd, and register a new session.
* Send Ping request.
* Register multiple MIB regions.
* Respond to SNMP GET request for values.
* Respond to SNMP GETNEXT request for values.
* Multiple MIB update method with custom frequency for each.


Example:

    $ snmpget -v2c -c public localhost .1.3.6.1.3.9999.100.1.0
    iso.3.6.1.3.9999.100.1.0 = Counter32: 1000



### SNMP Agent Configuration

You need to make sure the SNMP agent (snmpd) will act as AgentX master:

    master          agentx

Also make sure the SNMP agent accept requests for your MIB region:

    view   systemonly  included   .1.3.6.1.3.9999

To help debugging AgentX protocol run snmpd in foreground debug mode:

    sudo /usr/sbin/snmpd -f -Lsd  -Dagentx -Le -u snmp -g snmp -I -smux -p /var/run/snmpd.pid


### FAQ

[What's the difference between AgentX, SMUX and proxied SNMP?]
(http://net-snmp.sourceforge.net/wiki/index.php/FAQ:Agent_08)


### TODO

* Ping agentx master periodically.
* Helper function for tables.
* Tick isn't really once per second, need fixing.
