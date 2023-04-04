#!/usr/bin/env python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex

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

#Add features to html table
def post_process_table(df):
    #Wrap table in table-responsive
    df = '<div class="table-responsive tableHeader">\n  ' + df + "\n    </div>"
    
    #Center x's
    df = df.replace('<td><b>', '<td style="text-align:center"><b>')

    # df = df.replace('<td>red</td>', '<td style="background-color:#FF0000"></td>')
    # df = df.replace('<td>green</td>', '<td style="background-color:#00FF00"></td>')
    return df


#Generate Cards
def generate_cards_from_dict(yaml_file):
    html_string = ''
    html_string += '<div class="row row-cols-1 row-cols-md-2 g-4">\n'

    #generate diff color for each tag
    cmap = plt.get_cmap('tab20c')
    tags = yaml_file['tags'].keys()
    colors = {c[0]: rgb2hex(c[1]) for c in zip(tags, cmap(np.linspace(0, 1, len(tags))))}

    
    #Loop through tools
    html_string += ''.join([_gen_card(v, colors) for v in yaml_file['tools'].values()])

    html_string += '</div>\n'
    return html_string

def _gen_card(tool_dict, colors):

    html_buttons = "\n".join(f'<button style="background-color:{colors[t]};color: #FFF" type="button" class="btn">{t}</button>' for t in tool_dict['tags'])

    html_out = f"""
    <div class="col">
    <div class="card">
      <a href="{tool_dict['docs']}"><img width="10px" src="{tool_dict['img']}" class="card-img-top" alt="{tool_dict['title']}"></a>
      <div class="card-body">
        <h5 class="card-title">{tool_dict['title']}</h5>
        <p class="card-text">{tool_dict['description']}</p>
        <p class="card-text pt-2">{html_buttons}</p>
      </div>
    </div>
    </div>
    """
    #Add tags as cool buttons
    #Add images
    return html_out

#Load workflow tool data from yaml file
with open('workflow_tools.yaml', 'r') as in_file:
    workflow_tools_file = safe_load(in_file)

#Convert yaml data into table
df = convert_tools_to_df(workflow_tools_file)
bold_frmt = lambda x: f'<b>{x}</b>'
table_html = df.to_html(
    classes=["table", "table-bordered", "table-hover"],
    justify='center',
    formatters={k: bold_frmt for k in df.columns if k != 'Name'} ,
    escape=False
)
table_html = post_process_table(table_html)
cards_html = generate_cards_from_dict(workflow_tools_file)

#Load index template
environment = Environment(loader=FileSystemLoader("../templates/"))
index_template = environment.get_template("index.html")

#Generate index.html file
filename = "../index.html"
with open(filename, mode="w", encoding="utf-8") as out_file:
    out_file.write(index_template.render(table=table_html, cards=cards_html))

print(f"Generated {filename}")