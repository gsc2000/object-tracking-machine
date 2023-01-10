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

from yolov5_module.utils.augmentations import letterbox
from yolov5_module.utils.general import non_max_suppression, xyxy2xywh, scale_boxes
from yolov5_module.utils.plots import Annotator, colors, save_one_box
from yolov5_module.models.common import DetectMultiBackend

class Object_detector():
    '''
    Yoloで推論
    '''
    def __init__(self,
                 weights=ROOT / 'yolov5n.pt',  # model path or triton URL) -> None:
                 data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
                 device='cpu',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
                 dnn=False,  # use OpenCV DNN for ONNX inference
                 half=False,  # use FP16 half-precision inference
    ):
        self.device = device
        #モデルのインスタンス化
        self.model = DetectMultiBackend(weights, device=self.device, dnn=dnn, data=data, fp16=half)
        self.stride, self.names, self.pt = self.model.stride, self.model.names, self.model.pt

    def detect(self,
               source=ROOT / 'data/images',  # file/dir/URL/glob/screen/0(webcam)
               img = None,
               imgsz=(128, 128),  # inference size (height, width)
               conf_thres=0.25,  # confidence threshold
               iou_thres=0.45,  # NMS IOU threshold
               max_det=5,  # maximum detections per image
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
               vid_stride=1,  # video frame-rate stride
            ):
        #入力データの前処理
        im0 = img.copy()
        img, ratio, padding = preprocess(img, imgsz, False, self.device)

        # Inference
        pred = self.model(img, augment=augment, visualize=visualize)
        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        # print(pred)
        # 出力結果の事後処理
        center_pix, num_human_det = postprocess(pred, ratio, max_det)

        # GUI表示用画像作成
        for i, det in enumerate(pred):  # per image
            # seen += 1
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            annotator = Annotator(im0, line_width=line_thickness, example=str(self.names))
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                # for c in det[:, 5].unique():
                #     n = (det[:, 5] == c).sum()  # detections per class
                    # s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                        # with open(f'{txt_path}.txt', 'a') as f:
                        #     f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    # if save_img or save_crop or view_img:  # Add bbox to image
                    c = int(cls)  # integer class
                    label = None if hide_labels else (self.names[c] if hide_conf else f'{self.names[c]} {conf:.2f}')
                    annotator.box_label(xyxy, label, color=colors(c, True))
                    # if save_crop:
                    #     save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

            # Stream results
            im0 = annotator.result()
            # if view_img:
            #     if platform.system() == 'Linux' and p not in windows:
            #         windows.append(p)
            #         cv2.namedWindow(str(p), cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  # allow window resize (Linux)
            #         cv2.resizeWindow(str(p), im0.shape[1], im0.shape[0])
            #     cv2.imshow(str(p), im0)
            #     cv2.waitKey(1)  # 1 millisecond
        return im0, center_pix, num_human_det

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
    return img, ratio, padding,


def postprocess(pred, ratio, max_det):
    # assert ratio != 0.0
    center_pix = []
    num_detected: int = min(len(pred[0]), max_det)
    num_human_det = 0

    if num_detected <= 0:
        return center_pix, num_human_det

    for i in range(num_detected):
        if int(pred[0][i][5].item()) == 0:
            num_human_det += 1
            x1: float = pred[0][i][0].item() / ratio[0]
            # y0: float = (pred[0][i][1].item() - offset_y) / ratio[1]
            x2: float = pred[0][i][2].item() / ratio[0]
            # y1: float = (pred[0][i][3].item() - offset_y) / ratio[1]
            center_pix.append((x1 + x2)/2)
    return center_pix, num_human_det
