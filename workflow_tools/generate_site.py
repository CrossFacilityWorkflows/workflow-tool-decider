#!/usr/bin/env python
import pandas as pd
import numpy as np

from yaml import safe_load
from jinja2 import Environment
from jinja2 import FileSystemLoader


#Function to convert the yaml data into pandas dataframe
def convert_tools_to_df(yaml_file):
    #Load tags from yaml
    tag_mappings = yaml_file['tags']
    (tags, tag_headings) = map(list, zip(*tag_mappings.items()))
    table_headings = ['Name'] + tag_headings
    x_true = ['x'] * len(tag_headings)
    x_false = [''] * len(tag_headings)

    #Convert data into table
    data = [[v['title'], *np.where(np.isin(tags, v['tags']), x_true, x_false)] for v in yaml_file['tools'].values()]
    df = pd.DataFrame(data, columns=table_headings)

    #Add Docs links
    tool_urls = {v['title']: v['docs'] for v in yaml_file['tools'].values()}
    df['Name'] = df['Name'].apply(lambda x: f'<a href="{tool_urls[x]}">{x}</a>')

    return df.set_index('Name')

#Load workflow tool data from yaml file
with open('workflow_tools.yaml', 'r') as in_file:
    workflow_tools_file = safe_load(in_file)

#Convert yaml data into table
df = convert_tools_to_df(workflow_tools_file)
table_html = df.to_html(
    classes=["table", "table-bordered", "table-hover"],
    escape=False
)
#Wrap table in table-responsive
table_html = '<div class="table-responsive">\n  ' + table_html + "\n    </div>"

#Load index template
environment = Environment(loader=FileSystemLoader("../templates/"))
index_template = environment.get_template("index.html")

#Generate index.html file
filename = "../index.html"
with open(filename, mode="w", encoding="utf-8") as out_file:
    out_file.write(index_template.render(table=table_html))
    # print(index_template.render(name="hello world"))

print(f"Generated {filename}")