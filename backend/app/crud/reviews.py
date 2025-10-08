from crud.abstract import BaseCrud
from models.reviews import ApplicationReview


class ApplicationReviewCrud(BaseCrud):
    model = ApplicationReview