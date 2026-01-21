import platform
from staticFuncs import *
import traceback
import os
import sys
from getpass import getpass
import zipfile
import shutil
from time import sleep
from config import *
from requirements import *
import tempfile
from pathlib import Path

useFullNodePath=False
fullNodePath='C:/Program Files/nodejs/node.exe'
isUpdating=True if '--update' in sys.argv else False
if not platform.system() == "Windows":
    print("This installer only works on Windows")
    exit(1)
def main():
    global useFullNodePath
    global isUpdating
    data=getProgramData()
    envFileContent=None
    updateEnv=False
    def prepareDb(dbCreated,dbName,newUsername,newPassword,userCreated):
        exitFN=False
        while not exitFN: #Asks MySQL admin user
            print('TizonaServer needs a user and a password to connect to the database')
            print('Create a new user?')
            print('[y] --> yes')
            print('[n] --> no')
            exitFN=False
            if input().strip().lower()=='y':#User creation
                newUsername,newPassword,userCreated = userCreation(newUsername,newPassword,userCreated)
            else: 
                printYellow('\nYou refused to create a new user. When you are asked to set the database username and password ' \
                'in TizonaServer\'s .env file, make sure that this user has privileges on the database')
                
            #DB creation and set user privileges
            exitFN=False
            while not dbCreated and not exitFN:
                dbInput=input('Type database name (at least three characters): ')
                if len(dbInput)>2: dbName=dbInput
                dbCreated=createDB(dbName)
                if not dbCreated: 
                    printRed(f"Could not create database with name {dbName}")
                    print('[s] --> skip database creation')
                    print('Press Enter to try again')
                    if input().strip().lower()=='s': exitFN=True
                else:
                    setDbTables(dbName)
                    grantPrivileges(newUsername,dbName,newPassword)
                    exitFN=True
        return (dbCreated,dbName,newUsername,newPassword,userCreated)

    def moveFiles():
        global isUpdating
        data=getProgramData()
        if not data: isUpdating=False
        else:
            installationPath=data['installationPath']
            oldEnvFile=os.path.join(installationPath,'../Tizonaserver_old/.env')
            oldPluginsDir=os.path.join(installationPath,'../TizonaServer_old/plugins')
            env={}
            with open(oldEnvFile, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, value = line.split("=", 1)
                    env[key] = value.strip().strip('"')
            oldStatic=os.path.join(installationPath,'../TizonaServer_old/'+env['STATIC']).replace("'","")
            static=os.path.join(installationPath,'TizonaServer/'+env['STATIC']).replace("'","")
            envFile=os.path.join(installationPath,'Tizonaserver/.env')
            pluginsDir=os.path.join(installationPath,'TizonaServer/plugins')
            shutil.rmtree(static)
            shutil.move(oldEnvFile,envFile)
            if os.path.isdir(oldPluginsDir): shutil.move(oldPluginsDir,pluginsDir)
            shutil.move(oldStatic,static)
            shutil.rmtree(oldServerDir)
            temp_path = Path(tempfile.gettempdir())
            dest = temp_path / "installerLatest.exe"

            subprocess.Popen(
                ["cmd.exe", "/c", "del", "/f", "/q", str(dest)],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            


    def userCreation(newUsername,newPassword,userCreated):
        confirmPassword='a'
        while True:
            print('Type username')
            newUsername=input()
            newPassword=getpass('Type password: ')
            confirmPassword=getpass('Confirm password: ')
            if newPassword != confirmPassword: #Passwords don't match
                printRed("Passwords do not match")
            elif len(newUsername)>=2: #Username too short
               result=createUser(newUsername,newPassword) 
               if result!='userExists': 
                   userCreated=True
                   break #User was created
               else: printRed("This user already exists") #User already exists
            else: printRed("Username is not long enough") #Username too short
             #Something went wrong
            print('[s] --> skip user setup')
            print('Press Enter to try again')
            if input().strip().lower()=='s': return ('','',False)
            else: continue
        return (newUsername,newPassword,userCreated)
    
    #MAIN EXECUTION
    while True:
        printYellowLight("Note: This installation requires downloading additional resources from the Internet (e.g., Node.js, MySQL, Python).")
        printGray("Type LICENSE to view the license and third-party notices")
        print("Press enter to start installing") if not isUpdating else print("Press enter to start update")
        if input().lower()=='license':
            os.startfile(getResPath('LICENSE'))
            sleep(0.25)
            os.startfile(getResPath('LICENSES'))
        else: break
    print('Starting installation') if not isUpdating else print('Starting update') 
    #NODE CHECK
    inputVal=''
    restart=False
    while inputVal != 'n':
        path=False
        nodeVer=checkNode(False,path)
        if not nodeVer or restart:
            path=False
            if not restart: 
                printYellow('Node.js was not detected')
                printYellow('Do you want to install it?')
            else:
                printYellow('Do you want to install a new version?')
            print(f'[y] --> Download Node.js {nodeInstallingVersion} and install')
            print('[c] --> Check Node.js installation again')
            print('[n] --> Skip')

            restart=False
            inputVal=input().lower().strip()
            if restart and inputVal=='c': inputVal='n'
            if inputVal=='y':
                installMethod2=True
                nvmExists=os.system('nvm --version')
                if nvmExists==0:
                    printYellow('NVM was detected, Do you want to install Node.js using it?')
                    print(f'[y] --> Download Node.js {nodeInstallingVersion} and install with NVM')
                    print('[n] --> Download Node.js installer')
                    if input().lower().strip()=='y': installMethod2=False
                if installMethod2:
                    if not os.path.exists(getResPath(nodeRelPath)):
                        downloadResource(nodeDownloadUrl, nodeRelPath)
                    os.system(getResPath(nodeRelPath))
                    if nvmExists==0: os.system('nvm off')
                    #if(os.path.isfile(fullNodePath)):
                    #    useFullNodePath=True
                    else:
                        printGreen(
                        'Node.js has been installed. '
                        )
                        printYellow('Please restart the TizonaHub installer to make Node.js available.\n'
                        'If you started the TizonaHub installer using the command prompt, please open a new one.')
                        input('Press Enter to close installer. Remember to restart it')
                        return
                if not installMethod2:
                    os.system(f'nvm install {nvmNodeVer}')
                    os.system('nvm on')
                    os.system(f'nvm use {nvmNodeVer}')
                inputVal='c'

            if inputVal=='c':
                nodeVer=checkNode(False,False,True)
                if not nodeVer:nodeVer=checkNode(True)
                if not nodeVer:
                    printYellow('Could not find Node.js installation. Type your installation path or just press Enter')
                    path=input()
                else:
                    inputVal='n' 
                    if nodeVer>=nodeMinVer and nodeVer<nodeMaxVer: printGreen('Node.js was detected: '+nodeVer)
                    else: 
                        inputVal='c'
                        restart=True
                        printRed(f"mNode version should be greater than {nodeMinVer} and less than {nodeMaxVer}")
        else:
            inputVal='n' 
            if nodeVer>=nodeMinVer and nodeVer<nodeMaxVer: printGreen('Node.js was detected: '+nodeVer)
            else: 
                inputVal='c'
                restart=True
                printYellow(f"Node version should be greater than {nodeMinVer} and less than {nodeMaxVer}")

    if not nodeVer:
        printRed('Node.js must be installed to complete TizonaHub installation, but it was not detected')
        printRed('Please install it.')
        exit(1)
    #PYTHON CHECK
    checkPythonVersion()
    #MYSQL CHECK
    mysql=setServiceStartup()
    dbCreated=False
    exitFN=False
    username=''
    password=''
    adminLogged=False
    userCreated=False
    newUsername=''
    newPassword=False
    dbName='tizonaserver'
    if not mysql:
        printYellow('MySQL service was not detected')
        printYellow('MySQL is a database program used to enable features like user accounts and access control')
        printYellow("\nIf you want to enable user management later, you can install MySQL and run this installer again")
        print('Do you want to install MySQL?')
        print('[y] --> yes')
        print('[n] --> no')
        if input().strip().lower()=='y':
            installMySQL()
            input('Press enter when MySQL is installed')
            mysql=setServiceStartup()
    if mysql: 
        printGreen('MySQL service was detected ')
        if not isUpdating:    
            print('Do you want to skip MySQL version check?')
            print('[n] --> no')
            print('[Enter] --> yes')
            if input().strip().lower()=='': exitFN=True
            while not adminLogged and not exitFN: #Asks MySQL admin user
                print('Type MySQL admin username')
                username=input()
                password=getpass('Type password')
                adminLogged=checkMYSQLAdmin(username,password)
                if not adminLogged:  #Admin not verified
                    printRed('Could not check admin user')
                    print('Do you want to skip MySQL version check?')
                    print('[y] --> yes')
                    print('[n] --> no')
                    if input().strip().lower()=='y':
                        exitFN=True
            if adminLogged:
                checkMySQLVersion(username,password)
                printGreen('Admin user verified successfully')
                if not isUpdating:
                    print('Do you want to create and prepare a new database?')
                    print('[y] --> yes')
                    print('[n] --> no')
                    inputVal=input()
                    dbCreated=False
                    userCreated=False
                    if inputVal.lower().strip()=='y': #Install & prepare db
                        dbCreated,dbName,newUsername,newPassword,userCreated = prepareDb(dbCreated,dbName,newUsername,newPassword,userCreated)

            if not dbCreated:
                print()
                printYellow('You refused to create a new database')
    print()
    installationPath=r'C:\Program Files (x86)'
    #if not isUpdating:        
    exitFN=False
    if isUpdating:
        #moveFiles()   
        installationPath=data['installationPath']
        serverDir=os.path.join(installationPath,'TizonaServer')
        oldServerDir=os.path.join(installationPath,'../TizonaServer_old')
        envFileContent=os.path.join(installationPath,'Tizonaserver/.env')
        if os.path.isdir(oldServerDir):shutil.rmtree(oldServerDir)
        if os.path.isdir(serverDir):shutil.move(serverDir,oldServerDir)
    if not isUpdating:    
        print('Select installation folder')
        while not exitFN:
            print(r'Default: C:\Program Files (x86)\TizonaHub')
            print('[Enter] --> use default installation path')
            print('Or enter a custom path')
            inputVal=input()
            if len(inputVal.strip())==0: inputVal=installationPath
            if os.path.isdir(inputVal): 
                if os.path.isdir(os.path.abspath(inputVal+'/TizonaHub')):
                    exitFN=False
                    printYellow('TizonaHub folder already exists on this path.')
                    print('[u] --> just update .env file data')
                    print('[n] --> select path again')
                    print('[Enter] --> delete folder and install TizonaHub')
                    val=input()
                    if val.lower().strip()=='u':
                        updateEnv=True
                        exitFN=True
                    elif val.lower().strip=='n':
                        exitFN=False
                    elif len(val)==0:
                        updateEnv=False
                        exitFN=True
                else:
                    installationPath=inputVal
                    exitFN=True
            else: printRed('Could not resolve path, select another one')
        print()   
        #print('>> CREATING .env FILE <<')
        print('Summary: ')
        print(f'  *Database name: {dbName if dbCreated else 'Missing'}')
        print(f'  *Username: {newUsername if userCreated else 'Missing'}')
        print(rf'  *Installation path: {installationPath}\TizonaHub')
        print()
        if not dbCreated: dbName=input('Type database name:  ')
        if not newUsername: newUsername=input('Type database username:  ')
        if not newPassword: newPassword=getpass('Type database password: ')
        target = os.path.abspath(installationPath+r'\TizonaHub\TizonaServer')  
        targetRoot=os.path.abspath(installationPath+r'\TizonaHub')  
        createShortcut(targetRoot)
        createHomeLink(targetRoot)
    if updateEnv:
        createEnv(target,newUsername,newPassword,dbName)
        printGreen('.env file updated')
        print('Press Enter to exit')
    else:
        if isUpdating and envFileContent: 
            targetRoot=data['installationPath']
            target=os.path.join(targetRoot,'TizonaServer')
        elif isUpdating and not envFileContent: 
            installationPath=data['installationPath']
            serverDir=os.path.join(installationPath,'TizonaServer')
            oldServerDir=os.path.join(installationPath,'TizonaServer_old')
            envFileContent=os.path.join(installationPath,'Tizonaserver/.env')
            if os.path.isdir(serverDir):shutil.rmtree(serverDir)
            if os.path.isdir(oldServerDir):shutil.move(oldServerDir,serverDir)
            printRed(".env file was not found, aborting update")
            raise Exception(".env file was not found, aborting update")
        try:
            if os.path.isdir(targetRoot):shutil.rmtree(targetRoot)
        except Exception as e:
            if not isExe():
              print(e)
            printRed('Unable to remove the TizonaHub folder. Please make sure that no TizonaHub process is running and try again.' \
            'If the problem persists, restart your computer or manually delete:') 
            input('Press Enter to exit...')
            exit(1)
        try:
            with zipfile.ZipFile(getResPath(bundleName), 'r') as zip_ref:
                zip_ref.extractall(targetRoot)
                print('bundle zip extracted')
            if not isUpdating:    
                createEnv(target,newUsername,newPassword,dbName)
                print('.env created')
            print('Installing server dependencies...')
            npm_cmd = "C:/Program Files/nodejs/npm.cmd"
            npmCommand='npm.cmd' if not useFullNodePath else npm_cmd
            subprocess.run([npmCommand,'i','-g','pm2'],cwd=target,timeout=400)
            subprocess.run([npmCommand,'i','--omit=dev'],cwd=target,timeout=400)
            shutil.copy(getResPath('TizonaManager.exe'),getResPath(os.path.abspath(targetRoot+r'\TizonaManager.exe')))
            setProgramData(targetRoot)
            if isUpdating: moveFiles()
            ##DEALING WITH LICENSES
            try:
                #if os.path.isfile(targetRoot+r'\README.txt'): os.remove(targetRoot+r'\README.txt')
                if os.path.isfile(targetRoot+r'\LICENSES\ATTRIBUTIONS-TIZONACLIENT.txt'):
                    shutil.move(targetRoot+r'\LICENSES\ATTRIBUTIONS-TIZONACLIENT.txt',targetRoot+r'\LICENSES\LICENSES-TIZONACLIENT\ATTRIBUTIONS-TIZONACLIENT.txt')
                if os.path.isfile(targetRoot+r'\LICENSES\LICENSE-SUMMARY-TIZONACLIENT.txt'):
                    shutil.move(targetRoot+r'\LICENSES\LICENSE-SUMMARY-TIZONACLIENT.txt',targetRoot+r'\LICENSES\LICENSES-TIZONACLIENT\LICENSE-SUMMARY-TIZONACLIENT.txt')
                if os.path.isdir(targetRoot+'/LICENSES/LICENSES-TIZONAMANAGER'):shutil.rmtree(targetRoot+'/LICENSES/LICENSES-TIZONAMANAGER')
                shutil.copytree(getResPath('LICENSES/TizonaManager'),targetRoot+'/LICENSES/LICENSES-TIZONAMANAGER')
                #subprocess.run("npx license-checker --json > third-party-licenses.json", shell=True, cwd=targetRoot+'/TizonaServer')
                if os.path.isfile(targetRoot+'/TizonaServer/third-party-licenses.json'): 
                    os.rename(targetRoot+'/TizonaServer/third-party-licenses.json',targetRoot+'/LICENSES/LICENSES-TIZONASERVER/third-party-licenses.json')

            except Exception as e:
              if not isExe():printRed(f'An exception occurred at DEALING WITH LICENSES: {e}')
            ##
            printGreen('TizonaHub installed successfully')
            input('press enter to exit...')

            
        except subprocess.TimeoutExpired as e:
            printRed('The process took too long and was terminated.')
            printRed(f'Command: {" ".join(e.cmd)}')
            printRed('Could not install TizonaHub')
            printRed('Press Ctrl + C to exitFN...')
            return
        except Exception as e:
            restoreUpdate()
            printRed(e)
            printRed('Could not install TizonaHub')
            printRed('press enter to exit...')
            input()
            return


def initApp():
    try:
        if is_admin():
            main()
        else:
            #Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", getShell(), " ".join(sys.argv), None, True) #sys.executable

    except:
        if debug :traceback.print_exc()
        try:            
            input("\npress enter to exit...")
        except:
            None


initApp()