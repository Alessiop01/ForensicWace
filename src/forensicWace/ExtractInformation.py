import os
import sqlite3
import forensicWace.GlobalConstant as GlobalConstant    # Comment this to develop on local. Add to create package to download and install pip
#import GlobalConstant    # Uncomment this to develop on local. Add to create package to download and install pip
import subprocess
import shutil

from tkinter import messagebox
from pathlib import Path

def ExecuteQuery(inputPath,query):
    # Connessione al database
    conn = sqlite3.connect(inputPath)

    try:
        cursor = conn.cursor()
        results = cursor.execute(query)

        extractedData = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
    except Exception as error:
        messagebox.showerror("ERRORE!", "L'estrazione richiesta non ha prodotto in output alcun risultato in quanto all'interno del database non risultano presenti i dati richiesti\n\nErrore durante l'esecuzione della query: " + str(error))

    conn.close()

    return extractedData

def GetChatList(inputPath):
    if inputPath == "":
        messagebox.showerror("ERROR!", "Select a database first")
    else:
        query = GlobalConstant.queryChatList

        extractedData = ExecuteQuery(inputPath, query)
        return extractedData

def GetGpsData(inputPath):
    if inputPath == "":
        messagebox.showerror("ERROR!", "Select a database first")
    else:
        query = GlobalConstant.queryGpsData

        extractedData = ExecuteQuery(inputPath, query)

        return extractedData

def GetBlockedContacts(inputPath):
    if inputPath == "":
        messagebox.showerror("ERROR!", "Select a database first")
    else:
        query = GlobalConstant.queryBlockedContacts

        extractedData = ExecuteQuery(inputPath, query)

        return extractedData

def GetPrivateChat(inputPath, mediaType, phoneNumber):
    if inputPath == "":
        messagebox.showerror("ERROR!", "Select a database first")
    else:
        query = GlobalConstant.queryPrivateChatCountersPT1 + phoneNumber + GlobalConstant.queryPrivateChatCountersPT2

        counters = ExecuteQuery(inputPath, query)

        if mediaType == '0':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatMessagesPT2
        elif mediaType == '1' or mediaType == '38':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatImagesPT2
        elif mediaType == '2' or mediaType == '39':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatVideosPT2
        elif mediaType == '3':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatAudioPT2
        elif mediaType == '4':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatContactsPT2
        elif mediaType == '5':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatPositionsPT2
        elif mediaType == '15':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatStickersPT2
        elif mediaType == '7':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatUrlsPT2
        elif mediaType == '8':
            query = GlobalConstant.queryPrivateChatMessages + phoneNumber + GlobalConstant.queryPrivateChatFilesPT2

        extractedData = ExecuteQuery(inputPath, query)

        return counters, extractedData

def GetGroupChat(inputPath, mediaType, groupName):
    if inputPath == "":
        messagebox.showerror("ERROR!", "Select a database first")
    else:
        query = GlobalConstant.queryGroupChatCountersPT1 + groupName + GlobalConstant.queryGroupChatCountersPT2

        counters = ExecuteQuery(inputPath, query)

        query = GlobalConstant.queryGroupChatIdPT1 + groupName + GlobalConstant.queryGroupChatIdPT2

        groupId = ExecuteQuery(inputPath, query)

        if mediaType == '0':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatMessagesPT2
        elif mediaType == '1' or mediaType == '38':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatImagesPT2
        elif mediaType == '2' or mediaType == '39':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatVideosPT2
        elif mediaType == '3':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatAudioPT2
        elif mediaType == '4':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatContactsPT2
        elif mediaType == '5':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatPositionsPT2
        elif mediaType == '15':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatStickerPT2
        elif mediaType == '7':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatUrlsPT2
        elif mediaType == '8':
            query = GlobalConstant.queryGroupChatMessages + groupName + GlobalConstant.queryGroupChatFilesPT2

        extractedData = ExecuteQuery(inputPath, query)

        return counters, groupId, extractedData

def GetGroupList(inputPath):
    if inputPath == "":
        messagebox.showerror("ERROR!", "Select a database first")
    else:
        query = GlobalConstant.queryGroupList
        extractedData = ExecuteQuery(inputPath, query)

        return extractedData

def ExtractFullBackup(backupPath, udid, outputPath):
    basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

    homePath = str(Path.home()).replace('\\', '/')

    if os.path.exists(homePath + "/AppDomainGroup-group.net.whatsapp.WhatsApp.shared/"):
        shutil.rmtree(homePath + "/AppDomainGroup-group.net.whatsapp.WhatsApp.shared/")

    command = "python " + basePath + "/WhatsApp-Chat-Exporter-GitHub/__main__.py -i -b \"" + backupPath + "/Apple Computer/MobileSync/Backup/" + udid + "\" -o \"" + outputPath + "\" --move-media --no-html -j [JSON]"
    subprocess.run(command, shell=True)

    # Copy the Media Folder
    sourcePath = outputPath + '/AppDomainGroup-group.net.whatsapp.WhatsApp.shared/Message/Media'
    destinationPath = basePath + '/assets/Media'
    if os.path.exists(destinationPath):
        shutil.rmtree(destinationPath)
    shutil.copytree(sourcePath, destinationPath)

    # Copy the Profile Picture Folder
    sourcePath = outputPath + '/AppDomainGroup-group.net.whatsapp.WhatsApp.shared/Media/Profile'
    destinationPath = basePath + '/assets/Profile'
    if os.path.exists(destinationPath):
        shutil.rmtree(destinationPath)
    shutil.copytree(sourcePath, destinationPath)


def ExtractEncryptedFullBackup(backupPath, udid, outputPath, password):
    basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

    homePath = str(Path.home()).replace('\\', '/')

    if os.path.exists(homePath + "/AppDomainGroup-group.net.whatsapp.WhatsApp.shared/"):
        shutil.rmtree(homePath + "/AppDomainGroup-group.net.whatsapp.WhatsApp.shared/")

    command = "python " + basePath + "/WhatsApp-Chat-Exporter-GitHub/__main__.py -i -b \"" + backupPath + "/Apple Computer/MobileSync/Backup/" + udid + "\" -o \"" + outputPath + "\" --move-media --no-html -j [JSON] --password " + password
    subprocess.run(command, shell=True)

    # Copy the Media Folder
    sourcePath = outputPath + '/AppDomainGroup-group.net.whatsapp.WhatsApp.shared/Message/Media'
    destinationPath = basePath + '/assets/Media'
    if os.path.exists(destinationPath):
        shutil.rmtree(destinationPath)
    shutil.copytree(sourcePath, destinationPath)

    # Copy the Profile Picture Folder
    sourcePath = outputPath + '/AppDomainGroup-group.net.whatsapp.WhatsApp.shared/Media/Profile'
    destinationPath = basePath + '/assets/Profile'
    if os.path.exists(destinationPath):
        shutil.rmtree(destinationPath)
    shutil.copytree(sourcePath, destinationPath)