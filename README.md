# Stinger Annotation

User Experience:
- The app loads a new image of nematocysts to a web app
- User manually crops the image
- 5 images displaying different measurements / methods of measurement appear based on the image.
- Image name, length, width, and length-to-width ratio are written to a spreadsheet in the project repository

Our Stack:
- Javascript front-end
- Flask receives HTTP requests from the web app
- Python backend
  - OpenCV for image processing
- Redis database keeps track of which files have been processed

Image processing techniques:

Strategy #1: Morphological Analysis
- It is challenging to use classic morphological techniques on this problem, given the transparency of the nematocysts and the blurry edges.
- Our preferred approach is to use graph cuts for segmentation of the image. The basic gist of the algorithm compares adjacent regions, with similar regions being grouped together in the foreground or background.
- Our fallback approach is to use edge detection in order to find the contour of the nematocyst, using dilation and erosion in order to account for noise. This approach is very dependent on the pixels being _just right_ though, which is why we prefer the more robust graph cut approach.
- We use statistical image moments to find the center of the nematocyst as well as to normalize its orientation and scale. This will be helpful for future techniques as it makes it easier to compare the nematocyst structures programatically.

Strategy #2: Fitting an Elipse
- Ellipse was fitted by (a) identifying the quickest-varying regions of the image, and (b) fitting an ellipse to these areas.
- Current ellipse fitting is only based on the statistical moments of the quickest-varying region: goal is to implement a more sophisticated fitting algorithm

Things we tried that were unsuccessful or need more work:
- Using Hough ellipses to identify nematocysts in an image (autocrop)

Future Improvements and Directions
  Minor Improvements
  - Add an option to mark an image as "bad" in the front end and mark data as such in the spreadsheet
  - Read meters per pixel metadata to report size in nanometers
  - Calculate area of the nematocyst
  - Continue to improve length/width detection and ellipse fit modeling
  
  Future Directions
  - Autocrop images and flag images for review where our fit is outside some confidence window
  - Detect additional features of nematocysts
    - Via PCA on normalized images
    - Via additional algorithms we write
  - Host our app so others can help crop images (crowdsource!)
  - Associate measurements with associated metadata / classification
