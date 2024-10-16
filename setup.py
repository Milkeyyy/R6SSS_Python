from setuptools import setup, find_packages

def get_requirements_from_file():
	with open("./requirements.txt") as f:
		r = f.read().splitlines()
	return r

setup(
	name="r6sss",
	version="0.1.0",
	description="Rainbow Six Siege Server Status Web API Wrapper Library",
	author="Milkeyyy",
	packages=find_packages(),
	requires=get_requirements_from_file()
)
