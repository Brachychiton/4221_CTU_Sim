import pandas as pd 
from scipy.stats import truncnorm



class TimeLoader:
    def __init__(self, test_sample=[]):
        # loading time data
        self.data = pd.read_csv('overview_times.csv', index_col='Activity')
        # intitialising values
        self.times = 0
        self.sample = -1
        self.test_sample = test_sample
        self.activity = ""
    
    def get_activity_data(self, activity):
        self.activity = activity
        self.sample = -1
        # getting activity specific time
        self.times = self.data.loc[[self.activity],['Min', 'Mean', 'Max']]
        self.times = self.times.loc[self.activity]
        # rearranging to dict format
        self.times = self.times.to_dict()
        for _ in range(10):
            if self.sample <= 0:
                self.gen_time()
            else:
                break

    def gen_time(self):
        """ Takes process time min, max and mean and generates 1000 random samples."""
        t_min = self.times['Min']
        t_max = self.times['Max']
        t_sig = self.times['Mean']
        # generating activity time based on truncnorm distribution
        # see StatDistExp jupyter notebook for more details
        # if in test sample, activity time mean/max brought 25% closer
        # the min
        if self.activity in self.test_sample:
            t_max = min(int(t_min + (t_max - t_min)*3/4), t_max-1)
            t_sig = min(int(t_min + (t_sig - t_min)*3/4), t_sig-1)
            t_max = max(t_max, 1)
            t_sig = max(t_sig, 1)
        t_scale = min(t_sig-t_min, t_max-t_sig)/3*2
        #accounting for when activity time is always 1 day
        if t_min == t_max == t_sig:
            self.sample = t_min
        else:
            #this is the normal case generation of activity time
            self.sample = truncnorm.rvs(a=t_min-t_sig, b=t_max-t_sig, scale=t_scale, size=1)[0]
            self.sample += t_sig
            self.sample = int(self.sample)