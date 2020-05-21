import simpy
from simpy.events import AllOf
import pandas as pd
from TimeLoader import TimeLoader

""" Performs 100 simulations of the overview process diagram based on
overview_times.csv. Must be understood in reference to the diagram."""

# this assigns chain types to all individual chains of the overview process map
# acts as the 'cook book' which translates the process diagram for the model run
processes = {'Chain_Type': ['Single',
                            'Simple Parallel',
                            'Single',
                            'Simple Parallel',
                            'Single',
                            'Stage 2 Parallel',
                            'Single',
                            'Simple Parallel'],
             'Names': [# first single
                       ['Sponsor Contacts CT Co-ord/Mgr or PI',
                       'Refer to SSS or Co-ordinator',
                       'Complete CDA',
                       'Sponsor Provides Protocol',
                       'Co-ord and PI decide if they want to explore further',
                       'Co-ord and PI explore further - read Protocol ',
                       'Receive Key Trial Information from Sponsor',
                       'Provide Trial Start Up information to Sponsor'],
                       # first simple parallel
                       [['Feasibility Assessment by PI and Co-ord'],
                       ['Site Assessment Visit or Phonecall']],
                       # second single
                       ['Decision by Sponsor/CHS that Trial is Feasible'],
                       # second simple parallel
                       [['Acquite Relevant Docs from CHS (CDA and SPA Report)'],
                       ['Complete CTMG Submission Forms (Feas & Gov Sheet)'],
                       ['Develop Required Docs (Plain Language Summary)']],
                       # third single
                       ['Obtain PI Approval',
                       'Send REGO Submission for CTMG Meeting',
                       'CTMG Meeting',
                       'Notice received of  Approval to Proceed'],
                       # Stage 2 Parallel
                       [
                           [
                               [['Request Relevant Docs from Sponsor',
                               'Request Provider Quotes',
                               'Receive Provider Quotes'],
                               ['Request Relevant Docs from Sponsor',
                               'Supply CTRA and Budget to Finance Team',
                               'Update CTRA Schedule 1 and 2',
                               'Draft Budget Spreadsheet']],
                               ['Finance and Co-ord Review Budget',
                               'Negotiate Budget with Sponsor',
                               'Prepare Finance Summary']],
                       ['Request Relevant Docs from Sponsor',
                       'Lead Site Approved',
                       'Lead Site Approval Letter and Documents Received ',
                       'PICF\'s Updated',
                       'Sponsor Approval of PICF\'s'],
                       ['Preparation of Submission Documents']],
                       # fourth single
                       ['Submit for REGO with all attachments',
                       'REGO provide Approval',
                       'Create Visit Payment Schedule',
                       'Create Patient List',
                       'Creat Source Documents for Visits',
                       'Site Initiation Visit'],
                       # third simple parallel
                       [['Invoice Sponsor for Start Up Fee'],
                       ['Receive Notification of Site Activation']]
             ]
            }
#activities in the process which are being analysed for how varying
# process time affects total process length
test_samples = [
            [
                'Request Relevant Docs from Sponsor',
                'Lead Site Approved',
                'Lead Site Approval Letter and Documents Received',
                'PICF\'s Updated',
                'Sponsor Approval of PICF\'s'
            ],
            [
                'Request Relevant Docs from Sponsor',
                'Supply CTRA and Budget to Finance Team',
                'Update CTRA Schedule 1 and 2',
                'Draft Budget Spreadsheet'
            ],
            [
                'Finance and Co-ord Review Budget',
                'Negotiate Budget with Sponsor',
                'Prepare Finance Summary'
            ]
        ]
# boolean which defines whether testing is occurring
testing = False
all_names = []
def unnest(names):
    for name in names:
        if isinstance(name, str):
            all_names.append(name)
        else:
            unnest(name)
unnest(processes['Names'])


def print_process_info(name, length):
    """ Prints event details """
    print("%s took %i" % (name, length))
    print("Current time is ", env.now)
    #appending to activity time vector
    times.append(length)


def single(env, names, t_doc_request):
    """ Runs a single event """
    for name in names:
        #generation of trip time
        if name == 'Request Relevant Docs from Sponsor':
        # for simplification of model this process occurs in three chains
        # called at same time but requires consistency in activity time
            if t_doc_request == 0:
                #initialised to zero for first call
                TimeFetcher.get_activity_data(name)
                length = TimeFetcher.sample
                t_doc_request = length
            else:
                #else we already have a time for this process
                length = t_doc_request
        else:
            #else it's any of the other process so get time
            TimeFetcher.get_activity_data(name)
            length = TimeFetcher.sample
        #this yield call slots the event time within the process
        yield env.timeout(length)
        #additional call to print event info
        print_process_info(name, length)

def simple_parallel(env, names, t_doc_request):
    """ Runs n=len(names) events in parallel """
    parallel_events = [env.process(single(env, name, t_doc_request)) for name in names]
    yield AllOf(env, parallel_events)

def stage_2_sub_parallel(env, names, t_doc_request):
    """ Produces parallel process generator for parallel stage 1 stubs """
    #make list of all invididual sub processes chains
    parallel_events = [env.process(stage_2_sub_stub(env, name, t_doc_request)) for name in names]
    #yields them in parallel
    yield AllOf(env, parallel_events)

def stage_2_sub_stub(env, names, t_doc_request):
    """ Specific event run setup for the flow diagram stub in stage 2 sub """
    #this chain is a simple single process chain
    if names[0] == "Preparation of Submission Documents":
        yield env.process(single(env, names, t_doc_request))
    #this chain is the same
    elif names[0] == 'Request Relevant Docs from Sponsor':
        yield env.process(single(env, names, t_doc_request))
    #complex section of the chain must be further broken down
    else:
        for i, name in enumerate(names):
            #first chain is a simple parallel
            if i == 0:
                yield env.process(simple_parallel(env, name, t_doc_request))
            #second is single chain
            else:
                yield env.process(single(env, name, t_doc_request))

def chainer(env):
    """ Chains together all the separate process to operate the whole simulation.
    Goes off the 'processes' dict at top of file. """
    #initialising time for repated processes
    t_doc_request = 0
    #iterating through chain type
    for i, chain_type in enumerate(processes['Chain_Type']):
        #get relevant process name or nested list
        names = processes['Names'][i]
        #basing process function choice on chain type
        if chain_type == 'Single':
            yield env.process(single(env, names, t_doc_request))
        elif chain_type == 'Simple Parallel':
            yield env.process(simple_parallel(env, names, t_doc_request))
        elif chain_type == 'Stage 2 Parallel':
            yield env.process(stage_2_sub_parallel(env, names, t_doc_request))
        else:
            pass


#if this file is being run directly
if __name__ == "__main__":
    """ testing implies whether modification are made within the TimeLoader class to
    adjust target activity times """
    if not testing:
        #initialise time class
        TimeFetcher = TimeLoader()
        times_dict = {}
        #1000 stochastic simulations run
        for i in range(1000):
            times = []
            #run the simulation environment
            env = simpy.Environment()
            p = env.process(chainer(env))
            env.run()
            times_dict[i] = times
        #outputting results to csv file
        output = pd.DataFrame(data=times_dict, index=all_names)
        output.loc['Total Process Time'] = output.sum(axis=0)
        output['Mean Time'] = output.mean(axis=1)
        output.to_csv('sim_output.csv')
    if testing:
        #same as above but with test sample lists inputted to TimeLoader class
        for i, test_sample in enumerate(test_samples):
            TimeFetcher = TimeLoader(test_sample)
            times_dict = {}
            for j in range(1000):
                times = []
                #run the simulation environment
                env = simpy.Environment()
                p = env.process(chainer(env))
                env.run()
                times_dict[j] = times
            output = pd.DataFrame(data=times_dict, index=all_names)
            output.loc['Total Process Time'] = output.sum(axis=0)
            output['Mean Time'] = output.mean(axis=1)
            output.to_csv('sim_output_' + str(i) + '.csv')
    