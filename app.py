# importing necessary libraries
from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
import pandas as pd
from sys import platform

# defining the app name and session configuration to store variables in the session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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
        if TEST_NAME == 'ROS1' or TEST_NAME == 'ALK' or TEST_NAME == 'RET' or TEST_NAME == 'SYT' or TEST_NAME == 'BCL2' or TEST_NAME == 'BCL6' or TEST_NAME == 'CHOP' or TEST_NAME == 'EWSR1' or TEST_NAME == 'FKHR' or TEST_NAME == 'MYC':
            return render_template("table.html", TEST_NAME = TEST_NAME)
        else:
            return render_template("WIP.html")


@app.route("/nom", methods=['GET', 'POST'])
def nomenc():
    " This function parses and processes the values entered by the user and displays the ISCN nomenclature "
    # defining global variables to be parsed on to the nom.html
    global out_final
    global Nom
    global splt
    global fsd
    global iso5
    global iso3
    global add

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

        for i in range(df.shape[0]):
            if df['Red'].loc[i] > 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                split += 1  # adding 1 to the split case
            elif df['Red'].loc[i] == 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] > 0:
                fused += 1  # adding 1 to the fused case
            elif df['Red'].loc[i] == 0 and df['Green'].loc[i] > 0 and df['Yellow'].loc[i] >= 0:
                isolated5 += 1  # adding 1 to the isolated 5' case
            elif df['Red'].loc[i] > 0 and df['Green'].loc[i] == 0 and df['Yellow'].loc[i] >= 0:
                isolated3 += 1  # adding 1 to the isolated 3' case

        # total cells counted
        add = split + fused + isolated3 + isolated5

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
                int(num2)) + ")" + " [" + "<b>" + str(split) + "</b>" + "/" + str(df.shape[0]) + "] "  # split
        else:
            splt = ""

        if fused > 0:
            fsd = " (" + TEST_NAME + " x " + str(int(num1_f)) + ")" + " [" + "<b>" + str(fused) + "</b>" + "/" + str(
                df.shape[0]) + "] "  # fused
        else:
            fsd = ""

        if isolated5 > 0:
            iso5 = " (5' " + TEST_NAME + " x " + str(int(num4)) + ', ' + "3' " + TEST_NAME + " x " + str(
                int(num3)) + ")" + " [" + "<b>" + str(isolated5) + "</b>" + "/" + str(df.shape[0]) + "] "  # isolated 5'
        else:
            iso5 = ""

        if isolated3 > 0:
            iso3 = " (5' " + TEST_NAME + " x " + str(int(num6)) + ', ' + "3' " + TEST_NAME + " x " + str(
                int(num5)) + ")" + " [" + "<b>" + str(isolated3) + "</b>" + "/" + str(df.shape[0]) + "] "  # isolated 3'
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
            nom1 = splt
        elif a == "fused":
            nom1 = fsd
        elif a == "isolated5":
            nom1 = iso5
        elif a == "isolated3":
            nom1 = iso3

        if b == "split":
            nom2 = splt
        elif b == "fused":
            nom2 = fsd
        elif b == "isolated5":
            nom2 = iso5
        elif b == "isolated3":
            nom2 = iso3

        if c == "split":
            nom3 = splt
        elif c == "fused":
            nom3 = fsd
        elif c == "isolated5":
            nom3 = iso5
        elif c == "isolated3":
            nom3 = iso3

        if d == "split":
            nom4 = splt
        elif d == "fused":
            nom4 = fsd
        elif d == "isolated5":
            nom4 = iso5
        elif d == "isolated3":
            nom4 = iso3

        # adding all the nomenclature strings together
        nom = "nuc ish"
        Nom = nom + nom1 + "/" + nom2 + "/" + nom3 + "/" + nom4

        # Removing extra "/" for unused nom strings
        if Nom[-3] == "/":
            Nom = Nom[:-3]
        elif Nom[-2] == "/":
            Nom = Nom[:-2]
        elif Nom[-1] == "/":
            Nom = Nom[:-1]
        else:
            Nom = Nom

        # Obtaining macro for FISH report on WIKI
        out = str(df.to_csv(header=False, index=False))
        if platform == "win32":
            # Windows
            out_final = out.replace("\n", ";").replace("\r", "")
        else:
            # iOS or Linux
            out_final = out.replace("\n", ";")
        return redirect(url_for('nomenc'))
    return render_template('nom.html', Nom=Nom, out_final=out_final, TEST_NAME=TEST_NAME, add=add, fsd=fsd, splt=splt, iso3=iso3, iso5=iso5)


if __name__ == "__main__":
    app.run(debug=True)
    app.secret_key = '\xc2}{\xe8n\xc0\x0f\xd6\xbd\xcf\x05\x1e\xf0_\xfaPo\xfdUw\xde\x08i\xbf'
