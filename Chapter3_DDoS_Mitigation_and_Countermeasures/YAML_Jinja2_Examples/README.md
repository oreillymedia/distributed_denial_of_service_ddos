#Using YAML and Jinja2 for A10 Thunder TPS Config Generation

##Usage

1. Require jinja2 and pyyaml, i.e. pip install pyyaml jinja2 
```
$ python config_generate.py tps_base_config.yaml tps_base_config_template.txt
```

##Output
```
!
system anomaly log
system attack log
system ddos-attack log
!
glid 1
  description "10gbps rate limiter"
  bit-rate-limit 10000000
!
glid 2
  description "1gbps rate limiter"
  bit-rate-limit 1000000
!
ddos protection enable
ddos protection rate-interval 1sec

<skip>

ntp server 1.1.1.1

ntp server 2.2.2.2
!

$
```

##Overview

Jinja2, http://jinja.pocoo.org/docs/dev/, is a template engine widely used in Python web frameworks. Besides rendering HTML pages, it can also be used to render text files, such as A10 Thunder TPS configuration file. 

YAML, http://yaml.org/, is a language independent, human friendly way to serialize data for your programming language of choice. 

Together, we can use YAML to store the variable data that changes for each device to feed into the relatively static template file to generate network configuration files. 

#Quick Jinja2 Walk Thru
```
# {{ varaible }} is used as a placeholder 
>>> from jinja2 import Template
>>> t1 = Template("Hello {{ name }}")
>>> t1.render(name="Eric")
u'Hello Eric'
>>>
>>> configTemplate = Template("hostname {{ name }}")
>>> configTemplate.render(name="TPS4435")
u'hostname TPS4435'
>>>

# Render with a Python dictionary
>>> t2 = Template("neighbor {{ neighbor.ip }} remote-as {{ neighbor.remoteAS }}")
>>> neighbor1 = {"ip": "1.1.1.1", "remoteAS": "100"}
>>> t2.render(neighbor=neighbor1)
u'neighbor 1.1.1.1 remote-as 100'
>>>

# doing a loop
>>> devices = ["device1", "device2"]
>>> template = """
... {% for device in devices %}
... I like {{ device }}
... {% endfor %}
... """
>>> t3 = Template(template)
>>> t3.render(devices=devices)
u'\n\nI like device1\n\nI like device2\n'
>>>

There are a ton more features in Jinja2, please check out http://jinja.pocoo.org/docs/dev/.
```
 
##Quick YAML Walk Thru
```
# YAML files starts with "---" at the top

# This is a YAML dictionary
Name: Eric

# This is a YAML list
Likes:
  - Basketball
  - Football

# Combination
Teams:
  NBA:
    - Lakers
    - Warriors
  NFL:
    - Seahawks

# Example

echou-a10:tmp echou$ cat test.yml
---
Name: Eric

Likes:
  - Basketball
  - Football

Teams:
  NBA:
    - Lakers
    - Warriors
  NFL:
    - Seahawks


echou-a10:tmp echou$
echou-a10:tmp echou$ python
>>> import yaml
>>> with open('test.yml') as f:
...     dict = yaml.load(f)
...
>>> dict
{'Likes': ['Basketball', 'Football'], 'Name': 'Eric', 'Teams': {'NBA': ['Lakers', 'Warriors'], 'NFL': ['Seahawks']}}
>>>

Please check out http://yaml.org/ for more types.

```

## Putting it all together
```
echou-a10:a10_simple_example echou$ cat tps_base_config.yaml
---

glid1:
  description: "\"10gbps rate limiter\""
  bitRateLimit: 10000000


glid2:
  description: "\"1gbps rate limiter\""
  bitRateLimit: 1000000


ddosZoneTemplateTCP:
  name: "tcp-protect1"


ddosZoneTemplateUDP:
  name: "udp-protect1"
  spoofDetectTimeout: 5
  spoofDetectMinDelay: 2


logging: 10.10.10.10


bgp:
  asn: 2
  routerID: 11.11.11.11
  routeMap:
    ddosAdvertise: "ddos-advertise"
  neighbors:
    - ip: 12.12.12.12
      remoteAS: 1
      description: "upstream"
    - ip: 13.13.13.13
      remoteAS: 1
      description: "downsteam"

ntpServer:
 - 1.1.1.1
 - 2.2.2.2

echou-a10:a10_simple_example echou$ cat tps_base_config_template.txt
!
system anomaly log
system attack log
system ddos-attack log
!
glid 1
  description {{ config.glid1.description }}
  bit-rate-limit {{ config.glid1.bitRateLimit }}
!
glid 2
  description {{ config.glid2.description }}
  bit-rate-limit {{ config.glid2.bitRateLimit }}
!
ddos protection enable
ddos protection rate-interval 1sec
!
ddos zone-template tcp {{ config.ddosZoneTemplateTCP.name }}
  syn-authentication send-rst
  syn-authentication pass-action authenticate-src
  syn-authentication fail-action drop
!
ddos zone-template udp {{ config.ddosZoneTemplateUDP.name }}
  spoof-detect timeout {{ config.ddosZoneTemplateUDP.spoofDetectTimeout }}
  spoof-detect min-delay {{ config.ddosZoneTemplateUDP.spoofDetectMinDelay }}
  spoof-detect pass-action authenticate-src
  spoof-detect fail-action drop
  known-resp-src-port action drop
!
logging host {{ config.logging }}
!
router bgp {{ config.bgp.asn }}
  bgp router-id {{ config.bgp.routerID }}
  bgp log-neighbor-changes
  {% for neighbor in config.bgp.neighbors %}
  neighbor {{ neighbor.ip }} remote-as {{ neighbor.remoteAS }}
  neighbor {{ neighbor.ip }} description {{ neighbor.description }}
  neighbor {{ neighbor.ip }} route-map {{ config.bgp.routeMap.ddosAdvertise }} out
  {% endfor %}
!
route-map ddos-advertise permit 1
!
{% for ntp_server in config.ntpServer %}
ntp server {{ ntp_server }}
{% endfor %}
!
!


echou-a10:a10_simple_example echou$ cat config_generate.py
#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
import yaml, sys

ENV = Environment(loader=FileSystemLoader('./'))

yamlFile = sys.argv[1]
template = sys.argv[2]

with open(yamlFile) as f:
    dict =  yaml.load(f)

# Print dictionary generated from yaml
print("This is the dictionary attributes: ",  dict)

# Render template and print generated config to console
template = ENV.get_template(template)
print template.render(config=dict) #this will be the name of the dictionary in template

echou-a10:a10_simple_example echou$ python config_generate.py tps_base_config.yaml tps_base_config_template.txt
('This is the dictionary attributes: ', {'bgp': {'routerID': '11.11.11.11', 'neighbors': [{'ip': '12.12.12.12', 'description': 'upstream', 'remoteAS': 1}, {'ip': '13.13.13.13', 'description': 'downsteam', 'remoteAS': 1}], 'routeMap': {'ddosAdvertise': 'ddos-advertise'}, 'asn': 2}, 'glid2': {'bitRateLimit': 1000000, 'description': '"1gbps rate limiter"'}, 'glid1': {'bitRateLimit': 10000000, 'description': '"10gbps rate limiter"'}, 'logging': '10.10.10.10', 'ddosZoneTemplateUDP': {'spoofDetectMinDelay': 2, 'name': 'udp-protect1', 'spoofDetectTimeout': 5}, 'ntpServer': ['1.1.1.1', '2.2.2.2'], 'ddosZoneTemplateTCP': {'name': 'tcp-protect1'}})
!
system anomaly log
system attack log
system ddos-attack log
!
glid 1
  description "10gbps rate limiter"
  bit-rate-limit 10000000
!
glid 2
  description "1gbps rate limiter"
  bit-rate-limit 1000000
!
ddos protection enable
ddos protection rate-interval 1sec
!
ddos zone-template tcp tcp-protect1
  syn-authentication send-rst
  syn-authentication pass-action authenticate-src
  syn-authentication fail-action drop
!
ddos zone-template udp udp-protect1
  spoof-detect timeout 5
  spoof-detect min-delay 2
  spoof-detect pass-action authenticate-src
  spoof-detect fail-action drop
  known-resp-src-port action drop
!
logging host 10.10.10.10
!
router bgp 2
  bgp router-id 11.11.11.11
  bgp log-neighbor-changes

  neighbor 12.12.12.12 remote-as 1
  neighbor 12.12.12.12 description upstream
  neighbor 12.12.12.12 route-map ddos-advertise out

  neighbor 13.13.13.13 remote-as 1
  neighbor 13.13.13.13 description downsteam
  neighbor 13.13.13.13 route-map ddos-advertise out

!
route-map ddos-advertise permit 1
!

ntp server 1.1.1.1

ntp server 2.2.2.2

!
!


echou-a10:a10_simple_example echou$

```
