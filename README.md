# stinger-analysis

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
Strategy #1: 

Strategy #2: Fitting an Elipse
- Ellipse was fitted by (a) identifying the quickest-varying regions of the image, and (b) fitting an ellipse to these areas.
- Current ellipse fitting is only based on the statistical moments of the quickest-varying region: goal is to implement a more sophisticated fitting algorithm

Future Improvements and Directions
  Minor Improvements
  - Add an option to mark an image as "bad" in the front end and mark data as such in the spreadsheet
  - Read meters per pixel metadata to report size in nanometers
  - Calculate area of the nematocyst
  
  Future Directions
  - Autocrop images and flag images for review where our fit is outside some confidence window
  - Detect additional features of nematocysts
  - Host our app so others can help crop images (crowdsource!)
  - Associate measurements with associated metadata / classification
  
