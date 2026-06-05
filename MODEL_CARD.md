# UFO Country Predictor Model Card

This model predicts a likely UFO sighting country from duration, latitude, and longitude.

The classifier is for classroom deployment practice only. It is not a scientific UFO predictor. Latitude and longitude strongly reveal country-like regions, so the task is mostly a demonstration of model training, serialization, API/UI wiring, and local or Space deployment.

## Inputs

- `seconds`: sighting duration from 1 to 60
- `latitude`: decimal latitude from -90 to 90
- `longitude`: decimal longitude from -180 to 180

## Outputs

- predicted country label
- confidence for the predicted label
- probability distribution across known countries when supported by the model
