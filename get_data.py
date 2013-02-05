#!/usr/bin/python
import urllib, urllib2
import sys, getopt
import re, os
import cookielib
import json
import urlparse


def main(argv):

	# # default
	target_file = ''
	source_file = ''
	password = ''
	username = ''
	
	# # configurations
	main_path = os.path.dirname(__file__)
	conf_file_name = 'conf.json'
	conf_file = os.path.join(main_path, conf_file_name)
	if os.path.exists(conf_file):
		conf_json_file = open (conf_file, 'r')
		try:
			conf_json = json.load(conf_json_file)
		except Exception, e:
			raise Exception("Not valid JSON in configuration file: \n{1}\n\n{0}".format(e, conf_file))
			
		conf_json_file.close()
		
		try:
			username = conf_json['username']
		except:
			pass
		try:
			password = conf_json['password'];
		except:
			pass
		try:
			source_file = conf_json['source_file'];
		except:
			pass
		try:
			target_file = conf_json['target_file'];
		except:
			pass
		
	
	# # reading command line arguments
	# user can overwrite the following configurations: target directory, username, password, host, source directory
	try:
		opts, args = getopt.getopt(argv, "hu:p:s:t", ["help", "username=", "password=", "soucefile=", "targetfile="])
	except getopt.GetoptError:
		print "get_data.py -h <help> -u <username> -p <password> -s <sourcefile>  -t <targetfile>"
		
	
	for opt, arg in opts:
	
		if opt in ("-h", "--help"):
			print readme()
			sys.exit() 
		elif opt in ("-s", "--sourcefile"):
			source_file = arg
		elif opt in ("-t", "--targetfile"):
			target_file = arg
		elif opt in ("-u", "--username"):
			username = arg
		elif opt in ("-p", "--password"):
			password = arg
	
	
	# # validations
	# length of username and password should be greater than zero
	if len(username) == 0 or len(password) == 0:
		raise Exception("Error: please provide a valid username/password.")
	
	
	# host name should start with 'https' and end with 'iadcs.ucsd.edu'
	validateHost = re.search(r'^https://', source_file)
	if validateHost == None:
		raise Exception("Error: please provide a valid host name. (start with https://). Parameter sourcefile [{0}]".format(source_file))
	
	uriparser = urlparse.urlparse(source_file)
	host = "{0}://{1}".format(uriparser[0],uriparser[1])
	source_file = uriparser[2]
	
	validateHost = re.search(r'iadcs\.ucsd\.edu$', host)
	if validateHost == None:
		raise Exception("Error: please provide a valid host name. (end with .iadcs.ucsd.edu)")
		
	# source directory should be provided
	if len(source_file) == 0:
		raise Exception("Error: please provide a valid source file. Parameter sourcefile [{0}]".format(source_file))
	
		
	# target directory should be a valid directory
	if len(target_file) != 0:
		t_directory = os.path.dirname(target_file)
		if os.path.exists(t_directory) == False:
			raise  Exception("Error: Please create folder of target file: Parameter targetfile [{0}]".format(t_directory))
			
		
		# target file and source file must have same extension
		s_name, s_extension = os.path.splitext(source_file)
		t_name, t_extension = os.path.splitext(target_file)
		
		if (s_extension != t_extension):
			raise Exception("Error: please provide a target and source file with same extension. Parameter sourcefile [{0}] Parameter targetfile [{0}]".format(source_file, target_file))

	# # guess realm based on host name
	realm = ''
	matchHost = re.match(r'https://(.*)\.iadcs\.ucsd\.edu', host, re.I)
	if matchHost:
		if re.match(r'^dev', matchHost.group(1), re.I):
			realm = 'CCTG'
		elif re.match(r'^adcs-igiv', matchHost.group(1), re.I):
			realm = 'IGIV'
		else:
			realm = re.sub('-', '_', matchHost.group(1))
		realm = realm.upper() + " Online"	
	else:
		raise Exception("Error: failed to find realm information based on the host name provided.")
		
	
	
	##------------------------------------------------------------------------
	
	api_path = '/docs/api/1/get_file'
	
	# # connect to server
	# first attempt with basic auth
	auth_handler = urllib2.HTTPBasicAuthHandler()
	auth_handler.add_password(
		realm=realm,
		uri=host,
		user=username,
		passwd=password
		)
	opener = urllib2.build_opener(auth_handler)
	urllib2.install_opener(opener)
	
	# # call public docs api
	res = None
	params = urllib.urlencode({"f":source_file})
	try:
		response = urllib2.urlopen(host + api_path + "?" + params)
		# # get results
		res = response.read()
	except:
	    loginurl = '{0}/login'.format(host)	
	    
	    # create a cookiejar
	    cj = cookielib.CookieJar()
	    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	    data = {'credential_0':username, 'credential_1':password, 'destination':'/home'}
	    edata = urllib.urlencode(data)

	    # fake a user agent, some websites (like google) don't like automated exploration
	    headers = {'User-agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
	    
	    # create a request object
	    req = urllib2.Request(loginurl, edata, headers)
	    handle = opener.open(req)
	    
	    # open url using opener obj
	    try:
	    	response = opener.open(host + api_path + "?" + params)
	    except:
	    	raise Exception("Failed to get result from public docs api on {0}. Please confirm if {1} exists.".format(host, source_file))
	    res = response.read()
	if res == None:
		raise Exception("Failed to get result from public docs api on {0}.".format(host))
		
	
	if len(target_file) != 0:
		target_file = open ('{0}'.format(target_file), 'w')
		target_file.write(res)
		target_file.close()
		return True
	else:
		sys.stdout.write(res)
	
def readme():
	return """
README

-------------------------------------------------------------------------------
You see this message because you have -m parameter. i.e. python get_data.py -m
-------------------------------------------------------------------------------


------------------------------
Configuration
------------------------------

Using JSON
	- conf.json set the default configuration of the script.
	- Insert conf.json in the same folder of get_data.py.
	- See examples below.

Using get_data.py parameter
	- use them if conf.json is missing
	- use them to overwrite cong.json configuration
	- Usage: get_data.py -h <host> -u <username> -p <password> -s <sourcefile>  -t <targetfile> -m <help>
	- See examples below.

------------------------------
Download csv using conf.json
------------------------------

conf.json is:
{
"host" : "https://adcs-adni.iadcs.ucsd.edu",
"username": "xxxx",
"password" : "yyyy",
"source_file": "/docs/data1/filename.csv",
"target_file": "/root/folder/sub_folder/filename.csv"
}
python get_data.py


------------------------------
Download csv overwriting conf.json
------------------------------
dowload csv in a target file:
python get_data.py -h https://adcs-adni.iadcs.ucsd.edu -u xxxxx -p yyyyyy -s /docs/data1/adni2_visitid.csv  -t /tmp/adni2_visitid.csv

dowload csv and print STDOUT (standard output):
python get_data.py -h https://adcs-adni.iadcs.ucsd.edu -u xxxxx -p yyyyyy -s /docs/data1/adni2_visitid.csv

dowload csv and redirect STDOUT to target file: 
python get_data.py -h https://adcs-adni.iadcs.ucsd.edu -u xxxxx -p yyyyyy -s /docs/data1/adni2_visitid.csv  > /tmp/adni2_visitid.csv




------------------------------
Download zip using conf.json
------------------------------

conf.json is:
{
"host" : "https://adcs-project.iadcs.ucsd.edu",
"username": "xxxx",
"password" : "yyyyyy",
"source_file": "/docs/data1/filename.zip",
"target_file": "/root/folder/sub_folder/filename.zip"
}
python get_data.py &&  unzip /root/folder/sub_folder/filename.zip -d /unzipped/folder

------------------------------
Download zip overwriting conf.json
------------------------------
dowload zip file in a target zip file:
python get_data.py -h https://adcs-adni.iadcs.ucsd.edu -u xxxxx -p yyyyyy -s /docs/data1/adni2_visitid.zip  -t /tmp/adni2_visitid.zip

dowload zip file and redirect STDOUT to target zip file: 
python get_data.py -h https://adcs-adni.iadcs.ucsd.edu -u xxxxx -p yyyyyy -s /docs/data1/adni2_visitid.zip  > /tmp/adni2_visitid.zip 

dowload zip file and unzip in ./unzipfolder folder:
python get_data.py -h https://adcs-adni.iadcs.ucsd.edu -u xxxxx -p yyyyyy -s /docs/data1/adni2_visitid.zip  -t /tmp/adni2_visitid.zip && unzip /tmp/adni2_visitid.zip -d ./unzipfolder

"""

if __name__ == "__main__":
   main(sys.argv[1:])
