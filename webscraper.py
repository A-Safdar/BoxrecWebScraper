from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import json
import pandas as pd


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

        # Load the url
        self.driver.get(self.__address)

        # Attributes used to handle the basic rankings table
        self.basic_links_list = []
        self.basic_ranking_list = []
        self.basic_more_details = []
        self.basic_name_list = []
        self.basic_points_list = []
        self.basic_division_list = []
        self.basic_age_list = []
        self.basic_record_list = []
        self.basic_stance_list = []
        self.basic_residence_list = []
        self.__page_links = []
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
            self.basic_links_list.append(f"{template_url}{page}")

    def build_basic_information_lists(self):
        """
        Method used to begin scraping through the website and through different pages
        """
        for page_number, link in enumerate(self.basic_links_list):
            # First page at this point is already loaded so we can ignore
            if page_number != 0:
                self.__load_page(link)

            # Process current pages data
            self.__extract_current_page_data()

            for row in self.table_row_data:
                for count, data in enumerate(row):
                    if count == 0:
                        if bool(data.text):
                            self.basic_ranking_list.append(data.text)

                    elif count == 1:
                        self.basic_name_list.append(data.text)
                        more_details_link = data.find_element(By.TAG_NAME, "a")
                        self.basic_more_details.append(more_details_link.get_attribute("href"))

                    elif count == 2:
                        self.basic_points_list.append(data.text)

                    elif count == 4:
                        self.basic_division_list.append(data.text)

                    elif count == 5:
                        self.basic_age_list.append(data.text)

                    elif count == 6:
                        self.basic_record_list.append(data.text)

                    elif count == 8:
                        self.basic_stance_list.append(data.text)

                    elif count == 9:
                        self.basic_residence_list.append(data.text)

        # Once all data has been retrieved, generate a unique id for each entry
        self.create_id_from_link()

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
        basic_rankings_info = {
            "Id": self.basic_more_details,
            "Ranking": self.basic_ranking_list,
            "Name": self.basic_name_list,
            "Division": self.basic_division_list,
            "Age": self.basic_age_list,
            "Record": self.basic_record_list,
            "Stance": self.basic_stance_list,
            "Residence": self.basic_residence_list,
        }

        self.rankings_table = pd.DataFrame.from_dict(basic_rankings_info)

    def write_dataframe_to_csv(self):
        """
        Method used to create a csv file of all the data that was scraped
        """
        self.rankings_table.to_csv("test.csv")


if __name__ == "__main__":
    scraper = WebDriver(configuration_path="config.json")
    sleep(2)
    scraper.login()
    sleep(2)
    scraper.accept_cookies()
    sleep(2)
    scraper.load_rankings_page()
    sleep(2)
    scraper.build_list_of_page_links(3)
    scraper.build_basic_information_lists()
    scraper.create_basic_info_dataframe()
    scraper.write_dataframe_to_csv()


# TODO: Add method to class which retrieves a profile picture of each fighter
# TODO: Add method which generates a v4 UUID for each entry in the dataframe
