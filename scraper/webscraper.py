from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import json
import pandas as pd
import uuid
import os


class WebDriver:
    """
    The webdriver class is used to fetch a website, navigate through it and to find elements inside it

    Attributes:
        url (str): The url of the website to scrape

        username (str): OPTIONAL parameter for username in the website login credentials

        password (str): OPTIONAL parameter for password in the website login credentials

    Returns:
        None
    """

    def __init__(self, url: str, username: str = "", password: str = ""):
        # Initialise a webdriver when class is called
        # Delete all cookies
        self.driver = webdriver.Firefox()
        self.driver.delete_all_cookies()

        self.__address = url
        self.__username = username
        self.__password = password

        # Load the url
        self.driver.get(self.__address)

        # Initialise any private variables
        self.__page_links = []

        # Attributes used to handle the basic rankings table
        self.rankings_dict = {}
        self.rankings_table = None

        # Utility attributes used throughout the class
        self.table_data = []

    def __load_page(self, url: str):
        """
        PRIVATE method used to load a page with a specific url and wait 2 seconds once the request is made

        Args:
            url (str): The url of the website/page to load

        Returns:
            None
        """
        self.driver.get(url)
        sleep(2)

    def __extract_current_page_data(self):
        """
        PRIVATE method used to get all the relevant data within a specific page

        Args:
            None

        Returns:
            None
        """
        # Clear the table row data array every time this method is called
        self.table_data = []
        ratings_table = self.driver.find_element(By.ID, "ratingsResults")
        self.table_data = ratings_table.find_elements(By.TAG_NAME, "td")
        self.__clean_tabular_data()

    def __clean_tabular_data(self):
        """
        PRIVATE method used to remove the row in the table that contains an advert
        
        Args:
            None

        Returns:
            None
        """
        # Every 250th td element in the rankings table is an advert which we do not need
        self.table_data.pop(250)

    def __generate_uuid(self):
        """
        PRIVATE method used to generate uuid for each entry

        Args:
            None

        Returns:
            None
        """
        return str(uuid.uuid4())

    def accept_cookies(
        self, container_by: By, container_locator_string: str, button_by: By, button_locator_string: str
    ):
        """
        Method to find the manage cookies and accept cookies buttons and then click the button

        Args:
            container_by (By): Denotes the type of locator you'll use (e.g. By.ID or By.CLASS_NAME) to find the cookies container
            
            container_locator_string (str): The value for the string to locate the cookies container
            
            button_by (By): Denotes the type of locator you'll use to find the accept cookies button
            
            button_locator_string (str): The value for the string to locate the cookies container

        Returns:
            None
        """
        cookies_container = self.driver.find_element(container_by, container_locator_string)
        accept_button = cookies_container.find_element(button_by, button_locator_string)
        accept_button.click()

    def load_login_page(self, by: By, locator_string: str):
        """
        Method used to load the login page

        Args:
            by (By): Denotes the type of locator you'll use (e.g. By.ID or By.XPATH etc) to find login button/link
            
            locator_string (str): The value for the string to locate the login button/link

        Returns:
            None
        """
        login_button = self.driver.find_element(by, locator_string)
        login_button.click()
        sleep(2)

    def submit_login_credentials(
        self,
        username_field_by: By,
        username_field_locator: str,
        password_field_by: By,
        password_field_locator: str,
        submit_button_by: By,
        submit_button_locator: str,
    ):
        """
        Method used to fill in login form and submit credentials

        Args:
            username_field_by (By): Denotes the type of locator you'll use (e.g. By.ID or By.XPATH etc) to find username field

            username_field_locator (str): The value for the string to locate the username field

            password_field_by (By): Denotes the type of locator you'll use (e.g. By.ID or By.XPATH etc) to find password field

            password_field_locator (str): The value for the string to locate the password field

            submit_button_by (By): Denotes the type of locator you'll use (e.g. By.ID or By.XPATH etc) to find submit button

            submit_button_locator (str): The value for the string to locate the submit button

        Returns:
            None
        """
        # Find username, password and submit form elements
        form_username = self.driver.find_element(username_field_by, username_field_locator)
        form_password = self.driver.find_element(password_field_by, password_field_locator,)
        form_submit = self.driver.find_element(submit_button_by, submit_button_locator,)

        # Enter username and passwords into fields and click login
        form_username.send_keys(self.__username)
        form_password.send_keys(self.__password)
        form_submit.click()

    def navigate_to_page(self, by: By, page_button_locator: str):
        """
        Method to navigate to the rankings page

        Args:
            by (By): Denotes the type of locator you'll use to find button/link to the page (e.g. By.ID or By.XPATH etc.)

            page_button_locator (str): The value for the string to locate the page link/button

        Returns:
            None
        """
        page_link = self.driver.find_element(by, page_button_locator)
        page_link.click()

    def build_list_of_page_links(self, number_of_pages: int):
        """
        Method is used to generate a list containing the links to each page for the number of pages required

        Args:
            number_of_pages (int): Denotes the number of pages you want to generate the links for

        Returns:
            None
        """
        lst_page_offset = range(0, number_of_pages * 50, 50)
        template_url = "https://boxrec.com/en/ratings?offset="

        for page in lst_page_offset:
            self.__page_links.append(f"{template_url}{page}")

    def load_pages_and_extract_data(self):
        """
        Method used to go through each page requested and extract the data into a dictionary

        Args:
            None

        Returns:
            None
        """
        # Initialise dictionary entry count public variable
        self.dict_entry_count = 1
        # Go through each page requested, extract the data and then build the dict
        for page_number, link in enumerate(self.__page_links):
            # First page at this point is already loaded so we can ignore
            if page_number != 0:
                self.__load_page(link)
            # Process current pages data
            self.__extract_current_page_data()
            # Build dictionary
            self.__build_rankings_dictionary()

    def __build_rankings_dictionary(self):
        """
        PRIVATE method used to build dictionary containing the data extracted

        Args:
            None

        Returns:
            None
        """
        # Initialise current_fighter to ensure structure is the way I want
        current_fighter = {
            "Rank": None,
            "BoxerId": None,
            "Name": None,
            "Points": None,
            "Division": None,
            "Age": None,
            "Wins": None,
            "Draws": None,
            "Losses": None,
            "Stance": None,
            "Residence": None,
            "UUID": None,
        }
        # Go through each datapoint extracted and build up a profile for ONE fighter
        for count, data in enumerate(self.table_data):
            if count % 10 == 0:
                if bool(data.text):
                    # Generate a uuid for each row
                    current_fighter["UUID"] = self.__generate_uuid()
                    current_fighter["Rank"] = data.text

            elif count % 10 == 1:
                current_fighter["Name"] = data.text
                more_details_element = data.find_element(By.TAG_NAME, "a")
                more_details_link = more_details_element.get_attribute("href")
                current_fighter["BoxerId"] = more_details_link.split("/")[-1]

            elif count % 10 == 2:
                current_fighter["Points"] = data.text

            elif count % 10 == 4:
                current_fighter["Division"] = data.text

            elif count % 10 == 5:
                current_fighter["Age"] = data.text

            elif count % 10 == 6:
                current_fighter["Wins"] = data.text.split()[0]
                current_fighter["Draws"] = data.text.split()[1]
                current_fighter["Losses"] = data.text.split()[2]

            elif count % 10 == 8:
                current_fighter["Stance"] = data.text

            elif count % 10 == 9:
                current_fighter["Residence"] = data.text

                if any(current_fighter.values()):
                    self.rankings_dict[f"{self.dict_entry_count}"] = current_fighter
                    self.dict_entry_count += 1

                current_fighter = {
                    "Rank": None,
                    "BoxerId": None,
                    "Name": None,
                    "Points": None,
                    "Division": None,
                    "Age": None,
                    "Wins": None,
                    "Draws": None,
                    "Losses": None,
                    "Stance": None,
                    "Residence": None,
                    "UUID": None,
                }

    def create_basic_info_dataframe(self):
        """
        Method used to build the panda dataframe based on the data that has been scraped

        Args:
            None

        Returns:
            None
        """
        self.rankings_table = pd.DataFrame.from_dict(self.rankings_dict, orient="index")
        self.rankings_table.set_index("Rank", inplace=True)

    def write_dataframe_to_csv(self):
        """
        Method used to create a csv file of all the data that was scraped

        Args:
            None

        Returns:
            None
        """
        self.rankings_table.to_csv("scraper/test.csv")

    def write_raw_data_to_folder(self):
        """
        Method used to write raw data to a folder

        Args:
            None

        Returns:
            None
        """
        if not os.path.exists("scraper/raw_data"):
            os.mkdir("scraper/raw_data")

        with open("scraper/raw_data/data.json", "w") as fp:
            json.dump(self.rankings_dict, fp)


# TODO: Add method to class which retrieves a profile picture of each fighter
# TODO: Further abstract the class so that the config.json can be configured to scrape different websites
