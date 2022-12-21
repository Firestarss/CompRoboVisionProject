import numpy as np
import cv2
import copy
import pytesseract

def main():
    """
    Main function of the program. Is the entry point to the rest of the program
    """
    # Setup global variable to display the initial image and pass to various functions
    # Making it a global variable is specifically needed for the add_corner function as you can't pass img into it
    global img

    # Read the image from file and downscale it to fir on screen
    img = cv2.imread("images/IMG_1088.jpg")
    img = scale_image(30)

    # Create a clean copy of image that won't have points added to it to slice later
    clean_img = copy.deepcopy(img)

    # Set up mouse call back to register when a click occurs
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', add_corner)

    # Get the corners of the puzzle area
    get_corners()

    # transform image based on the 4 corners selected and resize it to be square
    warped = transform(clean_img)
    warped = cv2.resize(warped, (max(warped.shape), max(warped.shape)), interpolation = cv2.INTER_AREA)

    # split image into individual tiles
    tiles = split(warped)

    # Run OCR on each tile
    for tile in tiles:
        # Show each tile as they are being analyzed
        cv2.imshow("image", tile)
        extract_txt(tile)
        # require a keypress to advance to the next tile
        cv2.waitKey(0)

def extract_txt(t_img):
    """
    Takes an image and runs it through OCR to extract any text
    """

    # Pre-process the image to improve the likelyhood of recognizing text
    gray = cv2.cvtColor(t_img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    
    # Run image through pytesseract's OCR function
    value = pytesseract.image_to_string(gray)

    # If anything is found, print it. else print that nothing was found
    if len(value.strip()) > 0:
        print(value.strip())
    else:
        print("No Value Found :(")

def split(s_img, dim = 6):
    """
    Splits the input image into individual tiles. Assumes an NxN puzzle (i.e 5x5 or 3x3)

    Params:
        dim: the number of tiles on a side (i.e. if a puzzle is 5x5, dim = 5) 
    """

    # get the height and width of the original image
    imgheight=s_img.shape[0]
    imgwidth=s_img.shape[1]

    # Set up initial variables
    y1 = 0
    x1 = 0
    M = imgheight//dim
    N = imgwidth//dim

    # Step through the image and save each tile to output
    output = []
    for y in range(0,imgheight,M):
        for x in range(0, imgwidth, N):
            y1 = y + M
            x1 = x + N

            # Slice the original image into a smaller chunk
            tile = s_img[y:y1,x:x1]

            output.append(tile)

    # Slicing isn't always perfect and can generate small slivers on the ends. Filter those out
    filter = max([o.shape[0]*o.shape[1] for o in output])
    output = [o for o in output if o.shape[0]*o.shape[1] >= filter-10]
    
    return output

def get_corners():
    """
    Has user define 4 corners to bound the puzzle area
    """
    # initialize variable to track the 4 corners
    global corners
    corners = []

    # Instruct the user which order to selevt the corners
    # Order in which the corners are picked matters for the transform
    print("Please click on the corners in the following order:")
    print("\nTop-Left\nTop-Right\nBottom-Right\nBottom-Left")

    # keep picking corners until corners has been fully filled
    while len(corners) < 4:
        cv2.imshow('image',img)
        cv2.waitKey(10)

    # convert corners into a numpy array for later processing
    corners = np.array(corners, dtype = "float32")

    
def add_corner(event,x,y,flags,param):
    """
    Callback function that, on mouse click, adds the mouse's current position to the corners list
    """
    # If mouse is clicked and corners is not full
    if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
        # add mouse's current position to corners and draw a point where the click happend
        cv2.circle(img,(x,y),5,(0,0,255),-1)
        corners.append([x,y])

def scale_image(percent = 50):
    """
    Function for scaling image by a given percentage
    """

    # find the desired length & width
    width = int(img.shape[1] * percent / 100)
    height = int(img.shape[0] * percent / 100)
    dim = (width, height)

    # resize the image and output it
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return resized

def transform(t_img):
    """
    Takes 4 corners and transforms the image so that those corners form a square. The resulting image
    is effectively a "birds-eye" view of the selected area
    """

    # pull out each corner from corners
    tl, tr, br, bl = corners

    # Figure out how long the top and bottom edges are
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    # keep track of the longest edge. This will be the width of the transformed image
    maxWidth = max(int(widthA), int(widthB))

    # Figure out how tall the right and left edges are
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    # keep track of the longest edge. This will be the height of the transformed image
    maxHeight = max(int(heightA), int(heightB))

    # generate matrix with the target dimentions of the transformed image
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # generate a transformation matrix and then apply that to the input image
    M = cv2.getPerspectiveTransform(corners, dst)
    warped = cv2.warpPerspective(t_img, M, (maxWidth, maxHeight))

    # return the warped image
    return warped

if __name__ == "__main__":
    main()