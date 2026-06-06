CREATE TABLE readings (
    reading_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id text NOT NULL,
    timestamp timestamp with time zone NOT NULL,
    temperature double precision,
    humidity double precision,
    pressure double precision,
    location text NOT NULL
);