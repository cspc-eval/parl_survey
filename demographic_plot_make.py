# File to make the demographic figures for 2022 parliamentary survey (covid and science)
# spencer arbuckle 02/2022 (saarbuckle@gmail.com)

import matplotlib.pyplot as plt
import demographic_plot_funcs as dgp
import cspc_parliament_survey_2022_funcs as cspc

# GET SURVEY DATA:
# load survey data (keeping only "submitted" survey responses)
survey_raw = cspc.load_survey_data('PrelimData_Feb02.csv')

# PLOT DEMOGRAPHIC DATA (and save figs):
fig,_ = dgp.demographic_q1q2(survey_raw)
plt.close(fig)
fig.savefig('fig_q1_q2', dpi=1080)
fig,_ = dgp.demographic_q4(survey_raw)
fig.savefig('fig_q4', dpi=1080)
plt.close(fig)

# maps:
types = ('totalRespondants','regionRespondants','regionSenate','regionMP')
fig_name = "fig_q3_{map_type}"
for t in types:
	fig,_ = dgp.demographic_q3(survey_raw, t)
	fig.savefig(fig_name.format(map_type=t), dpi=1080)
	plt.close(fig)