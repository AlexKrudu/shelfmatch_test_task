import os

# path to file containing token
TOKEN_PATH = os.path.join('tmp', 'shelfmatch_token')
# authentication url
AUTH_URL = 'https://oauth.shelfmatch.com/'
# login for authentication
login = 'test.task.account'
# password for authentication
password = 'Z0w7S1qAdjzDZ5'
# url for image processing
RECOGNITION_URL = "https://tea-api.shelfmatch.com/"
# folder containing images to process
ROOT_FOLDER = "test_images"
# interval of requests (for task 1)
ASK_INTERVAL = 2  # seconds
