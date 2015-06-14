from setuptools import setup


setup(
    name = "pyagentx",
    version = "0.2",
    author = "Rayed Alrashed",
    author_email = "rayed@rayed.com",
    description = ("AgentX package to extend SNMP with pure Python"),
    license = "BSD",
    keywords = "snmp network agentx ",
    url = "https://github.com/rayed/pyagentx",
    packages=['pyagentx'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Environment :: No Input/Output (Daemon)",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
    ],
    long_description='''\
PyAgentX
--------------------
pyagentx is a pure Python implementation of AgentX protocol (RFC 2741), it
will allow you to extend SNMP agent (snmpd) by writing AgentX subagents,
without modifying your original SNMP agent.

''',
)
