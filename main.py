import platform
from staticFuncs import *
import traceback
import os
import sys
from getpass import getpass
import zipfile
import shutil
nodeDownloadUrl='https://nodejs.org/dist/v22.15.1/node-v22.15.1-x64.msi'
if not platform.system() == "Windows":
    print("You are not using Windows")
    exit(1)
def main():
    updateEnv=False
    def prepareDb(dbCreated,dbName,newUsername,newPassword,userCreated):
        exit=False
        while not exit: #Asks MySQL admin user
            print('TizonaServer needs a user and a password to connect to the database')
            print('Create a new user?')
            print('[y] --> yes')
            print('[n] --> no')
            exit=False
            if input().strip().lower()=='y':#User creation
                newUsername,newPassword,userCreated = userCreation(newUsername,newPassword,userCreated)
            else: 
                print('\033[33mYou refused to create a new user. When you are asked to set the database username and password ' \
                'in TizonaServer\'s .env file, make sure that this user has privileges on the database.\033[0m')
                print
            #DB creation and set user privileges
            exit=False
            while not dbCreated and not exit:
                dbInput=input('Type database name (at least three characters): ')
                if len(dbInput)>2: dbName=dbInput
                dbCreated=createDB(dbName)
                if not dbCreated: 
                    print(f"\033[91mCould not create database with name {dbName}\033[0m")
                    print('[s] --> skip database creation')
                    print('Press Enter to try again')
                    if input().strip().lower()=='s': exit=True
                else:
                    setDbTables(dbName)
                    grantPrivileges(newUsername,dbName,newPassword)
                    exit=True
        return (dbCreated,dbName,newUsername,newPassword,userCreated)

    def userCreation(newUsername,newPassword,userCreated):
        confirmPassword='a'
        while True:
            print('Type username')
            newUsername=input()
            newPassword=getpass('Type password: ')
            confirmPassword=getpass('Confirm password: ')
            if newPassword != confirmPassword: #Passwords don't match
                print("\033[91mPasswords do not match\033[0m")
            elif len(newUsername)>=2: #Username too short
               result=createUser(newUsername,newPassword) 
               if result!='userExists': 
                   userCreated=True
                   break #User was created
               else: print("\033[91mThis user already exists\033[0m") #User already exists
            else: print("\033[91mUsername is not long enough\033[0m") #Username too short
             #Something went wrong
            print('[s] --> skip user setup')
            print('Press Enter to try again')
            if input().strip().lower()=='s': return ('','',False)
            else: continue
        return (newUsername,newPassword,userCreated)
    
    #PYTHON CHECK
    checkPythonVersion()
    #NODE CHECK
    inputVal=''
    restart=False
    while inputVal != 'n':
        path=False
        nodeVer=checkNode(False,path)
        if not nodeVer or restart:
            path=False
            if not restart: 
                print('\033[33mNode.js was not detected\033[0m')
                print('\033[33mDo you want to install it?\033[0m')
            else:
                print('\033[33mDo you want to install a new version?\033[0m')
            print('[y] --> Download Node.js 22.15.1 and install')
            print('[c] --> Check Node.js installation again')
            print('[n] --> Skip')

            restart=False
            inputVal=input().lower().strip()
            if restart and inputVal=='c': inputVal='n'
            if inputVal=='y':
                installMethod2=True
                nvmExists=os.system('nvm --version')
                if nvmExists==0:
                    print('\033[33mNVM was detected, Do you want to install Node.js using it?\033[0m')
                    print('[y] --> Download Node.js 22.15.1 and install with NVM')
                    print('[n] --> Download Node.js installer')
                    if input().lower().strip()=='y': installMethod2=False
                if installMethod2:
                    if not os.path.exists(getResPath('node-v22.15.1-x64.msi')):
                        downloadResource(nodeDownloadUrl, 'node-v22.15.1-x64.msi')
                    os.system(getResPath('node-v22.15.1-x64.msi'))
                    if nvmExists==0: os.system('nvm off')
                    printGreen(
                        'Node.js has been installed. Please restart the TizonaHub installer to make Node.js available.\n'
                        'If you started the TizonaHub installer using the command prompt, please open a new one.'
                    )
                    input('Press Enter to close installer. Remember to restart it')
                    return
                if not installMethod2:
                    os.system('nvm install 22')
                    os.system('nvm on')
                    os.system('nvm use 22')
                inputVal='c'

            if inputVal=='c':
                nodeVer=checkNode(False,False,True)
                if not nodeVer:nodeVer=checkNode(True)
                if not nodeVer:
                    print('\033[33mCould not find Node.js installation. Type your installation path or just press Enter\033[0m')
                    path=input()
                else:
                    inputVal='n' 
                    if nodeVer>='20.17.1' and nodeVer<'23.0.0': print('\033[92mNode.js was detected:\033[0m '+nodeVer)
                    else: 
                        inputVal='c'
                        restart=True
                        print("\033[91mNode version should be greater than 20.17.1 and less than 23.0.0\033[0m")
        else:
            inputVal='n' 
            if nodeVer>='20.17.1' and nodeVer<'23.0.0': print('\033[92mNode.js was detected:\033[0m '+nodeVer)
            else: 
                inputVal='c'
                restart=True
                print("\033[91mNode version should be greater than 20.17.1 and less than 23.0.0\033[0m")

    #MYSQL CHECK
    mysql=setServiceStartup()
    if not mysql:
        print('\033[91mMySQL service was not detected\033[0m')
        printYellow('MySQL is a database program used to enable features like user accounts and access control')
        printYellow("\nIf you want to enable user management later, you can install MySQL and run this installer again")
        print('Do you want to install MySQL?')
        print('[y] --> yes')
        print('[n] --> no')
        if input().strip().lower()=='y':
            installMySQL()
            input()
            mysql=setServiceStartup()
    if mysql: 
        print('\033[92mMySQL service was detected\033[0m ')
        exit=False
        username=''
        password=''
        adminLogged=False
        dbCreated=False
        userCreated=False
        newUsername=''
        newPassword=False
        dbName='tizonaserver'
        print('Do you want to skip MySQL version check?')
        print('[y] --> yes')
        print('[Enter] --> no')
        if input().strip().lower()=='y': exit=True
        
        
        while not adminLogged and not exit: #Asks MySQL admin user
            print('Type MySQL admin username')
            username=input()
            password=getpass('Type password')
            adminLogged=checkMYSQLAdmin(username,password)
            if not adminLogged:  #Admin not verified
                print('\033[91mCould not check admin user\033[0m')
                print('Do you want to skip MySQL version check?')
                print('[y] --> yes')
                print('[n] --> no')
                if input().strip().lower()=='y':
                    exit=True
        if adminLogged:
            checkMySQLVersion(username,password)
            print('\033[92mAdmin user verified successfully\033[0m ')
            print('Do you want to create and prepare a new database?')
            print('[y] --> yes')
            print('[n] --> no')
            inputVal=input()
            dbCreated=False
            userCreated=False
            if inputVal.lower().strip()=='y': #Install & prepare db
                dbCreated,dbName,newUsername,newPassword,userCreated = prepareDb(dbCreated,dbName,newUsername,newPassword,userCreated)
                
        if not dbCreated:
            print('\033[33mYou refused to create a new database\033[0m')
        print()
        exit=False
        print('Select installation folder')
        while not exit:
            installationPath=r'C:\Program Files (x86)'
            print(r'Default: C:\Program Files (x86)\TizonaHub')
            print('[Enter] --> use default installation path')
            print('Or enter a custom path')
            inputVal=input()
            if len(inputVal.strip())==0: inputVal=installationPath
            if os.path.isdir(inputVal): 
                if os.path.isdir(os.path.abspath(inputVal+'/TizonaHub')):
                    exit=False
                    printYellow('\033[91mTizonaHub folder already exists on this path. If you continue, the installer will only update .env file data\033[0m')
                    print('[Enter] --> Continue')
                    print('[n] --> select path again')
                    if len(input())==0:
                        updateEnv=True
                        exit=True
                else:
                    installationPath=inputVal
                    exit=True
            else: print('\033[91mCould not resolve path, select another one \033[0m')
        print()   
        #print('>> CREATING .env FILE <<')
        print('Summary: ')
        print(f'  *Database name: {dbName if dbCreated else 'Missing'}')
        print(f'  *Username: {newUsername if userCreated else 'Missing'}')
        print(rf'  *Installation path: {installationPath}\TizonaHub')

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

        else:
            try:
                with zipfile.ZipFile(getResPath('TizonaHub_s0.3.0c0.3.0.zip'), 'r') as zip_ref:
                    zip_ref.extractall(target)
                    print('zip extracted')
                createEnv(target,newUsername,newPassword,dbName)
                print('.env created')
                print('Installing server dependencies...')
                subprocess.run(['npm.cmd','i','-g','pm2'],cwd=target,timeout=400)
                subprocess.run(['npm.cmd','i'],cwd=target,timeout=400)
                shutil.copy(getResPath('TizonaManager.exe'),getResPath(os.path.abspath(targetRoot+r'\TizonaManager.exe')))
                printGreen('TizonaHub installed successfully')
                input('Press Enter to exit...')
            except subprocess.TimeoutExpired as e:
                printRed('The process took too long and was terminated.')
                printRed(f'Command: {" ".join(e.cmd)}')
                printRed('Could not install TizonaHub')
                printRed('Press Ctrl + C to exit...')
                return
            except Exception as e:
                print(e)
                printRed('Could not install TizonaHub')
                printRed('Press Enter to exit...')
                input()
                return


def initApp():
    try:
        if is_admin():
            main()
        else:
            #Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", 'wt.exe', " ".join(sys.argv), None, True) #sys.executable

    except:
        #traceback.print_exc()
        input("\nPress enter to exit...")


initApp()