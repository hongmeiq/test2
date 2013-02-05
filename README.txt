README

============================================
get_data_dir.py
============================================

To download files from ADCS document repository, simply run the following command line in your terminal:

	python get_data_dir.py

To get help, run this command line:
	
	python get_data_dir.py -h
	or
	python get_data_dir.py --help

------------------------------
Configuration
------------------------------
You have two ways to define which directory to grab the files from, and where to save the files to:

	1. via command line arguments [see section "Command Line Arguments" for more details]
	2. in a conf.json file [see section "CONF FILE" for more details]

Note: the specs defined via the command line arguments will always have the higher precedents than the conf.json file.  

Things you can specify in both conf.json file and via the command line:

	- username: your adcs edc portal login name
	- password: your adcs edc portal password
	- source url: where to grab the files from ADCS Document Repository. e.g. https://adcs-adni.iadcs.ucsd.edu/docs/data1
	- target directory: where to store the files to on your machine/server
	- recursive: by default this feature is turned off; if specified, files under all subdirectories will also be saved
	
Things you can only specify via the command line:

	-h or --help: brings up this README page
	-v or --verbose: additional output messages

------------------------------
Command Line Arguments
------------------------------
-u or --username
-p or --password
-s or --sourceurl
-t or --targetdir
-r or --recursive
-v or --verbose
-h or --help

Example:
	python get_data_dir.py -s https://adcs-adni.iadcs.ucsd.edu/docs/data1 -v -r

------------------------------
CONF FILE
------------------------------
File name: conf.json
Location: always under the same directory with get_data_dir.py
	e.g. if get_data_dir.py is located under /Users/xxx/Desktop/data_folder, 
	then the conf.json has to be located under /Users/xxx/Desktop/data_folder

Note: if you are planning to define all the specs using command line arguments, you don't need to create a conf.json file

JSON keywords:
	username
	password
	source_url
	target_directory
	recursive
	
Example:
{
	"username": "userx",
	"password": "ppp",
	"source_url":"https://adcs-adni.iadcs.ucsd.edu/docs/data1",
	"target_directory":"/Users/xxx/Desktop/data_folder",
	"recursive":1        
}



============================================
get_data.py
============================================

-------------------------------------------------------------------------------
You see this message because you have -h parameter. i.e. python get_data.py -h
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

