import os
import sys
import forensicWace.Service as Service    # Comment this to develop on local. Add to create package to download and install pip
#import Service    # Uncomment this to develop on local. Add to create package to download and install pip

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

def CreateHorizontalDocHeaderAndFooter(canvas, doc):
    canvas.saveState()
    canvas.restoreState()
    page_num = canvas.getPageNumber()
    text = "Page %s" % page_num
    canvas.drawCentredString(148.5 * mm, 20 * mm, text)
    canvas.line(15 * mm, 25 * mm, 282 * mm, 25 * mm)

def CreateVerticalDocHeaderAndFooter(canvas, doc):
    canvas.saveState()
    canvas.drawImage(basePath + "/assets/img/Logo.png", A4[0] / 2 - 158, A4[1] - 65, width=300, height=52.5)
    canvas.restoreState()
    page_num = canvas.getPageNumber()
    text = "Page %s" % page_num
    canvas.drawCentredString(105 * mm, 20 * mm, text)
    canvas.line(15 * mm, 25 * mm, 195 * mm, 25 * mm)

def ChatListReport(outputPath, fileName, extractedDataList):

    data = [["Contact", "Username", "Phone number", "Number of messages", "Last Message Date"]]

    for extractedData in extractedDataList:
        data.append([extractedData["Contact"], extractedData["UserName"],
                     Service.FormatPhoneNumber(extractedData["PhoneNumber"]), extractedData["NumberOfMessages"], extractedData["MessageDate"]])

    outFileName = outputPath + fileName + "-ChatList.pdf"

    # Configurazione del documento
    doc = SimpleDocTemplate(outFileName, pagesize=A4)

    fileElements = []

    table = Table(data, colWidths=[100, 110, 110, 110])

    # Stili della tabella
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    table.setStyle(style)

    fileElements.append(table)

    # Scrittura del documento
    doc.build(fileElements, onFirstPage=CreateVerticalDocHeaderAndFooter, onLaterPages=CreateVerticalDocHeaderAndFooter)

    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")

def PrivateChatReport(outputPath, phoneNumber, extractedData):

    outFileName = outputPath + phoneNumber + "-Chat.pdf"

    # Define pages margins
    left_margin = 50
    right_margin = 50
    bottom_margin = 100
    top_margin = 100

    # Create the canvas for the report
    c = canvas.Canvas(outFileName, pagesize=A4)

    # Get starting positions to start writing
    x_offset = left_margin
    y_offset = c._pagesize[1] - top_margin

    # Define message box characteristics
    message_box_height = 40
    message_box_radius = 20

    # Define colors to use
    message_box_color_green = HexColor('#DCF8C6')
    message_box_color_blue = HexColor('#C6E9F9')
    message_box_text_color = HexColor('#000000')

    # Set line height
    line_height = 30

    # Insert logo and page number on the first page
    c.drawImage(basePath + "/assets/img/Logo.png", A4[0] / 2 - 150, A4[1] - 65, width=300, height=52.5)
    page_num = c.getPageNumber()
    text = "Page %s" % page_num
    c.drawCentredString(105 * mm, 20 * mm, text)
    c.line(15 * mm, 25 * mm, 195 * mm, 25 * mm)

    previousSender = 'NotAssigned'

    for chat in extractedData:

        # Check if the point where to write is inside the bottom margin
        # If YES save the ended page and update the position
        if y_offset < bottom_margin:
            c.showPage()
            y_offset = c._pagesize[1] - top_margin

            # Insert logo and page number on the page
            c.drawImage(basePath + "/assets/img/Logo.png", A4[0] / 2 - 150, A4[1] - 65, width=300, height=52.5)
            page_num = c.getPageNumber()
            text = "Page %s" % page_num
            c.drawCentredString(105 * mm, 20 * mm, text)
            c.line(15 * mm, 25 * mm, 195 * mm, 25 * mm)

        message_text = chat['text']
        message_width = 0
        if chat['ZMESSAGETYPE'] == 0:
            message_width = c.stringWidth(message_text, 'Helvetica', 12)

        message_box_width = message_width + 40
        message_box_height = 40

        allegati = -1
        eliminato = "This message has been deleted by the sender"

        if chat['ZMESSAGETYPE'] == 1:
            allegati = 1
        elif chat['ZMESSAGETYPE'] == 2:
            allegati = 2
            message_width = c.stringWidth(Service.ConvertSeconds(chat['durata']), 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 3:
            allegati = 3
            message_width = c.stringWidth(Service.ConvertSeconds(chat['durata']), 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 4:
            allegati = 4
            message_width = c.stringWidth(chat["ZPARTNERNAME"], 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 5:
            allegati = 5
            message_width = c.stringWidth(str(chat['latitudine']) + " , " + str(chat["longitudine"]), 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 6:
            allegati = 6
        elif chat['ZMESSAGETYPE'] == 7:
            allegati = 7
        elif chat['ZMESSAGETYPE'] == 8:
            allegati = 8
            if chat['text'] != 'None':
                message_width = c.stringWidth(chat['text'], 'Helvetica', 12)
                message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 11:  # GIF ID
            allegati = 11
            message_width = c.stringWidth("GIF", 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 14:
            allegati = 14
            message_width = c.stringWidth(eliminato, 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 15:  # Sticker ID
            allegati = 15
            message_width = c.stringWidth("Sticker", 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 38:  # Foto 1 visualizzazione
            allegati = 38
            message_width = c.stringWidth("Image", 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 39:  # Video 1 visualizzazione
            allegati = 39
            message_width = c.stringWidth(Service.ConvertSeconds(chat['durata']), 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 46:
            allegati = 46
            message_width = c.stringWidth("Poll", 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 0:
            allegati = 0  # Just a text message

        # Check if the box exceeds the margin
        # If NO then set the box dimensions
        if message_box_width > c._pagesize[0] - right_margin - left_margin:
            message_box_width = c._pagesize[0] - right_margin - left_margin

        # Check who wrote the message, then set the right color, user name and phone number
        if previousSender != chat['user']:
            if chat['user'] is not None:
                c.setFillColor(message_box_color_blue)
                c.drawString(x_offset, y_offset, chat['ZPARTNERNAME'] + " - " + "(" + Service.FormatPhoneNumber(chat['user']) + ")")
                y_offset -= 50
            else:
                c.setFillColor(message_box_color_green)
                c.drawString(x_offset, y_offset, "Database Owner")
                y_offset -= 50
        else:
            y_offset -= 30

        # Split the text on multiple rows
        lines = []
        line = ''
        if chat['ZMESSAGETYPE'] == 0:
            words = chat['text'].split()
            for word in words:
                if len(line + word) > 85:
                    lines.append(line)
                    line = word + ' '
                    message_box_height += 18
                    y_offset -= 18
                else:
                    line += word + ' '
            lines.append(line)

        num_lines = len(lines)

        # Check if the point where to write is inside the bottom margin
        # If YES save the ended page and update the position
        if y_offset < bottom_margin:
            c.showPage()
            y_offset = c._pagesize[1] - top_margin - num_lines * 35

            # Inserimento logo e numero di pagina sulla pagina
            c.drawImage(basePath + "/assets/img/Logo.png", A4[0] / 2 - 150, A4[1] - 65, width=300, height=52.5)
            page_num = c.getPageNumber()
            text = "Page %s" % page_num
            c.drawCentredString(105 * mm, 20 * mm, text)
            c.line(15 * mm, 25 * mm, 195 * mm, 25 * mm)

        # Set the right color and design the rectangle
        c.setFillColor(message_box_color_blue if chat['user'] is not None else message_box_color_green)
        c.roundRect(x_offset, y_offset, message_box_width, message_box_height, message_box_radius, stroke=0, fill=1)
        c.setFillColor(message_box_text_color)

        if allegati == 1:
            c.drawImage(basePath + "/src/icons/CameraNum.png" if chat['user'] is not None else basePath + "/src/icons/CameraUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            y_offset -= 16
        elif allegati == 2:
            c.drawImage(basePath + "/src/icons/VideoNum.png" if chat['user'] is not None else basePath + "/src/icons/VideoUser.png",
                x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, Service.ConvertSeconds(chat['durata']))
            y_offset -= 16
        elif allegati == 3:
            c.drawImage(basePath + "/src/icons/MicNum.png" if chat['user'] is not None else basePath + "/src/icons/MicUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, Service.ConvertSeconds(chat['durata']))
            y_offset -= 16
        elif allegati == 4:
            c.drawImage(basePath + "/src/icons/ContactNum.png" if chat['user'] is not None else basePath + "/src/icons/ContactUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, chat["ZPARTNERNAME"])
            y_offset -= 16
        elif allegati == 5:
            c.drawImage(basePath + "/src/icons/PositionNum.png" if chat['user'] is not None else basePath + "/src/icons/PositionUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6,
                         str(chat['latitudine']) + " , " + str(chat["longitudine"]))
            y_offset -= 16
        elif allegati == 6:
            c.drawImage( basePath + "/src/icons/GroupNum.png" if chat['user'] is not None else basePath + "/src/icons/GroupUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            y_offset -= 16
        elif allegati == 7:
            c.drawImage(basePath + "/src/icons/LinkNum.png" if chat['user'] is not None else basePath + "/src/icons/LinkUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            y_offset -= 16
        elif allegati == 8:
            c.drawImage(basePath + "/src/icons/DocNum.png" if chat['user'] is not None else basePath + "/src/icons/DocUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            if chat["text"] != 'None':
                c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, chat['text'])
            y_offset -= 16
        elif allegati == 11:
            c.drawImage(basePath + "/src/icons/GifNum.png" if chat['user'] == 'Database owner' else basePath + "/src/icons/GifUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, "GIF")
            y_offset -= 16
        elif allegati == 14:
            c.drawImage(basePath + "/src/icons/BinNum.png" if chat['user'] is not None else basePath + "/src/icons/BinUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, eliminato)
            y_offset -= 16
        elif allegati == 15:
            c.drawImage(basePath + "/src/icons/StickerNum.png" if chat['user'] is not None else basePath + "/src/icons/StickerUser.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, "Sticker")
            y_offset -= 16
        elif allegati == 38:
            c.drawImage(basePath + "/src/icons/OneTimeNum.png" if chat['user'] is not None else basePath + "/src/icons/OneTimeUSer.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, "Image")
            y_offset -= 16
        elif allegati == 39:
            c.drawImage(basePath + "/src/icons/OneTimeNum.png" if chat['user'] is not None else basePath + "/src/icons/OneTimeUSer.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, Service.ConvertSeconds(chat['durata']))
            y_offset -= 16
        elif allegati == 46:
            c.drawImage(basePath + "/src/icons/PollNum.png" if chat['user'] is not None else basePath + "/src/icons/PollUSer.png", x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, "Poll")
            y_offset -= 16

        # Check if the number of lines is >= 2
        # If YES them update the Y coordinate
        if num_lines >= 2:
            y_offset += message_box_height / 2 - 20

        # Print the message into the box
        for line in lines:
            c.drawString(x_offset + 20, y_offset + message_box_height / 2 - 6, line)
            y_offset -= 16

        if chat['user'] is None:
            c.setFont("Helvetica", 8)
            c.drawString(x_offset, y_offset, "Send date: " + Service.GetSentDateTime(chat['dateTimeInfos']))
            y_offset -= 12
            c.drawString(x_offset, y_offset, "Reading date: " + Service.GetReadDateTime(chat['dateTimeInfos']))
        else:
            c.setFont("Helvetica", 8)
            c.drawString(x_offset, y_offset, "Send date: " + chat['receiveDateTime'] + " UTC")

        y_offset -= 26
        c.setFont("Helvetica", 12)

        previousSender = chat['user']

    # Save the PDF file
    c.save()
    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")

def GpsLocations(outputPath, fileName, extractedDataList):

    data = [["Sender", "Receiver", "Date", "Latitude", "Longitude"]]

    for extractedData in extractedDataList:
        data.append([Service.FormatPhoneNumber(extractedData["Sender"]),
                     Service.FormatPhoneNumber(extractedData["Receiver"]), extractedData["MessageDate"], extractedData["Latitude"], extractedData["Longitude"]])

    outFileName = outputPath + fileName + "-GpsLocations.pdf"

    # Configurazione del documento
    doc = SimpleDocTemplate(outFileName, pagesize=A4)

    fileElements = []

    table = Table(data, colWidths=[100, 110, 110, 110])

    # Stili della tabella
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    table.setStyle(style)

    fileElements.append(table)

    # Scrittura del documento
    doc.build(fileElements, onFirstPage=CreateVerticalDocHeaderAndFooter, onLaterPages=CreateVerticalDocHeaderAndFooter)

    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")

def BlockedContactReport(outputPath, fileName, extractedDataList):

    data = [["Name", "Phone number"]]

    for extractedData in extractedDataList:
        if extractedData["Name"] == None:
            extractedData["Name"] = "Not Available"
        data.append([extractedData["Name"], Service.FormatPhoneNumber(extractedData["PhoneNumber"])])

    outFileName = outputPath + fileName + "-BlockedContacts.pdf"

    # Configurazione del documento
    doc = SimpleDocTemplate(outFileName, pagesize=A4)

    fileElements = []

    table = Table(data, colWidths=[100, 110, 110, 110])

    # Stili della tabella
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    table.setStyle(style)

    fileElements.append(table)

    # Scrittura del documento
    doc.build(fileElements, onFirstPage=CreateVerticalDocHeaderAndFooter, onLaterPages=CreateVerticalDocHeaderAndFooter)

    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")

def GroupListReport(outputPath, fileName, extractedDataList):

    data = [["Group Name", "Last message", "Number of messages", "Notification status"]]

    for extractedData in extractedDataList:
        if  extractedData["Is_muted"] == None:
            extractedData["Is_muted"] = "Active"
        else:
            extractedData["Is_muted"] = "Disabled"
        data.append([extractedData["Group_Name"], extractedData["Message_Date"], extractedData["Number_of_Messages"], extractedData["Is_muted"]])

    outFileName = outputPath + fileName + "-GroupList.pdf"

    # Configurazione del documento
    doc = SimpleDocTemplate(outFileName, pagesize=A4)

    fileElements = []

    table = Table(data, colWidths=[100, 110, 110, 110])

    # Stili della tabella
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    table.setStyle(style)

    fileElements.append(table)

    # Scrittura del documento
    doc.build(fileElements, onFirstPage=CreateVerticalDocHeaderAndFooter, onLaterPages=CreateVerticalDocHeaderAndFooter)

    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")

def GroupChatReport(outputPath, groupName, extractedData):

    words = groupName.split()
    groupNameNoSpaces = ''.join(words)

    outFileName = outputPath + groupNameNoSpaces + "-Chat.pdf"

    # Define pages margins
    left_margin = 50
    right_margin = 50
    bottom_margin = 100
    top_margin = 100

    # Create the canvas for the report
    c = canvas.Canvas(outFileName, pagesize=A4)

    # Get starting positions to start writing
    x_offset = left_margin
    y_offset = c._pagesize[1] - top_margin

    # Define message box characteristics
    message_box_height = 40
    message_box_radius = 20

    # Define colors to use
    message_box_color_green = HexColor('#DCF8C6')
    message_box_color_blue = HexColor('#C6E9F9')
    message_box_text_color = HexColor('#000000')

    # Set line height
    line_height = 30

    # Insert logo and page number on the first page
    c.drawImage(basePath + "/assets/img/Logo.png", A4[0] / 2 - 150, A4[1] - 65, width=300, height=52.5)
    page_num = c.getPageNumber()
    text = "Page %s" % page_num
    c.drawCentredString(105 * mm, 20 * mm, text)
    c.line(15 * mm, 25 * mm, 195 * mm, 25 * mm)

    previousSender = 'NotAssigned'

    for chat in extractedData:

        # Check if the point where to write is inside the bottom margin
        # If YES save the ended page and update the position
        if y_offset < bottom_margin:
            c.showPage()
            y_offset = c._pagesize[1] - top_margin

            # Insert logo and page number on the page
            c.drawImage(basePath + "/assets/img/Logo.png", A4[0] / 2 - 150, A4[1] - 65, width=300, height=52.5)
            page_num = c.getPageNumber()
            text = "Page %s" % page_num
            c.drawCentredString(105 * mm, 20 * mm, text)
            c.line(15 * mm, 25 * mm, 195 * mm, 25 * mm)

        message_text = chat['text']
        message_width = 0
        if chat['ZMESSAGETYPE'] == 0:
            message_width = c.stringWidth(message_text, 'Helvetica', 12)

        message_box_width = message_width + 40
        message_box_height = 40

        allegati = -1
        eliminato = "This message has been deleted by the sender"

        if chat['ZMESSAGETYPE'] == 1:
            allegati = 1
        elif chat['ZMESSAGETYPE'] == 2:
            allegati = 2
            message_width = c.stringWidth(Service.ConvertSeconds(chat['durata']), 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 3:
            allegati = 3
            message_width = c.stringWidth(Service.ConvertSeconds(chat['durata']), 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 4:
            allegati = 4
            message_width = c.stringWidth(chat["ZPARTNERNAME"], 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 5:
            allegati = 5
            message_width = c.stringWidth(str(chat['latitudine']) + " , " + str(chat["longitudine"]), 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 6:
            allegati = 6
        elif chat['ZMESSAGETYPE'] == 7:
            allegati = 7
        elif chat['ZMESSAGETYPE'] == 8:
            allegati = 8
            if chat['text'] != 'None':
                message_width = c.stringWidth(chat['text'], 'Helvetica', 12)
                message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 11:  # GIF ID
            allegati = 11
            message_width = c.stringWidth("GIF", 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 14:
            allegati = 14
            message_width = c.stringWidth(eliminato, 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 15:  # Sticker ID
            allegati = 15
            message_width = c.stringWidth("Sticker", 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 38:  # Foto 1 visualizzazione
            allegati = 38
            message_width = c.stringWidth("Image", 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 39:  # Video 1 visualizzazione
            allegati = 39
            message_width = c.stringWidth(Service.ConvertSeconds(chat['durata']), 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 46:
            allegati = 46
            message_width = c.stringWidth("Poll", 'Helvetica', 12)
            message_box_width = message_width + 52
        elif chat['ZMESSAGETYPE'] == 0:
            allegati = 0  # Just a text message

        # Check if the box exceeds the margin
        # If NO then set the box dimensions
        if message_box_width > c._pagesize[0] - right_margin - left_margin:
            message_box_width = c._pagesize[0] - right_margin - left_margin

        # Check who wrote the message, then set the right color, user name and phone number
        if previousSender != chat['user']:
            if chat['user'] is not None:
                c.setFillColor(message_box_color_blue)
                c.drawString(x_offset, y_offset,
                             chat['contactName'] + " - " + "(" + Service.FormatPhoneNumber(chat['user']) + ")")
                y_offset -= 50
            else:
                c.setFillColor(message_box_color_green)
                c.drawString(x_offset, y_offset, "Database Owner")
                y_offset -= 50
        else:
            y_offset -= 30

        # Split the text on multiple rows
        lines = []
        line = ''
        if chat['ZMESSAGETYPE'] == 0:
            words = chat['text'].split()
            for word in words:
                if len(line + word) > 85:
                    lines.append(line)
                    line = word + ' '
                    message_box_height += 18
                    y_offset -= 18
                else:
                    line += word + ' '
            lines.append(line)

        num_lines = len(lines)

        # Check if the point where to write is inside the bottom margin
        # If YES save the ended page and update the position
        if y_offset < bottom_margin:
            c.showPage()
            y_offset = c._pagesize[1] - top_margin - num_lines * 35

            # Inserimento logo e numero di pagina sulla pagina
            c.drawImage(basePath + "/assets/img/Logo.png", A4[0] / 2 - 150, A4[1] - 65, width=300, height=52.5)
            page_num = c.getPageNumber()
            text = "Page %s" % page_num
            c.drawCentredString(105 * mm, 20 * mm, text)
            c.line(15 * mm, 25 * mm, 195 * mm, 25 * mm)

        # Set the right color and design the rectangle
        c.setFillColor(message_box_color_blue if chat['user'] is not None else message_box_color_green)
        c.roundRect(x_offset, y_offset, message_box_width, message_box_height, message_box_radius, stroke=0, fill=1)
        c.setFillColor(message_box_text_color)

        if allegati == 1:
            c.drawImage(basePath + "/src/icons/CameraNum.png" if chat['user'] is not None else basePath + "/src/icons/CameraUser.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            y_offset -= 16
        elif allegati == 2:
            c.drawImage(basePath + "/src/icons/VideoNum.png" if chat['user'] is not None else basePath + "/src/icons/VideoUser.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, Service.ConvertSeconds(chat['durata']))
            y_offset -= 16
        elif allegati == 3:
            c.drawImage(basePath + "/src/icons/MicNum.png" if chat['user'] is not None else basePath + "/src/icons/MicUser.png", x_offset + 14,
                        y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, Service.ConvertSeconds(chat['durata']))
            y_offset -= 16
        elif allegati == 4:
            c.drawImage(basePath + "/src/icons/ContactNum.png" if chat['user'] is not None else basePath + "/src/icons/ContactUser.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, chat["ZPARTNERNAME"])
            y_offset -= 16
        elif allegati == 5:
            c.drawImage(basePath + "/src/icons/PositionNum.png" if chat['user'] is not None else basePath + "/src/icons/PositionUser.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6,
                         str(chat['latitudine']) + " , " + str(chat["longitudine"]))
            y_offset -= 16
        elif allegati == 6:
            c.drawImage(basePath + "/src/icons/GroupNum.png" if chat['user'] is not None else basePath + "/src/icons/GroupUser.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            y_offset -= 16
        elif allegati == 7:
            c.drawImage(basePath + "/src/icons/LinkNum.png" if chat['user'] is not None else basePath + "/src/icons/LinkUser.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            y_offset -= 16
        elif allegati == 8:
            c.drawImage(basePath + "/src/icons/DocNum.png" if chat['user'] is not None else basePath + "/src/icons/DocUser.png", x_offset + 14,
                        y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            if chat["text"] != 'None':
                c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, chat['text'])
            y_offset -= 16
        elif allegati == 11:
            c.drawImage(basePath + "/src/icons/GifNum.png" if chat['user'] == 'Database owner' else basePath + "/src/icons/GifUser.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, "GIF")
            y_offset -= 16
        elif allegati == 14:
            c.drawImage(basePath + "/src/icons/BinNum.png" if chat['user'] is not None else basePath + "/src/icons/BinUser.png", x_offset + 14,
                        y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, eliminato)
            y_offset -= 16
        elif allegati == 15:
            c.drawImage(basePath + "/src/icons/StickerNum.png" if chat['user'] is not None else basePath + "/src/icons/StickerUser.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, "Sticker")
            y_offset -= 16
        elif allegati == 38:
            c.drawImage(basePath + "/src/icons/OneTimeNum.png" if chat['user'] is not None else basePath + "/src/icons/OneTimeUSer.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, "Image")
            y_offset -= 16
        elif allegati == 39:
            c.drawImage(basePath + "/src/icons/OneTimeNum.png" if chat['user'] is not None else basePath + "/src/icons/OneTimeUSer.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, Service.ConvertSeconds(chat['durata']))
            y_offset -= 16
        elif allegati == 46:
            c.drawImage(basePath + "/src/icons/PollNum.png" if chat['user'] is not None else basePath + "/src/icons/PollUSer.png",
                        x_offset + 14, y_offset + message_box_height / 2 - 7, width=12, height=12)
            allegati = -1
            c.drawString(x_offset + 32, y_offset + message_box_height / 2 - 6, "Poll")
            y_offset -= 16

        # Check if the number of lines is >= 2
        # If YES them update the Y coordinate
        if num_lines >= 2:
            y_offset += message_box_height / 2 - 20

        # Print the message into the box
        for line in lines:
            c.drawString(x_offset + 20, y_offset + message_box_height / 2 - 6, line)
            y_offset -= 16

        if chat['user'] is None:
            c.setFont("Helvetica", 8)
            c.drawString(x_offset, y_offset, "Send date: " + Service.GetSentDateTime(chat['dateTimeInfos']))
            y_offset -= 12
            c.drawString(x_offset, y_offset, "Reading date: " + Service.GetReadDateTime(chat['dateTimeInfos']))
        else:
            c.setFont("Helvetica", 8)
            c.drawString(x_offset, y_offset, "Send date: " + chat['receiveDateTime'] + " UTC")

        y_offset -= 26
        c.setFont("Helvetica", 12)

        previousSender = chat['user']

    # Save the PDF file
    c.save()
    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")

def DbHash(inputPath, outputPath, fileName):

    data = [["Database file name", "Hash code - SHA256"], [fileName, Service.CalculateSHA256(inputPath)]]

    outFileName = outputPath + fileName + "-DatabaseHash.pdf"

    # Configurazione del documento
    doc = SimpleDocTemplate(outFileName, pagesize=landscape(A4))

    fileElements = []

    table = Table(data, colWidths=[350, 350])

    # Stili della tabella
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    table.setStyle(style)

    fileElements.append(table)

    fileElements.append(Spacer(1, 20))  # 1 unità di larghezza e 20 unità di altezza)

    data = [["Database file name", "Hash code - MD5"], [fileName, Service.CalculateMD5(inputPath)]]

    table = Table(data, colWidths=[350, 350])

    table.setStyle(style)

    fileElements.append(table)

    # Scrittura del documento
    doc.build(fileElements, onFirstPage=CreateHorizontalDocHeaderAndFooter)

    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")

def CalculateMediaSHA256(directory_path, outputPath, fileName):

    data = [["File PATH", "SHA256"]]

    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, directory_path)
            print(relative_path)
            data.append([os.path.basename(file_path), Service.CalculateSHA256(file_path)])

    outFileName = outputPath + fileName + "-Media-SHA256.pdf"

    # Configurazione del documento
    doc = SimpleDocTemplate(outFileName, pagesize=landscape(A4))

    fileElements = []

    table = Table(data, colWidths=[350, 350])

    # Stili della tabella
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    table.setStyle(style)

    fileElements.append(table)
    # Scrittura del documento
    doc.build(fileElements, onFirstPage=CreateHorizontalDocHeaderAndFooter)

    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")

def CalculateMediaMD5(directory_path, outputPath, fileName):

    data = [["File PATH", "MD5"]]

    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, directory_path)
            print(relative_path)
            data.append([os.path.basename(file_path), Service.CalculateMD5(file_path)])

    outFileName = outputPath + fileName + "-Media-MD5.pdf"

    # Configurazione del documento
    doc = SimpleDocTemplate(outFileName, pagesize=landscape(A4))

    fileElements = []

    table = Table(data, colWidths=[350, 350])

    # Stili della tabella
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    table.setStyle(style)

    fileElements.append(table)
    # Scrittura del documento
    doc.build(fileElements, onFirstPage=CreateHorizontalDocHeaderAndFooter)

    Service.CertificateReport(outFileName)

    # Verifica l'esistenza del file PDF appena creato.
    # SE esiste lo apre automaticamente
    # ALTRIMENTI stampa un messaggio di errore
    if os.path.exists(outFileName):

        if sys.platform.startswith('win'):
            # Windows
            os.system("start " + outFileName)
        elif sys.platform.startswith('darwin'):
            # macOS
            os.system("open " + outFileName)
        # elif sys.platform.startswith('linux'):
        # Linux
    else:
        print("Errore: il file PDF non è stato creato.")