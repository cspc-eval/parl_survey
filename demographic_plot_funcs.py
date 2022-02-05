# import packages
import textwrap
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import cspc_parliament_survey_2022_funcs as cspc

# FUNCTIONS TO PLOT DEMOGRAPHIC QUESTIONS

def demographic_q1q2(survey_raw):
    # ----- Q1. HOUSE AFFILIATION & Q2. PARTY AFFILIATION-----#
    # We will make a horiztonal stacked bar plot showing party affiliation
    # split by house affiliaiton.
    # GET DATA:
    # get data for first 2 demographic questions
    df = cspc.get_question(survey_raw, ('Q1','Q2'))
    # rename the columns for ease
    df = df.rename(columns={'Q1. House Affiliation': 'house', 'Q2. Party Affiliation': 'party'})
    # group party affiliation by house (crosstab) and convert to percentages (apply)
    df = (pd.crosstab(index=df['house'], columns=df['party']) / survey_raw.shape[0]) * 100

    # PLOT:
    fig, ax = plt.subplots(figsize=(10,8))
    cspc_colors = cspc.get_cspc_colors()
    ax = df.plot(kind='barh', #selecting the order of columns
                        stacked=True, 
                        color=cspc_colors,
                        ax=ax,
                        width=0.5)  
    cspc.label_proportions_stacked_bar(df,ax)
    # legend
    ax.legend(loc="upper center", bbox_to_anchor=(0,0.87,1,0.2), ncol = 2, prop={'size': 8}) #adjust the legend position and font size
    # x-axis formatting
    ax.set_xlim([0, 100])
    ax.set(xlabel='Percentage of respondants', ylabel='') #label for x axis
    ax.set_yticklabels([textwrap.fill(label, 14) for label in df.index]) #wraps the text
    ax.xaxis.set_major_formatter(mtick.PercentFormatter()) #add percent symbol to x-axis
    plt.show(block=False)
    return fig, ax


def demographic_q3(survey_raw, map_type):
    # ----- Q3. GEOGRAPHIC DESIGNATION -----#
    # GET DATA:
    # get Canada shapefile (used for plotting):
    df_can = cspc.load_canada_shapefile()
    # get geo designation
    df = cspc.get_question(survey_raw, ('Q1','Q3'))
    df = df.rename(columns={'Q1. House Affiliation': 'house', 'Q3. Geographical Designation': 'province'})
    df = pd.crosstab(index=df['province'], columns=df['house'])
    # merge the available seat count with the survey responses
    df = pd.merge(df, df_can[['province','seats_Senators_filled','seats_MPs','seats_Total_avail']], on='province', how='left')

    # PLOT:
    # We will make 4 plots:
    #   1. total % respondants from each province, pooled across senators and MPs
    #   2. % respondants of total SEATS from each prov (pooled across senators and MPs)
    #   3. % respondants of senators from each prov, normalized by filled seats
    #   4. % respondants of MPs from each prov, normalized by elected seats
    if map_type=='totalRespondants': 
        # total % respondants from each province, pooled across senators & MPs
        # define PLOTTING things:
        ax_cmap = 'Reds'
        ax_vmax = 60
        leg_label = '% of total respondants'
        fig_name = 'fig_q3_Total'
        # GET DATA:
        # calc respondants per province/territory (pool across senators & mps)
        df['plot_data'] = ((df['House of Commons'] + df['Senate']) / survey_raw.shape[0]) *100
    elif map_type=='regionRespondants': 
        # % respondants (per total SEATS from each prov), pooled across senators & MPs
        # define PLOTTING things:
        ax_cmap = 'Blues'
        ax_vmax = 20
        leg_label = '% of region seats'
        fig_name = 'fig_q3_normalizedTotal'
        # GET DATA:
        df['plot_data'] = ((df['House of Commons'] + df['Senate']) / df['seats_Total_avail']) *100
    elif map_type=='regionSenate':
        # % respondants of senators from each prov, normalized by filled seats
        # define PLOTTING things:
        ax_cmap = 'Purples'
        ax_vmax = 50
        leg_label = '% of region Senators'
        fig_name = 'fig_q3_normalizedSenate'
        # GET DATA:
        df['plot_data'] = (df['Senate'] / df['seats_Senators_filled']) *100
    elif map_type=='regionMP':
        # % respondants of MPs from each prov, normalized by elected seats
        # define PLOTTING things:
        ax_cmap = 'Greens'
        ax_vmax = 50
        leg_label = '% of region MPs'
        fig_name = 'fig_q3_normalizedMP'
        # GET DATA:
        df['plot_data'] = (df['House of Commons'] / df['seats_MPs']) *100
    else:
        print(map_type,' is not a valid map_type')

    # merge the demographics with the Canada geopandas dataframe
    df_can = pd.merge(df_can, df[['province','plot_data']], on='province', how='left')
    df_can['plot_data'] = df_can['plot_data'].replace(0,np.nan) # make 0% into nans so the region is plotted in grey
    df_can['plot_label'] = df_can['plot_data'].fillna(0) # change nan to 0% for text labels
    # now do plotting and labelling
    fig, ax = plt.subplots(figsize=(15,15))
    ax = df_can.plot(ax=ax, column='plot_data', vmax=ax_vmax, 
                 cmap=ax_cmap, linewidth=0.75, edgecolor='0.9', 
                 missing_kwds={'color': 'lightgrey'}, 
                 legend=True, 
                 legend_kwds={'shrink':0.3, 'label':leg_label}
                 )
    ax.set_axis_off()
    cspc.geoplot_add_value_labels(df_can, 'plot_label', ax)
    plt.show(block=False)

    return fig, ax


def demographic_q4(survey_raw):
    # ----- Q4. GENDER -----#
    # GET DATA:
    df = cspc.get_question(survey_raw, 'Q4')
    # count and convert to percent
    df = df['Q4. Gender'].value_counts(normalize=False, dropna=False).rename_axis('gender').to_frame('count')
    df['percent'] = (df['count'] / survey_raw.shape[0]) * 100

    # PLOT:
    fig, ax = plt.subplots(figsize=(5,5))
    ax.set_axis_off()
    cspc_colors = cspc.get_cspc_colors()
    df.plot.pie(y='percent', ax=ax, colors=cspc_colors, 
        autopct='%.0f%%', legend=False)
    ax.set_title('Respondant gender')
    plt.show(block=False)

    return fig, ax

# MISC HELPER FUNCTIONS are in cspc_parliament_survey_2022_funcs.py
