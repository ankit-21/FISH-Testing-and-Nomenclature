
# %%
import plotly.graph_objects as go

# %%
# set inputs

def fish_sunburst(
            TEST_NAME = "Example ROS1 Case",
            fused = 8,
            split = 34,
            isolated3 = 6,
            isolated5 = 2,
            cut =  "A ROS1 rearrangement is reported if more than 15% of cells show split signals."
            ):
    '''
    Takes test name and FISH counts to produce a sunburst diagram.
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

    # set ids, labels, parents
    ids = ["Total Counted", 
            "Non-Fused", 
            "Fused", 
            "Split", 
            "Isolated 3'", 
            "Isolated 5'"]
    
    labels = [f"Total Counted<br>{add}", 
            f"Non-Fused<br>{non_fused}/{add} ({non_fused_perc}%)", 
            f"Fused<br>{fused}/{add} ({fused_perc}%)", 
            f"Split<br>{split}/{add} ({split_perc}%)", 
            f"Isolated 3'<br>{isolated3}/{add} ({iso3_perc}%)", 
            f"Isolated 5'<br>{isolated5}/{add} ({iso5_perc}%)"]
    
    parents = ["",
               "Total Counted",
               "Total Counted",              
               "Non-Fused",
               "Non-Fused",
               "Non-Fused",]
    
    values = [add, non_fused, fused, split, isolated3, isolated5]
    
    # set colors for sections
    colors = ["white", "blue", "orange", "black", iso3_color, iso5_color]

    #  %% Draw the sunburst
    fig = go.Figure(go.Sunburst(
        ids = ids,
        labels = labels,
        parents = parents,
        values = values,
        branchvalues="total",
        ))
    
    # set the colors
    fig.update_traces(marker_colors=colors, selector=dict(type='sunburst'))
    
    # add a title
    fig.update_layout(
        title_text=f'{TEST_NAME} Break-Apart FISH Probe<br><span style="font-size: 10px;">{cut}</span>', 
        font_size=10)

    # %% Return the figure - TODO: make this produce html or render dynamically
    return fig

# %% 
if __name__ == "__main__":
    fish_sunburst().show()
# %%
