#!/usr/bin/python
import urllib, urllib2
import sys, getopt
import re, os
import cookielib
import json
import urlparse

def main(argv):
    ## configurations
    recursive = False
    verbose = False

    host = ''
    realm = ''
    target_directory = ''
    username = ''
    password = ''
    source_directory = ''

    
    ## overwrite the configurations from the .conf file 
    main_path = os.path.dirname(__file__)
    conf_file_name = 'conf.json'
    
    if os.path.exists(os.path.join(main_path, conf_file_name)) == True:
        conf_json_file = open (os.path.join(main_path, conf_file_name), 'r')
        try:
            conf_json = json.load(conf_json_file)
        except:
            print "Error: {0} is not a valid configuration file".format(os.path.join(main_path, conf_file_name))
            sys.exit(2)
            
        conf_json_file.close()
        
        try:
            target_directory = conf_json['target_url']
        except:
            target_directory = ''
    
        try:
            uriparser = urlparse.urlparse(conf_json['source_directory'])            
            host = uriparser[0]+"://"+uriparser[1]
            source_directory = uriparser[2]
        except:
            host = ''
            source_directory = ''
    
        try:
            username = conf_json['username']
        except:
            username = ''
    
        try:
            password = conf_json['password']
        except:
            password = ''
            
    
    ## reading command line arguments
    # user can overwrite the following configurations: target directory, username, password, host, source directory
    try:
        opts, args = getopt.getopt(argv, "s:t:u:p:rvh", ["sourceurl=","targetdir=","username=", "password=","recursive","verbose","help"])
    except getopt.GetoptError:
        print "get_data_dir.py -s <sourcedir> -t <targetdir> -u <username> -p <password> -r <recursive> -v <verbose>"
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-s", "--sourceurl"):
            uriparser = urlparse.urlparse(arg)
            host = uriparser[0]+"://"+uriparser[1]
            source_directory = uriparser[2]
        elif opt in ("-t", "--targetdir"):
            target_directory = arg
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-r", "--recursive"):
            recursive = True
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-h","--help"):
            print readme()
            sys.exit(2)
            
    ## validations
    # host name should start with 'https' and end with 'iadcs.ucsd.edu'
    validateHost = re.search(r'^https://', host)
    if validateHost == None:
        print "Error: please provide a valid source url. (start with https://)"
        sys.exit(2)
        
    validateHost = re.search(r'iadcs\.ucsd\.edu\s*$', host)
    if validateHost == None:
        print "Error: please provide a valid host name. (end with .iadcs.ucsd.edu)"
        sys.exit(2)
    
    # length of username and password should be greater than zero
    if len(username) == 0 or len(password) == 0:
        print "Error: please provde a valid username/password."
        sys.exit(2)

    # source url
    if len(host) == 0 or len(source_directory) == 0:
        print "Error: please specify a source url."
        sys.exit(2)        
    
    # remove trailing slash from the source directory
    if source_directory.endswith('/'):
        source_directory = source_directory[:-1]
                            
    # target directory should be a valid directory
    if len(target_directory) > 0 and os.path.exists(target_directory) == False:
        print "Error: please provide a valid target directory."
        sys.exit(2)
         
    # if user defined target directory doesn't end with "/", add it
    checkDir = re.search(r'/$', target_directory, re.I)
    if len(target_directory) > 0 and checkDir == None: 
        target_directory = target_directory + "/"

    ## guess realm based on host name
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
        print "Error: failed to find realm information based on the host name provided."
        sys.exit(2)
    
    # recursive hardstop: max of 50 levels
    hardstop = 50
    
    save_files (host, realm, username, password, source_directory, target_directory, verbose, recursive,"\t",hardstop)


def save_files (myhost, myrealm, myusername, mypassword, mysource_directory, mytarget_directory, myverbose, myrecursive,indent_txt,countdown):
    # hard stop
    if countdown == 0:
        return
        
    countdown=countdown-1;

    # if user defined target directory doesn't end with "/", add it
    mycheckDir = re.search(r'/$', mytarget_directory, re.I)
    if len(mytarget_directory) > 0 and mycheckDir == None: 
        mytarget_directory = mytarget_directory + "/"

    # if source directory end with /, remove it
    mysource_directory = re.sub(r'/\s*$', "", mysource_directory)

    if myverbose == True:
        print "\n{1}Processing {0} directory... ".format(mysource_directory, re.sub(r'^\t', "", indent_txt))
        main_path = os.path.dirname(__file__)
        if len(mytarget_directory) > 0:
            print "{1}All files will be saved under {0} directory.".format(os.path.join(main_path, mytarget_directory),indent_txt)
        else:
            print "{0}All files will be saved under current directory.".format(indent_txt)     
    
    ## call public docs api to grab directory contents
    api_path = '/docs/api/1/list.json'
    params = urllib.urlencode({"resource_pathname":mysource_directory})
    res = get(myhost + api_path + "?" + params, myhost, myrealm, myusername, mypassword)
    if res == None:
        print "{1}Error: Failed to get file listing for {0} directory from public docs api.".format(mysource_directory,indent_txt)
        return

    # grab each file under the directory and save it to mytarget_directory
    res_json = json.loads(res)     
    if myverbose == True:
        print "{1}# of files: {0}".format(res_json['file_count_returned'], indent_txt)
        print "{0}---------------------------".format(indent_txt)
    
    if res_json['item_count'] == 0:
        return
        
    for obj in res_json['directory_listing']:
        try:
            obj['type']
        except:
            print "{1}Error: failed to identify type (file/directory) from public docs api".format(indent_txt)
            continue
               
        if obj['type'].lower() == 'file':
            target_file = obj['name']
            if myverbose == True:
                print "\n{1}Downloading file {0}...".format(target_file,indent_txt)
            
            file_content = None
            try:    
                file_content = get(obj['get_file_url'], myhost, myrealm, myusername, mypassword)
            except:
                print "{1}Error: Failed to authenticate {0}.".format(myhost,indent_txt)   
                continue         
                
            if file_content == None:
                print "{1}Error: Failed to get {0} file.".format(target_file,indent_txt)
                continue
                
            # writing file
            target_filehandler = open ('{0}{1}'.format(mytarget_directory, target_file), 'w')
            target_filehandler.write(file_content)
            target_filehandler.close()
            
            if myverbose == True:
                print "{1}File {0} has been successfully saved.".format(target_file,indent_txt)
        elif obj['type'].lower() == 'directory' and myrecursive == True:
            # if doesn't exist the sub directory, make a new one
            try:
                subdir = obj['resource_pathname'].__str__().replace(res_json['directory_path'], "").replace("/", "")                
                if os.path.exists(os.path.join(mytarget_directory,subdir)) == False:
                    os.makedirs(os.path.join(mytarget_directory,subdir))
            except:
                print "{1}Failed to create new directory {0}".format(os.path.join(mytarget_directory,subdir),indent_txt)
                continue

            save_files(myhost, myrealm, myusername, mypassword, obj['resource_pathname'], os.path.join(mytarget_directory, subdir), myverbose, myrecursive, indent_txt+"\t", countdown)
            
    return
    
def get(myurl, myhost, myrealm, myusername, mypassword):
    res = None
    response = None

    ## connect to server
    # first attempt with basic auth
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm = myrealm,uri = myhost,user = myusername,passwd = mypassword)
    
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

    try:
        response = urllib2.urlopen(myurl)
        ## get results
        res = response.read()
    except:
        loginmyurl = '{0}/login'.format(myhost)    
        
        # create a cookiejar
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        data = {'credential_0':myusername,'credential_1':mypassword,'destination':'/home'}
        edata = urllib.urlencode(data)

        # fake a user agent, some websites (like google) don't like automated exploration
        headers = {'User-agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

        # create a request object
        req = urllib2.Request(loginmyurl, edata, headers)
        try:
            handle = opener.open(req)
        except:
            return res
        
        # open myurl using opener obj
        response = opener.open(myurl)
        res = response.read()
    
    return res

def readme():
    # dependencies
    #     - recommended python 2.6+, for older version of python, you need to install json library
    # push to get hub/ open repo
    #     - iadcs_opensource_toolkit
    #         - README
    #         - .py

    return """
    README

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
    
    Note: the specs defined via the command line arguments always have the higher precedents than the conf.json file.  
    
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
    
    """

if __name__ == "__main__":
   main(sys.argv[1:])