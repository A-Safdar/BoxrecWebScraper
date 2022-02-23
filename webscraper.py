from numpy import number
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

    '''
    Attributes
    ----------

    configuration_path :    str
                            The path for the json file which contains the url, username and password
    '''
    """

    def __init__(self, configuration_path: str):
        # Initialise a webdriver when class is called
        # Delete all cookies
        self.driver = webdriver.Firefox()
        self.driver.delete_all_cookies()
        self.configuration_path = configuration_path

        # Assign required attributes when initialising
        self.__scraper_config = self.__get_scraper_settings()
        self.__address = self.__scraper_config["url"]
        self.__username = self.__scraper_config["username"]
        self.__password = self.__scraper_config["password"]

        # Initialise any private variables
        self.__page_links = []

        # Load the url
        self.driver.get(self.__address)

        # Attributes used to handle the basic rankings table
        self.rankings_dict = {}
        self.rankings_table = None

        # Utility attributes used throughout the class
        self.table_row_data = []

    def __get_scraper_settings(self):
        """
        PRIVATE method used to extract relevant settings from the json config file
        """
        with open(self.configuration_path, "r") as f:
            return json.load(f)

    def __load_page(self, url: str):
        """
        PRIVATE method used to load a page with a specific url and wait 2 seconds once the request is made
        '''
        Attributes
        ----------

        url:    str
                The url of the page to load
        """
        self.driver.get(url)
        sleep(2)

    def __extract_current_page_data(self):
        """
        PRIVATE method used to get all the relevant data within a specific page
        """
        # Clear the table row data array every time this method is called
        self.table_row_data = []
        ratings_table = self.driver.find_element(By.ID, "ratingsResults")
        table_rows = ratings_table.find_elements(By.TAG_NAME, "tr")
        for row in table_rows:
            self.table_row_data.append(row.find_elements(By.TAG_NAME, "td"))

    def __generate_uuid(self):
        """
        PRIVATE method used to generate uuid for each entry
        """
        return str(uuid.uuid4())

    def accept_cookies(self):
        """
        Method to find the manage cookies and accept cookies buttons and then click the button
        """
        cookies_container = self.driver.find_element(By.XPATH, '//div[@id="qc-cmp2-ui"]')
        accept_button = cookies_container.find_element(By.XPATH, '//button[contains(@class, "css-1my9mvs")]')
        accept_button.click()

    def login(self):
        """
        Method to navigate to the login page and then fill in the login form with user credentials
        """
        # Find and click login button
        login_button = self.driver.find_element(By.LINK_TEXT, "login")
        login_button.click()

        # Find username, password and submit form elements
        form_username = self.driver.find_element(By.ID, "username")
        form_password = self.driver.find_element(By.ID, "password")
        form_submit = self.driver.find_element(By.CLASS_NAME, "submitButton")

        # Enter username and passwords into fields and click login
        # TODO: ADD SUPPORT FOR GETTING CREDENTIALS FROM JSON
        form_username.send_keys(self.__username)
        form_password.send_keys(self.__password)
        form_submit.click()

    def load_rankings_page(self):
        """
        Method to navigate to the rankings page
        """
        ratings_link = self.driver.find_element(By.LINK_TEXT, "ratings")
        ratings_link.click()

    def build_list_of_page_links(self, number_of_pages: int):
        """
        Method is used to generate a list containing the links to each page for the number of pages required

        '''
        Attributes
        ----------

        number_of_pages :   int
                            The number of required pages

        '''
        """
        lst_page_offset = range(0, number_of_pages * 50, 50)
        template_url = "https://boxrec.com/en/ratings?offset="

        for page in lst_page_offset:
            self.__page_links.append(f"{template_url}{page}")

    def build_rankings_dictionary(self):
        """
        Method used to begin scraping through the website and through different pages to create a dictionary
        """
        dict_entry_count = 0
        for page_number, link in enumerate(self.__page_links):
            # First page at this point is already loaded so we can ignore
            if page_number != 0:
                self.__load_page(link)

            # Process current pages data
            self.__extract_current_page_data()

            # Go through each row in the data extracted from the table
            for row in self.table_row_data:
                # Initialise an empty dict
                # Not necessary but done so that the structure is fixed
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
                # Go through each datapoint in the row being processed
                for count, data in enumerate(row):
                    if count == 0:
                        if bool(data.text):
                            # Generate a uuid for each row
                            current_fighter["UUID"] = self.__generate_uuid()
                            current_fighter["Rank"] = data.text

                    elif count == 1:
                        current_fighter["Name"] = data.text
                        more_details_element = data.find_element(By.TAG_NAME, "a")
                        more_details_link = more_details_element.get_attribute("href")
                        current_fighter["BoxerId"] = more_details_link.split("/")[-1]

                    elif count == 2:
                        current_fighter["Points"] = data.text

                    elif count == 4:
                        current_fighter["Division"] = data.text

                    elif count == 5:
                        current_fighter["Age"] = data.text

                    elif count == 6:
                        current_fighter["Wins"] = data.text.split()[0]
                        current_fighter["Draws"] = data.text.split()[1]
                        current_fighter["Losses"] = data.text.split()[2]

                    elif count == 8:
                        current_fighter["Stance"] = data.text

                    elif count == 9:
                        current_fighter["Residence"] = data.text

                if any(current_fighter.values()):
                    self.rankings_dict[f"{dict_entry_count}"] = current_fighter
                    dict_entry_count += 1

    def create_id_from_link(self):
        """
        Method used to create a unique id for each entry in the table
        """
        for count, link in enumerate(self.basic_more_details):
            self.basic_more_details[count] = self.basic_more_details[count].split("/")[-1]

    def create_basic_info_dataframe(self):
        """
        Method used to build the panda dataframe based on the data that has been scraped
        """
        self.rankings_table = pd.DataFrame.from_dict(self.rankings_dict, orient="index")
        self.rankings_table.set_index("Rank", inplace=True)

    def write_dataframe_to_csv(self):
        """
        Method used to create a csv file of all the data that was scraped
        """
        self.rankings_table.to_csv("test.csv")

    def write_raw_data_to_folder(self):
        if not os.path.exists("raw_data"):
            os.mkdir("raw_data")

        with open("raw_data/data.json", "w") as fp:
            json.dump(self.rankings_dict, fp)


if __name__ == "__main__":
    scraper = WebDriver(configuration_path="config.json")
    sleep(2)
    scraper.login()
    sleep(2)
    scraper.accept_cookies()
    sleep(2)
    scraper.load_rankings_page()
    sleep(2)
    scraper.build_list_of_page_links(1)
    scraper.build_rankings_dictionary()
    scraper.create_basic_info_dataframe()
    scraper.write_dataframe_to_csv()
    scraper.write_raw_data_to_folder()


# TODO: Add method to class which retrieves a profile picture of each fighter
# TODO: Refactor the build_rankings_dictionary() method to be less computationally expensive as it currently has nested for loops
# TODO: Further abstract the class so that the config.json can be configured to scrape different websites
