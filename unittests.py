import unittest
import datetime
import time
from selenium import webdriver
from parameterized import parameterized_class
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.safari.webdriver import WebDriver as SafariWebDriver

# list to store the different browsers
browsers = []

chrome_options = webdriver.ChromeOptions()
# Chrome can't auto-accept geolocation requests in headless mode. If you run the tests with Chrome in headless mode,
# test_current_location fails. This is expected. Include/exclude the line below as desired.
# chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.geolocation": 1})
chrome = Service(ChromeDriverManager().install())
browsers.append((webdriver.Chrome, chrome, chrome_options))

firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument('-headless')
firefox_options.set_preference("geo.prompt.testing", True)
firefox_options.set_preference("geo.prompt.testing.allow", True)
firefox = Service(GeckoDriverManager().install())
browsers.append((webdriver.Firefox, firefox, firefox_options))


# edge_options = webdriver.EdgeOptions()
# edge_options.add_argument('headless')
# edge_options.add_experimental_option("prefs", {"profile.default_content_setting_values.geolocation": 1})
# edge = Service(EdgeChromiumDriverManager().install())
# browsers.append((webdriver.Edge, edge, edge_options))

# safari_capabilities = {"safari.options": {"useSimulatedGPS": True}}
# # safari does not support headless mode
# safari = SafariWebDriver(desired_capabilities=safari_capabilities)
# browsers.append((webdriver.Safari, safari, safari_capabilities))


class ElementHasValue:
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        return element.get_attribute("value") != ""


@parameterized_class([
    {
        "browser_class": browser_class,
        "browser": browser,
        "option": option,
    }
    for browser_class, browser, option in browsers
])
class DBikesTests(unittest.TestCase):

    # set up the browser and load the page
    def setUp(self):
        self.driver = self.browser_class(service=self.browser, options=self.option)
        self.driver.get("http://127.0.0.1:5000/")

    # test if toggle markers button is clickable
    def test_toggle_markers_button(self):
        driver = self.driver
        toggle_markers_button = driver.find_element(By.XPATH, "//button[text()=\"Toggle Markers\"]")
        toggle_markers_button.click()

    # test if search bar works
    def test_search_bar(self):
        driver = self.driver
        search_bar = driver.find_element(By.ID, "autocomplete_search")
        search_bar.send_keys("Shelbourne Hotel")
        # sleep to give search results time to load
        time.sleep(1)
        # select first result and press enter
        search_bar.send_keys(Keys.DOWN)
        search_bar.send_keys(Keys.RETURN)

        assert search_bar.get_attribute("value") == "Shelbourne Hotel, Saint Stephen's Green, Dublin, Ireland"

    # test if travel mode dropdown works, i.e. options are clickable
    def test_travel_mode(self):
        driver = self.driver
        travel_mode_dropdown = driver.find_element(By.ID, "mode")
        travel_mode_dropdown.click()
        options = travel_mode_dropdown.find_elements(By.TAG_NAME, "option")
        for option in options:
            if option.get_attribute("value") == "DRIVING":
                option.click()

    # test if looking for a bike stand button is clickable
    def test_looking_for_bike_stand_button(self):
        driver = self.driver
        bike_stand_button = driver.find_element(By.XPATH, "//button[text()=\"I'm looking for a bike stand.\"]")
        bike_stand_button.click()

    # test if looking for a bike button is clickable
    def test_looking_for_bike_button(self):
        driver = self.driver
        bike_button = driver.find_element(By.XPATH, "//button[text()=\"I'm looking for a bike.\"]")
        bike_button.click()

    # test if date/time field can be populated and the correct value is stored
    def test_datetime_input(self):
        driver = self.driver
        datetime_input = driver.find_element(By.ID, "datetime")
        datetime_input.send_keys("12052023")
        datetime_input.send_keys(Keys.TAB)
        datetime_input.send_keys("15:00")
        datetime_value = datetime_input.get_attribute("value")
        date_time_format = "%Y-%m-%dT%H:%M"

        try:
            parsed_datetime = datetime.datetime.strptime(datetime_value, date_time_format)
        except ValueError:
            self.fail("Invalid date/time value: " + datetime_value)

    # test if getting current location works
    # Chrome can't accept location request in headless mode!
    def test_current_location(self):
        driver = self.driver
        current_location_button = driver.find_element(By.XPATH, "//button[text()='Use Current Location']")
        current_location_button.click()

        WebDriverWait(driver, 10).until(
            ElementHasValue((By.ID, "autocomplete_search"))
        )

    # test if availability table is populated correctly for different date/time values
    def test_availability_table(self):
        date_time_scenarios = [
            {"date": "12052023", "time": "15:00"},
            {"date": "13061960", "time": "09:00"},
            {"date": "24122050", "time": "23:00"},
            {"date": "15042023", "time": "00:00"},
        ]

        # loop through different date/time scenarions
        for date_time_scenario in date_time_scenarios:
            with self.subTest(date=date_time_scenario["date"], time=date_time_scenario["time"]):
                self._test_availability_table_scenario(date_time_scenario)

    # helper method calling the methods to populate/check the table for each scenario
    def _test_availability_table_scenario(self, date_time_scenario):
        self._populate_time(**date_time_scenario)
        self._populate_location(location="Shelbourne Hotel")
        self._find_closest_stations()
        self._check_table()

    # helper method to populate date/time for test_availability_table
    def _populate_time(self, date, time):
        # populating the time
        driver = self.driver
        datetime_input = driver.find_element(By.ID, "datetime")
        datetime_input.send_keys(date)
        datetime_input.send_keys(Keys.TAB)
        datetime_input.send_keys(time)

    # helper method to populate location for test_availability_table
    def _populate_location(self, location):
        # populating the location
        driver = self.driver
        search_bar = driver.find_element(By.ID, "autocomplete_search")
        search_bar.send_keys(location)
        # give time for the search results to appear
        time.sleep(1)
        # select first result and press enter
        search_bar.send_keys(Keys.DOWN)
        search_bar.send_keys(Keys.RETURN)
        # give time for value to be assigned
        time.sleep(1)

    # helper method to press the find closest stations button for test_availability_table
    def _find_closest_stations(self):
        driver = self.driver
        find_closest_stations_button = driver.find_element(By.XPATH, "//button[text()='Find closest stations']")
        find_closest_stations_button.click()

        # wait until table is created
        WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.TAG_NAME, "table")))

        # give time for table to be populated with data
        time.sleep(1)

    # helper method to check table contents for test_availability_table
    def _check_table(self):
        driver = self.driver
        table = driver.find_element(By.CSS_SELECTOR, ".stations-table tbody")
        rows = table.find_elements(By.TAG_NAME, "tr")

        # list to check if any of the numeric columns is all 0s
        zero_count = [0, 0, 0, 0]

        # loop through table body
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")

            # check that station  name is not empty
            self.assertNotEqual(cells[0].text.strip(), "", "There is an empty cell in the station name column.")

            # check that there are numbers in the other columns
            for col_index in range(1, 5):
                cell_value = cells[col_index].text
                self.assertTrue(cell_value.isdigit(),
                                f"Expecting numbers in column {col_index}, but found '{cell_value}'")
                if cell_value.strip() == "0":
                    zero_count[col_index - 1] += 1

            # check the body has ten rows
            self.assertEqual(len(rows), 10, f"There are {len(rows)} instead of 10.")

            # check no column is all 0s
            for index, count in enumerate(zero_count):
                self.assertNotEqual(count, len(rows), f"All values in column {index + 1} are zeros")

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
