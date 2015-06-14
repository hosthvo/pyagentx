## Python AgentX Implementation

"pyagentx" is pure Python implementation of AgentX protocol (RFC 2741), it will allow you to extend SNMP agent (snmpd) by writing AgentX subagents, without modifying your original SNMP agent.

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
* Multiple MIB update classes with custom frequency for each.
* Reconnect/Retry to master, in case the master restarted


### Installation

The package is registered on [Python Package Index](https://pypi.python.org/) under the name 
"pyagentx" [https://pypi.python.org/pypi/pyagentx](https://pypi.python.org/pypi/pyagentx)

You can install it by simply running:

    pip install pyagentx


### SNMP Agent Configuration

You need to make sure the SNMP agent (snmpd) will act as AgentX master:

    master          agentx

Also make sure the SNMP agent accept requests for your MIB region:

    # NET-SNMP-EXAMPLES-MIB
    view   systemview  included   .1.3.6.1.4.1.8072.2

To help debugging AgentX protocol run snmpd in foreground debug mode:

    sudo /usr/sbin/snmpd -f -Lsd  -Dagentx -Le -u snmp -g snmp -I -smux -p /var/run/snmpd.pid


### Example Agent

To test the implementation I wrote an example agent that implement small part of 
[NET-SNMP-EXAMPLES-MIB] (http://www.net-snmp.org/docs/mibs/NET-SNMP-EXAMPLES-MIB.txt)

To run the sub agent:

	sudo ./example-agent.py 

Then from another terminal query the master SNMP agent.

Scalar example:

    $ snmpwalk -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleScalars
    NET-SNMP-EXAMPLES-MIB::netSnmpExampleInteger.0 = INTEGER: 1000
    NET-SNMP-EXAMPLES-MIB::netSnmpExampleString.0 = STRING: String for NET-SNMP-EXAMPLES-MIB

Table example:

    $ snmptable -v 2c -c public -Ci localhost NET-SNMP-EXAMPLES-MIB::netSnmpIETFWGTable 
    SNMP table: NET-SNMP-EXAMPLES-MIB::netSnmpIETFWGTable
    
       index nsIETFWGChair1 nsIETFWGChair2
    "group1"     "member 1"     "member 2"
    "group2"     "member 1"     "member 2"


### FAQ

- What's the difference between AgentX, SMUX and proxied SNMP?

  Check the answer [here](http://net-snmp.sourceforge.net/wiki/index.php/FAQ:Agent_08)
- What is advatages of extending SNMP using agentx instead of something like "pass\_perssist"?

  I started pyagentx because I couldn't write a DateAndTime value using "pass\_perssist" which can't handle binary data very well.
  Another important reason is the decouple of master SNMP agent and its sub agents, which means you can start/stop one without affecting the other, and you don't have to change the snmpd.conf every time you want to add or remove a sub agent.

- Why do I need sudo to run my agentx agent?

  By default "snmpd" uses UNIX socket to communicate with agentx sub agents, it uses special permisssions to prevent unauthorized agents.  
  If you don't want to use "root" to run the agent you can use "agentXPerms" directive in snmpd.conf, check the man page for its options.
  


### TODO

* Ping agentx master periodically.
* Helper function for tables.

