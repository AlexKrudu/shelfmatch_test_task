from typing import List, Tuple
import cv2 as cv
import numpy as np

from utils import *

TOKEN_PATH = config.TOKEN_PATH
AUTH_URL = config.AUTH_URL
login = config.login
password = config.password
RECOGNITION_URL = config.RECOGNITION_URL
ROOT_FOLDER = config.ROOT_FOLDER
ASK_INTERVAL = config.ASK_INTERVAL


# Draws a frame by given points and prints a label close to it.
def draw_frame(img, points, name: str, font_scale: float, frame_thickness: float, font_thickness: float, index: int,
               offset: Tuple[int, int], frame_color: Tuple[int, int, int], text_color: Tuple[int, int, int]):
    pts = np.array([[int(points[0]['x']), int(points[0]['y'])],
                    [int(points[2]['x']), int(points[2]['y'])],
                    [int(points[3]['x']), int(points[3]['y'])],
                    [int(points[1]['x']), int(points[1]['y'])],
                    ])
    if font_scale == -1:
        text_size = cv.getTextSize(name, cv.FONT_HERSHEY_SIMPLEX, 1, 2)
        font_scale = (pts[2][0] - pts[0][0]) / (
                text_size[0][0] + 20)  # adjust text scale so it does not break the frame bounds
    img = cv.polylines(img, np.int32([pts]),
                       isClosed=True,
                       color=frame_color, thickness=frame_thickness)
    img = cv.putText(img, name, (pts[index][0] + offset[0], pts[index][1] + offset[1]),
                     cv.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness=font_thickness, bottomLeftOrigin=False)
    return img


# Draws a frame + label around all stillages, shelves and positions.
def draw_image(json, filename: str):
    img = cv.imread(filename)
    for stillage in json["session"]["stillages"]:
        img = draw_frame(img, stillage["points"], "Stillage" + str(stillage["stillageID"]), 4.5, 75, 17, 1, (75, -75),
                         (36, 255, 12), (0, 180, 150))
        for shelf in stillage['shelves']:
            img = draw_frame(img, [shelf['top']['points'][0], shelf['top']['points'][1], shelf['bot']['points'][0],
                                   shelf['bot']['points'][1]],
                             "Shelf" + str(shelf['shelfID']), 2.5, 12, 12, 0, (75, 150), (57, 20, 175), (57, 20, 175))
            for pos in shelf['positions']:
                img = draw_frame(img,
                                 [{"x": pos['x'], "y": pos['y']}, {"x": pos['x'] + pos['width'], "y": pos['y']},
                                  {"x": pos['x'], "y": pos['y'] + pos['height']},
                                  {"x": pos['x'] + pos['width'], "y": pos['y'] + pos['height']}],
                                 pos['positionLabel'], -1, 3, 3, 0, (15, 30), (255, 35, 0), (255, 35, 0))
    logging.info("Image {} has been successfully handled\n".format(filename))


# Sends an image for processing and immediately stars asking server if processing is done. When the processing is
# done, starts drawing frame and label around found classes.
def send_and_process_images(images: List[Tuple[str, str]], token: str):
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
        json = None
        while json is None:
            json = ask_server(token, session_id, img_name)
        draw_image(json, img_name)

    return sessions_id


# Asks server if processing of image is done. If it is - returns json response, None otherwise.
def ask_server(token: str, session_id: str, img_name: str):
    url = RECOGNITION_URL + "session"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get(url, params={"token": token, "sessionID": session_id}, headers=headers)
    logging.info("Asking server for session id {}... ".format(session_id))
    if response.status_code == 200:
        logging.info("Success! ")
        json = response.json()
        if json["session"]["processed"] == "PROCESSED":
            logging.info("Processing of image {} is done. \n".format(img_name))
            return json
        else:
            logging.info("Processing of image {} is not done yet. \n".format(img_name))
            return None


def main():
    init_logger("task2.log")
    token = get_token()
    if token is None:
        raise PermissionError("Unable to access token")
    images = list(map(to_base64, get_images_names("test_images")))
    if len(images) == 0:
        raise ValueError("No images found")
    if send_and_process_images(images, token) is None:
        raise ConnectionError("Error occurred while sending an for processing")


if __name__ == '__main__':
    main()
