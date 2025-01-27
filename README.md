
# Lost and Found System

A web application designed to track and recover lost items within a specific area. The system integrates location-based services, image recognition, and affiliate marketing to assist users in locating and managing lost items effectively.

## Features
- **Track and Recover Lost Items**: Users can report or search for lost items within a defined area.
- **Interactive Maps**: Integrated with the Leaflet library for maps and geo-encoding to mark the locations of lost or found items.
- **Object Detection**: Automatically generates item descriptions using the YOLO model and OpenCV library, making it easier for users to identify items.
- **Affiliate Shop**: Includes an affiliate shop for related products, providing recommendations for items like locks, tags, or tracking devices.

## Technologies Used
- **Backend**: Python, Django
- **Database**: SQLite
- **Frontend**: Django templates with Leaflet for maps
- **Machine Learning**: YOLO model for object detection
- **Libraries/Tools**: 
  - Leaflet.js for map visualization
  - OpenCV for image processing and item recognition

## Installation and Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/lost-and-found-system.git
   cd lost-and-found-system
   python -m venv venv
2.Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`

3.Install the required dependencies:
pip install -r requirements.txt
Run database migrations:
python manage.py migrate

4.Start the development server:
python manage.py runserver
Access the application in your browser:
http://127.0.0.1:8000
