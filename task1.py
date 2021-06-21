from typing import List, Tuple, Dict
from apscheduler.schedulers.blocking import BlockingScheduler

from utils import *

# scheduler needed for calling method in interval time
sched = BlockingScheduler()

TOKEN_PATH = config.TOKEN_PATH
AUTH_URL = config.AUTH_URL
login = config.login
password = config.password
RECOGNITION_URL = config.RECOGNITION_URL
ROOT_FOLDER = config.ROOT_FOLDER
ASK_INTERVAL = config.ASK_INTERVAL


# Sending images for processing. Returns array of session ids corresponding to each image, None otherwise
def send_images(images: List[Tuple[str, str]], token: str):
    sessions_id = {}
    url = RECOGNITION_URL + "session?token={}".format(token)
    for img_name, img in images:
        data = {"images": [img]}
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            return None
        session_id = response.json()["sessionID"]
        logging.info(
            "Image {} has been successfully sent. Session id: {}\n".format(img_name, session_id))
        sessions_id[session_id] = img_name
    return sessions_id


# Ask server if image processing is done. When processing of image corresponding to certain session id is done,
# session id is removed from the list. Method stops when list of session ids is empty.
def ask_server(token: str, sessions_id: Dict[str, str], elapsed: Dict[str, int]) -> None:
    if len(sessions_id) == 0:
        return
    logging.info("Started asking server if all sent images are done.")
    elems_to_remove = []
    url = RECOGNITION_URL + "session"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    for session_id, img_name in sessions_id.items():
        response = requests.get(url, params={"token": token, "sessionID": session_id}, headers=headers)
        logging.info("Asking server for session id {}... ".format(session_id))
        if response.status_code == 200:
            logging.info("Success! ")
            json = response.json()
            if json["session"]["processed"] == "PROCESSED":
                logging.info("Processing of image {} is done. \n".format(img_name))
                elems_to_remove.append(session_id)
                elapsed[session_id] = int(json["session"]["detectionTime"])
            else:
                logging.info("Processing of image {} is not done yet. \n".format(img_name))
        else:
            logging.info("Fail! Response status code: {}".format(response.status_code))
    for session_id in elems_to_remove:
        del sessions_id[session_id]
    if len(sessions_id) == 0:
        logging.info("All of images have been successfully processed")
        sched.shutdown(False)
    else:
        logging.info("Not all of images have been processed yet")


def main():
    init_logger("task1.log")
    token = get_token()
    if token is None:
        raise PermissionError("Unable to access token")
    images = list(map(to_base64, get_images_names("test_images")))
    if len(images) == 0:
        raise ValueError("No images found")
    sessions_id = send_images(images, token)
    elapsed = {}
    ask_server(token, sessions_id, elapsed)
    sched.add_job(ask_server, 'interval', args=[token, sessions_id, elapsed], seconds=ASK_INTERVAL)
    sched.start()
    logging.info("Number of processed images: {}.".format(len(elapsed)))
    logging.info("Total time elapsed: {}.".format(sum(elapsed.values())))
    logging.info("Average processing time: {}.".format(sum(elapsed.values()) / len(elapsed.values())))


if __name__ == '__main__':
    main()
