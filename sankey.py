
# %%
import plotly.graph_objects as go

# %%
# set inputs

def fish_sankey(
            TEST_NAME = "Example ROS1 Case",
            fused = 8,
            split = 34,
            isolated3 = 6,
            isolated5 = 2,
            cut =  "A ROS1 rearrangement is reported if more than 15% of cells show split signals."
            ):
    '''
    Takes test name and FISH counts to produce a Sankey diagram.
    Default values are for example case
    '''
    # set correct 3'/5' colors
    if TEST_NAME == 'Example ROS1 Case' or TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
        iso3_color, iso5_color = "red", "green"
    else:
        iso3_color, iso5_color = "green", "red"

    # do simple calculations for later display
    add = split + fused + isolated3 + isolated5
    fused_perc = round(100*(fused / add))
    split_perc = round(100*(split / add))
    iso5_perc = round(100*(isolated5 / add))
    iso3_perc = round(100*(isolated3 / add))
    non_fused = split + isolated5 + isolated3
    non_fused_perc = round(100 * (non_fused / add))

    # set node labels - unfortunately cannot add line breaks - it's a known bug
    labels = [f"Total Counted: {add}", 
            f"Non-Fused: {non_fused}/{add} ({non_fused_perc}%)", 
            f"Fused: {fused}/{add} ({fused_perc}%)", 
            f"Split: {split}/{add} ({split_perc}%)", 
            f"Isolated 3': {isolated3}/{add} ({iso3_perc}%)", 
            f"Isolated 5': {isolated5}/{add} ({iso5_perc}%)"]
    
    # set colors for nodes
    color = ["black", "blue", "orange", "white", iso3_color, iso5_color]
    x = [0.01, .5, .5, .99,.99,.99]
    y = [.01, .01, .01, .01, .01 , .01] 
    source = [0, 0, 1, 1, 1] # indices correspond to labels above
    target = [1, 2, 3, 4, 5]
    
    input_list = [labels, color, x, y, source, target]
    
    counts = [fused,
            split,
            isolated3,
            isolated5]
    
    for i, count in enumerate(counts):
        if count == 0:
            for input in input_list:
                del input[i+1]
        
    #  %% Draw the Sankey
    fig = go.Figure(data=[go.Sankey(
        valueformat = ".0f",
        arrangement = "snap",
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label = labels,
        color = color,
        x=x,
        y=y,
        source=source,
        target=target,
        ),
        link = dict(

        value = [non_fused, fused, split, isolated3, isolated5]
    ))])

    # add a title
    fig.update_layout(
        title_text=f'{TEST_NAME} Break-Apart FISH Probe<br><span style="font-size: 10px;">{cut}</span>', 
        font_size=10)

    # %% Return the figure - TODO: make this produce html or render dynamically
    return fig

# %% 
if __name__ == "__main__":
    fish_sankey().show()
# %%
