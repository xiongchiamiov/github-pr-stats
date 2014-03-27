from invoke import run, task

@task
def doc():
   run('cd docs && make html')

@task
def publish():
   run('rm MANIFEST')
   run('./setup.py sdist upload')

