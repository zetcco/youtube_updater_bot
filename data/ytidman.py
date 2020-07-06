#utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
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

mainDirectory = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir)
print(mainDirectory)
logFile = mainDirectory + "\\logs\\uploaderLog.log"
logging.basicConfig(filename=logFile, filemode='w',format='%(asctime)s-%(levelname)s - %(message)s', level=logging.INFO)	
chrome_path = mainDirectory + "\\data\\chromedriver.exe" # Chrome driver path
options = webdriver.ChromeOptions() 
driver = None
toBeUpdatedPath = mainDirectory + "\\ToBeUpdated"
failedVideoIDs = []
delay = 30
logo = mainDirectory + "\\data\\logo.png"
icon = mainDirectory + "\\data\\icon.ico"
channelURL = ""


def getProfileNames():
	folderNames = {}
	dropDownValues = []
	for name in os.listdir(os.getenv('LOCALAPPDATA') + "\\Google\\Chrome\\User Data\\"):
		if os.path.isdir(os.getenv('LOCALAPPDATA') + "\\Google\\Chrome\\User Data\\" + name) and (name[0:8] == "Profile "):
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
	return folderNames, dropDownValues

def startChrome():
	global driver
	global channelURL
	window.destroy()
	driver = webdriver.Chrome(chrome_path, options=options)
	driver.get("https://studio.youtube.com")
	channelURL = driver.current_url

def callback(selection):
	selection = selection.split(' ')
	profileID = selection[0] + " " + selection[1]
	print(profileID)
	options.add_argument("user-data-dir=" + os.getenv('LOCALAPPDATA') + "\\Google\\Chrome\\User Data\\")
	options.add_argument("profile-directory=%s" % profileID)

def goToVideoManager():
	#This function redirects the driver to the Video Manager page in YT stuio
	try:
		# driver.get(channelURL + "/videos/upload?filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D")
		javaScript = "document.getElementById('menu-item-1').click();"
		driver.execute_script(javaScript)
	except Exception as e:
		logging.critical("Go to Videos error", exc_info=True)

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

def goBack():
	# This method is not used when editing draft videos
	try:
		WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.nav-item-text.back-button-text.style-scope.ytcp-navigation-drawer')))
	except TimeoutException:
		logging.critical('Loading took too much time! - @getting_go_back_link')
	javaScript = "document.getElementById('back-button').click();"
	driver.execute_script(javaScript)

def closeEditingWindow():
	javaScript = "document.getElementById('close-button').click();"
	driver.execute_script(javaScript)

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
			# print("button active")
			return False
		elif nextButton.get_attribute("aria-disabled") == "true":
			# print("button inactive")
			return True
			logging.info("Updating completed")

	except Exception as e:
		logging.critical("Go to next page error", exc_info=True)

def editVideoProgressBar():
	while True:
		print("loading")
		progressBarWait = driver.find_element_by_tag_name('ytcp-navigation-drawer').get_attribute("layout")
		if (progressBarWait == "video"):
			print("finished loading")
			return

def updateDetails(title, description, tags):
	try:
		WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, 'textbox')))
	except:
		pass
	
	# Get the ids of the textboxes
	inputIDs = driver.find_elements_by_id('textbox')
	
	# Moves, Clicks, Clears then enter New data to the Title text box
	actions = ActionChains(driver)
	actions.move_to_element(inputIDs[0])
	actions.click(inputIDs[0])
	actions.perform()
	time.sleep(2)
	inputIDs[0].clear()
	time.sleep(2)
	inputIDs[0].send_keys(title)

	# Moves, Clicks, Clears then enter New data to the Description text box
	actions = ActionChains(driver)
	actions.move_to_element(inputIDs[1])
	actions.click(inputIDs[1])
	actions.perform()
	inputIDs[1].send_keys(description)

	#Set values for tags
	textInputElements = driver.find_elements_by_id('text-input')
	if (textInputElements[-1].get_attribute('placeholder') == 'Add tag'):
		textInputElements[-1].send_keys(tags)
	else:
		print("Couldn't find tag textbox")

	attempts = 0
	while True:
		print("Attempts: " + attempts)
		if (inputIDs[0].text[0:2] == "B0") and (attempts <= 3):
			print("Title not updated")
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

def editVideo(productID, title, description, tags):
	# global failedVideoIDs

	#Wait for edit box to appear
	try:
		updateDetails(title, description, tags)
		updateThumbnail(productID, tags, title)
		ageRestriction()
		pass
	except Exception as e:
		logging.critical("Critical error for '%s' " %(productID), exc_info=True)
		pass

def ageRestriction():
	madeForKids = driver.find_element_by_id('made-for-kids-group')
	notForKidsRadioButton = madeForKids.find_elements_by_id('radioLabel')[-1]
	actions = ActionChains(driver)
	actions.move_to_element(notForKidsRadioButton)
	actions.click(notForKidsRadioButton)
	actions.perform()

def getNewDetails(productID):
	productIDPath = toBeUpdatedPath + "\\" + productID
	detailPath = productIDPath + "\\details.txt"
	if os.path.exists(detailPath):
		text = open(detailPath,"r", encoding="utf8")
		lines = text.readlines()
		title = lines[0]
		title = title[:90]
		description_main = lines[2:lines.index('***** Technical Details *****\n')-2]
		description_additional = lines[lines.index('***** Additional Details *****\n')+2 : lines.index('***** Extra Details *****\n')-2]
		description = description_main + description_additional
		# description = lines[2:-2]
		lastLine = -1
		for line in reversed(description):
			if line[0] == "\n":
				lastLine -= 1
			else:
				break
		description = description[:lastLine]
		finalDescription = ""
		for line in description:
			finalDescription += line
		finalDescription = finalDescription.replace("<","")
		finalDescription = finalDescription.replace(">","")
		finalDescription = finalDescription[:5000]
		# tags = lines[-1]
		tags = lines[lines.index("***** Tags *****\n")+2:]
		tags += ","

		return title, finalDescription, tags
	else:
		logging.critical("Missing detail file on " + productID, exc_info=True)
		return

def updateEXIF(filename, tags, title):
	try:
		tags = tags.replace(",",";")

		im = Image.open(filename)
		exif_dict = piexif.load(im.info["exif"])
		# process im and exif_dict...
		w, h = im.size
		exif_dict["0th"][piexif.ImageIFD.XPKeywords] = tags.encode('utf-16')
		exif_dict["0th"][piexif.ImageIFD.XPComment] = title.encode('utf-16')
		exif_dict["0th"][piexif.ImageIFD.XPTitle] = title.encode('utf-16')
		exif_dict["0th"][piexif.ImageIFD.XPSubject] = title.encode('utf-16')
		exif_bytes = piexif.dump(exif_dict)
		im.save(filename, "jpeg", exif=exif_bytes)
	except Exception as e:
		logging.critical("EXIF updating error", exc_info=True)
		pass

def updateThumbnail(productID, tags, title):
	try:
		productIDPath = toBeUpdatedPath + "\\" + productID
		thumbnailPath = productIDPath + "\\" + "thumbnail.jpg"

		updateEXIF(thumbnailPath, tags, title)

		driver.execute_script(
    							"HTMLInputElement.prototype.click = function() {                     " +
   	 							"  if(this.type !== 'file') HTMLElement.prototype.click.call(this);  " +
    							"};                                                                  " )
		# trigger the upload
		driver.find_element_by_css_selector(".remove-default-style.style-scope.ytcp-thumbnails-compact-editor-uploader").click()
		# assign the file to the `<input>`
		driver.find_element_by_css_selector("input[type=file]").send_keys(thumbnailPath)
	except Exception as e:
		logging.critical("Thumbnail updating error", exc_info=True)
		pass

def saveChanges(productID):
	print("Attempting to find the save button")
	saveButtonContainer = driver.find_element_by_css_selector('.buttons.style-scope.ytcp-video-metadata-editor-old')
	saveButtonLocator = saveButtonContainer.find_element_by_id('save')
	print("Found the save button")
	if saveButtonLocator.get_attribute('label') == 'Save':
		actions = ActionChains(driver)
		actions.move_to_element(saveButtonLocator)
		actions.click(saveButtonLocator)
		actions.perform()
		print("Clicked on the save button")
	while True:
		changesSavedPopup = driver.find_element_by_css_selector('.style-scope paper-toast').text
		print(changesSavedPopup)
		if (changesSavedPopup == ""):
			break
		elif (changesSavedPopup == "Changes saved"):
			print("Still saving...")
			pass
	savedChangesAppear(productID)

def finalSaves(productID):
	while True:
		saveStatus = driver.find_element_by_css_selector('.style-scope.paper-toast')
		if (saveStatus.text == "Your video %s has been saved as draft" % (productID)):
			break

def progressBarAppearWait():
	while True:
		progressBar = driver.find_element_by_xpath('//*[@id="main-container"]/ytcp-header/header/paper-progress').get_attribute('hidden')
		if (progressBar == "true"):
			try:
				WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.style-scope.ytcp-video-row.cell-body.tablecell-video.floating-column.last-floating-column')))
				time.sleep(2)
				return
			except TimeoutException:
				print("Loading took too much time.")
		else:
			print("Progress bar appeared.")

def savedChangesAppear(productID):
	while True:
		try:
			savedChangesStatus = driver.find_element_by_css_selector('.style-scope.paper-toast').text
			if (savedChangesStatus == "Changes saved"):
				return
			elif (savedChangesStatus == "We had trouble saving your video, retrying in 5 seconds"):
				print("Couldn't save changes on: " + productID)
				undoButtonContainer = driver.find_element_by_css_selector('.buttons.style-scope.ytcp-video-metadata-editor')
				undoButtonLocator = undoButtonContainer.find_element_by_id('discard')
				print("Found the undo button")
				if undoButtonLocator.get_attribute('label') == 'Undo changes':
					actions = ActionChains(driver)
					actions.move_to_element(undoButtonLocator)
					actions.click(undoButtonLocator)
					actions.perform()
					print("Clicked on the Undo button")
					time.sleep(1)
					return
			else:
				print("Changes not saved yet.")
		except UnexpectedAlertPresentException:
			logging.warning("Couldn't save changes appeared. Trying to go back.")
			alert = driver.switch_to.alert
			alert.accept()
			return

def mainRunTime():
	allVideos = 0
	errorOccurredVideos = []
	while True:
		noOfLoopedThroughVids = 0
		progressBarAppearWait()
		while True:
			mainVideoElements = driver.find_elements_by_css_selector('.style-scope.ytcp-video-list-cell-video.video-title-wrapper')
			mainVideoElementsDraftCheck = driver.find_elements_by_id('video-thumbnail-container')
			print("No of vids: " + str(len(mainVideoElements)))
			for element in mainVideoElements:
				try:
					print("Current of vid: " + str(mainVideoElements.index(element)))
					videoTitle = element.find_element_by_id('video-title').text
					# time.sleep(1)
					processingAbandonedVideo = element.find_element_by_id('video-title').get_attribute('class') # If this value has 'no-link' in the end, then that means that video is too long and processing of that video is abandoned
					print(processingAbandonedVideo)
					
					# This is here to check whether the video is draft or not
					if (mainVideoElementsDraftCheck[mainVideoElements.index(element)].get_attribute('class') == "style-scope ytcp-video-list-cell-video draft-thumbnail"):
						draftVideo = True
						print("Draft video found")
					else:
						draftVideo = False
						print("Non-Draft video found")

					if (videoTitle[0:2] == "B0") and (processingAbandonedVideo != "style-scope ytcp-video-list-cell-video remove-default-style no-link") and (draftVideo == False) and (videoTitle not in errorOccurredVideos):
						#gets the Product ID
						print("NTBE video found")
						productID = videoTitle
						print("******" + productID + "******")

						print("Attempting to open editor window")
						videoElementID = driver.find_elements_by_id('video-thumbnail-container')[mainVideoElements.index(element)]
						driver.execute_script("arguments[0].click();", videoElementID)
						print("Successfully opened the editor window")

						try:
							print("Attempting to get product details")
							title, description, tags = getNewDetails(productID)
							print("Successfully got the product details")

							print("Attempting to edit the video")
							editVideo(productID, title, description, tags)
							print("Editing completed on  the video")

							print("Attempting to save the video")
							saveChanges(productID)
							print("Saving completed on  the video")
						except Exception as e:
							errorOccurredVideos.append(productID)
							logging.critical("Critical error for '%s' " %(productID), exc_info=True)
							pass

						print("Attempting to go back to videos")
						goBack()
						print("Went back to videos")

					elif (processingAbandonedVideo == "style-scope ytcp-video-list-cell-video remove-default-style no-link"):
						print('Processing abandoned video found: ' + videoTitle)
					noOfLoopedThroughVids += 1
				except StaleElementReferenceException:
					print("Random page refresh detected")
					progressBarAppearWait()
					noOfLoopedThroughVids = 0
					break
			allVideos += noOfLoopedThroughVids
			if (noOfLoopedThroughVids == len(mainVideoElements)):
				break
				# print("Random refresh detected.")
				# try:
				# 	WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.style-scope.ytcp-video-list-cell-video.video-title-wrapper')))
				# except TimeoutException:
				# 	logging.critical('Loading took too much time! - @random_refresh')	
		endOfPagesStatus = goToNextPage()
		if (endOfPagesStatus):
			return allVideos


profileNames, dropDownValues = getProfileNames()
startPage = 1

# Startup window
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
btn = Button(window, text="Continue", command=lambda: startChrome(), height = 150, width = 450,bg="#0075d6",fg="white")
btn.pack()
window.mainloop()

goToVideoManager()
allVideos = mainRunTime()
print(allVideos)