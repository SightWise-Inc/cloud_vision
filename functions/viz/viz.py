# basics
import os
import numpy as np
import matplotlib.pyplot as plt
# computer vision
import cv2
# local modules

# # (DEV) absolute import from package
# from server.functions.viz.utils import distance 
# from server.functions.object.object import draw
# from server.functions.hand.hand import visualize_hands

# (PROD) absolute import from server-level scripts
from functions.viz.utils import distance
from functions.object.object import draw
from functions.hand.hand import visualize_hands

# Highlight image
def highlight(img, pt1, pt2):
    img = img.copy()

    alpha = 2.2 # Simple contrast control
    beta = 30    # Simple brightness control

    hl = img[pt1[1]:pt2[1],pt1[0]:pt2[0]]
    hl = np.clip(alpha*hl + beta, 0, 255) # option 1: numpy
    # hl = cv2.convertScaleAbs(hl, alpha=alpha, beta=beta) # option 2: cv2
    img[pt1[1]:pt2[1],pt1[0]:pt2[0]] = hl
    print('dtype of img:', img.dtype, '', 'dtype of hl:', hl.dtype)

    return img
# modified from https://docs.opencv.org/3.4/d3/dc1/tutorial_basic_linear_transform.html


# add mask for selective image manipulation
def add_mask(mask, pt1, pt2):
    mask[pt1[1]:pt2[1],pt1[0]:pt2[0]] = 1
    return mask


# add mask for selective image manipulation
def apply_highlight(img, weak_mask, strong_mask):
    # weak -= np.logical_and(weak, strong) # remove overlap # unnecessary because strong overwrites weak

    alpha = 2.4 # Simple contrast control
    beta = 30    # Simple brightness control

    weak = np.clip(img * alpha/1.7 + beta/2, 0, 255).astype(np.uint8)
    strong = np.clip(img * alpha + beta, 0, 255).astype(np.uint8)

    highlighted = np.where(weak_mask, weak, img)
    highlighted = np.where(strong_mask, strong, highlighted)

    return highlighted


# TODO compute these in vector computations & logical operators
# but before that, profile the server. 
# and before that, finish everything.
def draw_viz(img, objects=None, texts=None, hands=None, selection=None, cursor=None):

    # initialize highlighting masks
    weak = np.zeros(shape=img.shape)
    strong = np.zeros(shape=img.shape)
    # center = (int(img.shape[1]/2), int(img.shape[0]/2))

    # iterate through each objects 
    # (color them in a consistent, aesthetic manner)

    if objects: 
        drawn = draw(img, objects['boxes'], objects['scores'], objects['class_ids'], objects['indices'])

    if texts:
        # iterate through each text
        for i, r in enumerate(texts): 
            # print(r)
            # points
            pt1 = [int(n) for n in r[0][0]]
            pt2 = [int(n) for n in r[0][2]]
            # add highlight
            try: weak = add_mask(weak, pt1, pt2)
            except Exception: print('highlight error')

    if hands:
        img = visualize_hands(hands, img)

    # selected text/object
    if selection:
        # pt1, pt2 = [int(n) for n in selection[0][0]], [int(n) for n in selection[0][2]]
        pt1, pt2 = [int(n) for n in selection['box'][0]], [int(n) for n in selection['box'][1]]
        pt1, pt2 = tuple(pt1), tuple(pt2) # OpenCV's rectangle doesn't like coordinates given in list
        strong = add_mask(strong, pt1, pt2)
        img = cv2.rectangle(img, pt1, pt2, (255,255,255), 15) # outline

    # selection cursor
    if cursor:
        # cursor = [int(cursor[0]*img.shape[0]), int(cursor[1]*img.shape[1])]
        # cursor = [int(cursor[1]*img.shape[1]), int(cursor[0]*img.shape[0])]
        # cursor = [int(cursor[0]*img.shape[1]), int(cursor[1]*img.shape[0])]
        print('cursor:', cursor)
        img = cv2.rectangle(img, cursor, cursor, (0,100,0), 20)

    # visualization
    # img = cv2.rectangle(img, pt1, pt2, (255,255,255), 15) # TODO add outline to everything!
    highlighted = apply_highlight(img, weak, strong)

    return highlighted


def main():
    # masking
    a = np.zeros(shape=[4,4])
    a = add_mask(a, (2,2), (3,3))
    print(a)

    folder = './tests/demo_images/'
    filename = 'demodemo2.jpg'
    print(os.path.exists(folder+filename))
    img = cv2.imread(folder+filename)
    
    # highlighted = highlight(img, (926, 1478), (2021, 1756))
    # print(highlighted.dtype)
    # plt.imshow(highlighted)
    weak = add_mask(np.zeros(shape=img.shape, dtype=np.uint8), (926, 1478), (2021, 1756))
    strong = add_mask(np.zeros(shape=img.shape, dtype=np.uint8), (1026, 1578), (2121, 1856))
    plt.imshow(apply_highlight(img, weak, strong)) # test
    plt.show()


if __name__ == "__main__": main()