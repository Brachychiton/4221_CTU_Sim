import simpy
from simpy.events import AllOf
from random import randint

processes = {'Chain_Type': ['Single',
                            'Simple Parallel',
                            'Single',
                            'Sinple Parallel',
                            'Single',
                            'Stage 2 Parallel',
                            'Single'
                            'Simple Parallel'],
             'Names': [# first single
                       ['Sponsor Contacts CT Co-ord/Mgr or PI',
                       'Refer to Start Up Specialist',
                       'Complete CDA',
                       'Sponsor Provides Protocol',
                       'Co-ord and PI decide if they want to explore further',
                       'Co-ord and PI explore further - read Protocol',
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
                       'PICFs Updated',
                       'Sponsor Approval of PICFs'],
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


def print_process_info(name, length):
    """ Prints event details """
    print("%s took %i" % (name, length))
    print("Current time is ", env.now)

def single(env, names, first_fixed=False):
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

def stage_2_sub_parallel(env, names):
    """ Produces parallel process generator for parallel stage 1 stubs """
    parallel_events = [env.process(stage_2_sub_stub(env, name)) for name in names]
    yield AllOf(env, parallel_events)

def stage_2_sub_stub(env, names):
    """ Specific event run setup for the flow diagram stub in stage 2 sub """
    if names[0] == "Preparation of Submission Documents":
        yield env.process(single(env, names))
    elif names[0] == 'Request Relevant Docs from Sponsor':
        yield env.process(single(env, names))
    else:
        for i, name in enumerate(names):
            if i == 0:
                yield env.process(simple_parallel(env, name))
            else:
                yield env.process(single(env, name))

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
        elif chain_type == 'Stage 2 Parallel':
            yield env.process(stage_2_sub_parallel(env, names))
        else:
            pass

#if this file is being run directly
if __name__ == "__main__":
    #run the simulation environment
    env = simpy.Environment()
    p = env.process(chainer(env))
    env.run()