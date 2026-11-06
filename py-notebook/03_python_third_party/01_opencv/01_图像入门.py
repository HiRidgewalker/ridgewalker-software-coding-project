import cv2 as cv
import numpy as np

# 读取图像
img = cv.imread('./static/picture_2.jpg', 0)
img

# 显示图像

# cv.imshow('image', img)
# cv.waitKey(0)
# cv.destroyAllWindows()

cv.namedWindow('image', cv.WINDOW_NORMAL)
cv.imshow('image',img)
cv.waitKey(0)
cv.destroyAllWindows()

# 保存图像
cv.imwrite('messigray.png',img)

# 完整案例
import numpy as np
import cv2 as cv

img = cv.imread('./static/picture_2.jpg',0)
cv.imshow('image',img)
k = cv.waitKey(0)
if k == 27: # ESC 退出
    cv.destroyAllWindows()
elif k == ord('s'): # 's' 保存退出
    cv.imwrite('messigray_1.png',img)
    cv.destroyAllWindows()

# 使用matplotlib显示图像
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

img = cv.imread('./static/picture_1.png',0)
plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
plt.xticks([]), plt.yticks([]) # 隐藏 X 和 Y 轴的刻度值
plt.show()


