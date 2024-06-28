# Google Maps Data Scraper

## Description
This project is a web scraper that extracts data from Google Maps.
It uses Selenium for web automation and for retireving data.
The scraper is configured to gather information:
  Business Name
  Business type
  Email (will extract only it the website given is a facebook link and the email is provied there)
  The url of the google maps listing
  Rating of Business
  Location of Business
  Contact Number 
  Website (if provided)

This can be further configured to extract the specific reviews from each listing but this feature is currently in development and is not implemented

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration](#configuration)
4. [Contributing](#contributing)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [License](#license)
8. [Credits](#credits)
9. [Contact](#contact)

## Installation

### Prerequisites
- Python 3.x
- Firefox Browser
- FireFoxDriver (compatible with your Chrome browser version)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Rivulet004/google-maps-scraper.git
   cd google-maps-scraper

2. Create a Virtual Enviorment:
   ```bash
   python -m venv .venv
   

4. Activate the Virtual Enviorment:
   ```bash
   # windows
   .venv/Scripts/Activate.ps1
   # linux
   source venv/bin/activate
   
6. Install the required packages
   ```bash
   pip install -r requirements.txt

## Usage
  Run Scraper with the required parameters
  ```bash
  python3 main.py "Houston, TX, USA"
  or (this parse the text copied to the clipboard so make sure that the text is corrent location, using this method in not recomended"
  ```bash
  python main.py 

## Configuration
  Yet to make

## Contributing 
  Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## Testing
  (I have not implemented the tests you can help in desigingnin the tests)
  To run tests, use:
    ```bash
    python -m unittest discover tests
  Ensure that all tests pass before submitting a pull request.

## Deployment
This project is intended for local use. For deployment in a production environment, consider containerizing it with Docker and using cloud services for scalability.

## License
  This project is licensed under the MIT License - see the LICENSE file for details.

## Credits
  Rivulet004
  Selenium

## Contact
  Emails:
    mbinshafique29@gmail.com
    rivulets004@gmail.com
  Linkedin Profile:
    https://www.linkedin.com/in/muhammad-bin-shfique-b63a05210/
  Discord:
    Rivulet004
  GitHub:
    https://github.com/Rivulet004/
  
