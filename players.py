# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 10:24:37 2018

@author: ANODEG
"""


import requests
import pandas as pd
import copy
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.widgets import Slider, Select,TextInput, DataTable, TableColumn, NumberFormatter
from bokeh.layouts import layout, widgetbox
from bokeh.models import HoverTool, PanTool, BoxZoomTool, ResetTool, TapTool
from bokeh.palettes import brewer, viridis
from bokeh.io import curdoc


fpl_data = requests.get('https://fantasy.premierleague.com/drf/bootstrap-static').json()
N = len(fpl_data['elements'])

allplayers = {}
allplayers['web_name'] = [None] * N
allplayers['total_points'] = [None] * N
allplayers['team'] = [None] * N
allplayers['now_cost'] = [None] * N
allplayers['element_type'] = [None] * N
allplayers['id'] = [None] * N
allplayers['bonus'] = [None] * N
allplayers['bps'] = [None] * N
allplayers['minutes'] = [None] * N
allplayers['selected_by_percent'] = [None] * N
allplayers['form'] = [None] * N
allplayers['threat'] = [None] * N
allplayers['creativity'] = [None] * N
allplayers['value_form'] = [None] * N
allplayers['value_season'] = [None] * N
allplayers['assists'] = [None] * N
allplayers['goals_scored'] = [None] * N
allplayers['ict_index'] = [None] * N
allplayers['transfers_in'] = [None] * N
allplayers['transfers_in_event'] = [None] * N
allplayers['transfers_out'] = [None] * N
allplayers['transfers_out_event'] = [None] * N
allplayers['event_points'] = [None] * N
allplayers['influence'] = [None] * N

# Choose axis, can be expanded
axis_map = {
    "Cost": "now_cost",
#    "Points per million GBP": "pointspercost",
    "Playtime": "playtime",
    "Points per 90 min": "pointsper90",
    "Bonus points": "bonus",
    "Points": "total_points",
    "Bonus point system": "bps",
    "Selected by": "selected_by_percent", 
    "Form": "form",
    "Threat": "threat",
    "Creativity": "creativity",
    "Value-form": "value_form",
    "Value-season": "value_season",
    "Assists": "assists",
    "Goals": "goals_scored",
    "ICT index": "ict_index",
    "Transfers in": "transfers_in",
    "Transfers in GW": "transfers_in_event",
    "Transfers out": "transfers_out",
    "Transfers out GW": "transfers_out_event",
    "Points GW": "event_points",
    "Influence": "influence"
}



color_map = copy.deepcopy(axis_map)
#color_map['Club'] = 'team_name'
color_map['Position'] = 'position'

for i in range(N):
    for key in allplayers.keys():
        allplayers[key][i] = fpl_data['elements'][i][key]
        if type(allplayers[key][i]) == str:
            try:
                allplayers[key][i] = float(allplayers[key][i])
            except:
                None

positions = ['GK','DEF','MID','FWD']
allplayers['team_name'] = [None] * N
allplayers['position'] = [None] * N
for i in range(N):
    allplayers['team_name'][i] = fpl_data['teams'][allplayers['team'][i]-1]['name']
    allplayers['position'][i] = positions[allplayers['element_type'][i]-1]

teams = [None] * 20
teamind = {}
teamstrength = []
for i in range(len(teams)):
    teams[i] = fpl_data['teams'][i]['name']
    teamstrength.append(fpl_data['teams'][i]['strength'])
    teamind[teams[i]] = i
del allplayers['team']

data = pd.DataFrame.from_dict(allplayers)
data['now_cost'] = data['now_cost']/10
data['pointsper90'] = data['total_points']/data['minutes']*90
data['playtime'] = data['minutes']/90

seqcolors = viridis(256)

positions.insert(0,"All")
teams.insert(0,"All")


# Create fixturetable placeholder
#fixturecolorcodes = ['#0b8a00','#7ad344','#feffd5','#ffa32a',' #cc2805']
#fixturecolors = [[] for _ in range(20)]                     

playersummary = requests.get('https://fantasy.premierleague.com/drf/element-summary/115').json()
                     
fixturedata = requests.get('https://fantasy.premierleague.com/drf/fixtures/').json()
fixturetable = [[] for _ in range(20)]

for fixture in fixturedata:
    fixturetable[fixture['team_h']-1].append(fixture['team_h_difficulty'])
    fixturetable[fixture['team_a']-1].append(fixture['team_a_difficulty'])
#    fixturecolors[fixture['team_h']-1].append(fixturecolorcodes[fixturetable[fixture['team_h']-1][-1]-1])
#    fixturecolors[fixture['team_a']-1].append(fixturecolorcodes[fixturetable[fixture['team_a']-1][-1]-1])

currentGW = fpl_data['current-event']
nextfixtures = [[] for _ in range(len(data))]
#nextfixturecolors = [[] for _ in range(len(data))]
nextfixturesstrings = []
for playeriloc in range(len(nextfixtures)):
    nextfixtures[playeriloc] = fixturetable[teamind[data['team_name'].iloc[playeriloc]]][currentGW:currentGW+6]
#    nextfixturecolors[playeriloc] = fixturecolors[teamind[data['team_name'].iloc[playeriloc]]][currentGW:currentGW+6]
#    
    newstring = '['
    for rating in nextfixtures[playeriloc]:
        newstring = newstring + str(rating) + ', '
    newstring = newstring[:-2]+ ']' 
    nextfixturesstrings.append(newstring)

data['fixtures'] = nextfixturesstrings


 
# Create Input controls
positionSelect = Select(title="Position", value="All", options = positions)
clubSelect = Select(title="Club", value="All", options=teams)
playerName = TextInput(title="Player name contains:")
maxCost = Slider(title = "Max cost", start = 4.0, end=13.5, value= 13.5, step=0.1)
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Cost")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Value-season")
markersize = Select(title="Marker Size", options=sorted(axis_map.keys()), value="Points")
markercolor = Select(title="Marker Colour", options=sorted(color_map.keys()), value="Position")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], size=[], points=[], cost=[],
                                    web_name=[], position=[], team_name=[], color=[],
                                    fixtures = [], ID = []))


hover = HoverTool()
hover.tooltips = [
    ('name', '@web_name'),
    ('team', '@team_name'),
    ('position', '@position'),
    ('points', '@points'),
    ('cost', '@cost{0.0 a}'),
    ('fixtures', '@fixtures')
#    ('matches', '$color[hex=False,swatch]:M1C)',
]

# Need to specify starting ranges to avoid auto-range 
padding = 0.1
xrange = max(data['now_cost'])-min(data['now_cost'])
yrange = max(data['value_season'])-min(data['value_season'])
xmin = min(data['now_cost'])-padding*xrange
xmax = max(data['now_cost'])+padding*xrange
ymin = max([0,min(data['value_season'])-padding*yrange])
ymax = max(data['value_season'])+padding*yrange

p = figure(plot_height=600, plot_width=700, title="", x_range = (xmin, xmax), y_range = (ymin, ymax), tools = [hover,BoxZoomTool(), PanTool(),ResetTool(),TapTool()], output_backend='webgl')
p.scatter(x="x", y="y",fill_alpha=0.45, source=source, size = 'size', color = 'color')



# Table for selected players
tablesource = ColumnDataSource(data = dict(position=[], web_name=[], team_name=[], event_points=[],
                                                total_points=[],  form=[],  now_cost=[], value_season=[],
                                                value_form=[], playtime=[], pointsper90=[], assists=[],
                                                goals_scored=[],ict_index=[], threat=[], creativity=[], influence=[],
                                                selected_by_percent=[]))

basicformat = NumberFormatter(format = '0.0', text_align = 'right')


columns = [
    TableColumn(field='position', title='Position'),
    TableColumn(field='web_name', title='Name'),
    TableColumn(field='team_name', title='Club'),
    TableColumn(field='event_points', title='GW points', formatter = basicformat),
    TableColumn(field='total_points', title='Points', formatter = basicformat),
    TableColumn(field='form', title='Form', formatter = basicformat),
    TableColumn(field='now_cost', title='Cost', formatter = basicformat),
    TableColumn(field='value_season', title='Season value', formatter = basicformat),
    TableColumn(field='value_form', title='Form value', formatter = basicformat),
    TableColumn(field='playtime', title='Full 90min', formatter = basicformat),
    TableColumn(field='pointsper90', title='Points/90min', formatter = basicformat),
    TableColumn(field='assists', title='Assists', formatter = basicformat),
    TableColumn(field='goals_scored', title='Goals', formatter = basicformat),
    TableColumn(field='ict_index', title='ICT', formatter = basicformat),
    TableColumn(field='threat', title='Threat'),
    TableColumn(field='creativity', title='Creativity', formatter = basicformat),
    TableColumn(field='influence', title='Influence', formatter = basicformat),
    TableColumn(field='selected_by_percent', title='Ownership', formatter = basicformat),
    ]

selecttable = DataTable(source=tablesource, columns=columns, width=1000, height=400, index_position = None)



def colormaker(series):
    
    if series.dtype == 'int64' or series.dtype == 'float64':
        x =  (series-min(series))/(max(series)-min(series))*255
        x = list(x.astype('int'))
        colors = [None] * len(x)
        for i in range(len(x)):
            colors[i] = seqcolors[x[i]]
  
    else:
        colors = brewer['Dark2'][len(data[series.name].unique())]
        colormap = {}
        ind = 0
        for uniquelement in data[series.name].unique():
            colormap[uniquelement] = colors[ind]
            ind += 1
        colors = [colormap[x] for x in series]
    
    return colors    

def select_players():
    club_val = clubSelect.value
    position_val = positionSelect.value
    player_val = playerName.value
    selected = data[
            data.now_cost <= maxCost.value
            ]
    if (club_val != "All"):
        selected = selected[selected.team_name.str.contains(clubSelect.value)==True]
    if (position_val != "All"):
        selected = selected[selected.position.str.contains(position_val)==True]
    if (player_val != ""):
        selected = selected[selected.web_name.str.contains(player_val)==True]

    selected = selected[selected.total_points > 0]
    
    return selected

def update():
    
    df = select_players()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]
    size_name = axis_map[markersize.value]
    color_name = color_map[markercolor.value]

    padding = 0.1
    xrange = max(data[x_name])-min(data[x_name])
    yrange = max(data[y_name])-min(data[y_name])
    
    p.x_range.start = max([0, min(data[x_name])-padding*xrange])
    p.x_range.end = max(data[x_name])+padding*xrange
    p.y_range.start = max([0,min(data[y_name])-padding*yrange])
    p.y_range.end =  max(data[y_name])+padding*yrange
    
    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d players selected" % len(df)
    
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        size = df[size_name]/max(data[size_name])*80,
        points = df['total_points'],
        cost = df['now_cost'],
        web_name = df['web_name'],
        ID = df['id'],
        position = df['position'],
        team_name = df['team_name'],
        color = pd.Series(colormaker(df[color_name])),
        fixtures = df['fixtures'],
#        selecteddf = df
        )


def selectupdate(attrname, old, new):

    if len(source.selected.indices)>0:
        
        selectionIndex = source.selected.indices
        
        selectedplayers = []
        for ind in selectionIndex:
            selectedplayers.append(source.data['ID'].iloc[ind])
            
        newtable = {}
        for key in tablesource.data.keys():
            values = []
            for player in selectedplayers:
                values.append(data[key][data['id'] == player].iloc[0])        
            newtable[key] = values
            
        tablesource.data = newtable
        
        


update()  # initial load of the data

controls = [positionSelect, clubSelect, playerName, maxCost, x_axis, y_axis, markersize, markercolor]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())
source.on_change('selected', selectupdate)

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [inputs, p],selecttable
], sizing_mode=sizing_mode)


curdoc().add_root(l)
curdoc().title = "Playerdata"





