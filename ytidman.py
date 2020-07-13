#utf-8
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from tkinter import *
import time
import os 
import piexif
from PIL import ImageTk, Image
import logging
import re
from tqdm import tqdm
import datetime

mainDirectory = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir)
logFile = mainDirectory + "\\logs\\uploaderLog {}.log".format(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
logging.basicConfig(filename=logFile, filemode='w',format='%(asctime)s-%(levelname)s - %(lineno)s  %(message)s', level=logging.INFO)
chrome_path = mainDirectory + "\\data\\chromedriver.exe" # Chrome driver path
options = webdriver.ChromeOptions() 
driver = None
toBeUpdatedPath = mainDirectory + "\\ToBeUpdated"
delay = 30
logo = mainDirectory + "\\data\\logo.png"
icon = mainDirectory + "\\data\\icon.ico"
channelURL = ""

def getProfileNames():
	try:
		folderNames = {}
		dropDownValues = []
		for name in os.listdir(os.getenv('LOCALAPPDATA') + "\\Google\\Chrome\\User Data\\"):
			if os.path.isdir(os.getenv('LOCALAPPDATA') + "\\Google\\Chrome\\User Data\\" + name) and (name[0:8] == "Profile "):
				if os.path.isfile(os.getenv('LOCALAPPDATA') + "\\Google\\Chrome\\User Data\\" + name + "\\Preferences"):
					with open(os.getenv('LOCALAPPDATA') + "\\Google\\Chrome\\User Data\\" + name + "\\Preferences", "r") as pref:
						prefData = pref.read()
						match = re.search(r'[\w\.-]+@[\w\.-]+', prefData)
						try:
							profileEmail = match.group(0)
						except AttributeError:
							profileEmail = "Not signed in"
					folderNames.update({name:profileEmail})
		for key, value in folderNames.items():
			dropDownValues.append("%s (%s)" % (key, value))
		logging.info("GETTING CHROME PROFILES SUCCESSFUL")
		return folderNames, dropDownValues
	except:
		logging.critical("GETTING CHROME PROFILES ERROR")

def startChrome(window):
	global driver
	global channelURL
	try:
		window.destroy()
		driver = webdriver.Chrome(chrome_path, options=options)
		driver.get("https://studio.youtube.com")
		channelURL = driver.current_url
		logging.info("STARTING CHROME SUCCESSFUL")
	except:
		logging.critical("STARTING CHROME ERROR", exc_info=True)

def callback(selection):
	try:
		selection = selection.split(' ')
		profileID = selection[0] + " " + selection[1]
		profileEmail = selection[2][1:-1]
		options.add_argument("user-data-dir=" + os.getenv('LOCALAPPDATA') + "\\Google\\Chrome\\User Data\\")
		options.add_argument("profile-directory=%s" % profileID)
		logging.info("SETTING CHROME OPTIONS SUCCESSFUL ------------ SELECTED PROFILE: {} , {}".format(profileID, profileEmail))
	except:
		logging.critical("SETTING CHROME OPTIONS ERROR", exc_info=True)

def goToVideoManager():
	#This function redirects the driver to the Video Manager page in YT stuio
	try:
		# driver.get(channelURL + "/videos/upload?filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D")
		javaScript = "document.getElementById('menu-item-1').click();"
		driver.execute_script(javaScript)
		logging.info("GO TO VIDEO MANAGER SUCCESSFUL")
	except:
		logging.critical("GO TO VIDEO MANAGER ERROR", exc_info=True)

def AlertAccept():
	i = 0
	while i<3:
		logging.warning("Browser Leave changes alert occured.")
		logging.info("Browser alert accept try: " + str(i+1))
		time.sleep(2)
		i += 1
		try:
			logging.warning("Trying to accept.")
			alert = driver.switch_to.alert.accept()
			break
		except NoAlertPresentException:
			logging.warning("Alert Not Found. Wait 3 Seconds then Try Again!")
			time.sleep(3)

def goToNextPage():
	try:
		#Waits till the Next button appears
		try:
			navButtons = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.rtl-flip.style-scope.ytcp-table-footer')))
		except TimeoutException:
			logging.critical('Loading took too much time! - @getting_go_back_link')
		#Assings the next button from Navigation buttons

		navButtons = driver.find_elements_by_css_selector('.rtl-flip.style-scope.ytcp-table-footer')
		nextButton = navButtons[2]

		#Checks if the Next button is disabled or not (If disabled that means the bot is running on the last page)
		if nextButton.get_attribute("aria-disabled") == "false":
			javaScript = "document.getElementById('navigate-after').click();"
			driver.execute_script(javaScript)
			return False
		elif nextButton.get_attribute("aria-disabled") == "true":
			return True
			logging.info("Updating completed")

	except Exception as e:
		logging.critical("Go to next page error", exc_info=True)

def editVideoProgressBar():
	while True:
		progressBarWait = driver.find_element_by_tag_name('ytcp-navigation-drawer').get_attribute("layout")
		if (progressBarWait == "video"):
			return

def updateDetails(title, description, tags):
	try:
		WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, 'textbox')))
	except:
		pass

	try:
		# Get the ids of the textboxes
		inputIDs = driver.find_elements_by_id('textbox')
		
		# Moves, Clicks, Clears then enter New data to the Title text box
		try:
			actions = ActionChains(driver)
			actions.move_to_element(inputIDs[0])
			actions.click(inputIDs[0])
			actions.perform()
			time.sleep(2)
			inputIDs[0].clear()
			time.sleep(2)
			inputIDs[0].send_keys(title)
			logging.info("SETTING TITLE SUCCESSFUL")
		except:
			logging.critical("SETTING TITLE ERROR", exc_info=True)

		# Moves, Clicks, Clears then enter New data to the Description text box
		try:
			actions = ActionChains(driver)
			actions.move_to_element(inputIDs[1])
			actions.click(inputIDs[1])
			actions.perform()
			inputIDs[1].send_keys(description)
			logging.info("SETTING DESCRIPTION SUCCESSFUL")
		except:
			logging.critical("SETTING DESCRIPTION ERROR", exc_info=True)
		#Set values for tags
		try:
			textInputElements = driver.find_elements_by_id('text-input')
			if (textInputElements[-1].get_attribute('placeholder') == 'Add tag'):
				textInputElements[-1].send_keys(tags)
				logging.info("SETTING TAGS SUCCESSFUL")
		except:
			logging.critical("SETTING TAGS ERROR", exc_info=True)

		attempts = 0
		while True:
			if (inputIDs[0].text[0:2] == "B0") and (attempts <= 3):
				logging.warning("TITLE UPDATING ERROR.... RETRYING..... ATTEMPT: " + str(attempts))
				actions = ActionChains(driver)
				actions.move_to_element(inputIDs[0])
				actions.click(inputIDs[0])
				actions.perform()
				time.sleep(2)
				inputIDs[0].clear()
				time.sleep(2)
				inputIDs[0].send_keys(title)
				attempts += 1
			else:
				return
	except:
		logging.critical("UPDATING DETAILS ERROR", exc_info=True)

def updateDetailsNew(title, description, tags):
	try:
		WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, 'textbox')))
	except:
		pass

	try:
		# Get the ids of the textboxes
		inputIDs = driver.find_elements_by_id('textbox')
		
		# Moves, Clicks, Clears then enter New data to the Title text box
		try:
			driver.execute_script("""document.querySelectorAll("[id='textbox']")[0].innerText = '""" + title.replace("\n","\\n").replace("'","\\'") + """';""")
			actions = ActionChains(driver)
			actions.move_to_element(inputIDs[0])
			actions.click(inputIDs[0])
			actions.perform()
			inputIDs[0].send_keys(" ")
			logging.info("SETTING TITLE SUCCESSFUL")
		except:
			logging.critical("SETTING TITLE ERROR", exc_info=True)

		try:
			driver.execute_script("""document.querySelectorAll("[id='textbox']")[1].innerText = '""" + description.replace("\n","\\n").replace("'","\\'") + """';""")
			actions = ActionChains(driver)
			actions.move_to_element(inputIDs[1])
			actions.click(inputIDs[1])
			actions.perform()
			inputIDs[1].send_keys(" ")
			logging.info("SETTING DESCRIPTION SUCCESSFUL")
		except:
			logging.critical("SETTING DESCRIPTION ERROR", exc_info=True)

		#Set values for tags
		try:
			textInputElements = driver.find_elements_by_id('text-input')
			if (textInputElements[-1].get_attribute('placeholder') == 'Add tag'):
				textInputElements[-1].send_keys(tags)
				logging.info("SETTING TAGS SUCCESSFUL")
		except:
			logging.critical("SETTING TAGS ERROR", exc_info=True)
	except:
		logging.critical("UPDATING DETAILS ERROR", exc_info=True)

def editVideo(productID, title, description, tags):
	updateDetailsNew(title, description, tags)
	updateThumbnail(productID, tags, title)

def getNewDetails(productID):
	productIDPath = toBeUpdatedPath + "\\" + productID
	if os.path.exists(productIDPath):
		detailPath = productIDPath + "\\details.txt"
		if os.path.exists(detailPath):
			try:
				with open(detailPath,"r", encoding="utf8") as text:
					lines = text.readlines()

					# Gets the title of the product
					title = lines[0]
					title = title[:90]

					# Gets the raw descriptions (Normal, Additional, Extra, descriptions and Similar prodcuts) of the product
					description_main = lines[2:lines.index('***** Technical Details *****\n')-2]
					description_additional = lines[lines.index('***** Additional Details *****\n')+2 : lines.index('***** Extra Details *****\n')-2]
					description_similar_products = lines[lines.index('***** Similar Products *****\n')+2 : lines.index('***** Tags *****\n')-2]
					description_extra = lines[lines.index('***** Extra Details *****\n')+2 : lines.index('***** Similar Products *****\n')-2]
					description = description_main + description_additional + description_similar_products

					# UNKNOWN CODE HERE 
					# description = lines[2:-2]
					# lastLine = -1
					# for line in reversed(description):
					# 	if line[0] == "\n":
					# 		lastLine -= 1
					# 	else:
					# 		break
					# description = description[:lastLine]

					# Processes the above raw descriptions
					finalDescription = ""
					for line in description:
						finalDescription += line
					finalDescription = finalDescription.replace("<","")
					finalDescription = finalDescription.replace(">","")
					finalDescription = finalDescription[:5000]

					# Gets the tags
					tags = lines[lines.index("***** Tags *****\n")+2:]
					tags += ","

					logging.info("GETTING DETAILS COMPLETED")
					return [title, finalDescription, tags]
			except:
				logging.critical("GETTING DETAILS ERROR " + productID)
		else:
			logging.critical("Missing detail file on " + productID)
			return None
	else:
		logging.critical("Missing prodcut folder: " + productID)
		return None

def updateEXIF(filename, tags, title):
	try:
		tags = ";".join(tags)
		im = Image.open(filename)
		exif_dict = piexif.load(im.info["exif"])
		# process im and exif_dict...
		exif_dict["0th"][piexif.ImageIFD.XPKeywords] = tags.encode('utf-16')
		exif_dict["0th"][piexif.ImageIFD.XPComment] = title.encode('utf-16')
		exif_dict["0th"][piexif.ImageIFD.ImageDescription] = title
		exif_bytes = piexif.dump(exif_dict)
		im.save(filename, "jpeg", exif=exif_bytes)
		logging.info("EXIF UPDATING COMPLETED")
	except Exception as e:
		logging.critical("EXIF UPDATING ERROR", exc_info=True)
		pass

def updateThumbnail(productID, tags, title):
	try:
		productIDPath = toBeUpdatedPath + "\\" + productID
		thumbnailPath = productIDPath + "\\" + "thumbnail.jpg"

		if os.path.exists(thumbnailPath):
			updateEXIF(thumbnailPath, tags, title)

			driver.execute_script(
	    							"HTMLInputElement.prototype.click = function() {                     " +
	   	 							"  if(this.type !== 'file') HTMLElement.prototype.click.call(this);  " +
	    							"};                                                                  " )

			try:
				# trigger the upload
				driver.execute_script("""document.querySelector(".remove-default-style.style-scope.ytcp-thumbnails-compact-editor-uploader").click();""")
				# assign the file to the `<input>`
				driver.find_element_by_css_selector("input[type=file]").send_keys(thumbnailPath)
				logging.info("THUMBNAIL UPLOADING SUCCESSFUL")
			except:
				logging.critical("THUMBNAIL UPLOADING ERROR", exc_info=True)
		else:
			logging.critical("Missing thumbnail file on " + productID)
	except Exception as e:
		logging.critical("MAIN THUMBNAIL UPDATING ERROR", exc_info=True)
		pass

def saveChanges():
	try:
		driver.execute_script("""document.querySelectorAll("#save")[1].click();""")
		logging.info("CLICKING ON SAVE BUTTON SUCCESSFUL")
		savedChangesAppear()
	except:
		logging.critical("CLICKING ON SAVE BUTTON ERROR", exc_info=True)

def progressBarAppearWait():
	while True:
		progressBar = driver.find_element_by_xpath('//*[@id="main-container"]/ytcp-header/header/paper-progress').get_attribute('hidden')
		if (progressBar == "true"):
			try:
				WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.style-scope.ytcp-video-row.cell-body.tablecell-video.floating-column.last-floating-column')))
				time.sleep(2)
				return
			except TimeoutException:
				logging.critical("Loading took too much time.", exc_info=True)

def savedChangesAppear():
	while True:
		try:
			savedChangesStatus = driver.find_element_by_css_selector('.style-scope.paper-toast').text
			if (savedChangesStatus == "Changes saved"):
				logging.info("VIDEO SAVING SUCCESSFUL")
				return
			elif (savedChangesStatus == "We had trouble saving your video, retrying in 5 seconds"):
				logging.critical("SAVING CHANGES FAILED")
				logging.info("ATTEMPTING UNDO CHANGES")
				driver.execute_script("""document.querySelectorAll("#discard")[0].click();""")
				logging.info("CLICKED ON UNDO CHANGES BUTTON")
				time.sleep(1)
				return
		except UnexpectedAlertPresentException:
			logging.warning("Couldn't save changes appeared. Trying to go back.")
			alert = driver.switch_to.alert
			alert.accept()
			return

def getVideoLinks():
	errorOccurredVideos = []
	toBeEditedVideoLinks = []
	while True:
		progressBarAppearWait()
		mainVideoElements = driver.find_elements_by_css_selector('.style-scope.ytcp-video-list-cell-video.video-title-wrapper')
		mainVideoElementsDraftCheck = driver.find_elements_by_id('video-thumbnail-container')
		for element in mainVideoElements:
			videoTitle = element.find_element_by_id('video-title').text
			videoLink = element.find_element_by_id('video-title').get_attribute('href')
			processingAbandonedVideo = element.find_element_by_id('video-title').get_attribute('class') # If this value has 'no-link' in the end, then that means that video is too long and processing of that video is abandoned
			
			# This is here to check whether the video is draft or not
			if (mainVideoElementsDraftCheck[mainVideoElements.index(element)].get_attribute('class') == "style-scope ytcp-video-list-cell-video draft-thumbnail"):
				draftVideo = True
			else:
				draftVideo = False

			if (videoTitle[0:2] == "B0") and (processingAbandonedVideo != "style-scope ytcp-video-list-cell-video remove-default-style no-link") and (draftVideo == False) and (videoTitle not in errorOccurredVideos):
				toBeEditedVideoLinks.append(videoLink)

		endOfPagesStatus = goToNextPage()
		if (endOfPagesStatus):
			break
	logging.info("GETTING VIDEO LINKS SUCCESSFUL")
	return toBeEditedVideoLinks

def runGUI():
	# Startup window
	try:
		window = Tk()
		window.geometry("700x220")
		window.iconbitmap(icon)
		window.title("Youtube Updater Bot")
		img = ImageTk.PhotoImage(Image.open(logo))
		panel = Label(window, image = img) 
		panel.pack(side = "top", fill = "both", expand = "yes")

		tkvar = StringVar(window)
		tkvar.set('Select a profile')
		lblProfile = Label(window, text="Choose a profile")
		lblProfile.pack()
		popupMenu = OptionMenu(window, tkvar, *dropDownValues, command=callback)
		popupMenu.pack()

		lbl = Label(window, text="Press continue after youtube studio is loaded. You have to go to the classic manually.")
		lbl.pack()
		btn = Button(window, text="Continue", command=lambda: startChrome(window), height = 150, width = 450,bg="#0075d6",fg="white")
		btn.pack()
		window.mainloop()
	except:
		logging.critical("GUI RUNNING ERROR")

def getProductID():
	try:
		return driver.find_element_by_id('original-filename').text[:-4]
	except:
		logging.critical("Critical error", exc_info=True)

profileNames, dropDownValues = getProfileNames()
runGUI()
goToVideoManager()
toBeEditedVideoLinks = getVideoLinks()

for link in tqdm(toBeEditedVideoLinks):
	driver.get(link)
	logging.info("------------ Started working on '%s'  ------------" %(link))
	try:
		productID = getProductID()
		logging.info("Product ID: " + productID)
		new_details = getNewDetails(productID) # Returns none if the details.txt or product folder itself is missing
		if new_details != None:
			editVideo(productID, new_details[0], new_details[1], new_details[2])
			saveChanges()
			pass
	except Exception as e:
		if driver.current_url == "https://studio.youtube.com/oops":
			pass