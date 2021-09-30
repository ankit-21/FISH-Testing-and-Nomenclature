# importing necessary libraries
import plotly.utils
from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
import pandas as pd
from sys import platform
import plotly.graph_objects as go
import json

# defining the app name and session configuration to store variables in the session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def fish_sankey(
        TEST_NAME,
        fused,
        split,
        isolated3,
        isolated5):
    '''
    Takes test name and FISH counts to produce a Sankey diagram.
    Default values are for example case
    '''

    iso5_green = ['ROS1', 'ALK', 'CHOP', 'FKHR', 'NTRK1', 'NTRK3', 'GENE_GREEN']

    # set correct 3'/5' colors
    if TEST_NAME in iso5_green:
        iso3_color, iso5_color = "red", "green"
    else:
        iso3_color, iso5_color = "green", "red"

    # # do simple calculations for later display
    add = split + fused + isolated3 + isolated5
    fused_perc = round(100 * (fused / add))
    split_perc = round(100 * (split / add))
    iso5_perc = round(100 * (isolated5 / add))
    iso3_perc = round(100 * (isolated3 / add))
    non_fused = split + isolated5 + isolated3
    non_fused_perc = round(100 * (non_fused / add))

    # set node labels - unfortunately cannot add line breaks - it's a known bug
    labels = [f"{add}",
              f"{non_fused}/{add} ({non_fused_perc}%)",
              f"{fused}/{add} ({fused_perc}%)",
              f"{split}/{add} ({split_perc}%)",
              f"{isolated3}/{add} ({iso3_perc}%)",
              f"{isolated5}/{add} ({iso5_perc}%)"]

    # set colors for nodes
    color = ["black", "blue", "orange", "white", iso3_color, iso5_color]

    # x = [0.01, .5, .5, .99, .99, .99]
    # y = [.01, .01, .01, .01, .01, .01]
    # source = [0, 0, 1, 1, 1]  # indices correspond to labels above
    # target = [1, 2, 3, 4, 5]
    #
    # input_list = [labels, color, x, y, source, target]
    #
    # counts = [fused,
    #           split,
    #           isolated3,
    #           isolated5]
    #
    # for i, count in enumerate(counts):
    #     if count == 0:
    #         for input in input_list:
    #             del input[i]
    #     else:
    #         pass

    #  %% Draw the Sankey
    fig = go.Figure(data=[go.Sankey(
        valueformat=".0f",
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            x=[0.01, .5, .5, .99, .99, .99],
            y=[.01, .01, .01, .01, .01, .01],
            color=color
        ),
        link=dict(source=[0, 0, 1, 1, 1],
        target=[1, 2, 3, 4, 5],
        value=[non_fused, fused, split, isolated3, isolated5]
        ))])

    fig.update_layout(
        font_size=12,
        autosize=False,
        width=600,
        height=400,
        margin=dict(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        ))

    # %% Return the figure
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route("/")
def dropdown():
    " This function displays the welcome page that redirects to the tables page based on the test name "
    " chosen by the user "
    return render_template('index.html')


@app.route("/count", methods=['GET', 'POST'])
def tables():
    " This function displays the table to enter the count on table.html page "
    if request.method == "POST":
        TEST_NAME = request.form['TEST_NAME']
        session['TEST_NAME'] = TEST_NAME
        return render_template("table.html", TEST_NAME=TEST_NAME)


@app.route("/nom", methods=['GET', 'POST'])
def nomenc():
    " This function parses and processes the values entered by the user and displays the ISCN nomenclature "
    # defining global variables to be parsed on to the nom.html
    global out_final
    global Nom
    global nom1
    global nom2
    global nom3
    global nom4
    global fsd
    global splt
    global iso3
    global iso5
    global add
    global cut
    global fused_perc
    global split_perc
    global iso5_perc
    global iso3_perc
    global non_fused
    global non_fused_perc
    global plotly_plot

    # parsing the test name stored in sessions earlier
    TEST_NAME = session['TEST_NAME']

    if request.method == "POST":
        cols = ['Red', 'Green', 'Yellow']
        rows = []
        for i in request.form:
            row = request.form[i]
            rows.append(row)
        col_red = rows[::3]
        col_green = rows[1::3]
        col_yellow = rows[2::3]

        # creating an empty dataframe and populating it with values obtained from the user in table.html
        df = pd.DataFrame(columns=cols)
        df.Red = col_red
        df.Green = col_green
        df.Yellow = col_yellow

        try:
            df['Red'] = df['Red'].astype(int)
            df['Green'] = df['Green'].astype(int)
            df['Yellow'] = df['Yellow'].astype(int)
        except ValueError:
            return render_template("miss.html")

        # beginning the counter for cell counts of different bins
        split = 0
        fused = 0
        isolated5 = 0
        isolated3 = 0

        iso5_green = ['ROS1', 'ALK', 'CHOP', 'FKHR', 'NTRK1', 'NTRK3', 'GENE_GREEN']
        iso5_red = ['MYC', 'BCL2', 'BCL6', 'RET', 'EWSR1', 'SYT', 'GENE_RED']

        # 5' Green and 3' Red
        if TEST_NAME in iso5_green:
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    split += 1  # adding 1 to the split case
                elif df['Red'].loc[i] == 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] > 0:
                    fused += 1  # adding 1 to the fused case
                elif df['Red'].loc[i] == 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    isolated5 += 1  # adding 1 to the isolated 5' case
                elif df['Red'].loc[i] > 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] >= 0:
                    isolated3 += 1  # adding 1 to the isolated 3' case

            # cells count
            add = split + fused + isolated3 + isolated5
            fused_perc = round(100*(fused / add))
            split_perc = round(100*(split / add))
            iso5_perc = round(100*(isolated5 / add))
            iso3_perc = round(100*(isolated3 / add))
            non_fused = split + isolated5 + isolated3
            non_fused_perc = round(100 * (non_fused / add))

            # Calculating the [{(R+G)/2} + Y] (only for split bin)
            tot1 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    tot1.append(df['Yellow'].loc[i] + (df['Red'].loc[i] + df['Green'].loc[i]) / 2)
            try:
                num1 = round(sum(tot1) / len(tot1))
            except ZeroDivisionError:
                num1 = 0

            # Calculating the [{(R+G)/2} + Y] (only for fused bin)
            tot2 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] == 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] > 0:
                    tot2.append(df['Yellow'].loc[i] + (df['Red'].loc[i] + df['Green'].loc[i]) / 2)
            try:
                num1_f = round(sum(tot2) / len(tot2))
            except ZeroDivisionError:
                num1_f = 0

            # Calculating min(R, G) (only for split bin)
            tol = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    tol.append(min(df['Red'].loc[i], df['Green'].loc[i]))
            try:
                num2 = round(sum(tol) / len(tol))
            except ZeroDivisionError:
                num2 = 0

            # Calculating the avg copy number status of red column for iso 5'
            tot_red1 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] == 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    tot_red1.append(df.Red.loc[i] + df.Yellow.loc[i])
            try:
                num3 = round(sum(tot_red1) / len(tot_red1))
            except ZeroDivisionError:
                num3 = 0

            # Calculating the avg copy number status of green column for iso 5'
            tot_green1 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] == 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    tot_green1.append(df.Green.loc[i] + df.Yellow.loc[i])
            try:
                num4 = round(sum(tot_green1) / len(tot_green1))
            except ZeroDivisionError:
                num4 = 0

            # Calculating the avg copy number status of red column for iso 3'
            tot_red2 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] >= 0:
                    tot_red2.append(df.Red.loc[i] + df.Yellow.loc[i])
            try:
                num5 = round(sum(tot_red2) / len(tot_red2))
            except ZeroDivisionError:
                num5 = 0

            # Calculating the avg copy number status of green column for iso 3'
            tot_green2 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] >= 0:
                    tot_green2.append(df.Green.loc[i] + df.Yellow.loc[i])
            try:
                num6 = round(sum(tot_green2) / len(tot_green2))
            except ZeroDivisionError:
                num6 = 0

            # Syntax for the nomenclature
            " Nomenclature for Break Apart "
            " Split: nuc ish (TEST_NAME x [{(R+G)/2} + Y]) (5' TEST_NAME sep 3' x min(R,G)) [split/total] "
            " Fused: nuc ish (TEST_NAME x [{(R+G)/2} + Y]) [fused/total] "
            " Isolated 5': nuc ish (5' TEST_NAME x avg(G), 3' TEST_NAME x avg(R)) [iso 5'/total] "
            " Isolated 3': nuc ish (5' TEST_NAME x avg(G), 3' TEST_NAME x avg(R)) [iso 3'/total] "

            if split > 0:
                splt = " (" + TEST_NAME + " x " + str(
                    int(num1)) + ")" + " (5' " + TEST_NAME + " sep " + "3' " + TEST_NAME + " x " + str(
                    int(num2)) + ")" + " [" + "<b>" + str(split) + "</b>" + "/" + str(add) + "] "  # split
            else:
                splt = ""

            if fused > 0:
                fsd = " (" + TEST_NAME + " x " + str(int(num1_f)) + ")" + " [" + "<b>" + str(fused) + "</b>" + "/" + str(
                    add) + "] "  # fused
            else:
                fsd = ""

            if isolated5 > 0:
                iso5 = " (5' " + TEST_NAME + " x " + str(int(num4)) + ', ' + "3' " + TEST_NAME + " x " + str(
                    int(num3)) + ")" + " [" + "<b>" + str(isolated5) + "</b>" + "/" + str(add) + "] "  # isolated 5'
            else:
                iso5 = ""

            if isolated3 > 0:
                iso3 = " (5' " + TEST_NAME + " x " + str(int(num6)) + ', ' + "3' " + TEST_NAME + " x " + str(
                    int(num5)) + ")" + " [" + "<b>" + str(isolated3) + "</b>" + "/" + str(add) + "] "  # isolated 3'
            else:
                iso3 = ""

        # 5' Red and 3' Green
        elif TEST_NAME in iso5_red:
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    split += 1  # adding 1 to the split case
                elif df['Red'].loc[i] == 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] > 0:
                    fused += 1  # adding 1 to the fused case
                elif df['Red'].loc[i] == 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    isolated3 += 1  # adding 1 to the isolated 5' case
                elif df['Red'].loc[i] > 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] >= 0:
                    isolated5 += 1  # adding 1 to the isolated 3' case

            # total cells counted
            add = split + fused + isolated3 + isolated5
            fused_perc = round(100 * (fused / add))
            split_perc = round(100 * (split / add))
            iso5_perc = round(100 * (isolated5 / add))
            iso3_perc = round(100 * (isolated3 / add))
            non_fused = split + isolated5 + isolated3
            non_fused_perc = round(100 * (non_fused / add))

            # Calculating the [{(R+G)/2} + Y] (only for split bin)
            tot1 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    tot1.append(df['Yellow'].loc[i] + (df['Red'].loc[i] + df['Green'].loc[i]) / 2)
            try:
                num1 = round(sum(tot1) / len(tot1))
            except ZeroDivisionError:
                num1 = 0

            # Calculating the [{(R+G)/2} + Y] (only for fused bin)
            tot2 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] == 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] > 0:
                    tot2.append(df['Yellow'].loc[i] + (df['Red'].loc[i] + df['Green'].loc[i]) / 2)
            try:
                num1_f = round(sum(tot2) / len(tot2))
            except ZeroDivisionError:
                num1_f = 0

            # Calculating min(R, G) (only for split bin)
            tol = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    tol.append(min(df['Red'].loc[i], df['Green'].loc[i]))
            try:
                num2 = round(sum(tol) / len(tol))
            except ZeroDivisionError:
                num2 = 0

            # Calculating the avg copy number status of red column for iso 5'
            tot_red1 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] >= 0:
                    tot_red1.append(df.Red.loc[i] + df.Yellow.loc[i])
            try:
                num3 = round(sum(tot_red1) / len(tot_red1))
            except ZeroDivisionError:
                num3 = 0

            # Calculating the avg copy number status of green column for iso 5'
            tot_green1 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] > 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] >= 0:
                    tot_green1.append(df.Green.loc[i] + df.Yellow.loc[i])
            try:
                num4 = round(sum(tot_green1) / len(tot_green1))
            except ZeroDivisionError:
                num4 = 0

            # Calculating the avg copy number status of red column for iso 3'
            tot_red2 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] == 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    tot_red2.append(df.Red.loc[i] + df.Yellow.loc[i])
            try:
                num5 = round(sum(tot_red2) / len(tot_red2))
            except ZeroDivisionError:
                num5 = 0

            # Calculating the avg copy number status of green column for iso 3'
            tot_green2 = []
            for i in range(df.shape[0]):
                if df['Red'].loc[i] == 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                    tot_green2.append(df.Green.loc[i] + df.Yellow.loc[i])
            try:
                num6 = round(sum(tot_green2) / len(tot_green2))
            except ZeroDivisionError:
                num6 = 0

            # Syntax for the nomenclature
            " Nomenclature for Break Apart "
            " Split: nuc ish (TEST_NAME x [{(R+G)/2} + Y]) (5' TEST_NAME sep 3' x min(R,G)) [split/total] "
            " Fused: nuc ish (TEST_NAME x [{(R+G)/2} + Y]) [fused/total] "
            " Isolated 5': nuc ish (5' TEST_NAME x avg(R), 3' TEST_NAME x avg(G)) [iso 5'/total] "
            " Isolated 3': nuc ish (5' TEST_NAME x avg(R), 3' TEST_NAME x avg(G)) [iso 3'/total] "

            if split > 0:
                splt = " (" + TEST_NAME + " x " + str(
                    int(num1)) + ")" + " (5' " + TEST_NAME + " sep " + "3' " + TEST_NAME + " x " + str(
                    int(num2)) + ")" + " [" + "<b>" + str(split) + "</b>" + "/" + str(add) + "] "  # split
            else:
                splt = ""

            if fused > 0:
                fsd = " (" + TEST_NAME + " x " + str(int(num1_f)) + ")" + " [" + "<b>" + str(fused) + "</b>" + "/" + str(
                    add) + "] "  # fused
            else:
                fsd = ""

            if isolated5 > 0:
                iso5 = " (5' " + TEST_NAME + " x " + str(int(num3)) + ', ' + "3' " + TEST_NAME + " x " + str(
                    int(num4)) + ")" + " [" + "<b>" + str(isolated5) + "</b>" + "/" + str(add) + "] "  # isolated 5'
            else:
                iso5 = ""

            if isolated3 > 0:
                iso3 = " (5' " + TEST_NAME + " x " + str(int(num5)) + ', ' + "3' " + TEST_NAME + " x " + str(
                    int(num6)) + ")" + " [" + "<b>" + str(isolated3) + "</b>" + "/" + str(add) + "] "  # isolated 3'
            else:
                iso3 = ""

        # storing the count as a key-value pair in the dictionary
        bin_dict = {'split': split, 'fused': fused, 'isolated5': isolated5, 'isolated3': isolated3}
        a_sorted_keys = sorted(bin_dict, key=bin_dict.get, reverse=True)

        # for presenting the nomenclature in descending order of counts of occurrences
        a = a_sorted_keys[0]
        b = a_sorted_keys[1]
        c = a_sorted_keys[2]
        d = a_sorted_keys[3]

        if a == "split":
            nom1 = '<p style="display:inline-block;color:white">' + splt + "</p>"
        elif a == "fused":
            nom1 = '<p style="display:inline-block;color:orange">' + fsd + "</p>"
        elif a == "isolated5":
            if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
                nom1 = '<p style="display:inline-block;color:green">' + iso5 + "</p>"
            else:
                nom1 = '<p style="display:inline-block;color:red">' + iso5 + "</p>"
        elif a == "isolated3":
            if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
                nom1 = '<p style="display:inline-block;color:red">' + iso3 + "</p>"
            else:
                nom1 = '<p style="display:inline-block;color:green">' + iso3 + "</p>"

        if b == "split":
            nom2 = '<p style="display:inline-block;color:white">' + splt + "</p>"
        elif b == "fused":
            nom2 = '<p style="display:inline-block;color:orange">' + fsd + "</p>"
        elif b == "isolated5":
            if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
                nom2 = '<p style="display:inline-block;color:green">' + iso5 + "</p>"
            else:
                nom2 = '<p style="display:inline-block;color:red">' + iso5 + "</p>"
        elif b == "isolated3":
            if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
                nom2 = '<p style="display:inline-block;color:red">' + iso3 + "</p>"
            else:
                nom2 = '<p style="display:inline-block;color:green">' + iso3 + "</p>"

        if c == "split":
            nom3 = '<p style="display:inline-block;color:white">' + splt + "</p>"
        elif c == "fused":
            nom3 = '<p style="display:inline-block;color:orange">' + fsd + "</p>"
        elif c == "isolated5":
            if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
                nom3 = '<p style="display:inline-block;color:green">' + iso5 + "</p>"
            else:
                nom3 = '<p style="display:inline-block;color:red">' + iso5 + "</p>"
        elif c == "isolated3":
            if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
                nom3 = '<p style="display:inline-block;color:red">' + iso3 + "</p>"
            else:
                nom3 = '<p style="display:inline-block;color:green">' + iso3 + "</p>"

        if d == "split":
            nom4 = '<p style="display:inline-block;color:white">' + splt + "</p>"
        elif d == "fused":
            nom4 = '<p style="display:inline-block;color:orange">' + fsd + "</p>"
        elif d == "isolated5":
            if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
                nom4 = '<p style="display:inline-block;color:green">' + iso5 + "</p>"
            else:
                nom4 = '<p style="display:inline-block;color:red">' + iso5 + "</p>"
        elif d == "isolated3":
            if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'CHOP' or TEST_NAME == 'FKHR' or TEST_NAME == 'NTRK1' or TEST_NAME == 'NTRK3' or TEST_NAME == "GENE_GREEN":
                nom4 = '<p style="display:inline-block;color:red">' + iso3 + "</p>"
            else:
                nom4 = '<p style="display:inline-block;color:green">' + iso3 + "</p>"

        # adding all the nomenclature strings together and removing extra "/" for unused nom strings
        nom = "nuc ish"
        if nom1 == '<p style="display:inline-block;color:red"></p>' or nom1 == '<p style="display:inline-block;color:green"></p>' or nom1 == '<p style="display:inline-block;color:orange"></p>' or nom1 == '<p style="display:inline-block;color:white"></p>':
            Nom = nom
        elif nom2 == '<p style="display:inline-block;color:red"></p>' or nom2 == '<p style="display:inline-block;color:green"></p>' or nom2 == '<p style="display:inline-block;color:orange"></p>' or nom2 == '<p style="display:inline-block;color:white"></p>':
            Nom = nom + " " + nom1
        elif nom3 == '<p style="display:inline-block;color:red"></p>' or nom3 == '<p style="display:inline-block;color:green"></p>' or nom3 == '<p style="display:inline-block;color:orange"></p>' or nom3 == '<p style="display:inline-block;color:white"></p>':
            Nom = nom + " " + nom1 + " / " + nom2
        elif nom4 == '<p style="display:inline-block;color:red"></p>' or nom4 == '<p style="display:inline-block;color:green"></p>' or nom4 == '<p style="display:inline-block;color:orange"></p>' or nom4 == '<p style="display:inline-block;color:white"></p>':
            Nom = nom + " " + nom1 + " / " + nom2 + " / " + nom3
        else:
            Nom = nom + " " + nom1 + " / " + nom2 + " / " + nom3 + " / " + nom4

        # Cut-off for different tests
        cut_off = ['ROS1', 'ALK', 'RET', 'SYT', 'BCL2', 'BCL6', 'EWSR1', 'FKHR', 'MYC', 'NTRK1', 'NTRK3', 'GENE_RED', 'GENE_GREEN']

        if TEST_NAME in cut_off:
            cut = 'A ROS1 rearrangement is reported if more than 15% of cells show split signals.'
        else:
            cut = 'A CHOP rearrangement is reported if more than 20% of cells show split signals.'

        # Obtaining macro for FISH report on WIKI
        out = str(df.to_csv(header=False, index=False))
        if platform == "win32":
            # Windows
            out_final = out.replace("\n", ";").replace("\r", "")
        else:
            # iOS or Linux
            out_final = out.replace("\n", ";")

        # Sankey diagram
        plotly_plot = fish_sankey(TEST_NAME=TEST_NAME, fused=fused, split=split, isolated3=isolated3, isolated5=isolated5)

        return redirect(url_for('nomenc'))
    return render_template('nom.html', Nom=Nom, out_final=out_final, TEST_NAME=TEST_NAME, add=add, nom1=nom1, nom2=nom2,
                           nom3=nom3, nom4=nom4, cut=cut, fused_perc=fused_perc, split_perc=split_perc,
                           iso5_perc=iso5_perc, iso3_perc=iso3_perc, non_fused_perc=non_fused_perc,
                           non_fused=non_fused, fsd=fsd, splt=splt, iso3=iso3, iso5=iso5, plotly_plot=plotly_plot)


if __name__ == "__main__":
    app.run()
    app.secret_key = '\xc2}{\xe8n\xc0\x0f\xd6\xbd\xcf\x05\x1e\xf0_\xfaPo\xfdUw\xde\x08i\xbf'
