from pydantic import BaseModel


class AddRepsExercisesRequest(BaseModel):
    name: str
    reps: int


class AddDurationExercisesRequest(BaseModel):
    name: str
    duration: int
