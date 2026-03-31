from app.requests.video_request import VideoRequest
from sqlmodel import Session
from app.requests.church_service_request import ChurchServiceRequest
from app.responses.add_video_response import AddVideoResponse


class MediaService:

    def __init__(self):
        pass

    def get_media(self):
        pass

    def update_services(self):
        pass

    def delete_service(self):
        pass

    def add_new_video(self, video: VideoRequest) -> AddVideoResponse:
        response: AddVideoResponse = AddVideoResponse()
        
        response.video_name = "test"
        
        return response
