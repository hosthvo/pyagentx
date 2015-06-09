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


### SNMP Agent Configuration

You need to make sure the SNMP agent (snmpd) will act as AgentX master:

    master          agentx

Also make sure the SNMP agent accept requests for your MIB region:

    view   systemonly  included   .1.3.6.1.3.9999   # CHANGE ACCORDINGLY

To help debugging AgentX protocol run snmpd in foreground debug mode:

    sudo /usr/sbin/snmpd -f -Lsd  -Dagentx -Le -u snmp -g snmp -I -smux -p /var/run/snmpd.pid


### Test It

Run the sub agent and keep it running:

	sudo ./main.py 

Then from another terminal query the master SNMP agent:

    $ snmpwalk -v2c -c public localhost .1.3.6.1.3.9999
    SNMPv2-SMI::experimental.9999.100.1.0 = Counter32: 1000
	SNMPv2-SMI::experimental.9999.100.2.0 = Counter32: 2000
	SNMPv2-SMI::experimental.9999.100.3.0 = STRING: "String for 100 MIB"
	SNMPv2-SMI::experimental.9999.200.1.0 = Counter32: 1433822190
	SNMPv2-SMI::experimental.9999.200.2.0 = Counter32: 2000
	SNMPv2-SMI::experimental.9999.200.3.0 = STRING: "String for 200 MIB"
	SNMPv2-SMI::experimental.9999.200.3.0 = No more variables left in this MIB View (It is past the end of the MIB tree)



### FAQ

- What's the difference between AgentX, SMUX and proxied SNMP?
  Check the anser [here] 
  (http://net-snmp.sourceforge.net/wiki/index.php/FAQ:Agent_08)
- What is advatages of extending SNMP using agentx instead of something like "pass\_perssist"?
  I started pyagentx because I couldn't write a DateAndTime value using "pass\_perssist" which can't handle binary data very well.
  Another important reason is the decouple of master SNMP agent and its sub agents, which means you can start/stop one without affecting the other, and you don't have to change the snmpd.conf every time you want to add or remove a sub agent.
- Why do I need sudo to run my agentx agent?
  By default "snmpd" uses UNIX socket to communicate with agentx sub agents, it uses special permisssions to prevent unauthorized agents.  
  If you don't want to use "root" to run the agent you can use "agentXPerms" directive in snmpd.conf, check the man page for its options.
  


### TODO

* Ping agentx master periodically.
* Helper function for tables.

