import simpy
from simpy.events import AllOf
from random import randint

""" This dictionary translates process maps into format which the chainer function can read off """
processes = {'Chain_Type': ['Single',
                            'Simple Parallel',
                            'Single',
                            'Stage 1 Parallel',
                            'Single'],
             'Names': [#first single
                       [
                       'Refer to Start Up Specialist',
                       'Completion of CDA',
                       'Sponsor Provides Protocol',
                       'Explore Further?',
                       'Provide Info to and Request Info From Sponsor'
                       ],
                       #first simple parallel
                       [['Email to Sponsor Disclosing Fees & Trial Setup Info',
                         'Site Inspection/Assessment Visit'],
                        [ 'Request Sponsor to Provide Key Trial Info Including Protocol',
                         'Feasability Assessment']
                       ], 
                       #second single
                       ['Trial Feasible?'],
                       #stage 1 sub parallel
                       [['Coordinator Develop Relevant Documentation'], 
                        ['Plain Language Summary',
                         'Protocol Summary'
                        ],
                        ['Coordinator Complete CTMG Submission Forms'], 
                        ['Feasability Forms',
                         'Governance Clearance Form'
                        ],
                        ['Request Radiation Safety Report & Copy of Latest Special Purpose Accounts'], 
                        ['Receive Radiation Safety Report',
                         'Receive Copy of Latest Special Purpose Account'
                        ]
                        ],
                        # third single
                        ['PI Approval',
                         'Electronic Submission to REGO',
                         'CTMG Meeting',
                         'Approval Received']
             ]
            }
def print_process_info(name, length):
    """ Prints event details """
    print("%s took %i" % (name, length))
    print("Current time is ", env.now)

def single(env, names):
    """ Runs a single event """
    for name in names:
        #current generation of trip time
        length = randint(1,5)
        yield env.timeout(length)
        #additional call to print event info
        print_process_info(name, length)

def simple_parallel(env, names):
    """ Runs n=len(names) events in parallel """
    parallel_events = [env.process(single(env, name)) for name in names]
    yield AllOf(env, parallel_events)

def stage_1_sub_parallel(env, names):
    """ Produces parallel process generator for parallel stage 1 stubs """
    parallel_events = [env.process(stage_1_sub_stub(env, name)) for name in names]
    yield AllOf(env, parallel_events)

def stage_1_sub_stub(env, names):
    """ Specific event run setup for the flow diagram stub in stage 1 sub """
    #iterating through the different events
    for name in names:
        #if there isn't another nested list
        if isinstance(name, str):
            #then it's just a single event run
            yield env.process(single(env, [name]))
        #otherwise there's a single nested list
        else:
            #run the parallel event function
            yield env.process(simple_parallel(env, name))


def chainer(env):
    """ Chains together all the separate process to operate the whole simulation.
    Goes off the 'processes' dict at top of file. """
    #iterating through chain type
    for i, chain_type in enumerate(processes['Chain_Type']):
        #get relevant process name or nested list
        names = processes['Names'][i]
        #basing process function choice on chain type
        if chain_type == 'Single':
            yield env.process(single(env, names))
        elif chain_type == 'Simple Parallel':
            yield env.process(simple_parallel(env, names))
        elif chain_type == 'Stage 1 Parallel':
            yield env.process(stage_1_sub_parallel(env, names))
        #inluding else for completeness lol
        else:
            pass

#if this file is being run directly
if __name__ == "__main__":
    #run the simulation environment
    env = simpy.Environment()
    p = env.process(chainer(env))
    env.run()