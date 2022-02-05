# File to hold several helper functions for CSPC parliamentary survey analyses
# spencer arbuckle 2022 (saarbuckle@gmail.com)

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# - - - - - - - - - - - #

def load_survey_data(survey_csv_filename):
	"""
	This function loads the raw survey data from a csv file.
	The data is arranged into a pandas dataframe object.
	Only 'submitted' responses are kept (all 'in progress' rows are dropped)
	---
	INPUTS:
	survey_csv_filename : path to survey csv file (string)
	OUTPUTS:
	survey_raw : raw survey responses (pandas dataframe)
	"""

	# load survey data
	survey_raw = pd.read_csv(survey_csv_filename, encoding = 'utf-8')
	# only keep submitted responses (i.e. completed)
	survey_raw = survey_raw[survey_raw['Status']  == 'Submitted']

	return survey_raw


def get_question(survey_raw, question_string):
	"""
	This function will pull out the specified question(s) from the 
	survey_raw dataframe.
	---
	INPUTS:
	survey_raw : raw survey responses (pandas dataframe)
	questions_to_keep : question number we will be keeping (string or tuple of strings)
		e.g.: questions_to_keep = 'Quesiton 1' for questions 1 and 3
	OUTPUTS:
	survey_kept : survey responses for specified questions (pandas dataframe)
	"""

	#extract all columns for Question 4 
	filter_col = [col for col in survey_raw if col.startswith(question_string)] #creates a list of column names for question
	#create a subset of data for question 12
	survey_kept = survey_raw[filter_col] 
	
	return survey_kept


def load_canada_shapefile():
	"""
	This function will load a canada shapefile used for geopandas plots
	"""

	# load canada shape file:
	can_map = gpd.read_file('canada_map/lpr_000b16a_e.shp')
	can_map.rename(columns={'PRENAME':'province'}, inplace=True)
	# get centroids of provinces/territories
	can_map['centroid_x'] = can_map.centroid.x
	can_map['centroid_y'] = can_map.centroid.y
	
	# add columns for # senator and MP seats per prov/territory
	prov = ('Ontario','Quebec',
		'British Columbia','Alberta','Manitoba','Saskatchewan',
		'Nova Scotia','New Brunswick','Prince Edward Island',
		'Newfoundland and Labrador','Northwest Territories','Yukon','Nunavut')
	region = ('Ontario','Quebec',
		'Western Canada','Western Canada','Western Canada','Western Canada',
		'Maritimes','Maritimes','Maritimes',
		'N/A','N/A','N/A','N/A')
	seat_sen = np.array([24, 24, 6, 6, 6, 6, 10, 10, 4, 6, 1, 1, 1])
	seat_vacant_sen = np.array([4, 0, 1, 2, 1, 1, 1, 2, 1, 1, 0, 0, 0])
	seat_mp = np.array([121, 78, 42, 34, 14, 14, 11, 10, 4, 7, 1, 1, 1])
	seat_fill_sen = seat_sen - seat_vacant_sen
	seat_total_avail = seat_sen + seat_mp
	tmp = {'province':prov, 'region':region, 'seats_Senators_total':seat_sen,
	'seats_Senators_vacant':seat_vacant_sen, 'seats_Senators_filled':seat_fill_sen,
	'seats_MPs':seat_mp, 'seats_Total_avail':seat_total_avail}
	tmp_df = pd.DataFrame(data=tmp) # make datastructure to then merge with can_map

	can_map = pd.merge(can_map, tmp_df, on='province', how='left')

	return can_map


def get_cspc_colors():
	"""
	This function will return a list of cspc colours coded as 6 hex digit
	"""

	cspc_colors = ['#203864', '#4472c4', '#b4c7e7', '#e3877d', '#c00000', '#a5a5a5', '#C5C9C7']
	return cspc_colors


def label_proportions_stacked_bar(df,ax):
	"""
	This function will apply proportion labels to each component of a stacked bar chart
	INPUTS:
	df : dataframe object that is plotted and will be used for labelling
	ax : axis object that labels will be applied to
	OUTPUTS:
	none
	"""
	
	#looping to label text for proportion text
	for n, x in enumerate([*df.index.values]):
		for (proportion, x_loc) in zip(df.loc[x], df.loc[x].cumsum()):
			if proportion>2: # only label the proportion if larger than some value (here, 2%)    
				ax.text(x=(x_loc - proportion) + (proportion / 2)*0.9, #placement of text
					y=n-0.02, # label location along y-axis
					s=round(proportion), # round label to zero decimal places
					#s="{:%.0f%%}".format(x['proortion'].round(0)),
					color="white",
					fontsize=8)


def geoplot_add_value_labels(df_can, col_name, ax):
	"""
	This function adds text labels to geopandas plot.
	Labels denote the % value associated with each prov/terr.
	INPUTS:
	df_can : geopandas dataframe that is plotted
	col_name : name of column that is used for labels
	ax :  axis object to label
	OUTPUTS:
	none
	"""
	df_can.apply(lambda x: ax.text(x['centroid_x'], x['centroid_y'],
		"{:.1%}".format(x[col_name]/100), fontsize=5, 
		horizontalalignment='center', color='black', 
		bbox={'facecolor': 'white', 'alpha':0.8, 'pad': 2, 'edgecolor':'none'}), 
		axis=1
		);
