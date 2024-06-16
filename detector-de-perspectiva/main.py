import sys
import math
import cv2 as cv
import numpy as np
import random


def ransac(lines, img):
   numberLines = len(lines)
   maiorSoma = 0
   pontoDeFuga = [0, 0]
   for i in range(0, 10):

      line1 = random.randint(0, numberLines-1)
      line2 = random.randint(0, numberLines-1)

      while line1 == line2:
         line2 = random.randint(0, numberLines-1)

      point = calculaPontoDeEncontro(lines[line1], lines[line2])

      if not point:
         continue
      
      x, y = point
      soma = 0
      for j in range(0, numberLines):
         if j != line1 and j != line2:
            dist = calculaDistEntrePontoReta(x, y, lines[j])
            if dist == None:
               continue
            if dist < 100:
               soma = soma + 1
      
      if soma > maiorSoma:
         maiorSoma = soma
         pontoDeFuga = [x, y]

   return pontoDeFuga


def calculaDistEntrePontoReta(x0, y0, line):
   
    rho, theta = line[0]
    if np.sin(theta)!=0:
      m = (-1*(np.cos(theta)))/np.sin(theta)
      c = rho/np.sin(theta)
      if (1 + m**2) != 0 and (1 + m**2) + c != 0:
         x = (x0 + m*y0 - m*c)/(1 + m**2)
         y = (m*x0 + (m**2)*y0 - (m**2)*c)/(1 + m**2) + c
         dist = math.sqrt((x - x0)**2 + (y - y0)**2)
         return dist
    
    return None

def calculaPontoDeEncontro(l1, l2):
   # rho e theta de cada linha
   rho1 = l1[0][0]
   theta1 = l1[0][1]
   rho2 = l2[0][0]
   theta2 = l2[0][1]

   # monta matriz com senos e cossenos
   A = np.array([
       [np.cos(theta1), np.sin(theta1)],
       [np.cos(theta2), np.sin(theta2)]
   ]) 

   # monta matriz com rhos
   b = np.array([[rho1], [rho2]])

   # calcula determinante para saber se matriz é invertível
   det_A = np.linalg.det(A)

   # se for, resolve equação linear
   if det_A != 0:
       solve = np.linalg.solve(A, b)
       x = solve[0]
       y = solve[1]
       x = int(x[0])
       y = int(y[0])

       return x, y
   else:
       return None


def detectaLinhas(img, j):
   # borra imagem
   blurImg = cv.GaussianBlur(img, [21, 21], 2.3, 2.3)
   cv.imwrite("./resultados/" + str(j) + "borrada.png", blurImg)
   
   # detecta bordas
   dst = cv.Canny(blurImg, 30, 90, None, 3)
   cv.imwrite("./resultados/" + str(j) + "canny.png", dst)
   
   # bota imagem em BGR
   cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
   
   # detecta linhas
   lines = cv.HoughLines(dst, 1, np.pi / 180, 100, None, 0, 0)
   
   # imprime linhas na imagem
   if lines is not None:
      green = 0
      red = 255
      blue = 0
      for i in range(0, len(lines)):
         rho = lines[i][0][0]
         theta = lines[i][0][1]
         a = math.cos(theta)
         b = math.sin(theta)
         x0 = a * rho
         y0 = b * rho
         pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
         pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
         cv.line(cdst, pt1, pt2, (blue, green, red), 3, cv.LINE_AA)
   
   
   cv.imwrite("./resultados/" + str(j) + "lines.png", cdst)

   return cdst, lines


def main():
 j = 1
 while j <= 8:

   if j <= 3:
      img = cv.imread("./images/image" + str(j) + ".jpeg", cv.IMREAD_GRAYSCALE)
   else: 
      img = cv.imread("./images/image" + str(j) + ".jpg", cv.IMREAD_GRAYSCALE)

   if img is None:
      print ('Error opening image!')
      return
   
   cv.imwrite("./resultados/" + str(j) + "source.png", img)
   
   imgWithLines, lines = detectaLinhas(img, j)

   x, y = ransac(lines, imgWithLines)

   img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
   img = cv.circle(img, (x,y), radius=10, color=(0, 0, 255), thickness=-1)
   
   cv.imwrite("./resultados/" + str(j) + "point.png", img)
   
   j = j + 1

 return 0
    

if __name__ == '__main__':
    main ()