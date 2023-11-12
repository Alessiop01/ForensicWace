import webbrowser
import forensicWace.ExtractInformation as ExtractInformation    # Comment this to develop on local. Add to create package to download and install pip
#import ExtractInformation    # Uncomment this to develop on local. Add to create package to download and install pip
import os
import sys

import forensicWace.GenerateReport as GenerateReport    # Comment this to develop on local. Add to create package to download and install pip
#import GenerateReport    # Uncomment this to develop on local. Add to create package to download and install pip
import forensicWace.Service as Service    # Comment this to develop on local. Add to create package to download and install pip
#import Service    # Uncomment this to develop on local. Add to create package to download and install pip
import flask
import tkinter as tk
import forensicWace.GlobalConstant as GlobalConstant    # Comment this to develop on local. Add to create package to download and install pip
#import GlobalConstant    # Uncomment this to develop on local. Add to create package to download and install pip

from flask import Flask, render_template, redirect, url_for, request
from tkinter import filedialog

app = Flask(__name__ , static_folder='assets')

InputPath = ""
OutputPath = ""
fileName = GlobalConstant.noDatabaseSelected
fileSize = GlobalConstant.noDatabaseSelected
dbSha256 = GlobalConstant.noDatabaseSelected
dbMd5 = GlobalConstant.noDatabaseSelected
noDbError = 1
noOutPathError = 1
extractionDone = 1

extractedDataList = None

ReportPath = GlobalConstant.noReportSelected
CertificatePath = GlobalConstant.noCertificateSelected
reportStatus = 0

backupPath = GlobalConstant.backupDefaultPath

phoneNumber = ""

@app.route('/')
def Home():
    global InputPath, OutputPath, fileName, fileSize, dbSha256, dbMd5, noDbError, ReportPath, CertificatePath, reportStatus
    ReportPath = GlobalConstant.noReportSelected
    CertificatePath = GlobalConstant.noCertificateSelected
    reportStatus = 0
    return render_template('index.html', inputPath=InputPath, outputPath=OutputPath, fileName=fileName, fileSize=fileSize, dbSha256=dbSha256, dbMd5=dbMd5, noDbError=noDbError, noOutPathError=noOutPathError)

@app.route('/inputPath')
def InputPath():

    rootIn = tk.Tk()
    # Create a hidden root window
    rootIn.attributes('-alpha', 0.0)  # Make it transparent
    rootIn.attributes('-topmost', 1)  # Put it on top of other windows

    global InputPath, OutputPath, fileName, fileSize, dbSha256, dbMd5, noDbError, noOutPathError

    InputPath = filedialog.askopenfilename(title=GlobalConstant.selectWaDatabase, filetypes=(("Database", "*.sqlite"), ("All files", "*.*")))
    if InputPath == "":
        InputPath = GlobalConstant.noDatabaseSelected
    else:
        OutputPath = InputPath.rsplit('/', 1)[0] + '/'
        fileName = InputPath[InputPath.rfind('/') + 1:]
        fileSize = str(round(Service.GetFileSize(InputPath), 1)) + " MB"
        dbSha256 = Service.CalculateSHA256(InputPath)
        dbMd5 = Service.CalculateMD5(InputPath)
        noDbError = 0
        noOutPathError = 0

    rootIn.destroy()

    return redirect(url_for('Home'))

@app.route('/outputPath')
def OutputPath():

    rootOut = tk.Tk()
    # Create a hidden root window
    rootOut.attributes('-alpha', 0.0)  # Make it transparent
    rootOut.attributes('-topmost', 1)  # Put it on top of other windows

    global InputPath, OutputPath, noOutPathError
    OutputPath = filedialog.askdirectory(title=GlobalConstant.selectOutputPath)

    if OutputPath == "":
        OutputPath = InputPath.rsplit('/', 1)[0] + '/'
    else:
        OutputPath = OutputPath + '/'

    noOutPathError = 0

    rootOut.destroy()

    return redirect(url_for('Home'))

@app.route('/blockedContact')
def BlockedContact():
    global noDbError, InputPath, extractedDataList

    if noDbError != 1:
        extractedDataList = ExtractInformation.GetBlockedContacts(InputPath)
        return render_template('blockedContact.html', blockedContactsData=extractedDataList, formatPhoneNumber=Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/blockedContactReport')
def BlockedContactReport():
    global noDbError, OutputPath, fileName, extractedDataList

    if noDbError != 1:
        GenerateReport.BlockedContactReport(OutputPath, fileName, extractedDataList)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/groupList')
def GroupList():
    global noDbError, InputPath, extractedDataList

    if noDbError != 1:
        extractedDataList = ExtractInformation.GetGroupList(InputPath)
        return render_template('groupList.html', chatListData = extractedDataList)
    else:
        return redirect(url_for('Home'))

@app.route('/selectGroup')
def SelectGroup():
    global noDbError, InputPath, extractedDataList

    if noDbError != 1:
        extractedDataList = ExtractInformation.GetGroupList(InputPath)
        return render_template('selectGroup.html', chatListData = extractedDataList)
    else:
        return redirect(url_for('Home'))

@app.route('/groupListReport')
def GroupListReport():
    global noDbError, OutputPath, fileName, extractedDataList

    if noDbError != 1:
        global InputPath
        GenerateReport.GroupListReport(OutputPath, fileName, extractedDataList)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/chatList')
def ChatList():
    global noDbError, InputPath, extractedDataList

    if noDbError != 1:
        extractedDataList = ExtractInformation.GetChatList(InputPath)
        return render_template('chatList.html', chatListData = extractedDataList, formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocation')
def GpsLocation():
    global noDbError, InputPath, extractedDataList
    if noDbError != 1:
        extractedDataList = ExtractInformation.GetGpsData(InputPath)
        return render_template('gpsLocation.html', gpsData = extractedDataList, formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocationReport')
def GpsLocationReport():
    global noDbError, OutputPath, fileName, extractedDataList

    if noDbError != 1:
        GenerateReport.GpsLocations(OutputPath, fileName, extractedDataList)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route("/insertPhoneNumber", methods=["GET", "POST"])
def InsertPhoneNumber():
    global phoneNumber

    if noDbError != 1:

        if request.method == "POST":
            if request.form["button"] == "del":
                # Delete last character inserted
                phoneNumber = phoneNumber[:-1]
            else:
                # Add selected character to the list
                phoneNumber += request.form["button"]

        return render_template("inputPhoneNumber.html", phoneNumber=phoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/privateChat/<mediaType>/<phoneNumber>')
def PrivateChat(mediaType, phoneNumber):
    global noDbError, InputPath

    if noDbError != 1:
        counters, messages = ExtractInformation.GetPrivateChat(InputPath, mediaType, phoneNumber)
        return render_template('privateChat.html', phoneNumber=Service.FormatPhoneNumber(phoneNumber), nonFormattedNumber = phoneNumber, counters = counters, messages = messages, str=str, vcardTelExtractor = Service.VcardTelExtractor, originalPhoneNumber = phoneNumber, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, GetUserProfilePicImage = Service.GetUserProfilePicImage)
    else:
        return redirect(url_for('Home'))

@app.route('/groupChat/<mediaType>/<groupName>')
def GroupChat(mediaType, groupName):
    global noDbError, InputPath

    if noDbError != 1:
        counters, groupId, messages = ExtractInformation.GetGroupChat(InputPath, mediaType, groupName)

        return render_template('groupChat.html', groupName=groupName, counters = counters, messages = messages, str=str, vcardTelExtractor = Service.VcardTelExtractor, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, FormatPhoneNumber=Service.FormatPhoneNumber, GetUserProfilePicImage = Service.GetUserProfilePicImage)
    else:
        return redirect(url_for('Home'))

@app.route('/checkReport')
def CheckReport():
    global ReportPath, CertificatePath, reportStatus, noDbError

    if (ReportPath != GlobalConstant.noReportSelected and CertificatePath != GlobalConstant.noCertificateSelected):
        reportStatus = Service.ReportCheckAuth(ReportPath, CertificatePath)

    return render_template('checkReport.html', reportPath=ReportPath, certificatePath=CertificatePath, reportStatus=reportStatus)

@app.route('/reportPath')
def ReportPath():
    global noDbError

    rootReportPath = tk.Tk()
    # Create a hidden root window
    rootReportPath.attributes('-alpha', 0.0)  # Make it transparent
    rootReportPath.attributes('-topmost', 1)  # Put it on top of other windows

    global ReportPath

    ReportPath = filedialog.askopenfilename(title=GlobalConstant.selectWaDatabase, filetypes=(("PDF", "*.pdf"), ("All files", "*.*")))

    rootReportPath.destroy()

    if ReportPath == "":
        ReportPath= GlobalConstant.noReportSelected

    return redirect(url_for('CheckReport'))

@app.route('/certificatePath')
def CertificatePath():
    global noDbError

    rootCertrPath = tk.Tk()
    # Create a hidden root window
    rootCertrPath.attributes('-alpha', 0.0)  # Make it transparent
    rootCertrPath.attributes('-topmost', 1)  # Put it on top of other windows

    global CertificatePath

    CertificatePath = filedialog.askopenfilename(title=GlobalConstant.selectWaDatabase, filetypes=(("Certificate", "*.tsr"), ("All files", "*.*")))

    rootCertrPath.destroy()

    if CertificatePath == "":
        CertificatePath= GlobalConstant.noCertificateSelected

    return redirect(url_for('CheckReport'))

@app.route('/calculateDbHash')
def CalculateDbHash():
    global noDbError

    if noDbError != 1:
        global InputPath
        GenerateReport.DbHash(InputPath, OutputPath, fileName)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/chatListReport')
def ChatListReport():
    global noDbError, OutputPath, fileName, extractedDataList

    if noDbError != 1:
        global InputPath
        GenerateReport.ChatListReport(OutputPath, fileName, extractedDataList)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/availableBackups')
def AvailableBackups():
    global noOutPathError, backupPath, noOutPathError

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    backupList = Service.GetAvailableBackups()
    return render_template('availableBackup.html', backupList=backupList, backupPath=backupPath, extractionStatus=0, outputPath=OutputPath, noOutPathError=noOutPathError)

@app.route('/extractBackup/<deviceSn>/<udid>')
def ExtractBackup(deviceSn, udid):
    global noOutPathError, backupPath, OutputPath, noOutPathError

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    if noOutPathError == 0:
        backupList = Service.GetAvailableBackups()
        ExtractInformation.ExtractFullBackup(backupPath, udid, OutputPath)
        Service.RemoveFileWithoutExtension()

    else:
        return redirect(url_for('AvailableBackups'))

    if sys.platform.startswith('win'):
        # Windows
        os.system("start " + OutputPath)
    elif sys.platform.startswith('darwin'):
        # macOS
        os.system("open " + OutputPath)
    # elif sys.platform.startswith('linux'):
        # Linux

    return render_template('availableBackup.html', backupList=backupList, backupPath=backupPath, extractionStatus=1, deviceSn=deviceSn, udid=udid, outputPath=OutputPath, noOutPathError=noOutPathError)

@app.route('/insertPassword/<deviceSn>/<udid>')
def InsertPassword(deviceSn, udid):
    global extractionDone
    extractionDone = 0
    return render_template('insertPassword.html', deviceSn=deviceSn, udid=udid)

@app.route('/extractEncryptedBackup/<deviceSn>/<udid>', methods=["POST"])
def ExtractEncryptedBackup(deviceSn, udid):
    global noOutPathError, backupPath, OutputPath, noOutPathError, extractionDone

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    if noOutPathError == 0:
        backupList = Service.GetAvailableBackups()
        if request.method == "POST" and extractionDone == 0:
            backupPsw = request.form["password"]
            ExtractInformation.ExtractEncryptedFullBackup(backupPath, udid, OutputPath, backupPsw)
            Service.RemoveFileWithoutExtension()
            extractionDone = 1
        else:
            return redirect(url_for('AvailableBackups'))

    else:
        return redirect(url_for('AvailableBackups'))

    if sys.platform.startswith('win'):
        # Windows
        os.system("start " + OutputPath)
    elif sys.platform.startswith('darwin'):
        # macOS
        os.system("open " + OutputPath)
    # elif sys.platform.startswith('linux'):
        # Linux

    return render_template('availableBackup.html', backupList=backupList, backupPath=backupPath, extractionStatus=1, deviceSn=deviceSn, udid=udid, outputPath=OutputPath, noOutPathError=noOutPathError)

@app.route('/ExtractionOutPath')
def ExtractionOutPath():

    rootOut = tk.Tk()
    # Create a hidden root window
    rootOut.attributes('-alpha', 0.0)  # Make it transparent
    rootOut.attributes('-topmost', 1)  # Put it on top of other windows

    global InputPath, OutputPath, noOutPathError
    OutputPath = filedialog.askdirectory(title=GlobalConstant.selectOutputPath)

    if OutputPath == "":
        OutputPath = InputPath.rsplit('/', 1)[0] + '/'
    else:
        OutputPath = OutputPath + '/'

    noOutPathError = 0

    rootOut.destroy()

    return redirect(url_for('AvailableBackups'))

@app.route('/generetePrivateChatReport/<phoneNumber>')
def GeneretePrivateChatReport(phoneNumber):
    global InputPath, OutputPath, fileName

    counters, messages = ExtractInformation.GetPrivateChat(InputPath, '0', phoneNumber)
    GenerateReport.PrivateChatReport(OutputPath, phoneNumber, messages)
    basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    GenerateReport.CalculateMediaSHA256(basePath + "/assets/Media/" + phoneNumber + "@s.whatsapp.net", OutputPath, phoneNumber)
    GenerateReport.CalculateMediaMD5(basePath + "/assets/Media/" + phoneNumber + "@s.whatsapp.net", OutputPath, phoneNumber)

    return redirect(url_for('PrivateChat', mediaType = 0, phoneNumber=phoneNumber))

@app.route('/genereteGroupChatReport/<groupName>')
def GenereteGroupChatReport(groupName):
    global InputPath, OutputPath, fileName

    counters, groupId, messages = ExtractInformation.GetGroupChat(InputPath, '0', groupName)
    GenerateReport.GroupChatReport(OutputPath, groupName, messages)
    basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    groupNameNoSpaces = groupName.replace(" ", "")
    groupId = groupId[0]['ZCONTACTJID']
    GenerateReport.CalculateMediaSHA256(basePath + "/assets/Media/" + groupId, OutputPath, groupNameNoSpaces)
    GenerateReport.CalculateMediaMD5(basePath + "/assets/Media/" + groupId, OutputPath, groupNameNoSpaces)

    return redirect(url_for('GroupChat', mediaType = 0, groupName=groupName))

@app.route('/about')
def About():
    return render_template('about.html')

def SetGlobalInOutVar(valueIn, valueOut):
    global InputPath, OutputPath
    InputPath = valueIn
    OutputPath = valueOut

def SetGlobalCheckReportVar(valueRep, valueCert):
    global ReportPath, CertificatePath
    ReportPath = valueRep
    CertificatePath = valueCert

@app.route('/exit')
def Exit():
    global fileName, fileSize, dbSha256, dbMd5, noDbError, noOutPathError, phoneNumber

    fileName = GlobalConstant.noDatabaseSelected
    fileSize = GlobalConstant.noDatabaseSelected
    dbSha256 = GlobalConstant.noDatabaseSelected
    dbMd5 = GlobalConstant.noDatabaseSelected
    noDbError = 1
    noOutPathError = 1

    SetGlobalInOutVar(GlobalConstant.selectDatabaseFile, GlobalConstant.selectOutputPath)
    SetGlobalCheckReportVar(GlobalConstant.noReportSelected, GlobalConstant.noCertificateSelected)

    phoneNumber = ""
    return redirect(url_for('Home'))

def main():
    SetGlobalInOutVar(GlobalConstant.selectDatabaseFile, GlobalConstant.selectOutputPath)
    SetGlobalCheckReportVar(GlobalConstant.noReportSelected, GlobalConstant.noCertificateSelected)

    webbrowser.open('http://localhost:5000')  # Disable for development Mode
    #app.run(debug=True, use_reloader=True)      # Enable for development Mode
    app.run(use_reloader=True)  # Disable for development Mode

if __name__ == '__main__':
    main()
