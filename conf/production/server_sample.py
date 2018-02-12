from fabric.state import env


def machine():
	"""
	Example configuration of a server.

	Copy and replace with actual values.
	""" 
    env.hosts = ['ubuntu@100.200.30.40']
    env.user = 'ubuntu'
    env.config_dir = 'production'
    env.git_branch = 'master'
    env.site_name = 'amazonbot'
    env.path = '~/sites/%s' % env.site_name
