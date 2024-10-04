DROP TABLE IF EXISTS tasks;

-- Table to store exercise tasks with status as 0 (not finished) or 1 (finished)
CREATE TABLE Tasks (
    user_id INT NOT NULL,
    task_id SERIAL PRIMARY KEY,
    exercise VARCHAR(100) NOT NULL,
    reps INT NOT NULL,
    status INT CHECK (status IN (0, 1)) NOT NULL,  -- 0 for not finished, 1 for finished
    assign_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date when task is assigned
);

-- Insert initial data into Tasks table (with assign_date and status as 0 or 1)
INSERT INTO Tasks (user_id, exercise, reps, status, assign_date) 
VALUES
(1, 'Bicep Curl', 10, 1, '2024-01-10 08:30:00'),  -- Finished, assigned on 2024-01-10
(2, 'Squat', 15, 0, '2024-01-11 09:00:00'),       -- Not finished, assigned on 2024-01-11
(1, 'Push Up', 20, 1, '2024-01-12 10:00:00'),     -- Finished, assigned on 2024-01-12
(3, 'Lunges', 12, 0, '2024-01-13 11:15:00'),      -- Not finished, assigned on 2024-01-13
(2, 'Pull Up', 8, 1, '2024-01-14 12:20:00');      -- Finished, assigned on 2024-01-14