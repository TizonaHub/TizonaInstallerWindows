import subprocess
import pymysql
import ctypes
import os
from os.path import abspath
import sys
import string
import requests
from win32com.client import Dispatch
import pathlib
import re
import shutil


CREATE_NO_WINDOW = 0x08000000
adminData={
     "username":'root',
     "password":'0000'
}
dbEnvData={
    "username":'',
    "db":'',
    'password':''
}
def getVersionNumber(string):
    if not string: return False
    match = re.search(r"\d+(\.\d+)*", string)
    if match:
        return match.group()
    return ''

def getPartitions():
    partitions = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            partitions.append(f"{letter}:\\")
        bitmask >>= 1
    return partitions

def checkNode(defaultPath=False,newPath=False,nvm=False):
    path='node'
    if newPath: path=newPath
    if defaultPath: path = r'C:\Program Files\nodejs\node.exe'
    if nvm: path= 'node'

    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True,
            text=True,
            check=True,
            creationflags=CREATE_NO_WINDOW
        )
        return getVersionNumber(result.stdout.strip())
    except Exception as e:
        return False


def getRandomString(specialChars=True,length=78):
    import random
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=<>?"
    if not specialChars: chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    string = ""

    for i in range(length):
        char = chars[random.randint(0,length)]
        string = string + char
    return string

def createDB(dbName):
    myDb = getConnection()
    if not myDb: return False
    mycursor = myDb.cursor()
    try:
        mycursor.execute(f"CREATE DATABASE {dbName};")
        return True
    except Exception as e:
        None
        #print('Exception at createDb: ', e)
    myDb.close()
    return False

def createUser(user,password):
    try:
        mydb = getConnection()
        mycursor = mydb.cursor()
        sql = "CREATE USER %s@'localhost' IDENTIFIED BY %s;"
        mycursor.execute(sql, (user,password))
        mydb.close()
        print('user created')
        return True
    except Exception as e:
        try:
            mydb = getConnection()
            mycursor = mydb.cursor()
            sql = "SELECT COUNT(user) FROM mysql.user WHERE user=%s;"
            mycursor.execute(sql, (user,))
            result = mycursor.fetchall()
            mydb.close()
            return 'userExists' if result[0][0] == 1 else False
        except Exception as e:
            return False
        
def setDbTables(db):
    with open(getResPath('setup.sql'), 'r') as sql:
        sql = sql.read()
        myDb = getConnection(db)
        if not myDb: return False
        mycursor = myDb.cursor()
        try:
            for statement in sql.strip().split(';'):
                if statement:
                    mycursor.execute(statement)
            return True
        except Exception as e:
            print('Exception at setDbTables: ', e)
        myDb.close()
    return False        
def checkMYSQLAdmin(user,password):
    try:
        mydb = pymysql.connect(
            host="localhost",
            user=user,
            password=password
        )
        dbCursor=mydb.cursor()
        randomString=getRandomString(False,10)
        dbCursor.execute(f"CREATE DATABASE {randomString};")
        dbCursor.execute(f"DROP DATABASE {randomString};")
        mydb.close()
        adminData["username"]=user
        adminData["password"]=password
        return True
    except Exception as e:
        return False
    
def getMYSQLVersion(user,password):
    try:
        mydb = pymysql.connect(
            host="localhost",
            user=user,
            password=password
        )
        mycursor = mydb.cursor()
        sql = "SELECT VERSION()"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        mydb.close()
        return result[0][0]
    except:
        return False
def installMySQL():
    installerUrl='https://cdn.mysql.com//Downloads/MySQLInstaller/mysql-installer-web-community-8.0.42.0.msi'
    print('Downloading installer...')
    downloadResource(installerUrl,'mysql-installer-web-community-8.0.42.0.msi')
    print('Press Enter when MySQL is installed')
    os.system(getResPath('mysql-installer-web-community-8.0.42.0.msi'))

def checkMySQLVersion(user,password):
    version=getMYSQLVersion(user,password)
    exit=False
    exitCondition=version >='8.0.0' and version <='9.0.0'
    while not exit:
            if exitCondition:
                printGreen('MySQL version: '+version)
                return version
            else:
                printRed('MySQL version must be 8.X.X')
                printRed(f'Current version: {version}')
                print('[Enter] -> Download new MySQL version')
                print('[s] -> Skip database installation')
                if input().strip().lower()=='s':
                    return False
                else:
                    installMySQL()
                    input()
                    version=getMYSQLVersion()
                    if exitCondition: exit=True



def getConnection(db=None):
    try:
        config = {
            'host': "localhost",
            'user': adminData["username"],
            'password': adminData["password"]
        }
        if db:
            config['database'] = db
        return pymysql.connect(**config)
    except:
        print('Could not connect to MySQL')
        return False
    
def getServiceInfo(service_name):
        result = subprocess.run(["sc", "qc", service_name], capture_output=True, text=True,
            creationflags=CREATE_NO_WINDOW)
        return result.stdout

def setServiceStartup():
    try:
        subprocess.run(
             ["powershell", "-Command", "Set-Service -Name 'MySQL80' -StartupType Automatic"],
            check=True,
            creationflags=CREATE_NO_WINDOW
        )
        return True
    except Exception as e:
        return False
    

def getShell():
    if shutil.which('wt'): return shutil.which('wt')
    if shutil.which('powershell'): return shutil.which('powershell')
    if shutil.which('cmd'): return shutil.which('cmd')

def supports_ansi():
    return sys.stdout.isatty() and ('WT_SESSION' in os.environ or 'TERM' in os.environ)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def isExe():
    try:
        base_path = sys._MEIPASS
        return True
    except Exception:
        return False
    
def getResPath(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    path=os.path.join(base_path, relative_path)
    return os.path.abspath(path)

def downloadResource(url, dest):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code != 200:
            printRed(f"Error downloading: status {response.status_code}")
            print('Press enter to exit')
            sys.exit(1)
            return False
        with open(getResPath(dest), 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        printRed("Could not download (no internet or server error).")
        print('Press enter to exit')
        input()
        sys.exit(1)
        return False

def grantPrivileges(user,db,password):
    myDb = getConnection(db)
    if not myDb: return False
    mycursor = myDb.cursor()
    try:
        mycursor.execute(f"GRANT ALL PRIVILEGES ON {db}.* TO {user}@'localhost';")
        dbEnvData['username']=user
        dbEnvData['db']=db
        dbEnvData['password']=password
        return True
    except Exception as e:
        print('Exception at grantPrivileges: ', e)
    myDb.close()
    return False

def createEnv(path,username,password,dbName):
    dict={
        "PASSPHRASE":"",
        "CRT":"",
        "SSL_KEY":"",
        "JWT_KEY":getRandomString(),
        #"MODE":"production", ??
        "ORIGINS":"["+'"*"'+"]",
        "DB_HOST":'127.0.0.1',
        "DB_USER":username,
        "DB_USER_PASSWORD":password,
        "DB":dbName,
        "STATIC":'storage',
        "NODE_ENV":"production",
    }
    text=''
    for elem in dict:
        value='""' if len(dict[elem])==0 else str(dict[elem])
        text=text+elem+'='+value+"\n"
    #print(text)
    try:
        with open(os.path.abspath(path+"/.env"),"w") as file: 
            file.write(text)
    except Exception as e:
      printRed('Could not write .env file: ',e)
    

def createShortcut(source):
    desktop = pathlib.Path.home() / 'Desktop'
    try:
        os.remove(desktop/ 'Tizona Manager')
    except:
        None
    source=abspath(source+'/TizonaManager.exe')
    try:
        os.symlink(source,desktop / 'Tizona Manager')
    except Exception as e:
        print('Unable to create shortcut')

def createHomeLink(source):
    menuFolder=r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    shell = Dispatch('WScript.Shell')
    source=abspath(source+'/TizonaManager.exe')
    access = shell.CreateShortcut(menuFolder+r"\Tizona Manager.lnk")
    access.TargetPath = source
    access.WorkingDirectory = os.path.dirname(source)
    access.Save()

def printRed(msg): print(f'\033[91m{msg}\033[0m') if supports_ansi() else print(msg)
def printGreen(msg): print(f'\033[92m{msg}\033[0m') if supports_ansi() else print(msg)
def printYellow(msg): print(f'\033[33m{msg}\033[0m') if supports_ansi() else print(msg)
def printYellowLight(msg): print(f'\033[93m{msg}\033[0m') if supports_ansi() else print(msg)
def printGray(msg): print(f'\033[90m{msg}\033[0m') if supports_ansi() else print(msg)

def getPythonVersion():
    try:
        result = subprocess.run(
            ['python', "--version"],
            capture_output=True,
            text=True,
            check=True,
            creationflags=CREATE_NO_WINDOW
        )
        return result.stdout.strip()
    except Exception as e:
        return False
    
def installPython():
    installerUrl='https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe'
    print('Downloading installer...')
    downloadResource(installerUrl,'python-3.13.3-amd64.exe')
    print('Press Enter when Python is installed')
    os.system(getResPath('python-3.13.3-amd64.exe'))

def checkPythonVersion():
    exit=False
    while not exit:
        pythonVersion=getVersionNumber(getPythonVersion())    
        if not pythonVersion:
            printYellow('Python installation was not detected')
            print('[Enter] -> Download and install Python 3.13')
            print('[s] -> Skip')
            if input().strip().lower()=='s':
                printYellow('Remember to install Python 3.13')
                return False
            installPython()
            return False
        elif pythonVersion >= '3.10.0' and pythonVersion <= '4.0.0':
            printGreen(f'Python version: {pythonVersion}')
            return pythonVersion
        else:
            printRed(f'Python version: {pythonVersion}')
            if pythonVersion < '3.10.0':
                printRed(f'Python version must be 3.10.0 or higher ')
            elif pythonVersion > '4.0.0':
                printRed('Python version must be less than 4.0.0')
            print('Download and install Python version 3.13.3 ?')
            print('[Enter] -> yes')
            print('[n] -> no')
            if input().strip().lower()=='n':
                return False
            else:
                installPython()
                return False
