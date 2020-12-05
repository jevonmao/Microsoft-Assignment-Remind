from selenium import webdriver
from bs4 import BeautifulSoup as soup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from dataclasses import dataclass

CREDS = {'email' : 'jingwen.mao@smhsstudents.org','passwd':r'xag4$%uop3'}
URL = "https://teams.microsoft.com/"

@dataclass
class SingleAssignment:
    name: str
    className: str
    dueDate: str
    pastDue: bool

class AssignmentBot:
    def __init__(self, creds, driver):
        self.cred = creds
        self.driver = driver

    def login(self):
        #login required
        emailField = self.driver.find_element_by_xpath('//*[@id="i0116"]')
        emailField.click()
        emailField.send_keys(CREDS['email'])
        self.driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()
        passwordField = self.driver.find_element_by_xpath('//*[@id="i0118"]') #Next button
        WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="i0118"]'))
        )
        passwordField = self.driver.find_element_by_xpath('//*[@id="i0118"]') #Next button
        passwordField.click()
        passwordField.send_keys(CREDS['passwd'])
        self.driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Sign in button
        self.driver.implicitly_wait(5)
        self.driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #remember login
        self.driver.implicitly_wait(5)

    def findAssignmentTab(self):
        buttons = self.driver.find_element_by_xpath('//*[@id="app-bar-66aeee93-507d-479a-a3ef-8f494af43945"]')
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="app-bar-66aeee93-507d-479a-a3ef-8f494af43945"]'))
        )
        buttons = self.driver.find_element_by_xpath('//*[@id="app-bar-66aeee93-507d-479a-a3ef-8f494af43945"]')
        buttons.click()

    def parseAssignments(self):
        iframe = self.driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/messages-header/div[2]/div/base-tab/div/div/div/extension-tab/div/embedded-page-container/div/iframe')
        self.driver.switch_to.frame(iframe)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[1]/div/div[2]/div'))
        )
        assignments = self.driver.find_element_by_xpath('//*[@id="root"]/div/div/div/div/div[1]/div[1]/div/div[2]/div')
        assignmentItems = assignments.find_elements_by_tag_name('a')
        return assignmentItems

    def getAssignmentDetails(self, assignmentItems):
        assignmentList = []
        for assignment in assignmentItems:
            # assignmentNameDiv = assignment.find_element_by_class_name('assignment-card-title__3vDaT')
            # assignmentName = assignmentNameDiv.find_element_by_tag_name("span")
            # class_Name = assignment.find_element_by_xpath("//*[contains(@class, 'assignment-card-class-name__3sMyJ u-hide-on-mobile__2d0Fg')]")
            innerText = re.sub('•|P\n', '', assignment.text)
            print(innerText)
            assignmentName = innerText.partition('\n')[0]
            className = innerText.partition('\n')[1]
            dueDate = innerText.partition('\n')[3]
            try:
                innerText.partition('\n'[3])
            except IndexError:
                newAssignment = SingleAssignment(assignmentName, className, dueDate, False)
            else:
                newAssignment = SingleAssignment(assignmentName, className, dueDate, True)
            assignmentList.append(newAssignment)
        return assignmentList
                    

class InitializeDriver:
    def __init__(self, url):
        self.URL = url
    
    def start_browser(self):

        driver = webdriver.Chrome()

        driver.get(URL)

        WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

        if("login.microsoftonline.com" in driver.current_url):
            return driver
        else:
            raise ValueError("Improper web URL.")

try:
    initDriver = InitializeDriver(url=URL)
    driver = initDriver.start_browser()
    bot = AssignmentBot(creds=CREDS, driver=driver)
    bot.login()
    bot.findAssignmentTab()
    items = bot.parseAssignments()
    assignments = bot.getAssignmentDetails(items)
    #print(assignments)
except ValueError:
    print("Failed to initialize bot.")