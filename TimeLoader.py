import pandas as pd 
from scipy.stats import truncnorm

class TimeLoader:
    def __init__(self):
        self.data = pd.read_csv('overview_times.csv', index_col='Activity')
        self.times = 0
        self.sample = -1
    
    def get_activity_data(self, activity):
        self.sample = -1
        self.times = self.data.loc[[activity],['Min', 'Mean', 'Max']]
        self.times = self.times.loc[activity]
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
        t_scale = min(t_sig-t_min, t_max-t_sig)/3*2
        if t_min == t_max == t_sig:
            self.sample = t_min
        else:
            self.sample = truncnorm.rvs(a=t_min-t_sig, b=t_max-t_sig, scale=t_scale, size=1)[0]
            self.sample += t_sig
            self.sample = int(self.sample)

if __name__ == "__main__":
    a = TimeLoader()
    a.get_activity_data('REGO provide Approval')