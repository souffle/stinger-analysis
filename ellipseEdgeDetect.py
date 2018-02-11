import cv2
import numpy as np
import matplotlib.pyplot as plt

import glob


def file2image(filename):
    # read image
    image = cv2.imread(filename)

    # who are my neighbors?
    imfl = np.sum(image, axis=2)
    plt.imshow(imfl)
    return imfl


def image2threshold(imfl, nn, lowert=20, uppert=10000):
    impad = np.ones([imfl.shape[0] + 2 * nn, imfl.shape[1] + 2 * nn]) * np.mean(imfl)
    impad[nn:(-nn), nn:(-nn)] = imfl

    # add up the neighbors
    neighbor_array = np.zeros([imfl.shape[0], imfl.shape[1], (2 * nn + 1) ** 2])
    count = 0;
    for i in np.arange(2 * nn + 1):
        for j in np.arange(2 * nn + 1):
            neighbor_array[:, :, count] = impad[i:i + imfl.shape[0], j:j + imfl.shape[1]]
            count += 1;

    # standard deviation
    sdarray = np.std(neighbor_array, axis=2).astype(np.uint8)

    # threshold of standard deviation values
    _, thre = cv2.threshold(sdarray, lowert, uppert, cv2.THRESH_BINARY)

    return thre


def calc_ellipse(thre, nn, multiplier=4):
    xy = np.nonzero(thre)
    xya = np.array([xy[0], xy[1]])

    mu = np.mean(xya, axis=1)
    sig = np.cov(xya, rowvar=1)

    eigs = np.linalg.eig(sig)
    if eigs[0][0] < eigs[0][1]:
        eigs2 = [np.array([eigs[0][1],eigs[0][0]]),[eigs[1][1],eigs[1][0]]]
        eigs = eigs2

    phi = 180 / np.pi * np.arctan2(eigs[1][1][0], eigs[1][1][1])
    width = multiplier * np.sqrt(eigs[0][0]) - 2 * nn
    height = multiplier * np.sqrt(eigs[0][1]) - 2 * nn
    mu = [mu[0], mu[1]]

    return [mu, width, height, phi]


def getEllipseArray(thre, mu, width, height, phi):
    elpsArr = np.zeros(thre.shape)

    phi2 = phi * np.pi / 180
    for i in range(thre.shape[0]):
        for j in range(thre.shape[1]):
            if 4 * (((i - mu[0]) * np.cos(phi2) + (j - mu[1]) * np.sin(phi2)) ** 2) / width ** 2 + 4 * (
                    ((j - mu[1]) * np.cos(phi2) - (i - mu[0]) * np.sin(phi2)) ** 2) / height ** 2 <= 1:
                elpsArr[i, j] = 1

    return elpsArr


def newThreshold(image, elpsArray, lowert=20):
    image2 = np.multiply(elpsArray, image) + np.median(image) * (np.ones(elpsArray.shape) - elpsArray)
    thre2 = image2threshold(image2, 5, lowert)
    return thre2


def file2ellipse(imfl, filename, plot=False):
    nn = 5
    thre = image2threshold(imfl, nn, lowert=20)
    ep = calc_ellipse(thre, nn, 5)  # ellipse_param
    elpsArr = getEllipseArray(thre, ep[0], ep[1], ep[2], ep[3])
    thre2 = newThreshold(imfl, elpsArr, lowert=20)
    ep2 = calc_ellipse(thre2, nn)
    elpsArr2 = getEllipseArray(thre, ep2[0], ep2[1], ep2[2], ep2[3])

    if plot:
        plt.imshow(imfl, cmap='Greys')
        plt.imshow(elpsArr2, alpha=0.2, cmap='Greys')
        plt.savefig("static/ellipses/{}".format(filename.replace('.jpg', '.png')))

    mux = ep2[0][1]
    muy = ep2[0][0]
    scale = np.sqrt(10000.0 / (ep2[1] * ep2[2]))
    rot = ep2[3]
    return [mux, muy, scale, rot]
