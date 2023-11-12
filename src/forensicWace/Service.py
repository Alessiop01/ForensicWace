import re
import os
import hashlib
import binascii
import rfc3161ng
import vobject
import iOSbackup
import forensicWace.GlobalConstant as GlobalConstant    # Comment this to develop on local. Add to create package to download and install pip
#import GlobalConstant    # Uncomment this to develop on local. Add to create package to download and install pip

from iOSbackup import iOSbackup
from protobuf_decoder.protobuf_decoder import Parser
from datetime import datetime, timezone

basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

def FormatPhoneNumber(phoneumber):
    if phoneumber.isdigit():
        # Rimuovi tutti i caratteri non numerici dal numero di telefono
        numberOnlyDigit = re.sub(r'\D', '', phoneumber)

        # Utilizza la funzione re.sub per aggiungere spazi nel formato desiderato
        formattedNumber = re.sub(r'(\d{2})(\d{3})(\d{3})(\d{4})', r'+\1 \2 \3 \4', numberOnlyDigit)

        return formattedNumber
    else:
        return phoneumber

def GetFileSize(filePath):
    try:
        # Get the file size in bytes
        bytesSize = os.path.getsize(filePath)

        # Convert bytes to megabytes (1 MB = 1024 * 1024 bytes)
        mbSize = bytesSize / (1024 * 1024)

        return mbSize
    except FileNotFoundError:
        return None  # Handle the case where the file does not exist

def CalculateSHA256(filePath):

    with open(filePath, 'rb') as file:
        hashSHA256 = hashlib.sha256()
        while True:
            chunk = file.read(8192)
            if not chunk:
                break
            hashSHA256.update(chunk)
        return hashSHA256.hexdigest()

def CalculateMD5(filePath):

    with open(filePath, 'rb') as file:
        hashMD5 = hashlib.md5()
        while True:
            chunk = file.read(8192)
            if not chunk:
                break
            hashMD5.update(chunk)
        return hashMD5.hexdigest()

def CertificateReport(reportPath):
    certificate = open(basePath + "/src/tsa.crt", 'rb').read()

    # create the object
    rt = rfc3161ng.RemoteTimestamper("https://freetsa.org/tsr", certificate=certificate, hashname='sha256')

    # file to be certificated
    with open(reportPath, 'rb') as f:
        timestamp = rt.timestamp(data=f.read())
    certificatePath = reportPath.replace('.pdf', '')
    with open(certificatePath + ".tsr", 'wb') as f:
        f.write(timestamp)

def ReportCheckAuth(pathFile, pathCert):
        certificate = open(basePath + "/src/tsa.crt", 'rb').read()
        rt = rfc3161ng.RemoteTimestamper("https://freetsa.org/tsr", certificate=certificate, hashname='sha256')

        timestamp = open(pathCert, 'rb').read()
        verified = False
        try:
            verified = rt.check(timestamp, data=open(pathFile, 'rb').read())
        except:
            return -1

        if verified:
            return 1

def GetAvailableBackups():
    return iOSbackup.getDeviceList()

def VcardTelExtractor(vcardText):
    vcard = vobject.readOne(vcardText)
    if vcard.tel:
        return vcard.tel.value
    else:
        return "Number not available"

def RemoveFileWithoutExtension():
    # Specify the directory path
    directory_path = os.getcwd()

    # Get a list of all files in the directory
    all_items = os.listdir(directory_path)

    # Select only files in current directory (ignore folders)
    files = [item for item in all_items if os.path.isfile(os.path.join(directory_path, item))]

    # Iterate through the files and remove files without extensions
    for file in files:
        # Check if the file has no extension
        if '.' not in file:
            file_path = os.path.join(directory_path, file)
            # Check if it is a file (not a directory) before removing
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed file: {file_path}")

def GetSentDateTime(blob):
    if (blob != None):
        hexData = binascii.hexlify(blob).decode()
        parsedData = Parser().parse(hexData)

        class ParsedResult:
            def __init__(self, field, wire_type, data):
                self.field = field
                self.wire_type = wire_type
                self.data = data

        class ParsedResults:
            def __init__(self, results):
                self.results = results

        field3Value = None
        for result in parsedData.results:
            if result.field == 3:
                field3Value = result.data
                break

        gmtDateTime = datetime.fromtimestamp(field3Value, tz=timezone.utc)
        messageDateTime = gmtDateTime.strftime('%Y-%m-%d %H:%M:%S %Z')

        return messageDateTime
    else:
        return GlobalConstant.infoNotAvailable

def GetReadDateTime(blob):
    if (blob != None):
        hexData = binascii.hexlify(blob).decode()
        parsedData = Parser().parse(hexData)

        class ParsedResult:
            def __init__(self, field, wire_type, data):
                self.field = field
                self.wire_type = wire_type
                self.data = data

        class ParsedResults:
            def __init__(self, results):
                self.results = results

        field3Value = None
        for result in parsedData.results:
            if result.field == 3:
                field3Value = result.data
                break

        field5InField2 = None
        for result in parsedData.results:
            if result.field == 2:
                for subResult in result.data.results:
                    if subResult.field == 5:
                        field5InField2 = subResult.data
                        break

        if(field5InField2 != None):
            readTimestamp = int(field3Value) + int(field5InField2)
            gmtDateTime = datetime.fromtimestamp(readTimestamp, tz=timezone.utc)
            messageDateTime = gmtDateTime.strftime('%Y-%m-%d %H:%M:%S %Z')
        else:
            messageDateTime = GlobalConstant.infoNotAvailable

        return messageDateTime
    else:
        return GlobalConstant.infoNotAvailable

def ConvertSeconds(secondi):
    minuti = secondi // 60
    secondi_rimasti = secondi % 60
    return "{:02d}:{:02d}".format(minuti, secondi_rimasti)

def GetUserProfilePicImage(fileName):
    directory = "/assets/Profile/"
    for file in os.listdir(basePath + "/assets/Profile/"):
        if file.startswith(fileName) and file.count('-') == 1:
            return os.path.join(directory, file)
    return "/assets/img/avatars/user.png"