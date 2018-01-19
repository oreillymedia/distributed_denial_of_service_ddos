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

