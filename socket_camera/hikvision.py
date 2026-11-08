import socket
import os

def capture_image(str = "shot"):
    """
    shot a picture
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 8888))
        s.sendall(str.encode())
        data = s.recv(1024)
        if not data:
            return False
        print("Received:{}/n".format(repr(data)) + "======Image Saved======")
        return True

def get_latest_image(path = r"C:\Users\DELL\Desktop\photo"):
    """
    返回指定文件夹中，以指定后缀结尾的最新图片的完整路径。
    """
    image_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    files = [os.path.join(path, f) for f in os.listdir(path) 
             if os.path.isfile(os.path.join(path, f)) and f.lower().endswith(image_ext)]
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def find(obj, color):
    """
    autumatically shot a picture and find the target object
    object to be find: 1.block; 2.zhou; 
    return #label;V_D_offs_x;V_D_offs_y;V_D_offs_rz
    """
    target_action = {"pick": "1", "place": "2"}[obj]
    target_color = {"red": "1", "green": "2", "blue": "3", "yellow": "4", "orange": "5", "purple": "6"}[color]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 8888))
        s.sendall((str(target_action) + str(target_color)).encode())
        data = s.recv(1024)
        print("Received:", repr(data))
    return repr(data)

# 使用示例
if __name__ == "__main__":
    # shot
    if not capture_image("A"):
        print("NG")
    # read image
    photo_dir = r"C:\Users\DELL\Desktop\photo"
    newest_pic = get_latest_image(photo_dir)
    