from time import sleep
from webscraper import WebDriver
from selenium.webdriver.common.by import By
import json


def main():
    # Get user login credentials
    credentials = get_credentials("scraper/credentials.json")
    # Initialise the webdrive
    scraper = WebDriver(url="https://boxrec.com", username=credentials["username"], password=credentials["password"])
    sleep(2)
    # Load login page and submit user credentials
    scraper.load_login_page(By.LINK_TEXT, "login")
    scraper.submit_login_credentials(
        username_field_by=By.ID,
        username_field_locator="username",
        password_field_by=By.ID,
        password_field_locator="password",
        submit_button_by=By.CLASS_NAME,
        submit_button_locator="submitButton",
    )
    sleep(2)
    # Accept cookies
    scraper.accept_cookies(
        container_by=By.XPATH,
        container_locator_string='//div[@id="qc-cmp2-ui"]',
        button_by=By.XPATH,
        button_locator_string='//button[contains(@class, "css-1my9mvs")]',
    )
    sleep(2)
    # Navigate to ratings page
    scraper.navigate_to_page(By.LINK_TEXT, "ratings")
    sleep(2)
    # Build links to all the pages required
    scraper.build_list_of_page_links(2)
    # Load each page one at a time and begin extracting the data
    scraper.load_pages_and_extract_data()
    # Create a pandas dataframe
    scraper.create_basic_info_dataframe()
    # Write the dataframe to a csv file
    scraper.write_dataframe_to_csv()
    # Formate and write the raw data into a json file
    scraper.write_raw_data_to_folder()


def get_credentials(credentials_path: str):
    """
    PRIVATE method used to extract relevant settings from the json config file

    Args:
        credentials_path (str): The file path where the user credentials are located

    Returns:
        username and password
    """
    with open(credentials_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
