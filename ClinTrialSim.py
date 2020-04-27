import simpy
from simpy.events import AllOf
from random import randint

processes = {'Chain_Type': ['Single',
                            'Simple Parallel',
                            'Single'],
             'Names': [[
                       'Refer to Start Up Specialist',
                       'Completion of CDA',
                       'Sponsor Provides Protocol',
                       'Explore Further?',
                       'Provide Info to and Request Info From Sponsor'
                       ],
                       [['Email to Sponsor Disclosing Fees & Trial Setup Info',
                         'Site Inspection/Assessment Visit'],
                        [ 'Request Sponsor to Provide Key Trial Info Including Protocol',
                         'Feasability Assessment']
                       ], 
                       ['Trial Feasible?'] 
             ]
            }
def print_process_info(name, length):
    print("%s took %i" % (name, length))
    print("Current time is ", env.now)

def single(env, names):
    for name in names:
        length = randint(1,5)
        yield env.timeout(length)
        print_process_info(name, length)

def simple_parallel(env, names):
    parallel_events = [env.process(single(env, name)) for name in names]
    yield AllOf(env, parallel_events)
    


def chainer(env):
    for i, chain_type in enumerate(processes['Chain_Type']):
        names = processes['Names'][i]
        if chain_type == 'Single':
            yield env.process(single(env, names))
        elif chain_type == 'Simple Parallel':
            yield env.process(simple_parallel(env, names))
        else:
            pass

env = simpy.Environment()
p = env.process(chainer(env))
env.run()