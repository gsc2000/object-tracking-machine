# AI関係
"""
Run YOLOv5 detection inference on images, videos, directories, globs, YouTube, webcam, streams, etc.

Usage - sources:
    $ python detect.py --weights yolov5s.pt --source 0                               # webcam
                                                     img.jpg                         # image
                                                     vid.mp4                         # video
                                                     screen                          # screenshot
                                                     path/                           # directory
                                                     list.txt                        # list of images
                                                     list.streams                    # list of streams
                                                     'path/*.jpg'                    # glob
                                                     'https://youtu.be/Zgi9g1ksQHc'  # YouTube
                                                     'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP stream

Usage - formats:
    $ python detect.py --weights yolov5s.pt                 # PyTorch
                                 yolov5s.torchscript        # TorchScript
                                 yolov5s.onnx               # ONNX Runtime or OpenCV DNN with --dnn
                                 yolov5s_openvino_model     # OpenVINO
                                 yolov5s.engine             # TensorRT
                                 yolov5s.mlmodel            # CoreML (macOS-only)
                                 yolov5s_saved_model        # TensorFlow SavedModel
                                 yolov5s.pb                 # TensorFlow GraphDef
                                 yolov5s.tflite             # TensorFlow Lite
                                 yolov5s_edgetpu.tflite     # TensorFlow Edge TPU
                                 yolov5s_paddle_model       # PaddlePaddle
"""

import argparse
import os
import platform
import sys
from pathlib import Path
import numpy as np

import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

# from yolov5_module.models.common import DetectMultiBackend
# from yolov5_module.utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadScreenshots, LoadStreams
# from yolov5_module.utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
#                            increment_path, non_max_suppression, print_args, scale_boxes, strip_optimizer, xyxy2xywh)
# from yolov5_module.utils.plots import Annotator, colors, save_one_box
# from yolov5_module.utils.torch_utils import select_device, smart_inference_mode

from yolov5_module.utils.augmentations import letterbox
from yolov5_module.utils.general import non_max_suppression, xyxy2xywh
from yolov5_module.models.common import DetectMultiBackend

class Object_detector():
    '''
    Yoloで推論
    '''
    # def __init__(self):

    def detect(
            self,
            weights=ROOT / 'yolov5s.pt',  # model path or triton URL
            source=ROOT / 'data/images',  # file/dir/URL/glob/screen/0(webcam)
            data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
            img = None,
            imgsz=(640, 640),  # inference size (height, width)
            conf_thres=0.0000001,  # confidence threshold
            iou_thres=0.45,  # NMS IOU threshold
            max_det=10,  # maximum detections per image
            device='cpu',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
            view_img=False,  # show results
            save_txt=False,  # save results to *.txt
            save_conf=False,  # save confidences in --save-txt labels
            save_crop=False,  # save cropped prediction boxes
            nosave=False,  # do not save images/videos
            classes=None,  # filter by class: --class 0, or --class 0 2 3
            agnostic_nms=False,  # class-agnostic NMS
            augment=False,  # augmented inference
            visualize=False,  # visualize features
            update=False,  # update all models
            project=ROOT / 'runs/detect',  # save results to project/name
            name='exp',  # save results to project/name
            exist_ok=False,  # existing project/name ok, do not increment
            line_thickness=3,  # bounding box thickness (pixels)
            hide_labels=False,  # hide labels
            hide_conf=False,  # hide confidences
            half=False,  # use FP16 half-precision inference
            dnn=False,  # use OpenCV DNN for ONNX inference
            vid_stride=1,  # video frame-rate stride
            ):
        #入力データの前処理
        img, ratio, padding = preprocess(img, imgsz, False, device)
        #モデルのインスタンス化
        model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
        # Inference
        pred = model(img, augment=augment, visualize=visualize)
        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        print(pred)
        # 出力結果の事後処理
        # return postprocess(pred)
        return 0

def preprocess(img, imgsz, fp16=False, device='cpu'):
    # リサイズ結果を取得
    img, ratio, padding = letterbox(img, imgsz)
    # Convert
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device)
    img = img.half() if fp16 else img.float()  # uint8 to fp16/32
    img /= 255  # 0 - 255 to 0.0 - 1.0
    if len(img.shape) == 3:
        img = img[None]  # expand for batch dim
    return img, ratio, padding


    # def postprocess(pred, ratio: Tuple[float, float], padding: Tuple[float, float], threshold: float, label_list: List[str], max_det) -> List[Dict[str, Any]]:
    #     # assert ratio != 0.0
    #
    #     num_detected: int = min(len(pred[0]), max_det)
    #
    #     if num_detected <= 0:
    #         return []
    #
    #     objects: List[Dict[str, Any]] = []
    #     offset_x: int = int(round(padding[0] - 0.1))
    #     offset_y: int = int(round(padding[1] - 0.1))
    #     for i in range(num_detected):
    #         x0: float = (pred[0][i][0].item() - offset_x) / ratio[0]
    #         y0: float = (pred[0][i][1].item() - offset_y) / ratio[1]
    #         x1: float = (pred[0][i][2].item() - offset_x) / ratio[0]
    #         y1: float = (pred[0][i][3].item() - offset_y) / ratio[1]
    #         xywh: Tuple[float, float, float, float] = (x0, y0, x1 - x0, y1 - y0)
    #         label_index: int = int(pred[0][i][5].item())
    #         if label_index < len(label_list):
    #             label: str = label_list[label_index]
    #         else:
    #             # REVEW: label_index >= len(label_list) の場合の処理
    #             label: str = ''
    #         score: Dict[str, float] = {'confidence': pred[0][i][4].item()}
    #
    #         objects.append({
    #             'label': label,
    #             'label_index': label_index,
    #             'score': score,
    #             'xywh': xywh,
    #         })
    #
    #     return objects
