def setup(globalEnv, localEnv):
   localEnv['message'] = 'hai!'

def analyze_pull(globalEnv, localEnv):
   print localEnv['message']

def print_report(globalEnv, localEnv):
   print 'onigoshimosh'

