import faceAPI.faceTool as ft
import configparser

COMMAND = {
    'add_face' : (3,ft.add_face_to_facegroup),
    'create' : (1,ft.create_face_group),
    'delete' : (2,ft.delete_face_group),
    'get' : (1,ft.get_face_group),
    'recognize' : (3,ft.recognize_face_in_facegroup),
    'take' : (0,ft.take_photo),
    'status' : (0,ft.get_led_status),
    'set' : (4,ft.set_led_status),
    'weather' : (4,ft.get_environment)
}

def face_api(command,option=None):
    command_index = COMMAND[command][0]
    action = COMMAND[command][1]
    config = configparser.ConfigParser()
    config.read('faceAPI/cht2.conf')
    apiKey = config.get('demo-key', 'apiKey')
    
    imagePath = 'faceAPI/image/verify.jpg'
    
    if command_index==0:
        response = action()
    elif command_index==1:
        response = action(apiKey=apiKey)
    elif command_index==2:
        response = action(apiKey=apiKey,GROUP_ID=option)
    elif command_index==3:
        response = action(apiKey=apiKey,GROUP_ID=option,imagePath=imagePath)
    elif command_index==4:
        response = action(option)
    return response
