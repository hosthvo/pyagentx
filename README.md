
# Looking for a New Maintainer

Please contact me if you are interested on maintaining the package!


# Python AgentX Implementation

"pyagentx" is pure Python implementation of AgentX protocol (RFC 2741), it will allow you to extend SNMP agent (snmpd) by writing AgentX subagents, without modifying your original SNMP agent.

[RFC 2741: Agent Extensibility (AgentX) Protocol Version 1]
(http://www.ietf.org/rfc/rfc2741.txt)


## Features

Currently the code is capable of the following:

* Open a session with AgentX master, e.g. net-snmpd snmpd, and register a new session.
* Send Ping request.
* Register multiple MIB regions.
* Multiple MIB update classes with custom frequency for each.
* Support snmpset operations.
* Reconnect/Retry to master, in case the master restarted.


## Installation

The package is registered on [Python Package Index](https://pypi.python.org/) under the name  "pyagentx" [https://pypi.python.org/pypi/pyagentx](https://pypi.python.org/pypi/pyagentx).

You can install it by simply running:

    pip install pyagentx


## SNMP Agent Configuration

You need to make sure the SNMP agent (snmpd) will act as AgentX master:

    master          agentx

Also make sure the SNMP agent accept requests for your MIB region:

    # NET-SNMP-EXAMPLES-MIB
    view   systemview  included   .1.3.6.1.4.1.8072.2

__NOTE__: You need to change the OID to reflect your own OID.

## Minimal Agent

To implement agent you need to provide one "Agent" class and one or more "Updater" classes, a sample code:

    import pyagentx

    # Updater class that set OID values
    class NetSnmpPlaypen(pyagentx.Updater):
        def update(self):
            self.set_INTEGER('1.0', 1000)
            self.set_OCTETSTRING('3.0', 'String for NET-SNMP-EXAMPLES-MIB')

    class MyAgent(pyagentx.Agent):
        def setup(self):
            # Register Updater class that responsd to
            # the tree under "netSnmpPlaypen": 1.3.6.1.4.1.8072.9999.9999
            self.register('1.3.6.1.4.1.8072.9999.9999', NetSnmpPlaypen)

    # Main
    pyagentx.setup_logging()
    try:
        a = MyAgent()
        a.start()
    except Exception as e:
        print "Unhandled exception:", e
        a.stop()
    except KeyboardInterrupt:
        a.stop()

To test:

    snmpwalk -v 2c -c public localhost NET-SNMP-MIB::netSnmpPlaypen


## Example Agent

To test the implementation I wrote an example agent that implement small parts of
[NET-SNMP-EXAMPLES-MIB](http://www.net-snmp.org/docs/mibs/NET-SNMP-EXAMPLES-MIB.txt) including a table.

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

SNMP Set example:

    $ snmpset -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleInteger.0 i 10
    # pass without errors, if not check snmpd.conf permissions

    $ snmpset -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleInteger.0 i 200
    # wrongValue error

    $ snmpset -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleString.0 s "Test"
    # notWritable error


## FAQ


### What OID should I use for my agent?

If you are just playing and experminting you can put everything under "NET-SNMP-MIB::netSnmpPlaypen" OID "1.3.6.1.4.1.8072.9999.9999" tree, but you shouldn't use it for any public work.

If you need to publish your work you should apply for your own enterprise OID on the IANA [PEN Application page](http://pen.iana.org/pen/PenApplication.page), this will give you your own private tree, e.g. Net-Snmp uses 1.3.6.1.4.1.8072, Google uses 1.3.6.1.4.1.11129

So your company would have an OID 1.3.6.1.4.1.xxxxx

You also need to write your own MIB to allow your customer to use in thier Network Managment System (NMS):

<http://www.net-snmp.org/wiki/index.php/Writing_your_own_MIBs>


### Is there other ways to extend SNMP agent?

Some SNMP agents can be extended using many mechanisms, e.g. net-snmp can be extended using:

* running external commands (exec, extend, pass)
* loading new code dynamically (embedded perl, dlmod)
* communicating with other agents (proxy, SMUX, AgentX)

Check "EXTENDING AGENT FUNCTIONALITY" in snmpd.conf man page for more details.

### What's the difference between AgentX, SMUX and proxied SNMP?

Check the answer [here](http://net-snmp.sourceforge.net/wiki/index.php/FAQ:Agent_08)   

### What is advatages of extending SNMP using agentx instead of something like "pass\_perssist"?
 
I started pyagentx because I couldn't write a DateAndTime value using "pass\_perssist" which can't handle binary data very well.
  
Another important reason is the decouple of master SNMP agent and its sub agents, which means you can start/stop one without affecting the other, and you don't have to change the snmpd.conf every time you want to add or remove a sub agent.

### Why do I need sudo to run my agentx agent?

By default "snmpd" uses UNIX socket to communicate with agentx sub agents, it uses special permisssions to prevent unauthorized agents.

If you don't want to use "root" to run the agent you can use "agentXPerms" directive in snmpd.conf, check the man page for its options.
  
### My agent connected to the master but I couldn't get result with snmpwalk?

First make sure you can get result from the agent, try something basic:

    snmpwalk -v 2c -c public localhost .
    
If the command doesn't return anything double check your agent community and Access List.

If it works on standard OIDs but it doesn't work on your sub agent, make sure you include the correct OID view:

    view   systemview  included   .1.3.6.1.4.1.8072.2 

### How can I test it on Mac OSX?

SNMP agent from net-snmp is already installed on OSX, but first you need to load it:

    sudo launchctl load -w /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist

Then you can start and stop it with these commands:

    sudo launchctl start org.net-snmp.snmpd
    sudo launchctl start org.net-snmp.snmpd

configuration file can be found on the default location "/etc/snmp/snmpd.conf".

